"""
parallel_calls.py
고급 비즈니스 프로그래밍 · 3주차 실습 6 — 직렬 호출과 병렬 호출
Advanced Business Programming · Week 3 Practice 6 — Serial vs Parallel Calls

슬라이드 16(직렬 호출과 병렬 호출)의 6.4초 대 2.8초를 직접 측정한다.
Measures the 6.4s vs 2.8s from slide 16 yourself.

LLM 호출이 없다. asyncio.sleep 으로 느린 도구를 흉내 낸다 — 무료다.
No LLM here: asyncio.sleep imitates slow tools. Free to run.

실행 (run): python3 parallel_calls.py
"""

import asyncio
import time

# 느린 도구 세 개 — 서로 의존하지 않는다 (three slow, INDEPENDENT tools)
LATENCY = {"weather": 1.2, "calendar": 0.9, "flights": 1.1}
GENERATION = 0.8  # 모델이 한 번 생성하는 데 걸리는 시간 (one generation phase)


async def slow_tool(name: str, call_id: str) -> tuple[str, str]:
    """도구 하나를 호출한다. 결과에 call_id 를 함께 돌려준다."""
    await asyncio.sleep(LATENCY[name])
    return call_id, f"{name} 결과"


async def serial() -> float:
    """하나씩 순서대로: 생성 → 도구 → 생성 → 도구 → ... (slide 16, 위쪽)"""
    start = time.perf_counter()
    for i, name in enumerate(LATENCY, start=1):
        await asyncio.sleep(GENERATION)      # 모델이 호출을 생성
        await slow_tool(name, f"call_{i}")   # 도구 실행
    await asyncio.sleep(GENERATION)          # 마지막 답변 생성
    return time.perf_counter() - start


async def parallel() -> float:
    """한 번의 생성에서 세 호출을 동시에: 생성 → (셋 동시) → 생성 (slide 16, 아래쪽)"""
    start = time.perf_counter()
    await asyncio.sleep(GENERATION)
    results = await asyncio.gather(
        *(slow_tool(name, f"call_{i}") for i, name in enumerate(LATENCY, start=1))
    )
    await asyncio.sleep(GENERATION)
    # 결과는 순서 없이 도착할 수 있다 → call_id 로 짝을 맞춘다
    # Results can arrive out of order → match them back by call_id.
    by_id = dict(results)
    print("  call_id 로 짝 맞추기 (matched by call_id):", by_id)
    return time.perf_counter() - start


# ---------------------------------------------------------------------------
# 병렬로 하면 안 되는 경우 (when you must NOT parallelize)
# 앞 호출의 결과가 있어야 다음 호출의 인자를 만들 수 있다.
# ---------------------------------------------------------------------------
DEPENDENT_CHAIN = [
    ("find_customer", "이름 → 고객 ID"),
    ("get_orders", "고객 ID → 주문 목록"),     # 앞 결과가 인자가 된다
    ("refund_order", "주문 번호 → 환불"),       # 되돌릴 수 없다
]


async def main():
    print("실습 6 — 직렬 vs 병렬 (Practice 6)\n")
    s = await serial()
    print(f"직렬 (serial):   {s:.1f}초")
    p = await parallel()
    print(f"병렬 (parallel): {p:.1f}초   → {s - p:.1f}초 절약\n")

    print("병렬로 하면 안 되는 체인 (must stay sequential):")
    for i, (name, why) in enumerate(DEPENDENT_CHAIN, start=1):
        print(f"  {i}. {name:15s} {why}")
    print("  → 2번은 1번의 결과가 있어야 인자를 만들 수 있다. 동시에 부를 수 없다.")

    print("\n[생각해 보기] 위 세 도구 중 하나가 실패하면 gather 는 어떻게 동작할까?")
    print("  힌트: asyncio.gather(..., return_exceptions=True) 를 넣고 다시 돌려 보세요.")


if __name__ == "__main__":
    asyncio.run(main())
