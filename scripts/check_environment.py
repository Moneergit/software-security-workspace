"""Reject unlisted installed distributions and missing/wrong versions."""

import importlib.metadata
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def main():
    expected = {"workspace-csv": "1.0.0"}
    for line in (ROOT / "requirements.txt").read_text().splitlines():
        name, version = line.split("==")
        expected[normalize(name)] = version
    actual = {normalize(d.metadata["Name"]): d.version for d in importlib.metadata.distributions()}
    if actual != expected:
        raise RuntimeError(
            f"Installed dependency inventory differs: expected {expected}; actual {actual}"
        )
    print(f"PASS: all {len(expected)} installed distributions match the approved inventory")


if __name__ == "__main__":
    main()
