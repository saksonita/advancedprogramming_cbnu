"""Helpers to read and write data/*.json files."""
import json

from src import config


def load(name: str) -> dict:
    """Read data/<name>.json and return it as a dict."""
    path = config.DATA_DIR / f"{name}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(name: str, data: dict) -> None:
    """Write dict to data/<name>.json with indent=2, ensure_ascii=False."""
    path = config.DATA_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
