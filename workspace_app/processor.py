"""Has no resource signing key, database handle or account file."""
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from workspace_csv import render_csv

from workspace_app.common import bearer, key, remote, verify

app = FastAPI(title="CSV Processing Service")
PROCESSOR_KEY = key("PROCESSOR_KEY")
RESOURCE_URL = os.environ["RESOURCE_URL"]


class ExportJob(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    resource_token: str = Field(min_length=20, max_length=2048)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/export/{dataset_id}")
def export(dataset_id: int, body: ExportJob, token: Annotated[str, Depends(bearer)]):
    c = verify(token, PROCESSOR_KEY, "processor")
    if c["action"] != "process" or c["resource"] != dataset_id:
        raise HTTPException(403, "Invalid job scope")
    target = RESOURCE_URL + f"/jobs/{dataset_id}"
    data = remote("GET", target, body.resource_token)
    values = data["values"]
    if len(values) > 100 or any(type(value) is not int or abs(value) > 1_000_000 for value in values):
        raise HTTPException(502, "Invalid resource output")
    return remote("PUT", target, body.resource_token, {"csv": render_csv(values)})
