"""Run every test on a temporary copy of data/ so real data is never changed."""
import shutil
from pathlib import Path

import pytest

from src import config


@pytest.fixture(autouse=True)
def temp_data(tmp_path, monkeypatch):
    shutil.copytree(Path(config.PROJECT_ROOT) / "data", tmp_path / "data")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    yield tmp_path / "data"
