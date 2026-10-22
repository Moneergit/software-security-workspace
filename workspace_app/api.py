"""Authenticates seeded users and delegates narrowly scoped operations."""

import hashlib
import hmac
import json
import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from workspace_app.common import (
    DatasetInput,
    LoginInput,
    bearer,
    issue,
    key,
    remote,
    verify,
)

app = FastAPI(title="Private Dataset Workspace")
USER_KEY, RESOURCE_KEY, PROCESSOR_KEY = (
    key("USER_KEY"),
    key("RESOURCE_KEY"),
    key("PROCESSOR_KEY"),
)
RESOURCE_URL = os.environ["RESOURCE_URL"]
PROCESSOR_URL = os.environ["PROCESSOR_URL"]
with open(os.environ["ACCOUNTS"], encoding="utf-8") as account_file:
    ACCOUNTS = json.load(account_file)


def session(token: Annotated[str, Depends(bearer)]) -> dict:
    c = verify(token, USER_KEY, "api")
    if c["action"] != "session" or c["sub"] not in ACCOUNTS:
        raise HTTPException(401, "Invalid session")
    c["role"] = ACCOUNTS[c["sub"]]["role"]
    return c


def grant(c, action, resource=0):
    return issue(RESOURCE_KEY, "resource", c["sub"], action, resource, c["role"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/login")
def login(body: LoginInput):
    user = ACCOUNTS.get(body.username)
    # A dummy derivation also runs for unknown accounts.
    salt = bytes.fromhex(user["salt"] if user else "00" * 16)
    digest = hashlib.scrypt(body.password.encode(), salt=salt, n=16384, r=8, p=1).hex()
    if user is None or not hmac.compare_digest(digest, user["digest"]):
        raise HTTPException(401, "Invalid credentials")
    return {
        "access_token": issue(
            USER_KEY, "api", body.username, "session", role=user["role"], ttl=900
        ),
        "token_type": "bearer",  # nosec B105: OAuth response scheme, not a password.
    }


@app.post("/datasets", status_code=201)
def create(body: DatasetInput, c: Annotated[dict, Depends(session)]):
    return remote("POST", RESOURCE_URL + "/datasets", grant(c, "create"), body.model_dump())


@app.get("/datasets")
def search(c: Annotated[dict, Depends(session)], q: str = Query(default="", max_length=80)):
    return remote("GET", RESOURCE_URL + "/datasets", grant(c, "list"), params={"q": q})


@app.get("/datasets/{dataset_id}")
def read(dataset_id: int, c: Annotated[dict, Depends(session)]):
    return remote("GET", RESOURCE_URL + f"/datasets/{dataset_id}", grant(c, "read", dataset_id))


@app.post("/datasets/{dataset_id}/export")
def export(dataset_id: int, c: Annotated[dict, Depends(session)]):
    process_token = issue(PROCESSOR_KEY, "processor", c["sub"], "process", dataset_id)
    return remote(
        "POST",
        PROCESSOR_URL + f"/export/{dataset_id}",
        process_token,
        {"resource_token": grant(c, "export", dataset_id)},
    )


@app.get("/results/{dataset_id}")
def result(dataset_id: int, c: Annotated[dict, Depends(session)]):
    return remote("GET", RESOURCE_URL + f"/results/{dataset_id}", grant(c, "result", dataset_id))


@app.get("/admin/metadata")
def metadata(c: Annotated[dict, Depends(session)]):
    if c["role"] != "admin":
        raise HTTPException(403, "Admin required")
    return remote("GET", RESOURCE_URL + "/admin/metadata", grant(c, "audit"))
