"""
agent_loop.py
고급 비즈니스 프로그래밍 · 3주차 실습 3–4 — 도구 호출 루프와 사람 승인
Advanced Business Programming · Week 3 Practice 3-4 — Tool Loop & Human Approval

슬라이드 11~13(Function Calling 동작 원리, 호출의 흐름, 호출 루프)을 코드로 옮긴 예제입니다.
Mirrors slides 11-13.

반드시 들어가야 하는 안전장치 네 가지 (the four required safeguards):
    1. 이름 → 함수 매핑     모델이 준 이름으로 직접 호출하지 않는다
    2. 없는 도구 처리       오류를 결과로 돌려주고 루프를 계속한다
    3. 반복 한도            한도 없는 루프는 과금 사고가 된다
    4. 호출 로그            call ID · 인자 · 결과 · 소요 시간

실습 4: create_order 처럼 되돌릴 수 없는 도구는 사용자가 yes 를 입력해야 실행된다.
Practice 4: irreversible tools only run after the user types yes.

실행 (run):
    python3 agent_loop.py             # 가짜 LLM — API 키 없이, 무료로 (fake LLM, no key)
    python3 agent_loop.py --real      # 진짜 Groq LLM (needs GROQ_KEY in .env)
"""

import json
import os
import sys
import time

from schemas import TOOLS, ValidationError, validate
from tools import FUNCS, NEEDS_APPROVAL

MAX_TURNS = 5  # 안전장치 3 — 반복 한도 (safeguard 3: turn limit)

SYSTEM_PROMPT = (
    "너는 사내 헬프데스크 에이전트다. 재고·가격·주문 질문에 답한다. "
    "필요하면 도구를 사용하고, 도구 결과에 없는 숫자는 지어내지 않는다. "
    "You are an internal helpdesk agent. Use tools when needed; never invent numbers."
)


# ---------------------------------------------------------------------------
# 호출 로그 (safeguard 4) — 제출물이자 디버깅 근거
# The call log: part of your submission and your main debugging tool.
# ---------------------------------------------------------------------------
TRACE: list[dict] = []


def log_call(call_id, name, args, result, seconds):
    TRACE.append(
        {"call_id": call_id, "tool": name, "args": args, "result": result, "seconds": round(seconds, 3)}
    )
    print(f"  [tool] {name}({args}) -> {result}  ({seconds:.2f}s)  id={call_id}")


# ---------------------------------------------------------------------------
# 실습 4. 사람 승인 (Practice 4: human approval)
# ---------------------------------------------------------------------------
def approved(name: str, args: dict, auto: str | None = None) -> bool:
    """되돌릴 수 없는 도구를 실행하기 전에 사용자에게 묻는다."""
    if name not in NEEDS_APPROVAL:
        return True
    print(f"  [승인 필요] {name}({args}) 를 실행할까요?")
    answer = auto if auto is not None else input("  yes / no > ")
    return answer.strip().lower() in {"y", "yes", "네"}


# ---------------------------------------------------------------------------
# 도구 하나를 실행한다: 검증 → 승인 → 실행 → 로그
# Run one tool: validate → approve → execute → log
# ---------------------------------------------------------------------------
def run_tool(call_id: str, name: str, raw_args: dict, auto_approve: str | None = None) -> dict:
    start = time.perf_counter()

    fn = FUNCS.get(name)  # 안전장치 1 — 이름 → 함수 매핑
    if fn is None:  # 안전장치 2 — 없는 도구
        result = {"error": f"알 수 없는 도구: {name}. 사용 가능: {list(FUNCS)}"}
        log_call(call_id, name, raw_args, result, time.perf_counter() - start)
        return result

    try:
        args = validate(name, raw_args)  # 검증 후 실행 (validate, then run)
    except ValidationError as e:
        result = {"error": str(e)}  # 오류도 결과로 돌려준다 → 모델이 고쳐서 재시도
        log_call(call_id, name, raw_args, result, time.perf_counter() - start)
        return result

    if not approved(name, args, auto_approve):
        result = {"error": "사용자가 실행을 거절했습니다. 다른 방법을 제안하세요."}
        log_call(call_id, name, args, result, time.perf_counter() - start)
        return result

    result = fn(**args)
    log_call(call_id, name, args, result, time.perf_counter() - start)
    return result


# ---------------------------------------------------------------------------
# 루프 본체 (the loop) — 슬라이드 13
# ---------------------------------------------------------------------------
def run_agent(question: str, client=None, auto_approve: str | None = None) -> str:
    """모델이 도구를 그만 부를 때까지, 최대 MAX_TURNS 번 반복한다."""
    client = client or make_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    print(f"\n{'=' * 70}\n[질문] {question}")

    for turn in range(MAX_TURNS):
        message = client.chat(messages, TOOLS)
        messages.append(message)

        calls = message.get("tool_calls") or []
        if not calls:  # 도구가 더 필요 없다 → 최종 답변
            answer = message.get("content", "")
            print(f"[답변] {answer}\n{'=' * 70}")
            return answer

        for call in calls:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"])
            result = run_tool(call["id"], name, args, auto_approve)
            # 같은 id를 붙여 결과를 돌려준다 (슬라이드 12의 3번 패널)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    # 안전장치 3 — 한도에 도달하면 멈춘다
    print(f"[중단] 반복 한도 {MAX_TURNS}회 초과\n{'=' * 70}")
    return f"반복 한도({MAX_TURNS}회)에 도달해 중단했습니다."


# ---------------------------------------------------------------------------
# LLM 클라이언트 — 진짜(Groq) 또는 가짜(스크립트)
# The LLM client: real (Groq) or fake (scripted), so you can debug for free.
# ---------------------------------------------------------------------------
def make_client(real: bool = False):
    if real:
        from llm import GroqClient

        return GroqClient()
    from llm import FakeClient

    return FakeClient()


if __name__ == "__main__":
    real = "--real" in sys.argv
    client = make_client(real)
    print("모드 (mode):", "진짜 LLM (Groq)" if real else "가짜 LLM (무료, 스크립트)")

    questions = [
        "안녕하세요!",                              # 도구 불필요 (no tool)
        "A-100 재고 얼마나 남았어요?",                # 도구 하나 (one tool)
        "A-100을 20% 할인하면 50개에 얼마인가요?",     # 두 도구, 순서 필요 (dependent)
        "A-999 재고 알려주세요",                     # 오류 후 모델이 고친다 (error → retry)
    ]
    for q in questions:
        run_agent(q, client, auto_approve="yes" if not real else None)

    print(f"\n총 도구 호출 (total tool calls): {len(TRACE)}")
    for entry in TRACE:
        print(" ", entry["call_id"], entry["tool"], entry["seconds"], "s")
