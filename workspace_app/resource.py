"""Owns records and results. No other component opens the database."""

import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from workspace_app.common import DatasetInput, bearer, key, verify

app = FastAPI(title="Resource Service")
RESOURCE_KEY = key("RESOURCE_KEY")
DATABASE = os.environ["DATABASE"]
log = logging.getLogger("uvicorn.error")


@contextmanager
def database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def claims(token: Annotated[str, Depends(bearer)]) -> dict:
    return verify(token, RESOURCE_KEY, "resource")


def authority(c: dict, action: str, resource: int = 0):
    if c["action"] != action or c["resource"] != resource:
        raise HTTPException(403, "Grant does not cover this operation")


def owned(connection, dataset_id: int, subject: str):
    row = connection.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,)).fetchone()
    if row is None or row["owner"] != subject:
        log.info("resource denied subject=%s dataset=%s", subject, dataset_id)
        raise HTTPException(404, "Dataset unavailable")
    return row


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/datasets", status_code=201)
def create(body: DatasetInput, c: Annotated[dict, Depends(claims)]):
    authority(c, "create")
    with database() as connection:
        cursor = connection.execute(
            "INSERT INTO datasets(owner,title,values_json) VALUES(?,?,?)",
            (c["sub"], body.title, json.dumps(body.values)),
        )
        return {"id": cursor.lastrowid}


@app.get("/datasets")
def search(c: Annotated[dict, Depends(claims)], q: str = Query(default="", max_length=80)):
    authority(c, "list")
    with database() as connection:
        # Values stay data even when q contains SQL metacharacters.
        rows = connection.execute(
            "SELECT id,owner,title FROM datasets WHERE owner=? AND title LIKE ?",
            (c["sub"], "%" + q + "%"),
        ).fetchall()
        return [dict(row) for row in rows]


@app.get("/datasets/{dataset_id}")
def read(dataset_id: int, c: Annotated[dict, Depends(claims)]):
    authority(c, "read", dataset_id)
    with database() as connection:
        row = owned(connection, dataset_id, c["sub"])
        return {
            "id": row["id"],
            "title": row["title"],
            "values": json.loads(row["values_json"]),
        }


@app.get("/admin/metadata")
def metadata(c: Annotated[dict, Depends(claims)]):
    authority(c, "audit")
    if c["role"] != "admin":
        raise HTTPException(403, "Admin required")
    with database() as connection:
        return [dict(row) for row in connection.execute("SELECT id,owner,title FROM datasets")]


@app.get("/jobs/{dataset_id}")
def job_read(dataset_id: int, c: Annotated[dict, Depends(claims)]):
    authority(c, "export", dataset_id)
    with database() as connection:
        row = owned(connection, dataset_id, c["sub"])
        return {"values": json.loads(row["values_json"])}


class ExportResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    csv: str = Field(max_length=4096)


@app.put("/jobs/{dataset_id}")
def job_save(dataset_id: int, body: ExportResult, c: Annotated[dict, Depends(claims)]):
    authority(c, "export", dataset_id)
    with database() as connection:
        row = owned(connection, dataset_id, c["sub"])
        # Recompute the expected numeric serialization before trusting processor output.
        values = json.loads(row["values_json"])
        expected = "value\n" + "".join(f"{value}\n" for value in values)
        if body.csv != expected:
            raise HTTPException(422, "CSV does not match the authorized dataset")
        connection.execute(
            "INSERT INTO results(dataset_id,owner,csv) VALUES(?,?,?) "
            "ON CONFLICT(dataset_id,owner) DO UPDATE SET csv=excluded.csv",
            (dataset_id, c["sub"], body.csv),
        )
        return {"dataset_id": dataset_id, "status": "ready"}


@app.get("/results/{dataset_id}")
def result(dataset_id: int, c: Annotated[dict, Depends(claims)]):
    authority(c, "result", dataset_id)
    with database() as connection:
        row = connection.execute(
            "SELECT csv FROM results WHERE dataset_id=? AND owner=?",
            (dataset_id, c["sub"]),
        ).fetchone()
        if row is None:
            raise HTTPException(404, "Result unavailable")
        return {"csv": row["csv"]}
