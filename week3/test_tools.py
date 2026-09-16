"""
test_tools.py
고급 비즈니스 프로그래밍 · 3주차 실습 1–2 — 단위 테스트
Advanced Business Programming · Week 3 Practice 1-2 — Unit tests

규칙: 모든 도구는 LLM에 연결하기 전에 이 테스트를 먼저 통과해야 한다.
Rule: every tool passes these tests BEFORE you connect it to an LLM.

실행 (run) — 둘 다 됩니다:
    python3 test_tools.py      # pytest 없이 (no pytest needed)
    pytest test_tools.py       # pytest 가 있다면
"""

from schemas import ValidationError, validate
from tools import calc_discount, create_order, get_inventory


# --- 실습 1: 도구 함수 (Practice 1: tool functions) -------------------------
def test_valid_id_returns_stock():
    out = get_inventory("A-100")
    assert out["stock"] == 42
    assert out["below_safety_stock"] is True


def test_bad_format_returns_error_not_exception():
    out = get_inventory("a100")          # 예외가 아니라 오류 '결과'
    assert "error" in out and "형식" in out["error"]


def test_missing_product_returns_error():
    out = get_inventory("A-999")          # 형식은 맞지만 존재하지 않는다
    assert "error" in out
    assert "A-100" in out["error"]        # 고칠 수 있게 후보를 알려준다


def test_discount_math():
    out = calc_discount("A-100", 0.2, 50)
    assert out["unit_price"] == 9600
    assert out["total"] == 480_000
    assert out["needs_approval"] is False


def test_discount_over_20_percent_needs_approval():
    assert calc_discount("A-100", 0.3)["needs_approval"] is True


def test_rate_out_of_range_returns_error():
    out = calc_discount("A-100", 20)      # 20% 를 20 으로 넘긴 흔한 실수
    assert "error" in out and "0~1" in out["error"]


def test_sold_out_cannot_be_ordered():
    out = create_order("D-100", 1)
    assert "error" in out and "품절" in out["error"]


def test_order_over_stock_returns_error():
    assert "error" in create_order("B-200", 999)


# --- 실습 2: 스키마 검증 (Practice 2: schema validation) --------------------
def test_schema_accepts_valid_args():
    assert validate("get_inventory", {"product_id": "A-100"}) == {"product_id": "A-100"}


def test_schema_fills_default():
    assert validate("calc_discount", {"product_id": "A-100", "rate": 0.2})["quantity"] == 1


def test_schema_rejects_missing_required():
    _expect_rejection("get_inventory", {}, "필수")


def test_schema_rejects_bad_pattern():
    _expect_rejection("get_inventory", {"product_id": "a100"}, "형식")


def test_schema_rejects_out_of_range():
    _expect_rejection("calc_discount", {"product_id": "A-100", "rate": 20}, "이하")


def test_schema_rejects_unknown_tool():
    _expect_rejection("drop_database", {}, "알 수 없는")


def test_schema_passes_but_product_does_not_exist():
    """★ 실습 2의 핵심: 형식 검사는 사실을 보장하지 않는다."""
    args = validate("get_inventory", {"product_id": "A-999"})   # 스키마는 통과
    assert "error" in get_inventory(**args)                      # 실행하면 실패


def _expect_rejection(tool, args, fragment):
    try:
        validate(tool, args)
    except ValidationError as e:
        assert fragment in str(e), f"예상과 다른 메시지: {e}"
        return
    raise AssertionError(f"{tool}{args} 는 거절되어야 합니다")


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} 통과 (passed)")
    raise SystemExit(1 if failed else 0)
