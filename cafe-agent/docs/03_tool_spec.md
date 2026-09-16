# Tool Specifications

Write the spec BEFORE implementing a tool. The "Purpose" line becomes the tool description the LLM reads.

## Template
```
## Tool: <name>
- File: src/tools/<file>.py
- Purpose: <one clear sentence — this is what the LLM sees>
- Type: read | write | compute
- Parameters: <name> (<type>, required|optional) — <description>
- Returns: <example JSON>
- Errors: <when> → <example error JSON with a hint>
- Example request: "<a user sentence that should trigger this tool>"
```

---

## Tool: get_menu
- File: src/tools/menu_tools.py
- Purpose: Get all menu items with their prices in KRW and categories.
- Type: read
- Parameters: category (string, optional) — filter by "coffee", "tea", or "dessert"
- Returns: `{"items": [{"name": "latte", "price": 4500, "category": "coffee"}]}`
- Errors: unknown category → `{"error": "Unknown category 'juice'. Valid: coffee, tea, dessert."}`
- Example request: "What desserts do we sell?"

## Tool: check_stock
- File: src/tools/stock_tools.py
- Purpose: Check how many units of a menu item are left in stock.
- Type: read
- Parameters: item (string, required) — exact menu item name, e.g. "latte"
- Returns: `{"item": "latte", "quantity": 12}`
- Errors: item not found → `{"error": "Item 'mocha' not found. Call get_menu to see valid item names."}`
- Example request: "Do we still have lattes?"

## Tool: calculate
- File: src/tools/calculator.py
- Purpose: Evaluate a math expression. Use this for all prices, discounts, and totals.
- Type: compute
- Parameters: expression (string, required) — e.g. "3 * 4500 * 0.9"
- Returns: `{"expression": "3 * 4500 * 0.9", "result": 12150.0}`
- Errors: invalid expression → `{"error": "Invalid expression. Use numbers and + - * / ( ) only."}`
- Example request: "How much are 3 lattes with 10% off?"

## Tool: record_sale
- File: src/tools/sales_tools.py
- Purpose: Record a sale of a menu item. Reduces stock and adds revenue. Only call after the user confirms.
- Type: write
- Parameters: item (string, required); qty (integer, required) — must be ≥ 1
- Returns: `{"item": "latte", "qty": 2, "amount": 9000, "remaining_stock": 18}`
- Errors:
  - item not found → `{"error": "Item 'mocha' not found. Call get_menu to see valid item names."}`
  - not enough stock → `{"error": "Only 1 latte left. Cannot sell 2."}`
  - qty < 1 → `{"error": "qty must be at least 1."}`
- Example request: "Sell 2 americanos."

## Tool: get_sales_report
- File: src/tools/sales_tools.py
- Purpose: Get a summary of today's sales: total revenue, number of items sold, and best-selling item.
- Type: read
- Parameters: none
- Returns: `{"date": "2026-09-17", "total_revenue": 32000, "items_sold": 7, "best_seller": "latte"}`
- Errors: no sales → return zeros and `"best_seller": null` (not an error)
- Example request: "How did we do today?"

> Note: return a SUMMARY, not every record. Big tool results waste context.

---

## YOUR TOOL (Task 9)
Copy the template above and fill it in here.
