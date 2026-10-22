"""Real HTTP regression tests; fixtures start independent server processes."""

import json

import httpx
import pytest

from workspace_app.common import issue


@pytest.fixture
def client(services):
    with httpx.Client(base_url=services["api"], timeout=10, trust_env=False) as connection:
        yield connection


def auth(client, username="ali"):
    response = client.post(
        "/login", json={"username": username, "password": username + "-demo-password"}
    )
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}


def test_three_processes(services):
    assert len(set(services["pids"])) == 3


def test_create_list_read(client):
    headers = auth(client)
    response = client.post(
        "/datasets", headers=headers, json={"title": "New data", "values": [1, 2]}
    )
    assert response.status_code == 201
    dataset_id = response.json()["id"]
    assert client.get(f"/datasets/{dataset_id}", headers=headers).json()["values"] == [
        1,
        2,
    ]
    assert all(row["owner"] == "ali" for row in client.get("/datasets", headers=headers).json())


def test_export_all_three_and_result_isolation(client):
    headers = auth(client)
    assert client.post("/datasets/1/export", headers=headers).status_code == 200
    assert client.get("/results/1", headers=headers).json() == {"csv": "value\n10\n20\n30\n"}
    assert client.get("/results/1", headers=auth(client, "john")).status_code == 404


def test_v1_sql_injection(client):
    response = client.get("/datasets", params={"q": "' OR 1=1 --"}, headers=auth(client))
    assert response.status_code == 200
    assert all(row["owner"] == "ali" for row in response.json()), json.dumps(response.json())


def test_v2_cross_user_read(client):
    response = client.get("/datasets/2", headers=auth(client))
    assert response.status_code == 404, response.text


def test_v3_row_quota(client):
    response = client.post(
        "/datasets",
        headers=auth(client),
        json={"title": "Oversized", "values": [1] * 101},
    )
    assert response.status_code == 422, response.text


def test_v4_confused_deputy_export(client):
    response = client.post("/datasets/2/export", headers=auth(client))
    assert response.status_code == 404, response.text


@pytest.mark.parametrize("username,expected", [("ali", 403), ("admin", 200)])
def test_admin_metadata(client, username, expected):
    response = client.get("/admin/metadata", headers=auth(client, username))
    assert response.status_code == expected
    if expected == 200:
        assert all(set(row) == {"id", "owner", "title"} for row in response.json())
        assert client.get("/datasets/1", headers=auth(client, username)).status_code == 404


@pytest.mark.parametrize("path", ["/datasets", "/datasets/1", "/results/1", "/admin/metadata"])
def test_missing_authentication(client, path):
    assert client.get(path).status_code == 401


def test_wrong_password_and_unknown_user(client):
    for username in ["ali", "unknown"]:
        assert (
            client.post("/login", json={"username": username, "password": "wrong"}).status_code
            == 401
        )


@pytest.mark.parametrize("kind", ["expired", "audience", "signature", "missing_claim", "action"])
def test_bad_user_token(client, services, kind):
    key = services["keys"]["USER_KEY"]
    token = issue(
        key,
        "wrong" if kind == "audience" else "api",
        "ali",
        "wrong" if kind == "action" else "session",
        ttl=-10 if kind == "expired" else 60,
    )
    if kind == "signature":
        token = issue("untrusted" * 8, "api", "ali", "session")
    if kind == "missing_claim":
        import jwt

        token = jwt.encode({"sub": "ali"}, key, algorithm="HS256")
    assert client.get("/datasets", headers={"Authorization": "Bearer " + token}).status_code == 401


@pytest.mark.parametrize(
    "action,resource,path",
    [
        ("read", 1, "/datasets/2"),
        ("create", 0, "/datasets/1"),
        ("export", 1, "/jobs/2"),
    ],
)
def test_resource_scope(services, action, resource, path):
    token = issue(services["keys"]["RESOURCE_KEY"], "resource", "ali", action, resource)
    response = httpx.get(
        services["resource"] + path,
        headers={"Authorization": "Bearer " + token},
        trust_env=False,
    )
    assert response.status_code == 403


def test_processor_cannot_forge_resource_grant(services):
    token = issue(services["keys"]["PROCESSOR_KEY"], "resource", "ali", "read", 2)
    assert (
        httpx.get(
            services["resource"] + "/datasets/2",
            headers={"Authorization": "Bearer " + token},
            trust_env=False,
        ).status_code
        == 401
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "", "values": [1]},
        {"title": "X", "values": [True]},
        {"title": "X", "values": [1_000_001]},
        {"title": "X", "values": [1], "owner": "john"},
    ],
)
def test_malformed_dataset(client, payload):
    assert client.post("/datasets", headers=auth(client), json=payload).status_code == 422


def test_direct_resource_owner_and_role(services):
    key = services["keys"]["RESOURCE_KEY"]
    for action, resource, path, expected in [
        ("read", 2, "/datasets/2", 404),
        ("audit", 0, "/admin/metadata", 403),
        ("export", 2, "/jobs/2", 404),
    ]:
        token = issue(key, "resource", "ali", action, resource)
        assert (
            httpx.get(
                services["resource"] + path,
                headers={"Authorization": "Bearer " + token},
                trust_env=False,
            ).status_code
            == expected
        )
