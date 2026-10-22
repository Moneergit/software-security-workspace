"""Small shared protocol helpers; each process receives only its own keys."""
import os
import time
import uuid

import httpx
import jwt
from fastapi import Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field


class DatasetInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str = Field(min_length=1, max_length=80)
    values: list[int]  # V3 intentionally missing the row quota at this milestone.


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    username: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=128)


def issue(key: str, audience: str, subject: str, action: str, resource: int = 0,
          role: str = "user", ttl: int = 60) -> str:
    now = int(time.time())
    return jwt.encode({"iss": "workspace-api", "aud": audience, "sub": subject,
                       "action": action, "resource": resource, "role": role,
                       "iat": now, "exp": now + ttl, "jti": uuid.uuid4().hex},
                      key, algorithm="HS256")


def verify(token: str, key: str, audience: str) -> dict:
    try:
        return jwt.decode(token, key, algorithms=["HS256"], audience=audience,
                          issuer="workspace-api", options={"require": [
                              "exp", "iat", "sub", "aud", "iss", "action", "resource", "role", "jti"]})
    except jwt.InvalidTokenError as exc:
        raise HTTPException(401, "Invalid or expired credential") from exc


def bearer(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer credential required")
    return authorization[7:]


def remote(method: str, url: str, token: str, body=None, params=None):
    """Fixed service URLs, bounded wait, no proxy inheritance or redirects."""
    try:
        with httpx.Client(timeout=5, trust_env=False, follow_redirects=False) as client:
            response = client.request(method, url, headers={"Authorization": "Bearer " + token},
                                      json=body, params=params)
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Service unavailable") from exc
    if response.status_code >= 300:
        raise HTTPException(response.status_code if response.status_code < 500 else 502,
                            "Downstream request rejected")
    return response.json()


def key(name: str) -> str:
    value = os.environ[name]
    if len(value) < 32:
        raise RuntimeError("Service keys must contain at least 32 characters")
    return value
