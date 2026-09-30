"""Menu tools."""
from src.tools.data_store import load


def get_menu(category: str | None = None) -> dict:
    """Get all menu items with prices (KRW) and categories, optionally filtered by category."""
    menu = load("menu")
    valid_categories = list(dict.fromkeys(info["category"] for info in menu.values()))
    if category is not None and category not in valid_categories:
        return {"error": f"Unknown category '{category}'. Valid: {', '.join(valid_categories)}."}
    items = [
        {"name": name, "price": info["price"], "category": info["category"]}
        for name, info in menu.items()
        if category is None or info["category"] == category
    ]
    return {"items": items}


GET_MENU_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_menu",
        "description": "Get all menu items with their prices in KRW and categories.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Filter by category: coffee, tea, or dessert.",
                }
            },
            "required": [],
        },
    },
}
