"""Tool registry: the single place where tools are connected to the agent.

TOOL_SCHEMAS   -> sent to the LLM (what the model can SEE)
TOOL_FUNCTIONS -> used by agent.py (what actually RUNS)

When you add a tool: import its function and schema, then add both below.
"""
from src.tools.calculator import CALCULATE_SCHEMA, calculate

# TODO (Tasks 8-12): from src.tools.<your>_tools import <NAME>_SCHEMA, <name>

TOOL_SCHEMAS = [
    CALCULATE_SCHEMA,
]

TOOL_FUNCTIONS = {
    "calculate": calculate,
}
