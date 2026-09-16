"""
description_ab.py
고급 비즈니스 프로그래밍 · 3주차 실습 5 — 도구 설명 A/B 비교
Advanced Business Programming · Week 3 Practice 5 — Tool Description A/B Test

슬라이드 18(좋은 도구 설계 원칙)의 첫 번째 원칙을 숫자로 확인한다:
    "LLM은 description을 읽고 도구를 고른다."
Confirms principle #1 from slide 18 in numbers: the model picks tools by reading
their descriptions.

같은 질문 10개를 두 번 돌린다.
    조건 A  애매한 설명 — "데이터를 가져온다"
    조건 B  상세한 설명 — 언제 쓰는지, 언제 쓰지 않는지까지
Run the same 10 questions twice: vague vs detailed descriptions.

이 실습은 진짜 모델이 필요하다 (가짜 모델은 설명을 읽지 않는다).
Needs a real model — the fake client ignores descriptions.

실행 (run): python3 description_ab.py --real
"""

import copy
import json
import sys

from schemas import TOOLS

# ---------------------------------------------------------------------------
# 테스트 질문 — 각 질문에 호출되어야 할 도구를 미리 정해 둔다
# The 10 questions, each with the tool that SHOULD be called.
# ---------------------------------------------------------------------------
TESTS = [
    ("A-100 재고 얼마나 남았나요?",            "get_inventory"),
    ("B-100 몇 개 있어요?",                    "get_inventory"),
    ("D-100 품절인가요?",                      "get_inventory"),
    ("C-200 안전재고보다 적나요?",             "get_inventory"),
    ("A-200 10% 할인하면 얼마예요?",           "calc_discount"),
    ("B-200을 5개 사면 총액이 얼마죠?",         "calc_discount"),
    ("C-100 30% 할인 가능한가요?",             "calc_discount"),
    ("A-100 정가가 얼마인가요?",               "calc_discount"),
    ("C-100 20개 주문해 주세요",               "create_order"),
    ("오늘 날씨 어때요?",                      None),          # 도구를 부르면 안 된다
]

# ---------------------------------------------------------------------------
# 조건 A — 애매한 설명 (vague descriptions)
# ---------------------------------------------------------------------------
VAGUE = {
    "get_inventory": "데이터를 가져온다.",
    "calc_discount": "계산한다.",
    "create_order": "처리한다.",
}

# 조건 B — 상세한 설명은 schemas.py 의 TOOLS 에 이미 들어 있다
# Condition B: the detailed descriptions already live in schemas.py


def with_descriptions(overrides: dict | None) -> list[dict]:
    """도구 명세를 복사해서 설명만 바꾼다. Copy the specs, swap descriptions."""
    tools = copy.deepcopy(TOOLS)
    if overrides:
        for tool in tools:
            name = tool["function"]["name"]
            tool["function"]["description"] = overrides[name]
    return tools


def first_tool(client, question: str, tools: list[dict]) -> str | None:
    """질문 하나에 대해 모델이 처음 고른 도구 이름을 돌려준다."""
    message = client.chat(
        [
            {"role": "system", "content": "사내 헬프데스크 에이전트다. 필요하면 도구를 사용한다."},
            {"role": "user", "content": question},
        ],
        tools,
    )
    calls = message.get("tool_calls") or []
    return calls[0]["function"]["name"] if calls else None


def run_condition(client, label: str, overrides: dict | None) -> float:
    tools = with_descriptions(overrides)
    correct = 0
    print(f"\n조건 {label}")
    for question, expected in TESTS:
        chosen = first_tool(client, question, tools)
        ok = chosen == expected
        correct += ok
        mark = "O" if ok else "X"
        print(f"  {mark} {question:32s} 기대 {expected or '(없음)':14s} 실제 {chosen or '(없음)'}")
    accuracy = correct / len(TESTS)
    print(f"  정답률 (accuracy): {accuracy:.0%}")
    return accuracy


if __name__ == "__main__":
    if "--real" not in sys.argv:
        print(__doc__)
        print("이 실습은 진짜 모델이 필요합니다. 다시 실행하세요:")
        print("    python3 description_ab.py --real")
        raise SystemExit(0)

    from llm import GroqClient

    client = GroqClient()
    a = run_condition(client, "A — 애매한 설명 (vague)", VAGUE)
    b = run_condition(client, "B — 상세한 설명 (detailed)", None)

    print("\n" + "=" * 60)
    print(f"A 애매한 설명: {a:.0%}    B 상세한 설명: {b:.0%}    차이: {b - a:+.0%}")
    print("=" * 60)
    print("[보고할 것] 어떤 질문에서 차이가 났는지, 왜 그랬는지 한 문단으로 적는다.")
    print("  힌트: 애매한 설명에서는 재고 질문과 가격 질문이 섞이기 쉽다.")
