"""
agent.py
고급 비즈니스 프로그래밍 · 1주차 라이브 데모 — 계산기 에이전트 (Calculator Agent)
Advanced Business Programming · Week 1 Live Demo — Calculator Tool Agent

슬라이드 16~17 "파이썬 코드로 보는 에이전트 구조"의 STEP 1~5를 그대로 코드로 옮긴 예제입니다.
This mirrors STEP 1-5 from slides 16-17 ("Agent Structure in Python Code") 1:1.

    STEP 1  도구 함수 정의        Define the tool function     -> calculator()
    STEP 2  도구 목록 작성        Write the tool spec          -> TOOLS
    STEP 3  사용자 입력 받기      Observe: get user input      -> observe()
    STEP 4  LLM 응답 해석        Think: decide to call a tool -> think()
    STEP 5  결과 반환            Act: run tool & respond      -> act()

think() 함수는 Groq API(실제 LLM)를 호출하여 도구 호출 여부와 파라미터를
스스로 판단하게 합니다. API 키는 .env 파일의 GROQ_KEY에서 읽어옵니다.
The think() function calls the Groq API (a real LLM) so the model itself
decides whether/how to call a tool. The API key is read from GROQ_KEY in .env.
"""

import ast
import json
import operator
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_KEY"])
_MODEL = "openai/gpt-oss-120b"


# ---------------------------------------------------------------------------
# STEP 1. 도구 함수 정의 (Define the Tool Function)
#          Act의 실행 수단 — 에이전트가 실제로 호출할 계산 로직
#          The actual calculation logic the agent calls to execute an action
# ---------------------------------------------------------------------------

# 사칙연산과 거듭제곱만 허용하는 안전한 연산자 매핑
# Only allow basic arithmetic operators for safe evaluation (no eval()!)
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> float:
    """
    수식 문자열을 받아 계산 결과를 반환하는 도구(Tool) 함수.
    Tool function: takes a math expression string and returns the result.

    예 (e.g.): calculator("(23 + 19) * 4") -> 168.0

    파이썬 내장 eval() 대신 ast 모듈로 직접 파싱하여 안전하게 계산합니다.
    Uses the ast module instead of Python's built-in eval() for safety.
    """
    # '×', '÷' 같은 한글 입력 기호를 파이썬 연산자로 정규화
    # Normalize Korean/typographic symbols to Python operators
    normalized = expression.replace("×", "*").replace("x", "*").replace("÷", "/")

    tree = ast.parse(normalized, mode="eval")
    return _eval_node(tree.body)


def _eval_node(node):
    if isinstance(node, ast.Constant):  # 숫자 (a number)
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"허용되지 않은 수식입니다 (Unsupported expression): {node}")


# ---------------------------------------------------------------------------
# STEP 2. 도구 목록 작성 (Write the Tool List)
#          LLM에게 전달할 정보 — 어떤 함수를 언제 쓰는지 설명하는 명세
#          Information passed to the LLM: a spec of when to use which function
#
#          실제 LLM API(OpenAI function calling 등)에 그대로 넘길 수 있는 형태로
#          작성해 둡니다. 오늘은 이 명세를 직접 호출하지 않고, think() 함수가
#          규칙 기반으로 같은 역할을 대신합니다.
#          Written in a shape you could hand directly to a real LLM API (e.g.
#          OpenAI's function-calling format). We don't call it today — think()
#          plays the same role with simple rules instead.
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "사칙연산 수식을 계산합니다. (Evaluates a basic arithmetic expression.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수식, 예: '(23 + 19) * 4' (The expression to evaluate)",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

# ---------------------------------------------------------------------------
# STEP 3. 사용자 입력 받기 — Observe 단계 (Get User Input — Observe)
#          질문을 다음 단계(Think)에 전달할 형태로 정리
#          Format the question so it's ready for the Think stage
# ---------------------------------------------------------------------------

def observe(user_input: str) -> str:
    print(f"[Observe] 사용자 입력 (user input): {user_input!r}")
    return user_input.strip()


# ---------------------------------------------------------------------------
# STEP 4. LLM 응답 해석 — Think 단계 (Parse LLM Response — Think)
#          Groq LLM을 호출하여 도구 호출이 필요한지 스스로 판단하게 함
#          Calls the Groq LLM so it decides for itself whether a tool call is needed
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You must use the calculator tool whenever the user's message contains "
    "an arithmetic expression to evaluate, even if it's mixed with other text "
    "or a different language. Otherwise, respond without calling a tool."
)


def think(user_input: str) -> dict | None:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        tools=TOOLS,
        tool_choice="auto",
    )
    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        call = tool_calls[0]
        arguments = json.loads(call.function.arguments)
        print(f"[Think]   LLM이 도구 호출을 요청했습니다 (LLM requested a tool call): {call.function.name}({arguments!r})")
        return {"tool": call.function.name, "arguments": arguments}

    print("[Think]   LLM이 도구 호출이 필요 없다고 판단했습니다 (LLM decided no tool call is needed)")
    return None


# ---------------------------------------------------------------------------
# STEP 5. 결과 반환 — Act 단계 마무리 (Return Result — Wrapping Up Act)
#          도구 실행 결과를 정리해 사용자에게 응답
#          Runs the tool (if needed) and formats the final response
# ---------------------------------------------------------------------------

def act(decision: dict | None, user_input: str) -> str:
    if decision is None:
        response = "죄송해요, 계산할 수식을 찾지 못했어요. (Sorry, I couldn't find an expression to calculate.)"
        print(f"[Act]     {response}")
        return response

    if decision["tool"] == "calculator":
        expression = decision["arguments"]["expression"]
        result = calculator(expression)
        response = f"{expression} = {result}"
        print(f"[Act]     도구 실행 결과 (tool result): {response}")
        return response

    raise ValueError(f"알 수 없는 도구입니다 (unknown tool): {decision['tool']}")


# ---------------------------------------------------------------------------
# Observe → Think → Act 루프 (The Observe → Think → Act Loop)
#   목표에 도달할 때까지(여기서는 한 번의 질문-응답) 반복되는 행동 루프
#   슬라이드 12의 "관찰 → 판단 → 행동" 3단계를 그대로 함수 호출로 표현합니다.
# ---------------------------------------------------------------------------

def run_agent(user_input: str) -> str:
    print("\n" + "=" * 60)
    perceived = observe(user_input)          # 1. 관찰 (Observe)
    decision = think(perceived)              # 2. 판단 (Think)
    response = act(decision, perceived)       # 3. 행동 (Act)
    print("=" * 60)
    return response


# ---------------------------------------------------------------------------
# 실행 및 결과 확인 (Run & Check the Result)
#   슬라이드 18 미니 실습에서 그대로 따라 입력해 볼 수 있는 테스트 질문들입니다.
#   Test questions you can type along with during the hands-on exercise.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_questions = [
        "(23 + 19) × 4는?",          # 슬라이드 17에 등장한 예시 질문
        "안녕하세요, 오늘 날씨 어때요?",   # 수식이 없는 질문 -> 도구 호출 안 함
        "100 / 4 - 5 계산해줘",
    ]

    for question in test_questions:
        answer = run_agent(question)
        print(f"최종 응답 (final answer): {answer}\n")

    # 직접 질문을 입력해보고 싶다면 아래 주석을 해제하세요.
    # Uncomment below to try your own questions interactively.
    #
    # while True:
    #     user_input = input("질문을 입력하세요 (또는 'exit'): ")
    #     if user_input.lower() == "exit":
    #         break
    #     run_agent(user_input)
