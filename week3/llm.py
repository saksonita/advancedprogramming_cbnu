"""
llm.py
고급 비즈니스 프로그래밍 · 3주차 — LLM 클라이언트 두 가지
Advanced Business Programming · Week 3 — Two LLM clients

GroqClient  진짜 LLM. 1주차 agent.py와 같은 Groq API를 사용한다. (.env의 GROQ_KEY)
FakeClient  가짜 LLM. 미리 짜 둔 도구 호출을 돌려준다. API 키도, 비용도 필요 없다.

가짜 클라이언트를 먼저 쓰는 이유 (why start fake):
    루프 버그는 대부분 LLM이 아니라 우리 코드에 있다. 무료로, 항상 같은 결과로
    루프를 먼저 고친 다음 진짜 모델에 연결한다.
    Most loop bugs are in OUR code. Fix them for free and deterministically first.

두 클라이언트는 같은 모양의 응답을 돌려준다 (both return the same shape):
    {"role": "assistant", "content": str, "tool_calls": [ {id, function:{name, arguments}} ]}
"""

import json
import os
import re


# ---------------------------------------------------------------------------
# 진짜 LLM (real LLM) — Groq
# ---------------------------------------------------------------------------
class GroqClient:
    MODEL = "openai/gpt-oss-120b"  # 1주차와 같은 모델 (same model as Week 1)

    def __init__(self):
        from dotenv import load_dotenv
        from groq import Groq

        load_dotenv()
        self._client = Groq(api_key=os.environ["GROQ_KEY"])

    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=1024,  # 안전장치 — 토큰 한도 (token cap)
        )
        message = response.choices[0].message
        out = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            out["tool_calls"] = [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {"name": c.function.name, "arguments": c.function.arguments},
                }
                for c in message.tool_calls
            ]
        # 토큰 사용량 — 실습 8의 비용 측정에 쓴다 (used by Practice 8)
        out["usage"] = getattr(response, "usage", None) and response.usage.total_tokens
        return out


# ---------------------------------------------------------------------------
# 가짜 LLM (fake LLM) — 규칙으로 도구 호출을 흉내 낸다
# ---------------------------------------------------------------------------
class FakeClient:
    """
    아주 단순한 규칙으로 '모델이 도구를 고른 것처럼' 응답한다.
    Pretends to be a model choosing tools, using very simple rules.

    진짜 모델이 아니므로 판단력은 없다. 루프·검증·로그·승인을 시험하는 용도다.
    No real judgement — it exists to exercise the loop, validation, log, approval.
    """

    def __init__(self):
        self._counter = 0

    def _call(self, name, **args):
        self._counter += 1
        return {
            "id": f"call_{self._counter:03d}",
            "type": "function",
            "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)},
        }

    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        question = next(m["content"] for m in messages if m["role"] == "user")
        results = [m for m in messages if m["role"] == "tool"]
        product = (re.search(r"[A-Da-d]-\d{3}", question) or [None])[0]
        product = product.upper() if product else None
        rate = re.search(r"(\d+)\s*%", question)
        qty = re.search(r"(\d+)\s*개", question)

        # 마지막 도구 결과가 오류였다면 — 모델이 읽고 대응하는 상황을 흉내 낸다
        if results and "error" in (last := json.loads(results[-1]["content"])):
            err = last["error"]
            if "거절" in err:  # 실습 4 — 사용자가 승인을 거절했다 (user said no)
                return self._reply("알겠습니다. 주문을 진행하지 않았습니다. 필요하시면 다시 말씀해 주세요.")
            if len(results) == 1 and ("없음" in err or "형식 오류" in err):  # 한 번만 고쳐 보고 포기한다
                return self._reply("요청하신 제품 ID를 찾을 수 없습니다. 다시 확인해 주세요.")

        if product is None:
            return self._reply("안녕하세요! 재고·가격·주문에 대해 무엇이든 물어보세요.")

        # 재고 질문이 먼저다 — "재고 얼마나"의 '얼마'를 가격으로 오해하지 않도록
        # Stock questions first, so "재고 얼마나" isn't read as a price question.
        stock_question = ("재고" in question or "품절" in question) and not rate

        # 가격 질문 → 재고 확인 후 할인 계산 (두 단계, 순서 있음)
        if not stock_question and (rate or "얼마" in question or "할인" in question):
            if not results:
                return self._tool(self._call("get_inventory", product_id=product))
            if len(results) == 1:
                return self._tool(
                    self._call(
                        "calc_discount",
                        product_id=product,
                        rate=int(rate.group(1)) / 100 if rate else 0,
                        quantity=int(qty.group(1)) if qty else 1,
                    )
                )
            data = json.loads(results[-1]["content"])
            return self._reply(
                f"{product} {data['quantity']}개, {int(data['rate'] * 100)}% 할인 시 "
                f"개당 {data['unit_price']:,}원, 총 {data['total']:,}원입니다."
            )

        # 주문 질문 → 행동 도구 (승인 필요)
        if "주문" in question:
            if not results:
                return self._tool(self._call("create_order", product_id=product, quantity=int(qty.group(1)) if qty else 1))
            data = json.loads(results[-1]["content"])
            if "error" in data:
                return self._reply(f"주문하지 못했습니다: {data['error']}")
            return self._reply(f"주문 {data['order_id']} 이 생성되었습니다.")

        # 그 밖에는 재고 조회
        if not results:
            return self._tool(self._call("get_inventory", product_id=product))
        data = json.loads(results[-1]["content"])
        if "error" in data:
            return self._reply(f"조회하지 못했습니다: {data['error']}")
        warn = " (안전재고 미만입니다)" if data["below_safety_stock"] else ""
        return self._reply(f"{product} 재고는 {data['stock']}개입니다{warn}.")

    @staticmethod
    def _reply(text):
        return {"role": "assistant", "content": text, "usage": 0}

    @staticmethod
    def _tool(call):
        return {"role": "assistant", "content": "", "tool_calls": [call], "usage": 0}
