"""Load project settings from the .env file.

TODO (Task 1):
- Use python-dotenv to load .env from the project root.
- Expose these constants: API_KEY, BASE_URL, MODEL, MAX_TOOL_ROUNDS (int), MAX_HISTORY_MESSAGES (int).
- Expose PROJECT_ROOT, DATA_DIR, SYSTEM_PROMPT_PATH as pathlib.Path objects.
- If API_KEY is missing, raise a clear error telling the student to copy .env.example to .env.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.md"

# TODO: load .env and define API_KEY, BASE_URL, MODEL, MAX_TOOL_ROUNDS, MAX_HISTORY_MESSAGES
