# 아키텍처 (Architecture)

## 구성 요소 (Components)
```
main.py  ──►  agent.py  ──►  llm_client.py  ──►  LLM API (Groq / xAI)
                 │
                 └──►  tools/__init__.py (registry)  ──►  tools/*.py  ──►  data/*.json
```
main.py (CLI) ──┐
                ├──►  agent.py  ──►  llm_client.py / tools
app.py  (UI)  ──┘

| 파일 (File) | 역할 (Responsibility) |
|---|---|
| `src/main.py` | CLI 루프: 사용자 입력을 읽고, `agent.run()`을 호출한 뒤 답을 출력. `exit` 입력 시 종료. (CLI loop: read user input, call `agent.run()`, print answer. Type `exit` to quit.) |
| `src/config.py` | `.env`에서 설정을 읽어와 상수로 로드. (Load settings from `.env` into constants.) |
| `src/llm_client.py` | `chat(messages, tools)` → 어시스턴트 메시지를 반환. 그 외 기능 없음. (`chat(messages, tools)` → returns the assistant message. Nothing else.) |
| `src/agent.py` | 메시지 히스토리를 보관하고 에이전트 루프를 실행. (Holds message history and runs the agent loop.) |
| `src/tools/__init__.py` | `TOOL_SCHEMAS`(LLM에 보낼 목록)와 `TOOL_FUNCTIONS`(이름 → 함수). (`TOOL_SCHEMAS` (list sent to LLM) and `TOOL_FUNCTIONS` (name → function).) |
| `src/tools/*.py` | 도구 구현. 순수 Python, LLM 호출 없음. (Tool implementations. Pure Python, no LLM calls.) |
| `src/tools/data_store.py` | `data/*.json`를 위한 `load(name)` / `save(name, data)` 헬퍼. (`load(name)` / `save(name, data)` helpers for `data/*.json`.) |

## 에이전트 루프 (The agent loop, in `agent.py`)
```
add user message to history
repeat up to MAX_TOOL_ROUNDS:
    response = chat(system_prompt + history, TOOL_SCHEMAS)
    add response to history
    if response has no tool_calls:
        return response.content          # final answer
    for each tool_call:
        result = TOOL_FUNCTIONS[name](**arguments)   # catch errors → {"error": ...}
        add {"role": "tool", "tool_call_id": id, "content": json(result)} to history
return "Sorry, I could not finish this request."
```

## 매 호출마다 LLM에 전달되는 컨텍스트 (Context sent to the LLM on every call)
1. **시스템 프롬프트 (System prompt)** — `prompts/system_prompt.md`에서 가져옴 (항상 맨 앞에 위치, 절대 잘리지 않음) (always first, never trimmed)
2. **도구 스키마 (Tool schemas)** — 이름, 설명, 파라미터 (names, descriptions, parameters)
3. **히스토리 (History)** — 사용자 메시지, 어시스턴트 메시지, 도구 결과 (최근 `MAX_HISTORY_MESSAGES`개로 잘라냄) (trimmed to last `MAX_HISTORY_MESSAGES`)

이 목록에 들어가는 모든 것은 토큰 비용을 발생시키고 에이전트의 판단에 영향을 줍니다. 깔끔하게 유지하세요.
Everything in this list costs tokens and affects the agent's decisions. Keep it clean.

## 데이터 파일 (Data files)
- `data/menu.json` — `{"latte": {"price": 4500, "category": "coffee"}, ...}` (가격 단위: 원, prices in KRW)
- `data/stock.json` — `{"latte": 20, ...}`
- `data/sales.json` — `{"date": "YYYY-MM-DD", "records": [{"item": "latte", "qty": 2, "amount": 9000}]}`
