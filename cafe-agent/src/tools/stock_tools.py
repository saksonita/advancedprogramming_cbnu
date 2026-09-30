"""Stock tools."""
from src.tools.data_store import load, save


def check_stock(item: str) -> dict:
    """Check how many units of a menu item are left in stock."""
    stock = load("stock")
    if item not in stock:
        return {"error": f"Item '{item}' not found. Call get_menu to see valid item names."}
    return {"item": item, "quantity": stock[item]}


CHECK_STOCK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_stock",
        "description": "Check how many units of a menu item are left in stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Exact menu item name, e.g. 'latte'"}
            },
            "required": ["item"],
        },
    },
}


def restock_item(item: str, qty: int) -> dict:
    """Add units to a menu item's stock when a delivery arrives."""
    if qty < 1:
        return {"error": "qty must be at least 1."}
    stock = load("stock")
    if item not in stock:
        return {"error": f"Item '{item}' not found. Call get_menu to see valid item names."}
    stock[item] += qty
    save("stock", stock)
    return {"item": item, "added": qty, "new_quantity": stock[item]}


RESTOCK_ITEM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "restock_item",
        "description": "Add units to a menu item's stock when a delivery arrives.",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {"type": "string", "description": "Exact menu item name, e.g. 'croissant'"},
                "qty": {"type": "integer", "description": "Units to add, must be at least 1"},
            },
            "required": ["item", "qty"],
        },
    },
}
