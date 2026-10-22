"""Additional negative tests at internal boundaries, not just the public API."""

import httpx
import pytest

from workspace_app.common import issue


def headers(services, subject="ali", action="export", resource=1, audience="resource", ttl=60):
    token = issue(services["keys"]["RESOURCE_KEY"], audience, subject, action, resource, ttl=ttl)
    return {"Authorization": "Bearer " + token}


@pytest.mark.parametrize(
    "subject,dataset_id,csv,expected",
    [
        ("ali", 2, "value\n40\n50\n", 404),
        ("ali", 1, "value\n999\n", 422),
        ("ali", 1, "value\n10\n20\n30\n", 200),
    ],
)
def test_job_save_owner_and_content(services, subject, dataset_id, csv, expected):
    response = httpx.put(
        services["resource"] + f"/jobs/{dataset_id}",
        headers=headers(services, subject, resource=dataset_id),
        json={"csv": csv},
        trust_env=False,
    )
    assert response.status_code == expected


@pytest.mark.parametrize("audience,ttl", [("api", 60), ("resource", -10)])
def test_resource_audience_and_expiry(services, audience, ttl):
    response = httpx.get(
        services["resource"] + "/jobs/1",
        headers=headers(services, audience=audience, ttl=ttl),
        trust_env=False,
    )
    assert response.status_code == 401


def test_direct_services_deny_without_auth(services):
    assert httpx.get(services["resource"] + "/datasets", trust_env=False).status_code == 401
    assert (
        httpx.post(
            services["processor"] + "/export/1",
            json={"resource_token": "x" * 30},
            trust_env=False,
        ).status_code
        == 401
    )


def test_wrong_processor_scope_and_malformed_job(services):
    token = issue(services["keys"]["PROCESSOR_KEY"], "processor", "ali", "process", 2)
    auth = {"Authorization": "Bearer " + token}
    assert (
        httpx.post(
            services["processor"] + "/export/1",
            headers=auth,
            json={"resource_token": "x" * 30},
            trust_env=False,
        ).status_code
        == 403
    )
    assert (
        httpx.post(
            services["processor"] + "/export/2",
            headers=auth,
            json={"resource_token": "x" * 30, "url": "http://example.invalid"},
            trust_env=False,
        ).status_code
        == 422
    )


def test_resource_schema_independently(services):
    response = httpx.post(
        services["resource"] + "/datasets",
        headers=headers(services, action="create", resource=0),
        json={"title": "Too many", "values": [1] * 101},
        trust_env=False,
    )
    assert response.status_code == 422
