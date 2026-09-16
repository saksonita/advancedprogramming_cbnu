"""Helpers to read and write data/*.json files.

TODO (Task 2):
- load(name) -> dict: read data/<name>.json (name like "menu", "stock", "sales").
- save(name, data) -> None: write dict to data/<name>.json with indent=2, ensure_ascii=False.
Use config.DATA_DIR. Always use encoding="utf-8".
"""


def load(name: str) -> dict:
    raise NotImplementedError("Task 2")


def save(name: str, data: dict) -> None:
    raise NotImplementedError("Task 2")
