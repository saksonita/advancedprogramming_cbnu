# Instructions for AI Coding Assistant

## Project
A team-designed assistant that uses LLM tool calling (function calling).
Read `docs/01_brief.md` for the goal. The domain is the team's own idea.

## Before writing any code
1. Read `docs/02_architecture.md`.
2. Read ONLY the section of `docs/03_tool_spec.md` for the tool(s) in the current task.
3. Do ONLY the task the student names from `docs/04_tasks.md`. Never start other tasks.
4. If the tool has no spec, or the spec has unfilled `<...>` placeholders, STOP and ask the student to finish the spec. Never invent a spec.

## Rules
- Python 3.11+, `openai` SDK (OpenAI-compatible APIs: Groq or xAI).
- All settings come from `src/config.py`. Never hardcode API keys, URLs, or model names.
- One tool group per file in `src/tools/`. Register every tool in `src/tools/__init__.py`.
- Each tool file defines the function and its `<NAME>_SCHEMA`. Follow the format of `src/tools/calculator.py`.
- Tools read and write `data/*.json` only, through `src/tools/data_store.py`. No external APIs, no databases.
- Tools must NEVER raise exceptions to the agent. Return `{"error": "..."}` with a hint on what to do next.
- Tool results must be short JSON dicts. The LLM reads them, so keep them small.
- Tool descriptions in schemas must match the "Purpose" line in `docs/03_tool_spec.md` exactly.
- Schema parameter names must match the function's parameter names. `required` lists exactly the parameters with no default value.
- Keep functions under ~30 lines. Every tool function gets a docstring.
- Do not change files in `docs/` or `prompts/` unless the task says so.
- Do not change the generic files copied from the café agent: `src/config.py`, `src/llm_client.py`, `src/agent.py`, `src/main.py`, `src/app.py`, `src/tools/data_store.py`.
- Do not change `tests/test_tool_format.py` or `tests/conftest.py`.
- Do not modify the structure of the project, only add new files or modify existing ones.

## After finishing a task
- Run `python -m pytest tests/test_tool_format.py` and fix any failure for the tool you just built.
- Tick the task checkbox in `docs/04_tasks.md`.
- Tell the student in 3 bullets: what changed, which files, how to test it.
