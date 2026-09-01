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

오늘은 구체적인 LLM API(OpenAI 등)를 아직 정하지 않았으므로(슬라이드 15),
"LLM이 도구 호출 여부를 판단한다"는 부분을 규칙 기반(rule-based)으로 흉내 냅니다.
Because we haven't picked a specific LLM API yet (slide 15), the "LLM decides
whether to call a tool" part is simulated with a simple rule-based check today.
다음 주(2주차)에는 이 think() 함수 자리에 실제 LLM 호출이 들어갑니다.
Next week (Week 2), a real LLM call will replace the think() function here.
"""

import ast
import operator
import re


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

# 수식처럼 보이는 입력을 감지하기 위한 간단한 패턴
# A simple pattern to detect input that "looks like" a math expression
_MATH_PATTERN = re.compile(r"[\d().]\s*[+\-*/×x÷]\s*[\d(]")


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
#          도구 호출이 필요한지 코드로 판단
#          Code decides whether a tool call is needed
#
#          NOTE: 오늘은 실제 LLM을 호출하지 않고, 정규식으로 "수식이 포함되어
#          있는가?"만 판단하는 규칙 기반 버전입니다. 다음 주에는 이 자리에
#          LLM API 호출이 들어가고, LLM이 TOOLS 명세를 보고 스스로 도구 호출
#          여부와 파라미터를 결정하게 됩니다.
#          Today this is a rule-based stand-in (regex: "does this look like
#          math?"). Next week, a real LLM call goes here and the model itself
#          decides — using the TOOLS spec — whether and how to call a tool.
# ---------------------------------------------------------------------------

def think(user_input: str) -> dict | None:
    needs_tool = bool(_MATH_PATTERN.search(user_input))

    if needs_tool:
        expression = _extract_expression(user_input)
        print(f"[Think]   수식을 감지했습니다 → 도구 호출 필요 (tool call needed): calculator({expression!r})")
        return {"tool": "calculator", "arguments": {"expression": expression}}

    print("[Think]   수식이 없습니다 → 도구 호출 불필요 (no tool call needed)")
    return None


def _extract_expression(user_input: str) -> str:
    """사용자 문장에서 수식 부분만 뽑아냅니다. (Pull just the expression out of the sentence.)"""
    match = re.search(r"[0-9().\s+\-*/×x÷]+", user_input)
    return match.group().strip() if match else user_input


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
