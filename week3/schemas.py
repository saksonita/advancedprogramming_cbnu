"""
schemas.py
고급 비즈니스 프로그래밍 · 3주차 실습 2 — 스키마와 입력 검증
Advanced Business Programming · Week 3 Practice 2 — Schemas & Input Validation

슬라이드 12(도구 호출은 이렇게 오간다)와 14(형식 검사)를 코드로 옮긴 예제입니다.
This mirrors slide 12 (how a tool call travels) and slide 14 (format checks).

TOOLS 목록은 그대로 LLM API에 넘길 수 있는 형태입니다 (1주차 agent.py와 같은 형식).
The TOOLS list can be handed to the LLM API as-is (same shape as Week 1's agent.py).

validate()는 슬라이드 14의 네 가지 검사를 그대로 구현합니다:
    구문 → 형태(필수 필드) → 타입 → 값(범위·패턴)
    syntax → shape (required fields) → types → values (range/pattern)

실무에서는 jsonschema 라이브러리를 쓰지만, 여기서는 무엇을 검사하는지
직접 보이도록 40줄짜리 검사기를 직접 만듭니다.
Real projects use the `jsonschema` library; here we hand-roll ~40 lines so you
can SEE what is being checked.

이 파일도 LLM을 호출하지 않습니다. python3 schemas.py 로 실행해 보세요.
"""

import re

from tools import PRODUCT_ID_PATTERN

# ---------------------------------------------------------------------------
# 도구 명세 (Tool specs) — 이름 · 설명 · 인자 형식
# description이 도구의 사용 설명서다. "언제 쓰는지"까지 적는다 (실습 5에서 비교).
# The description IS the manual. Say WHEN to use it (compared in Practice 5).
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": (
                "제품 ID로 현재 재고 수량과 안전재고를 조회한다. "
                "재고·품절·입고 가능 여부를 물을 때 사용한다. "
                "가격 계산에는 사용하지 않는다. "
                "(Look up stock and safety stock for one product.)"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "pattern": f"^{PRODUCT_ID_PATTERN}$",
                        "description": "제품 ID, 예: 'A-100' (product ID)",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc_discount",
            "description": (
                "제품의 할인가와 총액을 계산한다. "
                "'얼마인가', '할인하면' 같은 가격 질문에 사용한다. "
                "재고 확인에는 사용하지 않는다. "
                "(Calculate discounted unit price and total.)"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "pattern": f"^{PRODUCT_ID_PATTERN}$"},
                    "rate": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "할인율 소수, 20% 할인은 0.2 (discount as a decimal)",
                    },
                    "quantity": {"type": "integer", "minimum": 1, "default": 1},
                },
                "required": ["product_id", "rate"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": (
                "주문을 생성한다. 되돌릴 수 없는 작업이므로 사용자가 확인한 뒤에만 호출한다. "
                "(Create an order. Irreversible — only after the user confirms.)"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "pattern": f"^{PRODUCT_ID_PATTERN}$"},
                    "quantity": {"type": "integer", "minimum": 1},
                },
                "required": ["product_id", "quantity"],
            },
        },
    },
]

# 이름으로 스키마를 찾기 위한 표 (name → parameters schema)
SCHEMAS = {t["function"]["name"]: t["function"]["parameters"] for t in TOOLS}

_TYPES = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "object": dict}


class ValidationError(ValueError):
    """검증 실패. 루프는 이 메시지를 모델에게 오류로 돌려준다."""


def validate(tool_name: str, args: dict) -> dict:
    """
    도구 인자를 검사하고, 통과하면 기본값을 채워 돌려준다.
    Check the arguments; on success return them with defaults filled in.

    슬라이드 14의 네 단계를 순서대로 수행한다.
    """
    schema = SCHEMAS.get(tool_name)
    if schema is None:
        raise ValidationError(f"알 수 없는 도구: {tool_name}")
    if not isinstance(args, dict):  # ① 구문 (syntax)
        raise ValidationError(f"인자는 object여야 합니다: {args!r}")

    props = schema["properties"]
    checked = dict(args)

    for field in schema.get("required", []):  # ② 형태 (shape)
        if field not in checked:
            raise ValidationError(f"필수 인자 누락: {field}")

    for key, value in list(checked.items()):
        rule = props.get(key)
        if rule is None:
            raise ValidationError(f"알 수 없는 인자: {key}")

        expected = _TYPES[rule["type"]]  # ③ 타입 (types)
        if rule["type"] == "integer" and isinstance(value, bool):
            raise ValidationError(f"{key}는 정수여야 합니다: {value!r}")
        if not isinstance(value, expected):
            raise ValidationError(f"{key} 타입 오류: {rule['type']} 기대, {value!r} 받음")

        if "pattern" in rule and not re.fullmatch(rule["pattern"].strip("^$"), value):  # ④ 값
            raise ValidationError(f"{key} 형식 오류: {value!r} (예: 'A-100')")
        if "minimum" in rule and value < rule["minimum"]:
            raise ValidationError(f"{key}는 {rule['minimum']} 이상이어야 합니다: {value!r}")
        if "maximum" in rule and value > rule["maximum"]:
            raise ValidationError(f"{key}는 {rule['maximum']} 이하여야 합니다: {value!r}")

    for key, rule in props.items():  # 기본값 채우기 (fill defaults)
        if key not in checked and "default" in rule:
            checked[key] = rule["default"]

    return checked


if __name__ == "__main__":
    print("통과 (passes):", validate("get_inventory", {"product_id": "A-100"}))
    print("기본값 (default filled):", validate("calc_discount", {"product_id": "A-100", "rate": 0.2}))

    for name, args in [
        ("get_inventory", {"product_id": "a100"}),      # 형식 오류
        ("get_inventory", {}),                           # 필수 인자 누락
        ("calc_discount", {"product_id": "A-100", "rate": 20}),  # 범위 초과 (20% ≠ 20)
    ]:
        try:
            validate(name, args)
        except ValidationError as e:
            print(f"거절 (rejected): {e}")

    # ★ 실습 2의 핵심 — 스키마는 통과하지만 존재하지 않는 제품
    # The point of Practice 2: passes the schema, still wrong.
    from tools import get_inventory

    args = validate("get_inventory", {"product_id": "A-999"})
    print("\n스키마는 통과 (schema ok):", args)
    print("하지만 실행하면 (but running it):", get_inventory(**args)["error"])
    print("→ 형식 검사와 사실 검사는 다른 층이다.")
