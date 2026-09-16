"""
reliability.py
고급 비즈니스 프로그래밍 · 3주차 실습 7 — 실패 주입과 재시도
Advanced Business Programming · Week 3 Practice 7 — Failure Injection & Retries

슬라이드 19(도구 사용 평가)의 '운영' 항목을 코드로 확인한다.
Checks the "operations" row of slide 19 in code.

도구는 실패한다. 타임아웃, 속도 제한, 일시적 오류 — 데모에서는 안 나던 것들이
실서비스에서는 매일 난다. 재시도가 있을 때와 없을 때의 성공률을 직접 재 본다.
Tools fail. Measure the success rate with and without retries.

LLM 호출이 없다 (no LLM). 실행: python3 reliability.py
"""

import random
import time

from tools import get_inventory

TIMEOUT_RATE = 0.2   # 20% 확률로 실패 (fails 20% of the time)
MAX_RETRIES = 3
TRIALS = 200


def flaky(fn, rate: float = TIMEOUT_RATE):
    """도구를 감싸서 무작위로 실패시킨다. Wrap a tool so it randomly fails."""

    def wrapped(**kwargs):
        if random.random() < rate:
            raise TimeoutError("도구 응답 시간 초과 (tool timed out)")
        return fn(**kwargs)

    return wrapped


def with_retry(fn, max_retries: int = MAX_RETRIES, base_delay: float = 0.01):
    """
    지수 백오프 재시도. 마지막까지 실패하면 예외 대신 오류 '결과'를 돌려준다.
    Exponential backoff. On final failure, RETURN an error instead of raising —
    the model can then tell the user honestly rather than crashing the loop.
    """

    def wrapped(**kwargs):
        for attempt in range(max_retries):
            try:
                return fn(**kwargs)
            except TimeoutError:
                if attempt == max_retries - 1:
                    return {
                        "error": "도구가 응답하지 않습니다. 잠시 후 다시 시도해 주세요.",
                        "is_error": True,
                    }
                time.sleep(base_delay * (2 ** attempt))  # 0.01 → 0.02 → 0.04초
        return None

    return wrapped


def success_rate(tool, trials: int = TRIALS) -> float:
    ok = 0
    for _ in range(trials):
        try:
            result = tool(product_id="A-100")
        except TimeoutError:
            continue
        if isinstance(result, dict) and not result.get("is_error") and "error" not in result:
            ok += 1
    return ok / trials


if __name__ == "__main__":
    random.seed(42)  # 결과를 재현할 수 있게 (reproducible)

    unreliable = flaky(get_inventory)
    protected = with_retry(unreliable)

    without = success_rate(unreliable)
    with_ = success_rate(protected)

    print(f"실습 7 — 실패 주입과 재시도 (Practice 7)\n")
    print(f"타임아웃 확률 (failure rate): {TIMEOUT_RATE:.0%}, 시도 {TRIALS}회")
    print(f"  재시도 없음 (no retry):   성공률 {without:.1%}")
    print(f"  재시도 {MAX_RETRIES}회 (with retry): 성공률 {with_:.1%}")
    print(f"\n이론값 (expected): 재시도 {MAX_RETRIES}회면 실패 확률은 "
          f"{TIMEOUT_RATE}^{MAX_RETRIES} = {TIMEOUT_RATE ** MAX_RETRIES:.1%}")

    print("\n[보고할 것] 재시도는 성공률을 올리지만 지연과 비용도 함께 올린다.")
    print("  실패가 계속되면 예외를 던지지 말고 오류를 결과로 돌려준다 —")
    print("  그래야 모델이 사용자에게 솔직히 말할 수 있다.")
