# 프로젝트 개요 (Project Brief)

## 목표 (Goal)
작은 카페 사장님을 위한 웹 UI 어시스턴트를 만듭니다.
Build a Web UI assistant for the owner of a small café.
사장님이 자연어로 질문을 입력하면, 어시스턴트는 **도구(tools)**를 사용해 사실을 확인하고 행동을 취합니다.
The owner types questions in natural language; the assistant uses **tools** to get facts and take actions.

## 사용자 (Users)
카페 사장님 한 명. 비전문가(기술 지식 없음). 짧고 정확한 답을 원함.
One café owner. Not technical. Wants short, correct answers.

## 어시스턴트가 할 수 있는 일 (What the assistant can do)
- 메뉴와 가격 보여주기 (Show the menu and prices)
- 특정 품목의 재고 확인 (Check stock for an item)
- 가격, 할인, 합계 계산 (Calculate prices, discounts, and totals)
- 판매 기록 (재고와 매출을 갱신) (Record a sale (updates stock and revenue))
- 오늘의 매출 보고 (Report today's sales)
- 브라우저에서의 간단한 채팅 UI (Simple chat UI in the browser)

## 범위 밖 (Out of scope)
- 데이터베이스, 실제 결제, 실제 외부 API, 다중 사용자 (databases, real payments, real external APIs, multiple users)

## 성공 기준 (Success criteria)
- 숫자를 절대 추측하지 않음: 모든 가격, 재고, 합계는 도구(tool)에서 가져옴.
  Never guesses numbers: all prices, stock, and totals come from tools.
- 도구 2~3개를 연속으로 호출해야 하는 질문에도 답할 수 있음.
  Can answer questions that need 2–3 tools in a row.
- 도구 오류(예: 잘못된 품목명)가 나도 죽지 않고 복구함.
  Recovers from tool errors (e.g. wrong item name) instead of crashing.
- 데이터를 변경하기 전(record_sale)에는 확인을 요청함.
  Asks for confirmation before changing data (record_sale).
