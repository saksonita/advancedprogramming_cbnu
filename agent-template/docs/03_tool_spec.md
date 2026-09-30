# Tool Specifications

Write the spec BEFORE implementing a tool. The "Purpose" line becomes the tool description the LLM reads.

## Template
```
## Tool: <name>
- Owner: <team member who can explain this tool>
- File: src/tools/<file>.py
- Purpose: <one clear sentence — this is what the LLM sees>
- Type: read | write | compute
- Parameters: <name> (<type>, required|optional) — <description>
- Returns: <example JSON>
- Errors: <when> → <example error JSON with a hint>
- Example request: "<a user sentence that should trigger this tool>"
```

## Where each spec line goes in the code
| Spec line | Becomes |
|---|---|
| name | function name, `"name"` in the schema, key in `TOOL_FUNCTIONS` — all three identical |
| Purpose | `"description"` in the schema, word for word |
| Parameters | the function's parameters, and `"properties"` in the schema |
| required / optional | `"required"` in the schema; optional parameters get a default value in the function |
| Returns | the dict the function returns on success |
| Errors | the `{"error": "..."}` dict the function returns, plus one test |
| Example request | one row in `tests/scenarios.md` |

## Tool map
Fill this in first. It shows on one screen whether your tools can chain.

| Tool | Type | Owner | Often used after / before |
|---|---|---|---|
| calculate | compute | (given) | after any tool that returns numbers |
| <name> | <type> | <owner> | <...> |
| <name> | <type> | <owner> | <...> |
| <name> | <type> | <owner> | <...> |
| <name> | <type> | <owner> | <...> |

---

## Tool: calculate
- Owner: (given — already implemented, use it as the example)
- File: src/tools/calculator.py
- Purpose: Evaluate a math expression. Use this for all prices, discounts, and totals.
- Type: compute
- Parameters: expression (string, required) — e.g. "3 * 4500 * 0.9"
- Returns: `{"expression": "3 * 4500 * 0.9", "result": 12150.0}`
- Errors: invalid expression → `{"error": "Invalid expression. Use numbers and + - * / ( ) only."}`
- Example request: "How much are 3 lattes with 10% off?"

---

## YOUR TOOLS (Tasks 3–4)
Copy the template once per tool and fill it in here. At least 4 tools: one `read`, one `write`, and one with no café equivalent.

> Note: return a SUMMARY, not every record. Big tool results waste context.
