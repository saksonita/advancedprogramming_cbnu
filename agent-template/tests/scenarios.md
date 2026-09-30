# Test Scenarios

Run `python -m src.main` and type each prompt. Compare the tool calls with the expected ones.
The exact order may vary slightly; what matters is that the agent uses tools instead of guessing.

Write these BEFORE you build the tools (Task 5). Rows A–C are required.

| # | Kind | Prompt | Expected tool calls | What to check |
|---|---|---|---|---|
| A | 3 tools in a row | <prompt> | `<tool>` → `<tool>` → `<tool>` | <the correct final answer> |
| B | Error recovery | <prompt with a wrong name or value> | `<tool>` → error → `<tool>` | Recovers, explains the problem |
| C | Confirm before write | <prompt> | (asks to confirm) → `<write tool>` | Confirms first, data changes after "yes" |
| D | <your choice> | <prompt> | <...> | <...> |

> After testing a write tool, reset your data: restore the changed `data/*.json` files. Keep a copy of `data/` before you start testing.
