# 🧩 Agent Template — Team Project Starter

한국어: [README.ko.md](README.ko.md)

An empty agent in the same format as the café agent. Your team brings the idea.
Read `ASSIGNMENT.md` first.

## Setup
```bash
cp -r agent-template my-agent    # name it after your idea
cd my-agent
```

Copy the generic files from your team's best **finished** café agent. They work for any agent:
```bash
CAFE=../cafe-agent               # path to the finished café agent
cp $CAFE/src/config.py $CAFE/src/llm_client.py $CAFE/src/agent.py $CAFE/src/main.py $CAFE/src/app.py src/
cp $CAFE/src/tools/data_store.py src/tools/
cp $CAFE/.env .env               # or: cp .env.example .env, then add your API key
```

Then:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> `src/app.py` may still say "Café" in its title. Change the title text. Do not change anything else in the copied files.

> The `*.ko.md` files are Korean versions of the documents. Teams working in Korean: see `README.ko.md`. Other teams can ignore them.

## Run
```bash
python -m src.main                              # chat with the agent
streamlit run src/app.py                        # chat in the browser
python -m pytest tests/test_tool_format.py      # check the format of every tool
python -m pytest tests                          # format check + your own tool tests
```

## How to work on this project
1. Open `docs/04_tasks.md` and do the next unchecked task.
2. Design tasks (Part 1) are for your team, not for the AI assistant.
3. For build tasks, ask your AI coding assistant:
   > Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.
4. After every tool: run the format checker.
5. Understand the code before moving on. You will be asked to explain it.

## What is already here, and what you write
| Already here | Copied from the café agent | Your team writes |
|---|---|---|
| `src/tools/calculator.py` | `src/config.py`, `src/llm_client.py` | `docs/01_brief.md`, `docs/03_tool_spec.md` |
| `src/tools/__init__.py` (registry) | `src/agent.py`, `src/main.py`, `src/app.py` | `data/*.json` |
| `tests/test_tool_format.py` | `src/tools/data_store.py` | `src/tools/<your>_tools.py` |
| `AGENTS.md`, `docs/02_architecture.md` | | `prompts/system_prompt.md`, `tests/scenarios.md`, `tests/test_tools.py` |
