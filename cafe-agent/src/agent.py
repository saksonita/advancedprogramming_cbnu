"""The agent: keeps conversation history and runs the tool-calling loop."""
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
        return [{"role": "system", "content": self.system_prompt}] + self._trim_history(self.history)

    @staticmethod
    def _trim_history(history: list) -> list:
        """Keep only the last MAX_HISTORY_MESSAGES messages, never starting mid tool_call/tool pair."""
        if len(history) <= config.MAX_HISTORY_MESSAGES:
            return history
        cut = len(history) - config.MAX_HISTORY_MESSAGES
        while cut < len(history) and history[cut]["role"] == "tool":
            cut += 1
        return history[cut:]

    @staticmethod
    def _parse_args(arguments_json: str) -> dict:
        try:
            return json.loads(arguments_json) if arguments_json else {}
        except json.JSONDecodeError:
            return {}

    def _execute_tool(self, name: str, arguments_json: str) -> dict:
        """Run one tool safely. Never raise: return {"error": ...} on any problem."""
        func = TOOL_FUNCTIONS.get(name)
        if func is None:
            return {"error": f"Unknown tool '{name}'."}
        args = self._parse_args(arguments_json)
        try:
            return func(**args)
        except Exception as e:
            return {"error": f"Tool '{name}' failed: {e}"}

    @staticmethod
    def _message_to_dict(response) -> dict:
        """Convert the assistant response object into a plain dict for history."""
        message = {"role": "assistant", "content": response.content}
        if response.tool_calls:
            message["tool_calls"] = [tc.model_dump() for tc in response.tool_calls]
        return message

    def run(self, user_input: str) -> dict:
        """Handle one user message. Returns {"answer": str, "steps": [...]}."""
        self.history.append({"role": "user", "content": user_input})
        steps = []
        for _ in range(config.MAX_TOOL_ROUNDS):
            response = chat(self._build_context(), TOOL_SCHEMAS)
            self.history.append(self._message_to_dict(response))
            if not response.tool_calls:
                return {"answer": response.content, "steps": steps}
            for tc in response.tool_calls:
                args = self._parse_args(tc.function.arguments)
                result = self._execute_tool(tc.function.name, tc.function.arguments)
                print(f"🔧 {tc.function.name}({args}) → {result}")
                steps.append({"tool": tc.function.name, "arguments": args, "result": result})
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
        return {"answer": "Sorry, I could not finish this request.", "steps": steps}
