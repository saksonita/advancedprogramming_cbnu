"""The agent: keeps conversation history and runs the tool-calling loop.

TODO (Task 4): implement run() following the pseudocode in docs/02_architecture.md.
TODO (Task 7): print each tool call and its result.
TODO (Task 9): trim history before sending (keep system prompt; don't split tool_call/tool pairs).
"""
import json

from src import config
from src.llm_client import chat
from src.tools import TOOL_FUNCTIONS, TOOL_SCHEMAS


class CafeAgent:
    def __init__(self):
        self.system_prompt = config.SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        self.history: list = []  # user, assistant, and tool messages (NOT the system prompt)

    def _build_context(self) -> list:
        """Return the messages to send to the LLM: system prompt + (trimmed) history."""
        # TODO (Task 9): trim self.history safely
        return [{"role": "system", "content": self.system_prompt}] + self.history

    def _execute_tool(self, name: str, arguments_json: str) -> dict:
        """Run one tool safely. Never raise: return {"error": ...} on any problem."""
        # TODO (Task 4): look up TOOL_FUNCTIONS[name], parse JSON args, call it, catch exceptions
        raise NotImplementedError("Task 4")

    def run(self, user_input: str) -> str:
        """Handle one user message and return the final answer text."""
        # TODO (Task 4): the agent loop
        raise NotImplementedError("Task 4")
