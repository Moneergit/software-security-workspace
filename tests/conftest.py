"""Shared isolated cluster fixture."""

import shutil
from pathlib import Path

import pytest

from scripts.run import cluster


@pytest.fixture(scope="module")
def services(tmp_path_factory):
    directory = tmp_path_factory.mktemp("services")
    with cluster(directory) as running:
        yield running
    output = Path("reports")
    output.mkdir(exist_ok=True)
    for log in directory.glob("*.log"):
        shutil.copy(log, output / log.name)
