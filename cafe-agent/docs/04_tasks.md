# Tasks

Do ONE task at a time. After each task: run tests, try the scenario, and make sure you understand the code.

Prompt for your AI assistant:
> Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.

## Part 1 — Foundation
- [ ] **1. Config & LLM client.** Implement `src/config.py` (load `.env`) and `src/llm_client.py` (`chat(messages, tools=None)`). Check: `python -m src.llm_client` prints a reply to "Hello".
- [ ] **2. Data store.** Implement `load()` and `save()` in `src/tools/data_store.py`. Check: `pytest tests/test_tools.py -k data_store`.

## Part 2 — First tool & the agent loop
- [ ] **3. get_menu.** Implement it in `menu_tools.py` and register its schema in `tools/__init__.py`. Check: `pytest -k get_menu`.
- [ ] **4. Agent loop.** Implement `run()` in `src/agent.py` following `docs/02_architecture.md`, and `src/main.py`. Check: Scenario A.

## Part 3 — Many tools
- [ ] **5. check_stock + calculate.** Implement and register. Check: `pytest -k "stock or calculate"`, Scenario B.
- [ ] **6. record_sale + get_sales_report.** Implement and register. Check: `pytest -k sale`, Scenarios C and D.
- [ ] **7a. Make the agent visible.** In `agent.py`, print each tool call and a short result like `🔧 check_stock({"item": "latte"}) → {"quantity": 12}`. Check: run Scenario C and read the steps.
- [ ] **7b. Chat UI.** Change `run()` to return `{"answer": str, "steps": [...]}`
  where each step is a tool name, arguments, and result. Update main.py for the new format.
  Build `src/app.py` with Streamlit: chat history, input box, and each step shown
  in a collapsible "🔧 Tool calls" section. Check: Scenario C in the browser.

## Part 4 — Context engineering
- [ ] **8. Robustness.** Run Scenario E (errors). If the agent fails, improve the tool error messages or `prompts/system_prompt.md` (not the code).
- [ ] **9. History trimming.** Keep the system prompt always, but only send the last `MAX_HISTORY_MESSAGES` messages. Never cut between an assistant tool_call message and its tool results. Check: Scenario F.
- [ ] **10. Description experiment.** Change `check_stock`'s description to "does stuff". Run Scenario B. What happens? Restore it and write 2 sentences about why in `tests/scenarios.md`.

## Part 5 — Your own tool
- [ ] **11. Design your tool.** Write its spec in `docs/03_tool_spec.md` FIRST (ideas: `add_menu_item`, `apply_coupon`, `restock_item`, `get_weather` with fake data).
- [ ] **12. Build it.** Implement, register, test. Write a scenario that needs your tool plus at least 2 other tools.
