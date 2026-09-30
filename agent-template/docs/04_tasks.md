# Tasks

Do ONE task at a time. Part 1 is for your team: think and write, no AI assistant, no code.

Prompt for your AI assistant (Part 2 only):
> Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.

## Part 0 — Setup
- [ ] **0. Copy the generic files.** Follow the Setup steps in `README.md`. Check: `python -m pytest tests/test_tool_format.py` runs, and only `test_team_has_four_new_tools` fails.

## Part 1 — Design (no code)
- [ ] **1. Brief.** Fill in `docs/01_brief.md`. Check: a classmate from another team can say who the user is and what the agent does.
- [ ] **2. Data.** Create your `data/*.json` files by hand with 5–10 realistic entries. List them in `docs/02_architecture.md` under "Data files".
- [ ] **3. Tool map.** Fill in the "Tool map" table in `docs/03_tool_spec.md`. Check the requirements in `ASSIGNMENT.md` and do the reskin test.
- [ ] **4. Tool specs.** Each member writes the spec for the tool they own in `docs/03_tool_spec.md`. Every error needs a hint.
- [ ] **5. Scenarios.** Fill in `tests/scenarios.md`: a 3-tool chain, an error recovery, a confirmation before a write.

## Part 2 — Build (one tool per prompt)
- [ ] **6. System prompt.** Fill in `prompts/system_prompt.md`.
- [ ] **7. Tool 1:** `<name>`. Implement, write the schema, register it in `src/tools/__init__.py`, add one ok test and one error test to `tests/test_tools.py`. Check: `python -m pytest tests -k <name>`.
- [ ] **8. Tool 2:** `<name>`. Same steps.
- [ ] **9. Tool 3:** `<name>`. Same steps.
- [ ] **10. Tool 4:** `<name>`. Same steps.
- [ ] **11. More tools (optional).** Same steps.

## Part 3 — Verify
- [ ] **12. Format check.** `python -m pytest tests` passes with no failures.
- [ ] **13. Scenarios.** Run every scenario with `python -m src.main`. If the agent picks the wrong tool or gives up after an error, improve the tool description, the error hint, or the system prompt — not the agent code.
- [ ] **14. Demo.** Practice the 3-minute demo in `ASSIGNMENT.md`. Every member can explain their own tool.
