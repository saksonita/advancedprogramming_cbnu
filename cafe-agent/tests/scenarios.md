# Test Scenarios

Run `python -m src.main` and type each prompt. Compare the tool calls with the expected ones.
The exact order may vary slightly; what matters is that the agent uses tools instead of guessing.

| # | Prompt | Expected tool calls | What to check |
|---|---|---|---|
| A | What coffee drinks do we have? | `get_menu(category="coffee")` | Lists 3 coffees with prices |
| B | Do we have enough vanilla latte for 3 cups? | `check_stock` | Says only 2 left |
| C | A customer wants 3 lattes with 10% off. How much, and do we have enough? | `get_menu` → `check_stock` → `calculate` | 12,150 KRW, enough stock |
| D | Sell 2 americanos, then tell me today's revenue. | (asks to confirm) → `record_sale` → `get_sales_report` | Confirms first, revenue 7,000 |
| E | How many mochas are left? | `check_stock` → error → `get_menu` | Recovers, says mocha isn't on the menu |
| F | Chat for 15+ turns, then ask "what did I first ask?" | — | No crash; notice what the agent forgets after trimming |

> After testing D, reset data: set `records` in `data/sales.json` to `[]` and restore `data/stock.json`.

## Task 10 notes (description experiment)
_Write your observations here._

## My scenario (Task 12)
| Prompt | Expected tool calls | What to check |
|---|---|---|
|  |  |  |
