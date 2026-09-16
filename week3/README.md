# Week 3 — 도구 (Tool) 실습 / Tool Practices

3주차 슬라이드 "핵심 구성요소(2) — 도구 · 지식(RAG) · 플래닝" 중
**도구(Tool)** 부분을 코드로 옮긴 여덟 단계 실습입니다.

Eight hands-on practices for the **Tool** half of Week 3, building up from a
plain Python function to a full evaluation script.

모든 실습이 같은 시나리오를 씁니다: **사내 헬프데스크 에이전트**
(재고 조회 · 할인 계산 · 주문 생성). 각 단계의 결과물이 그대로 최종 과제가 됩니다.

---

## 빠른 시작 (Quick start)

```bash
cd week3
pip install -r requirements.txt      # 오프라인 실습만 할 거면 생략 가능
./run_all.sh                         # API 키 없이 오프라인 실습 전체 실행
```

진짜 LLM을 쓰려면 저장소 루트와 같은 방식으로 키를 넣습니다:

```bash
cp .env.example .env                 # .env 에 GROQ_KEY=... 입력
python3 agent_loop.py --real
```

`.env` 는 커밋하지 않습니다 (루트 `.gitignore` 에 이미 포함).

### 웹 UI (수업용 · Web UI for class)

```bash
python3 app.py                       # → http://localhost:8600
```

같은 모듈(`tools.py` · `schemas.py` · `llm.py` · `evaluate.py`)을 그대로 호출해
브라우저에서 한 단계씩 보여줍니다. 1주차 `app.py` 처럼 표준 라이브러리만 씁니다.

| 탭 | 보여주는 것 | 실습 |
|----|-----------|------|
| ① 도구 호출 루프 | LLM 판단 → 검증 → 승인 → 실행 → 결과 반환 → 다시 LLM, 턴 카운터, `messages[]`, `TRACE`. `create_order` 는 화면에서 **yes / no** 를 눌러야 실행됩니다 | 3 · 4 |
| ② 스키마 검증 | 도구 이름과 인자 JSON 을 직접 고쳐 **어느 층(구문·형태·타입·값·사실)** 에서 걸리는지 확인 | 2 |
| ③ 평가 | `evaluate.CASES` 를 돌려 선택·인자·과제·비용 점수와 케이스별 실패 층 | 8 |
| ④ 참고 | `TOOLS` 명세(description 강조), 재고 데이터, 규정 | 5 |

가짜 LLM 이 기본이라 API 키 없이 동작하고, 화면에서 **진짜 LLM (Groq)** 으로 바꾸면
`.env` 의 `GROQ_KEY` 를 씁니다 (`pip install -r requirements.txt` 필요).

---

## 실습 여덟 단계 (The eight practices)

| # | 실습 | 파일 | 슬라이드 | API | 시간 |
|---|------|------|---------|-----|------|
| 1 | 도구를 평범한 함수로 작성 | `tools.py` | 05 · 18 | **불필요** | 30분 |
| 2 | 스키마와 입력 검증 | `schemas.py`, `test_tools.py` | 12 · 14 | **불필요** | 30분 |
| 3 | 도구 호출 루프 구현 | `agent_loop.py` | 11–13 | 필요\* | 45분 |
| 4 | 행동 도구에 사람 승인 | `agent_loop.py` | 07 · 18 | 필요\* | 20분 |
| 5 | 도구 설명 A/B 비교 | `description_ab.py` | 17–19 | 필요 | 30분 |
| 6 | 직렬 호출과 병렬 호출 | `parallel_calls.py` | 16 | **불필요** | 30분 |
| 7 | 실패 주입과 재시도 | `reliability.py` | 19 | **불필요** | 30분 |
| 8 | 평가 스크립트 (최종 과제) | `evaluate.py` | 19 · 39 | 필요\* | 과제 |

\* 가짜 LLM(`FakeClient`)으로 API 키 없이 먼저 돌려볼 수 있습니다.

### 1–2 · 함수와 스키마 — LLM 없이 시작하기

```bash
python3 tools.py          # 정상 / 형식 오류 / 없는 제품 / 품절 주문
python3 schemas.py        # 네 가지 검사: 구문 → 형태 → 타입 → 값
python3 test_tools.py     # 단위 테스트 15개 (pytest 없이도 실행됨)
```

핵심 규칙 두 가지:

- **오류를 예외로 던지지 말고 결과로 돌려준다.** 그래야 모델이 읽고 인자를 고쳐 재시도할 수 있습니다.
- **스키마는 형식만 보장한다.** `A-999` 는 스키마를 통과하지만 존재하지 않는 제품입니다. 형식 검사와 사실 검사는 다른 층입니다.

### 3–4 · 호출 루프와 승인

```bash
python3 agent_loop.py          # 가짜 LLM — 무료, 항상 같은 결과
python3 agent_loop.py --real   # 진짜 Groq LLM
```

