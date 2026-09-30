# 🧩 에이전트 템플릿 — 팀 프로젝트 시작 파일

English: [README.md](README.md)

카페 에이전트와 같은 형식의 빈 에이전트입니다. 아이디어는 팀이 채웁니다.
먼저 `ASSIGNMENT.ko.md`를 읽으세요.

## 준비
```bash
cp -r agent-template my-agent    # 팀 아이디어에 맞는 이름으로 바꾸세요
cd my-agent
```

팀에서 가장 잘 **완성된** 카페 에이전트에서 공통 파일을 복사합니다. 이 파일들은 어떤 에이전트에서도 그대로 동작합니다.
```bash
CAFE=../cafe-agent               # 완성된 카페 에이전트의 경로
cp $CAFE/src/config.py $CAFE/src/llm_client.py $CAFE/src/agent.py $CAFE/src/main.py $CAFE/src/app.py src/
cp $CAFE/src/tools/data_store.py src/tools/
cp $CAFE/.env .env               # 또는: cp .env.example .env 후 API 키 입력
```

그다음:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> `src/app.py`의 제목에 아직 "Café"라고 쓰여 있을 수 있습니다. 제목 글자만 바꾸세요. 복사한 파일의 다른 부분은 바꾸지 않습니다.

### 한국어 템플릿으로 작업하려면 (선택)
채워 넣는 문서의 한국어 버전이 `*.ko.md`로 들어 있습니다. 한국어로 작업할 팀은 아래 명령으로 원래 파일을 한국어 버전으로 바꾸세요.
```bash
for f in docs/01_brief docs/03_tool_spec docs/04_tasks tests/scenarios prompts/system_prompt; do cp $f.ko.md $f.md; done
```

내용은 한국어로 써도 됩니다. 단, 다음은 영어 그대로 둡니다.
- 도구 이름과 매개변수 이름 (`check_stock`, `item`처럼 영어 소문자와 밑줄)
- 명세의 항목 이름 (`## Tool:`, `- Purpose:`, `- Type:` 등). 형식 검사기와 AI 어시스턴트가 이 이름으로 내용을 찾습니다.
- 파일 이름. 검사기는 `docs/03_tool_spec.md`만, 에이전트는 `prompts/system_prompt.md`만 읽습니다. `.ko.md` 파일에 직접 쓰면 반영되지 않습니다.

## 실행
```bash
python -m src.main                              # 에이전트와 대화
streamlit run src/app.py                        # 브라우저에서 대화
python -m pytest tests/test_tool_format.py      # 모든 도구의 형식 검사
python -m pytest tests                          # 형식 검사 + 직접 쓴 도구 테스트
```

## 작업 방법
1. `docs/04_tasks.md`를 열고, 체크되지 않은 다음 과제를 합니다.
2. 설계 과제(Part 1)는 AI 어시스턴트가 아니라 팀이 직접 합니다.
3. 구현 과제는 AI 코딩 어시스턴트에게 이렇게 요청합니다.
   > Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.
4. 도구를 하나 만들 때마다 형식 검사기를 실행합니다.
5. 코드를 이해한 뒤에 다음으로 넘어갑니다. 코드를 설명해 보라는 질문을 받게 됩니다.

## 이미 있는 것과 팀이 쓰는 것
| 이미 있음 | 카페 에이전트에서 복사 | 팀이 작성 |
|---|---|---|
| `src/tools/calculator.py` | `src/config.py`, `src/llm_client.py` | `docs/01_brief.md`, `docs/03_tool_spec.md` |
| `src/tools/__init__.py` (레지스트리) | `src/agent.py`, `src/main.py`, `src/app.py` | `data/*.json` |
| `tests/test_tool_format.py` | `src/tools/data_store.py` | `src/tools/<your>_tools.py` |
| `AGENTS.md`, `docs/02_architecture.md` | | `prompts/system_prompt.md`, `tests/scenarios.md`, `tests/test_tools.py` |
