"""
evaluate.py
고급 비즈니스 프로그래밍 · 3주차 실습 8 — 평가 스크립트 (최종 과제)
Advanced Business Programming · Week 3 Practice 8 — Evaluation Script (final project)

슬라이드 19(도구 사용 평가)의 네 층위를 그대로 점수로 만든다.
Turns the four layers of slide 19 into numbers.

    선택 (selection)  기대한 도구가 호출됐는가
    인자 (arguments)  값이 기대와 일치하는가
    과제 (task)       최종 답이 맞는가
    비용 (cost)       평균 소요 시간과 토큰

고정된 테스트 데이터를 쓴다. 날씨처럼 매번 달라지는 데이터로는
같은 스크립트가 매번 다른 점수를 내서 채점도 재현도 불가능하다.
Fixed test data only — otherwise the same script scores differently every run.

실행 (run):
    python3 evaluate.py           # 가짜 LLM (무료)
    python3 evaluate.py --real    # 진짜 Groq LLM
"""

import sys
import time

import agent_loop
from agent_loop import make_client, run_agent

# ---------------------------------------------------------------------------
# 테스트 케이스 — 최종 과제에서는 10~15개로 늘린다
# Test cases — grow this to 10-15 for the final project.
# ---------------------------------------------------------------------------
CASES = [
    {
        "q": "A-100 재고 얼마나 남았어요?",
        "tools": ["get_inventory"],
        "args": {"product_id": "A-100"},
        "answer": "42",
    },
    {
        "q": "A-100을 20% 할인하면 50개에 얼마인가요?",
        "tools": ["get_inventory", "calc_discount"],
        "args": {"rate": 0.2, "quantity": 50},
        "answer": "480,000",
    },
    {
        "q": "B-200 재고 알려주세요",
        "tools": ["get_inventory"],
        "args": {"product_id": "B-200"},
        "answer": "6",
    },
    {
        "q": "안녕하세요!",
        "tools": [],                 # 도구를 부르면 안 된다 (must NOT call a tool)
        "args": {},
        "answer": "",
    },
    {
        "q": "C-100 100개 주문할게요",
        # 규정상 50개 이상은 대량 주문 → 재고를 먼저 확인한 뒤 주문해야 한다
        # Policy: 50+ is a bulk order → check stock BEFORE creating it.
        "tools": ["get_inventory", "create_order"],
        "args": {"product_id": "C-100", "quantity": 100},
        "answer": "ORD-",
    },
    {
        "q": "A-999 재고 알려주세요",
        "tools": ["get_inventory"],  # 한 번 시도하고 오류를 사용자에게 알려야 한다
        "args": {"product_id": "A-999"},
        "answer": "찾을 수 없",
    },
]


def evaluate(client, cases=CASES) -> dict:
    score = {"selection": 0, "arguments": 0, "task": 0}
    seconds, calls = [], []
    failures = []

    for case in cases:
        agent_loop.TRACE.clear()          # 케이스마다 로그를 새로 받는다
        start = time.perf_counter()
        answer = run_agent(case["q"], client, auto_approve="yes")
        elapsed = time.perf_counter() - start

        used_tools = [t["tool"] for t in agent_loop.TRACE]
        used_args = {k: v for t in agent_loop.TRACE for k, v in t["args"].items()}

        ok_selection = used_tools == case["tools"]
        ok_arguments = all(used_args.get(k) == v for k, v in case["args"].items())
        ok_task = case["answer"] in answer

        score["selection"] += ok_selection
        score["arguments"] += ok_arguments
        score["task"] += ok_task
        seconds.append(elapsed)
        calls.append(len(agent_loop.TRACE))

        # 어느 층에서 실패했는지 기록한다 — 회고의 근거
        # Record WHICH layer failed — this is what your reflection analyses.
        if not (ok_selection and ok_arguments and ok_task):
            failures.append(
                {
                    "q": case["q"],
                    "layer": "선택" if not ok_selection else "인자" if not ok_arguments else "과제",
                    "expected_tools": case["tools"],
                    "used_tools": used_tools,
                    "answer": answer[:60],
                }
            )

    n = len(cases)
    return {
        "n": n,
        "selection": score["selection"] / n,
        "arguments": score["arguments"] / n,
        "task": score["task"] / n,
        "avg_seconds": sum(seconds) / n,
        "avg_calls": sum(calls) / n,
        "failures": failures,
    }


def report(result: dict) -> None:
    print("\n" + "=" * 70)
    print(f"평가 결과 (evaluation) — 케이스 {result['n']}개")
    print("=" * 70)
    print(f"  도구 선택 (selection): {result['selection']:.0%}")
    print(f"  인자     (arguments): {result['arguments']:.0%}")
    print(f"  과제     (task):      {result['task']:.0%}")
    print(f"  평균 시간 (avg time):  {result['avg_seconds']:.2f}초")
    print(f"  평균 호출 (avg calls): {result['avg_calls']:.1f}회")

    if not result["failures"]:
        print("\n실패 없음 (no failures).")
        return
    print(f"\n실패 {len(result['failures'])}건 — 어느 층에서 틀렸는가:")
    for f in result["failures"]:
        print(f"  [{f['layer']}] {f['q']}")
        print(f"      기대 도구 {f['expected_tools']} / 실제 {f['used_tools']}")
        print(f"      답변: {f['answer']}")


if __name__ == "__main__":
    client = make_client(real="--real" in sys.argv)
    report(evaluate(client))
