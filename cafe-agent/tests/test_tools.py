"""Tool tests. No LLM needed. Tests for unfinished tasks will fail — that's expected.
Run one group:  python -m pytest tests -k get_menu
"""
from src.tools.calculator import calculate


# ---- Already done ----
def test_calculate_ok():
    assert calculate("3 * 4500 * 0.9")["result"] == 12150.0


def test_calculate_error_has_hint():
    assert "error" in calculate("import os")


# ---- Task 2 ----
def test_data_store_roundtrip():
    from src.tools import data_store
    data = data_store.load("stock")
    data["latte"] = 99
    data_store.save("stock", data)
    assert data_store.load("stock")["latte"] == 99


# ---- Task 3 ----
def test_get_menu_all():
    from src.tools.menu_tools import get_menu
    assert len(get_menu()["items"]) == 6


def test_get_menu_category():
    from src.tools.menu_tools import get_menu
    items = get_menu("dessert")["items"]
    assert {i["name"] for i in items} == {"cheesecake", "croissant"}


def test_get_menu_bad_category():
    from src.tools.menu_tools import get_menu
    assert "error" in get_menu("juice")


# ---- Task 5 ----
def test_check_stock_ok():
    from src.tools.stock_tools import check_stock
    assert check_stock("latte") == {"item": "latte", "quantity": 20}


def test_check_stock_not_found_hint():
    from src.tools.stock_tools import check_stock
    assert "get_menu" in check_stock("mocha")["error"]


# ---- Task 6 ----
def test_record_sale_ok():
    from src.tools.sales_tools import record_sale
    r = record_sale("latte", 2)
    assert r["amount"] == 9000 and r["remaining_stock"] == 18


def test_record_sale_not_enough_stock():
    from src.tools.sales_tools import record_sale
    assert "error" in record_sale("croissant", 1)


def test_record_sale_bad_qty():
    from src.tools.sales_tools import record_sale
    assert "error" in record_sale("latte", 0)


def test_sales_report_summary():
    from src.tools.sales_tools import get_sales_report, record_sale
    record_sale("latte", 2)
    record_sale("americano", 1)
    r = get_sales_report()
    assert r["total_revenue"] == 12500 and r["items_sold"] == 3 and r["best_seller"] == "latte"


def test_sales_report_empty():
    from src.tools.sales_tools import get_sales_report
    assert get_sales_report()["best_seller"] is None


# ---- Registry check (run after Task 6) ----
def test_registry_consistent():
    from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS
    names = {s["function"]["name"] for s in TOOL_SCHEMAS}
    assert names == set(TOOL_FUNCTIONS)
    assert len(names) >= 5
