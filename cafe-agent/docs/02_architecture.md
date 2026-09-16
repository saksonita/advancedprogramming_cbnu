# Architecture

## Components
```
main.py  ──►  agent.py  ──►  llm_client.py  ──►  LLM API (Groq / xAI)
                 │
                 └──►  tools/__init__.py (registry)  ──►  tools/*.py  ──►  data/*.json
```
main.py (CLI) ──┐
                ├──►  agent.py  ──►  llm_client.py / tools
app.py  (UI)  ──┘

| File | Responsibility |
|---|---|
| `src/main.py` | CLI loop: read user input, call `agent.run()`, print answer. Type `exit` to quit. |
| `src/config.py` | Load settings from `.env` into constants. |
| `src/llm_client.py` | `chat(messages, tools)` → returns the assistant message. Nothing else. |
| `src/agent.py` | Holds message history and runs the agent loop. |
| `src/tools/__init__.py` | `TOOL_SCHEMAS` (list sent to LLM) and `TOOL_FUNCTIONS` (name → function). |
| `src/tools/*.py` | Tool implementations. Pure Python, no LLM calls. |
| `src/tools/data_store.py` | `load(name)` / `save(name, data)` helpers for `data/*.json`. |

## The agent loop (in `agent.py`)
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

## Context sent to the LLM on every call
1. **System prompt** — from `prompts/system_prompt.md` (always first, never trimmed)
2. **Tool schemas** — names, descriptions, parameters
3. **History** — user messages, assistant messages, tool results (trimmed to last `MAX_HISTORY_MESSAGES`)

Everything in this list costs tokens and affects the agent's decisions. Keep it clean.

## Data files
- `data/menu.json` — `{"latte": {"price": 4500, "category": "coffee"}, ...}` (prices in KRW)
- `data/stock.json` — `{"latte": 20, ...}`
- `data/sales.json` — `{"date": "YYYY-MM-DD", "records": [{"item": "latte", "qty": 2, "amount": 9000}]}`
