# 도구 명세

도구를 구현하기 **전에** 명세를 씁니다. "Purpose" 줄이 곧 LLM이 읽는 도구 설명이 됩니다.

> 항목 이름(`## Tool:`, `- Purpose:` 등)과 도구 이름은 영어 그대로 둡니다. 형식 검사기와 AI 어시스턴트가 이 이름으로 내용을 찾습니다. 내용은 한국어로 써도 됩니다.

## 템플릿
```
## Tool: <도구 이름>
- Owner: <이 도구를 설명할 수 있는 팀원>
- File: src/tools/<파일>.py
- Purpose: <명확한 한 문장 — LLM이 보는 설명>
- Type: read | write | compute
- Parameters: <이름> (<타입>, required|optional) — <설명>
- Returns: <예시 JSON>
- Errors: <언제> → <힌트가 들어 있는 예시 오류 JSON>
- Example request: "<이 도구를 호출하게 만드는 사용자 문장>"
```

## 명세의 각 줄이 코드에서 가는 곳
| 명세 줄 | 코드에서 |
|---|---|
| 도구 이름 | 함수 이름, 스키마의 `"name"`, `TOOL_FUNCTIONS`의 키 — 셋이 모두 같아야 함 |
| Purpose | 스키마의 `"description"`, 글자 그대로 |
| Parameters | 함수의 매개변수, 그리고 스키마의 `"properties"` |
| required / optional | 스키마의 `"required"`. optional 매개변수는 함수에서 기본값을 가짐 |
| Returns | 성공했을 때 함수가 돌려주는 dict |
| Errors | 함수가 돌려주는 `{"error": "..."}` dict, 그리고 테스트 하나 |
| Example request | `tests/scenarios.md`의 한 행 |

## 도구 지도
이 표를 가장 먼저 채웁니다. 도구들이 서로 이어질 수 있는지 한눈에 보입니다.

| 도구 | 유형 | 담당자 | 주로 이 도구의 앞 / 뒤에 쓰이는 도구 |
|---|---|---|---|
| calculate | compute | (제공됨) | 숫자를 돌려주는 도구 뒤에 |
| <이름> | <유형> | <담당자> | <...> |
| <이름> | <유형> | <담당자> | <...> |
| <이름> | <유형> | <담당자> | <...> |
| <이름> | <유형> | <담당자> | <...> |

---

## Tool: calculate
- Owner: (제공됨 — 이미 구현되어 있습니다. 예시로 참고하세요)
- File: src/tools/calculator.py
- Purpose: Evaluate a math expression. Use this for all prices, discounts, and totals.
- Type: compute
- Parameters: expression (string, required) — e.g. "3 * 4500 * 0.9"
- Returns: `{"expression": "3 * 4500 * 0.9", "result": 12150.0}`
- Errors: invalid expression → `{"error": "Invalid expression. Use numbers and + - * / ( ) only."}`
- Example request: "How much are 3 lattes with 10% off?"

---

## 우리 팀의 도구 (과제 3–4)
도구마다 템플릿을 한 번씩 복사해서 여기에 채웁니다. 도구는 4개 이상이고, `read` 하나, `write` 하나, 카페에는 없는 도구 하나가 들어 있어야 합니다.

> 참고: 모든 기록이 아니라 **요약**을 돌려주세요. 도구 결과가 크면 컨텍스트를 낭비합니다.
