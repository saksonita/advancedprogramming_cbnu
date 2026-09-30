# Team Practice — Build Your Own Agent

한국어: [ASSIGNMENT.ko.md](ASSIGNMENT.ko.md)

You built the café agent. Now your team invents a new one.

**Keep the format. Change the idea.**

The agent loop, the LLM client, and the config do not know anything about coffee. You will copy them unchanged. Everything that made the café agent a *café* agent was in the brief, the tool specs, the tools, the data, and the system prompt. Those are the parts you write.

## What your team makes

An assistant for a user and a problem you choose. For example: a dorm laundry room, a club treasurer, a pet clinic front desk, a study planner. These are only starters. An idea nobody else has is the best kind.

## Requirements

Your agent must have:

- [ ] **At least 4 new tools.** `calculate` is already there and does not count.
- [ ] **All three types:** at least one `read`, one `write`, and one `compute` tool. (`calculate` can be your compute tool.)
- [ ] **One tool with no café equivalent.** See "The reskin test" below.
- [ ] **A spec for every tool** in `docs/03_tool_spec.md`, written *before* the code.
- [ ] **Local JSON data only** in `data/`. Fake data is fine (fake weather, fake prices).
- [ ] **A write tool that asks first.** The agent confirms with the user before it changes data.
- [ ] **Three scenarios** in `tests/scenarios.md`:
  - one that needs 3 tools in a row,
  - one where a tool returns an error and the agent recovers,
  - one that shows the confirmation before a write.
- [ ] **The format checker passes:** `python -m pytest tests/test_tool_format.py`

## The reskin test

Take your tool list and replace your nouns with café words. If you get the café agent back, you have a reskin.

| Tool list | Verdict |
|---|---|
| `get_books`, `check_copies`, `record_loan`, `get_loan_report` | Reskin. This is the café agent with books. |
| `get_books`, `check_copies`, `record_loan`, `find_next_return_date`, `suggest_similar_book` | Good. The last two only make sense in a library. |

Ask: *what does my user need that a café owner never needs?* That answer is your most interesting tool.

## Team roles

Work in teams of 2. Each of you owns two tools: you write their specs, and you can explain their code.

| Role | Job |
|---|---|
| Lead | Writes `docs/01_brief.md`. Decides what is in and out of scope. |
| Designer | Keeps `docs/03_tool_spec.md` consistent. Checks that tools can chain. |
| Driver | Types the prompts for the AI coding assistant. One tool at a time. |
| Tester | Writes tests and scenarios. Runs the format checker after every tool. |

With two people, one of you is Lead and Designer. The other is Driver and Tester.

## Steps

Follow `docs/04_tasks.md`. In short:

| Step | What you do | Time |
|---|---|---|
| 1. Idea | Pick a user and a problem. Fill in `docs/01_brief.md`. | 10 min |
| 2. Design | Write data files (`data/*.json`), tool specs (`docs/03_tool_spec.md`), and scenarios (`tests/scenarios.md`). **No code yet.** | 25 min |
| 3. Build | One tool at a time: implement, write the schema, register, test. | 45 min |
| 4. Verify | Run the format checker. Run all three scenarios. | 10 min |
| 5. Demo | Show it to the class. | 3 min per team |

## Demo (3 minutes)

1. Say the user and the problem in one sentence.
2. Run your 3-tool scenario live. Show the tool calls.
3. Run your error scenario live.
4. The instructor picks one team member and one tool. That person explains the code.

## Common mistakes

- **Coding before the spec.** The Purpose line in the spec is the description the LLM reads. Write it first.
- **One giant tool.** `manage_library(action, ...)` is hard for the LLM to use. Make small tools with one job each.
- **Returning everything.** A tool that returns 200 records wastes context. Return a summary.
- **Errors with no hint.** `{"error": "not found"}` stops the agent. `{"error": "Book 'Dune 2' not found. Call search_books to see valid titles."}` lets it recover.
- **Asking the AI assistant for everything at once.** One tool per prompt. Check it. Then the next.
