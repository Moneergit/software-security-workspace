"""Dependency gate tests are separate from optional malicious-package experiments."""

import hashlib
import json

import pytest

from scripts.check_artifacts import verify_artifacts


@pytest.mark.parametrize("mutation", ["changed", "unexpected", "missing", "valid"])
def test_dependency_inventory(tmp_path, mutation):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    artifact = wheels / "approved.whl"
    artifact.write_bytes(b"approved synthetic artifact")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({artifact.name: hashlib.sha256(artifact.read_bytes()).hexdigest()})
    )
    if mutation == "changed":
        artifact.write_bytes(b"different bytes")
    elif mutation == "unexpected":
        (wheels / "unapproved.whl").write_bytes(b"extra")
    elif mutation == "missing":
        artifact.unlink()
    if mutation == "valid":
        assert verify_artifacts(wheels, manifest) == 1
    else:
        with pytest.raises(ValueError):
            verify_artifacts(wheels, manifest)
