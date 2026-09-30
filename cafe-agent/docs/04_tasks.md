# 작업 목록 (Tasks)

한 번에 하나의 작업만 진행하세요. 각 작업 후에는 테스트를 실행하고, 시나리오를 직접 시도해보고, 코드를 이해했는지 확인하세요.
Do ONE task at a time. After each task: run tests, try the scenario, and make sure you understand the code.

AI 어시스턴트에게 줄 프롬프트 (Prompt for your AI assistant):
> Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.

## Part 1 — 기반 다지기 (Foundation)
- [x] **1. Config & LLM client.** `src/config.py`(`.env` 로드)와 `src/llm_client.py`(`chat(messages, tools=None)`)를 구현하세요. (Implement `src/config.py` (load `.env`) and `src/llm_client.py` (`chat(messages, tools=None)`).) 확인 (Check): `python -m src.llm_client`가 "Hello"에 대한 응답을 출력하는지 확인.
- [x] **2. Data store.** `src/tools/data_store.py`에 `load()`와 `save()`를 구현하세요. (Implement `load()` and `save()` in `src/tools/data_store.py`.) 확인 (Check): `pytest tests/test_tools.py -k data_store`.

## Part 2 — 첫 도구와 에이전트 루프 (First tool & the agent loop)
- [x] **3. get_menu.** `menu_tools.py`에 구현하고 `tools/__init__.py`에 스키마를 등록하세요. (Implement it in `menu_tools.py` and register its schema in `tools/__init__.py`.) 확인 (Check): `pytest -k get_menu`.
- [x] **4. Agent loop.** `docs/02_architecture.md`를 따라 `src/agent.py`의 `run()`과 `src/main.py`를 구현하세요. (Implement `run()` in `src/agent.py` following `docs/02_architecture.md`, and `src/main.py`.) 확인 (Check): 시나리오 A (Scenario A).

## Part 3 — 여러 도구 (Many tools)
- [x] **5. check_stock + calculate.** 구현하고 등록하세요. (Implement and register.) 확인 (Check): `pytest -k "stock or calculate"`, 시나리오 B (Scenario B).
- [x] **6. record_sale + get_sales_report.** 구현하고 등록하세요. (Implement and register.) 확인 (Check): `pytest -k sale`, 시나리오 C, D (Scenarios C and D).
- [x] **7a. 에이전트 동작을 눈에 보이게 만들기 (Make the agent visible).** `agent.py`에서 각 도구 호출과 짧은 결과를 출력하세요. 예: `🔧 check_stock({"item": "latte"}) → {"quantity": 12}`. (In `agent.py`, print each tool call and a short result like `🔧 check_stock({"item": "latte"}) → {"quantity": 12}`.) 확인 (Check): 시나리오 C를 실행하고 단계별 출력을 읽어보기.
- [x] **7b. 채팅 UI (Chat UI).** `run()`이 `{"answer": str, "steps": [...]}` 형태를 반환하도록 변경하세요.
  각 step은 도구 이름, 인자, 결과로 구성됩니다. `main.py`도 새 형식에 맞게 업데이트하세요.
  (Change `run()` to return `{"answer": str, "steps": [...]}` where each step is a tool name, arguments, and result. Update main.py for the new format.)
  Streamlit으로 `src/app.py`를 만드세요: 채팅 히스토리, 입력창, 그리고 각 step을 접이식(collapsible)
  "🔧 Tool calls" 섹션에 표시. (Build `src/app.py` with Streamlit: chat history, input box, and each step shown
  in a collapsible "🔧 Tool calls" section.) 확인 (Check): 브라우저에서 시나리오 C (Scenario C in the browser).

## Part 4 — 컨텍스트 엔지니어링 (Context engineering)
- [x] **8. Robustness.** 시나리오 E(오류)를 실행해보세요. 에이전트가 실패하면 도구 오류 메시지나 `prompts/system_prompt.md`를 개선하세요 (코드 자체는 건드리지 말 것). (Run Scenario E (errors). If the agent fails, improve the tool error messages or `prompts/system_prompt.md` (not the code).)
- [x] **9. History trimming.** 시스템 프롬프트는 항상 유지하되, 최근 `MAX_HISTORY_MESSAGES`개의 메시지만 전송하세요. 어시스턴트의 tool_call 메시지와 그 도구 결과 사이는 절대 자르지 마세요. (Keep the system prompt always, but only send the last `MAX_HISTORY_MESSAGES` messages. Never cut between an assistant tool_call message and its tool results.) 확인 (Check): 시나리오 F (Scenario F).
- [x] **10. Description experiment.** `check_stock`의 설명을 "does stuff"로 바꿔보세요. 시나리오 B를 실행하면 어떻게 되나요? 원래대로 되돌리고, `tests/scenarios.md`에 왜 그런지 두 문장으로 적으세요. (Change `check_stock`'s description to "does stuff". Run Scenario B. What happens? Restore it and write 2 sentences about why in `tests/scenarios.md`.)

## Part 5 — 나만의 도구 (Your own tool)
- [x] **11. Design your tool.** `docs/03_tool_spec.md`에 명세부터 작성하세요 (아이디어 예시: `add_menu_item`, `apply_coupon`, `restock_item`, 가짜 데이터를 쓰는 `get_weather`). (Write its spec in `docs/03_tool_spec.md` FIRST (ideas: `add_menu_item`, `apply_coupon`, `restock_item`, `get_weather` with fake data).)
- [x] **12. Build it.** 구현하고, 등록하고, 테스트하세요. 내가 만든 도구를 포함해 최소 2개 이상의 다른 도구가 필요한 시나리오를 작성하세요. (Implement, register, test. Write a scenario that needs your tool plus at least 2 other tools.)
