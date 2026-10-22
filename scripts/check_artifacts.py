"""Validate the exact consumer-approved artifact inventory before installation."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify_artifacts(directory: Path, manifest: Path):
    approved = json.loads(manifest.read_text(encoding="utf-8"))
    actual = {path.name for path in directory.iterdir() if path.is_file()}
    if actual != set(approved):
        raise ValueError("Unapproved or missing artifact in vendor inventory")
    for name, digest in approved.items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Artifact digest mismatch: " + name)
    return len(approved)


def main():
    count = verify_artifacts(ROOT / "vendor", ROOT / "dependencies.sha256.json")
    with zipfile.ZipFile(ROOT / "vendor/workspace_csv-1.0.0-py3-none-any.whl") as wheel:
        if (
            wheel.read("workspace_csv/__init__.py")
            != (ROOT / "helper/src/workspace_csv/__init__.py").read_bytes()
        ):
            raise ValueError("Helper source does not match approved wheel")
    print(f"PASS: exact inventory and SHA-256 verified for {count} wheels; helper source matches")


if __name__ == "__main__":
    main()
