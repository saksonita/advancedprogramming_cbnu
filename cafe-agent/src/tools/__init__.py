"""Tool registry: the single place where tools are connected to the agent.

TOOL_SCHEMAS   -> sent to the LLM (what the model can SEE)
TOOL_FUNCTIONS -> used by agent.py (what actually RUNS)

When you add a tool: import its function and schema, then add both below.
"""
from src.tools.calculator import CALCULATE_SCHEMA, calculate
from src.tools.menu_tools import GET_MENU_SCHEMA, get_menu
from src.tools.sales_tools import (
    GET_SALES_REPORT_SCHEMA,
    RECORD_SALE_SCHEMA,
    get_sales_report,
    record_sale,
)
from src.tools.stock_tools import (
    CHECK_STOCK_SCHEMA,
    RESTOCK_ITEM_SCHEMA,
    check_stock,
    restock_item,
)

TOOL_SCHEMAS = [
    CALCULATE_SCHEMA,
    GET_MENU_SCHEMA,
    CHECK_STOCK_SCHEMA,
    RESTOCK_ITEM_SCHEMA,
    RECORD_SALE_SCHEMA,
    GET_SALES_REPORT_SCHEMA,
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
    "get_menu": get_menu,
    "check_stock": check_stock,
    "restock_item": restock_item,
    "record_sale": record_sale,
    "get_sales_report": get_sales_report,
}