반드시 들어가야 하는 안전장치 네 가지:

1. **이름 → 함수 매핑** (`FUNCS`) — 모델이 준 이름으로 직접 호출하지 않는다
2. **없는 도구 처리** — 오류를 결과로 돌려주고 루프를 계속한다
3. **반복 한도** (`MAX_TURNS = 5`) — 한도 없는 루프는 과금 사고가 된다
4. **호출 로그** (`TRACE`) — call ID · 인자 · 결과 · 소요 시간

`create_order` 는 되돌릴 수 없으므로 `yes` 를 입력해야 실행됩니다.
**거절했을 때 모델이 어떻게 응답하는지 반드시 확인하세요.**

### 5 · 도구 설명 A/B — 설명이 곧 성능

```bash
python3 description_ab.py --real
```

같은 질문 10개를 애매한 설명과 상세한 설명으로 각각 돌려 정답률을 비교합니다.
가짜 모델은 설명을 읽지 않으므로 이 실습만은 진짜 모델이 필요합니다.

### 6 · 직렬 vs 병렬 (오프라인)

```bash
python3 parallel_calls.py     # 6.4초 → 2.8초
```

슬라이드 16의 숫자를 직접 측정합니다. 결과가 순서 없이 도착해도
`call_id` 로 짝을 맞춘다는 점, 그리고 의존 관계가 있는 체인
(고객 ID → 주문 조회 → 환불)은 병렬화할 수 없다는 점을 확인하세요.

### 7 · 실패 주입과 재시도 (오프라인)

```bash
python3 reliability.py        # 20% 타임아웃: 81% → 99.5%
```

### 8 · 평가 스크립트 — 최종 과제

```bash
python3 evaluate.py           # 가짜 LLM
python3 evaluate.py --real    # 진짜 LLM
```

네 가지를 점수로 보고합니다: **도구 선택 · 인자 · 과제 성공 · 비용**.
실패한 케이스는 **어느 층에서 틀렸는지** 함께 출력합니다.

기본 케이스 6개 중 하나는 일부러 실패하도록 두었습니다
(재고를 확인하지 않고 바로 주문 생성). 최종 과제에서는 케이스를
**10–15개**로 늘리세요.

---

## 모든 실습에 적용되는 코딩 규칙

| | 규칙 | 코드에서 |
|---|------|---------|
| 01 | API 키는 환경변수로 | `os.environ["GROQ_KEY"]`, `.env` 는 커밋 금지 |
| 02 | 모든 루프에 한도 | `MAX_TURNS = 5`, `max_tokens=1024` |
| 03 | LLM 연결 전에 테스트 | `test_tools.py` 를 먼저 통과 |
| 04 | 검증 후 실행 | `validate()` → `fn()` |
| 05 | 모델 출력을 직접 실행하지 않는다 | `eval` · `exec` 금지 (1주차 `calculator` 도 `ast` 사용) |
| 06 | 전부 로그로 남긴다 | `TRACE` — 제출물이자 디버깅 근거 |

**비용 줄이기**: 오프라인 단계(1 · 2 · 6 · 7)를 먼저 하고, 루프 버그는
가짜 LLM으로 잡은 뒤에 `--real` 로 넘어가세요.

---

## 최종 과제 제출물 (Final submission)

1. **소스 코드** — 도구 2개 이상, 검증, 승인, 루프
2. **실행 로그** — call ID · 인자 · 결과 · 소요 시간
3. **평가 결과** — 테스트 케이스 10–15개에 대한 네 가지 점수
4. **1페이지 회고** — 실패를 **층위별로** 분석 (선택 / 인자 / 순서 / 그럴듯한 오답)

---

## 파일 구조

```
week3/
├── data/
│   ├── inventory.csv        고정된 재고 데이터 (채점 재현을 위해 모두 같은 파일)
│   └── order_policy.md      주문·할인·환불 규정
├── tools.py                 실습 1 — 도구 함수 세 개
├── schemas.py               실습 2 — 도구 명세와 검증기
├── test_tools.py            실습 1–2 — 단위 테스트 15개
├── llm.py                   GroqClient (진짜) / FakeClient (무료)
├── agent_loop.py            실습 3–4 — 호출 루프와 승인
├── description_ab.py        실습 5 — 설명 A/B 비교
├── parallel_calls.py        실습 6 — 직렬 vs 병렬
├── reliability.py           실습 7 — 실패와 재시도
├── evaluate.py              실습 8 — 평가 스크립트
├── app.py                   웹 UI 서버 (표준 라이브러리, :8600)
├── web/                     index.html · style.css · script.js
├── run_all.sh               오프라인 실습 전체 실행
├── requirements.txt
└── .env.example
```

---

## 다음 주 (Next week)

오늘 만든 도구를 **REST API 로 노출하고 MCP 로 연결**합니다.
`get_inventory` 가 그대로 출발점이 됩니다.
