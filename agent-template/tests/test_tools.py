"""Tool tests. No LLM needed. Add at least one ok test and one error test per tool.
Run one group:  python -m pytest tests -k calculate
"""
from src.tools.calculator import calculate


# ---- Already done ----
def test_calculate_ok():
    assert calculate("3 * 4500 * 0.9")["result"] == 12150.0


def test_calculate_error_has_hint():
    assert "error" in calculate("import os")


# ---- Task 7: <tool name> ----
# def test_<tool>_ok():
#     from src.tools.<your>_tools import <tool>
#     assert <tool>(<good input>) == <the "Returns" example from your spec>
#
#
# def test_<tool>_error_has_hint():
#     from src.tools.<your>_tools import <tool>
#     assert "<name of the tool the hint points to>" in <tool>(<bad input>)["error"]
