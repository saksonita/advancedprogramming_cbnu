# Instructions for AI Coding Assistant

## Project
A command-line café manager assistant that uses LLM tool calling (function calling).
Read `docs/01_brief.md` for the goal.

## Before writing any code
1. Read `docs/02_architecture.md`.
2. Read ONLY the section of `docs/03_tool_spec.md` for the tool(s) in the current task.
3. Do ONLY the task the student names from `docs/04_tasks.md`. Never start other tasks.

## Rules
- Python 3.11+, `openai` SDK (OpenAI-compatible APIs: Groq or xAI).
- All settings come from `src/config.py`. Never hardcode API keys, URLs, or model names.
- One tool group per file in `src/tools/`. Register every tool in `src/tools/__init__.py`.
- Tools read and write `data/*.json` only. No external APIs, no databases.
- Tools must NEVER raise exceptions to the agent. Return `{"error": "..."}` with a hint on what to do next.
- Tool results must be short JSON dicts. The LLM reads them, so keep them small.
- Tool descriptions in schemas must match the "Purpose" line in `docs/03_tool_spec.md`.
- Keep functions under ~30 lines. Every tool function gets a docstring.
- Do not change files in `docs/` or `prompts/` unless the task says so.
- Do not modify the structure of the project, only add new files or modify existing ones.
- The UI (src/app.py) only calls CafeAgent.run() and displays results.
- No tool logic, no LLM calls, no JSON file access in the UI.
- Keep the CafeAgent in st.session_state so history survives reruns.

## After finishing a task
- Tick the task checkbox in `docs/04_tasks.md`.
- Tell the student in 3 bullets: what changed, which files, how to test it.
