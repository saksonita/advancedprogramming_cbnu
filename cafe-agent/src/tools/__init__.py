"""Tool registry: the single place where tools are connected to the agent.

TOOL_SCHEMAS   -> sent to the LLM (what the model can SEE)
TOOL_FUNCTIONS -> used by agent.py (what actually RUNS)

When you add a tool: import its function and schema, then add both below.
"""
from src.tools.calculator import CALCULATE_SCHEMA, calculate

# TODO (Task 3): from src.tools.menu_tools import GET_MENU_SCHEMA, get_menu
# TODO (Task 5): from src.tools.stock_tools import CHECK_STOCK_SCHEMA, check_stock
# TODO (Task 6): from src.tools.sales_tools import ...

TOOL_SCHEMAS = [
    CALCULATE_SCHEMA,
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
}
