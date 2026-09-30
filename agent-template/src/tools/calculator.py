"""Calculator tool (reused from Week 1). ALREADY IMPLEMENTED — use it as the example for other tools."""
import ast
import operator

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported")


def calculate(expression: str) -> dict:
    """Safely evaluate a math expression with + - * / and parentheses."""
    try:
        result = _eval(ast.parse(expression, mode="eval").body)
        return {"expression": expression, "result": result}
    except ZeroDivisionError:
        return {"error": "Division by zero."}
    except Exception:
        return {"error": "Invalid expression. Use numbers and + - * / ( ) only."}


CALCULATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a math expression. Use this for all prices, discounts, and totals.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression, e.g. '3 * 4500 * 0.9'"}
            },
            "required": ["expression"],
        },
    },
}
