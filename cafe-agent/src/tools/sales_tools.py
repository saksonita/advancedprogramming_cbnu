"""Sales tools."""
from src.tools.data_store import load, save


def record_sale(item: str, qty: int) -> dict:
    """Record a sale: reduce stock, add a record with the amount to sales.json."""
    menu = load("menu")
    if item not in menu:
        return {"error": f"Item '{item}' not found. Call get_menu to see valid item names."}
    if qty < 1:
        return {"error": "qty must be at least 1."}
    stock = load("stock")
    if stock.get(item, 0) < qty:
        return {"error": f"Only {stock.get(item, 0)} {item} left. Cannot sell {qty}."}
    amount = menu[item]["price"] * qty
    stock[item] -= qty
    save("stock", stock)
    sales = load("sales")
    sales.setdefault("records", []).append({"item": item, "qty": qty, "amount": amount})
    save("sales", sales)
    return {"item": item, "qty": qty, "amount": amount, "remaining_stock": stock[item]}


RECORD_SALE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "record_sale",
        "description": (
            "Record a sale of a menu item. Reduces stock and adds revenue. "
            "Only call after the user confirms."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Exact menu item name, e.g. 'latte'"},
                "qty": {"type": "integer", "description": "Number of units sold, must be at least 1"},
            },
            "required": ["item", "qty"],
        },
    },
}


def get_sales_report() -> dict:
    """Return a SHORT summary of today's sales (not every record)."""
    sales = load("sales")
    records = sales.get("records", [])
    if not records:
        return {"date": sales.get("date"), "total_revenue": 0, "items_sold": 0, "best_seller": None}
    total_revenue = sum(r["amount"] for r in records)
    items_sold = sum(r["qty"] for r in records)
    qty_by_item: dict = {}
    for r in records:
        qty_by_item[r["item"]] = qty_by_item.get(r["item"], 0) + r["qty"]
    best_seller = max(qty_by_item, key=qty_by_item.get)
    return {
        "date": sales.get("date"),
        "total_revenue": total_revenue,
        "items_sold": items_sold,
        "best_seller": best_seller,
    }


GET_SALES_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_sales_report",
        "description": (
            "Get a summary of today's sales: total revenue, number of items sold, and best-selling item."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}
