"""Sales tools. TODO (Task 6): implement record_sale, get_sales_report and their schemas per docs/03_tool_spec.md."""


def record_sale(item: str, qty: int) -> dict:
    """Record a sale: reduce stock, add a record with the amount to sales.json."""
    raise NotImplementedError("Task 6")


def get_sales_report() -> dict:
    """Return a SHORT summary of today's sales (not every record)."""
    raise NotImplementedError("Task 6")


RECORD_SALE_SCHEMA = None
GET_SALES_REPORT_SCHEMA = None
