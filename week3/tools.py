"""
tools.py
고급 비즈니스 프로그래밍 · 3주차 실습 1 — 도구를 평범한 함수로 작성하기
Advanced Business Programming · Week 3 Practice 1 — Tools as Plain Functions

슬라이드 05(도구란 무엇인가)와 18(좋은 도구 설계 원칙)을 코드로 옮긴 예제입니다.
This mirrors slide 05 (What is a tool) and slide 18 (Tool design principles).

핵심 규칙 (the rule that matters):
    잘못된 입력에서 예외를 던지지 말고, 모델이 읽고 고칠 수 있는
    오류 메시지를 "결과로" 돌려준다.
    Don't raise on bad input — RETURN an error the model can read and fix.

이 파일은 LLM을 전혀 호출하지 않습니다. python3 tools.py 로 바로 실행해 보세요.
This file calls no LLM. Just run: python3 tools.py
"""

import csv
import re
from pathlib import Path

DATA = Path(__file__).parent / "data"
PRODUCT_ID_PATTERN = r"[A-D]-\d{3}"


def _load_inventory() -> dict:
    """고정된 CSV에서 재고를 읽어온다. Load inventory from the fixed CSV."""
    rows = {}
    with open(DATA / "inventory.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[row["product_id"]] = {
                "name": row["name"],
                "price": int(row["price"]),
                "stock": int(row["stock"]),
                "safety_stock": int(row["safety_stock"]),
            }
    return rows


INVENTORY = _load_inventory()


# ---------------------------------------------------------------------------
# 도구 1. 재고 조회 (Tool 1: check stock) — 인식(perception) 도구
# ---------------------------------------------------------------------------
def get_inventory(product_id: str) -> dict:
    """
    제품 ID로 현재 재고를 조회한다.
    재고, 입고 가능 여부, 품절 여부를 물을 때 사용한다.
    제품 ID를 모르면 먼저 사용자에게 물어본다.

    Look up current stock for one product. Use when the user asks about
    stock or availability. If you don't know the product ID, ask the user.
    """
    # 1) 형식 검사 — 슬라이드 14의 "구문/형태" 단계
    if not isinstance(product_id, str) or not re.fullmatch(PRODUCT_ID_PATTERN, product_id):
        return {"error": f"product_id 형식 오류: {product_id!r}. 예: 'A-100'"}

    # 2) 사실 검사 — 형식이 맞아도 존재하지 않을 수 있다 (실습 2의 핵심)
    row = INVENTORY.get(product_id)
    if row is None:
        return {
            "error": f"제품 {product_id} 없음. 사용 가능한 ID: {', '.join(sorted(INVENTORY))}"
        }

    return {
        "product_id": product_id,
        "name": row["name"],
        "stock": row["stock"],
        "safety_stock": row["safety_stock"],
        "below_safety_stock": row["stock"] < row["safety_stock"],
    }


# ---------------------------------------------------------------------------
# 도구 2. 할인가 계산 (Tool 2: discounted price) — 계산(computation) 도구
# ---------------------------------------------------------------------------
def calc_discount(product_id: str, rate: float, quantity: int = 1) -> dict:
    """
    제품의 할인가와 총액을 계산한다.
    rate는 0 이상 1 이하의 소수다 (20% 할인은 0.2).
    "얼마인가", "할인하면" 같은 질문에 사용한다.

    Calculate the discounted price and total. rate is a decimal between
    0 and 1 (20% off is 0.2). Use for "how much" / "with a discount" questions.
    """
    row = INVENTORY.get(product_id)
    if row is None:
        return {"error": f"제품 {product_id} 없음. get_inventory로 먼저 확인하세요."}

    # 타입과 범위 검사 — 모델이 만든 값을 그대로 믿지 않는다
    if not isinstance(rate, (int, float)) or not 0 <= rate <= 1:
        return {"error": f"rate는 0~1 사이의 소수여야 합니다. 받은 값: {rate!r} (20% → 0.2)"}
    if not isinstance(quantity, int) or quantity < 1:
        return {"error": f"quantity는 1 이상의 정수여야 합니다. 받은 값: {quantity!r}"}

    unit_price = round(row["price"] * (1 - rate))
    return {
        "product_id": product_id,
        "list_price": row["price"],
        "rate": rate,
        "unit_price": unit_price,
        "quantity": quantity,
        "total": unit_price * quantity,
        # 규정상 20% 초과 할인은 승인이 필요하다 (data/order_policy.md 제2조)
        "needs_approval": rate > 0.2,
    }


# ---------------------------------------------------------------------------
# 도구 3. 주문 생성 (Tool 3: create an order) — 행동(action) 도구
# 되돌릴 수 없으므로 실습 4에서 사람 승인을 붙인다.
# An ACTION tool: irreversible, so Practice 4 puts a human approval in front.
# ---------------------------------------------------------------------------
ORDERS: list[dict] = []  # 데모용 메모리 저장소 (in-memory store for the demo)


def create_order(product_id: str, quantity: int) -> dict:
    """
    주문을 생성한다. 되돌릴 수 없는 작업이므로 사용자 확인 후에만 호출한다.
    Create an order. Irreversible — only call after the user confirms.
    """
    stock = get_inventory(product_id)
    if "error" in stock:
        return stock
    if stock["stock"] == 0:
        return {"error": f"{product_id}는 품절입니다. 주문할 수 없습니다. (규정 제3조)"}
    if quantity > stock["stock"]:
        return {"error": f"재고 부족: 요청 {quantity}개, 재고 {stock['stock']}개"}

    order_id = f"ORD-{len(ORDERS) + 1:03d}"
    ORDERS.append({"order_id": order_id, "product_id": product_id, "quantity": quantity})
    return {"order_id": order_id, "product_id": product_id, "quantity": quantity, "status": "created"}


# 이름 → 함수 매핑. 실습 3의 루프가 이 표를 보고 도구를 찾는다.
# Name → function table. The Practice 3 loop looks tools up here.
FUNCS = {
    "get_inventory": get_inventory,
    "calc_discount": calc_discount,
    "create_order": create_order,
}

# 승인이 필요한 도구 (실습 4) — Tools that need human approval (Practice 4)
NEEDS_APPROVAL = {"create_order"}


if __name__ == "__main__":
    print("정상 (ok):        ", get_inventory("A-100"))
    print("형식 오류 (bad format):", get_inventory("a100"))
    print("없는 제품 (missing):   ", get_inventory("A-999")["error"])
    print("할인 계산 (discount): ", calc_discount("A-100", 0.2, 50))
    print("잘못된 rate (bad rate):", calc_discount("A-100", 20))
    print("품절 주문 (sold out):  ", create_order("D-100", 1))
