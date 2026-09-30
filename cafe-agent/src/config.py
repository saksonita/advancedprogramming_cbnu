"""Load project settings from the .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.md"

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

if not API_KEY:
    raise ValueError(
        "API_KEY is missing. Copy .env.example to .env and add your API key."
    )
