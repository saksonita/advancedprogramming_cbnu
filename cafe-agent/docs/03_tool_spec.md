# 도구 명세 (Tool Specifications)

도구를 구현하기 **전에** 명세부터 작성하세요. "Purpose" 줄이 곧 LLM이 읽게 될 도구 설명이 됩니다.
Write the spec BEFORE implementing a tool. The "Purpose" line becomes the tool description the LLM reads.

## 템플릿 (Template)
```
## Tool: <name>
- File: src/tools/<file>.py
- Purpose: <한 문장으로 명확하게 — LLM이 보게 될 설명> (<one clear sentence — this is what the LLM sees>)
- Type: read | write | compute
- Parameters: <name> (<type>, required|optional) — <description>
- Returns: <example JSON>
- Errors: <when> → <example error JSON with a hint>
- Example request: "<이 도구를 호출하게 만들 사용자 문장> (a user sentence that should trigger this tool)"
```

---

## Tool: get_menu
- File: src/tools/menu_tools.py
- Purpose: 원화(KRW) 가격과 카테고리를 포함한 전체 메뉴 항목을 가져옵니다. (Get all menu items with their prices in KRW and categories.)
- Type: read
- Parameters: category (string, optional) — "coffee", "tea", "dessert" 중 하나로 필터링 (filter by "coffee", "tea", or "dessert")
- Returns: `{"items": [{"name": "latte", "price": 4500, "category": "coffee"}]}`
- Errors: 알 수 없는 카테고리 (unknown category) → `{"error": "Unknown category 'juice'. Valid: coffee, tea, dessert."}`
- Example request: "What desserts do we sell?" (디저트 뭐 있어요?)

## Tool: check_stock
- File: src/tools/stock_tools.py
- Purpose: 메뉴 항목의 재고 수량을 확인합니다. (Check how many units of a menu item are left in stock.)
- Type: read
- Parameters: item (string, required) — 정확한 메뉴 항목명, 예: "latte" (exact menu item name, e.g. "latte")
- Returns: `{"item": "latte", "quantity": 12}`
- Errors: 항목을 찾을 수 없음 (item not found) → `{"error": "Item 'mocha' not found. Call get_menu to see valid item names."}`
- Example request: "Do we still have lattes?" (라떼 아직 있어요?)

## Tool: calculate
- File: src/tools/calculator.py
- Purpose: 수식을 계산합니다. 모든 가격, 할인, 합계 계산에 이 도구를 사용하세요. (Evaluate a math expression. Use this for all prices, discounts, and totals.)
- Type: compute
- Parameters: expression (string, required) — 예: "3 * 4500 * 0.9" (e.g. "3 * 4500 * 0.9")
- Returns: `{"expression": "3 * 4500 * 0.9", "result": 12150.0}`
- Errors: 잘못된 수식 (invalid expression) → `{"error": "Invalid expression. Use numbers and + - * / ( ) only."}`
- Example request: "How much are 3 lattes with 10% off?" (라떼 3잔 10% 할인하면 얼마예요?)

## Tool: record_sale
- File: src/tools/sales_tools.py
- Purpose: 메뉴 항목의 판매를 기록합니다. 재고를 줄이고 매출을 추가합니다. 사용자가 확인한 뒤에만 호출하세요. (Record a sale of a menu item. Reduces stock and adds revenue. Only call after the user confirms.)
- Type: write
- Parameters: item (string, required); qty (integer, required) — 1 이상이어야 함 (must be ≥ 1)
- Returns: `{"item": "latte", "qty": 2, "amount": 9000, "remaining_stock": 18}`
- Errors:
  - 항목을 찾을 수 없음 (item not found) → `{"error": "Item 'mocha' not found. Call get_menu to see valid item names."}`
  - 재고 부족 (not enough stock) → `{"error": "Only 1 latte left. Cannot sell 2."}`
  - qty < 1 → `{"error": "qty must be at least 1."}`
- Example request: "Sell 2 americanos." (아메리카노 2잔 판매요.)

## Tool: get_sales_report
- File: src/tools/sales_tools.py
- Purpose: 오늘의 매출 요약(총매출, 판매 개수, 베스트셀러)을 가져옵니다. (Get a summary of today's sales: total revenue, number of items sold, and best-selling item.)
- Type: read
- Parameters: none
- Returns: `{"date": "2026-09-17", "total_revenue": 32000, "items_sold": 7, "best_seller": "latte"}`
- Errors: 판매 없음 (no sales) → 0값과 `"best_seller": null` 반환 (오류 아님) (return zeros and `"best_seller": null` (not an error))
- Example request: "How did we do today?" (오늘 매출 어때요?)

> 참고 (Note): 모든 레코드가 아니라 요약(SUMMARY)을 반환하세요. 큰 도구 결과는 컨텍스트를 낭비합니다. (return a SUMMARY, not every record. Big tool results waste context.)

---

## 내가 만든 도구 (YOUR TOOL) (Task 9)

## Tool: restock_item
- File: src/tools/stock_tools.py
- Purpose: 배송이 도착했을 때 메뉴 항목의 재고를 늘립니다. (Add units to a menu item's stock when a delivery arrives.)
- Type: write
- Parameters: item (string, required) — 정확한 메뉴 항목명 (exact menu item name); qty (integer, required) — 추가할 수량, 1 이상이어야 함 (units to add, must be ≥ 1)
- Returns: `{"item": "croissant", "added": 15, "new_quantity": 15}`
- Errors:
  - 항목을 찾을 수 없음 (item not found) → `{"error": "Item 'mocha' not found. Call get_menu to see valid item names."}`
  - qty < 1 → `{"error": "qty must be at least 1."}`
- Example request: "We just got 15 more croissants delivered." (크루아상 15개가 방금 배송됐어요.)
