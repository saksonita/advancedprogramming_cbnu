# 이 도구는 어떻게 동작하나요? (학생용 설명)

이 데모는 세 부분으로 이루어져 있습니다. 브라우저 화면, Flask 서버, 그리고 외부 LLM API입니다. 코드는 전부 합쳐 300줄이 안 되고, 여러분이 꼭 이해해야 할 부분은 그중 30줄 정도입니다.

```
 브라우저 (templates/index.html)          Flask 서버 (app.py)              LLM API (Groq, xAI...)
 ┌──────────────────────────┐          ┌──────────────────────┐         ┌──────────────────┐
 │ 영수증 textarea          │          │                      │         │                  │
 │ 질문 input               │ POST /ask│  build_messages()    │ HTTPS   │  모델이 답을      │
 │ [모델에게만 질문]        │ ───────▶ │   질문 (+ 카페 정보) │ ──────▶ │  생성            │
 │ [카페 정보와 함께 질문]  │          │   → messages 리스트  │         │                  │
 │                          │ ◀─────── │  ask_llm()           │ ◀────── │                  │
 │ 답변 패널 2개            │ JSON     │   → 답변 문자열      │ JSON    │                  │
 │                          │          │                      │         └──────────────────┘
 │ 2초마다 GET /info        │ ───────▶ │  cafe_info.txt 읽기  │ ──┐
 │ [파일에 저장] POST /info │ ───────▶ │  cafe_info.txt 쓰기  │ ──┼──▶ 디스크의 cafe_info.txt
 └──────────────────────────┘          └──────────────────────┘   │
                                                                  └──  VS Code로도 편집 가능
```

핵심 메시지는 하나입니다. **모델은 바뀌지 않습니다. 바뀌는 것은 프롬프트에 들어가는 텍스트뿐입니다.**

---

## 1. 질문 하나가 처리되는 과정

"카페 정보와 함께 질문" 버튼을 눌렀을 때 일어나는 일을 순서대로 따라가 봅시다.

1. **브라우저**가 질문 칸의 글, 영수증 textarea의 글, 그리고 모드(`"rag"`)를 JSON으로 묶어 `/ask`에 POST 요청을 보냅니다.
2. **Flask 서버**의 `ask()` 함수가 요청을 받습니다. 모드가 `"rag"`이면 영수증 텍스트를 `context`로 쓰고, `"plain"`이면 `context`를 `None`으로 둡니다.
3. `build_messages(question, context)`가 LLM에 보낼 **메시지 리스트**를 만듭니다. 이 함수가 데모의 전부입니다.
4. `ask_llm(messages)`가 OpenAI 호환 API로 메시지를 보내고 답변 문자열을 돌려받습니다.
5. 서버는 답변과 함께, 실제로 보낸 프롬프트 전체를 문자열로 합쳐 JSON으로 돌려줍니다.
6. **브라우저**는 답변을 Markdown으로 렌더링해 패널에 보여 주고, "전송된 프롬프트 보기"에 프롬프트 원문을 채웁니다.

"둘 다 질문"을 누르면 1~6을 `plain`과 `rag` 두 모드로 동시에 실행합니다. 같은 질문, 같은 모델, 다른 프롬프트입니다.

---

## 2. 꼭 읽어야 할 함수: `build_messages()`

```python
def build_messages(question, context=None):
    if context is None:
        return [{"role": "user", "content": question}]
    return [
        {
            "role": "system",
            "content": "아래 카페 정보만 사용해서 한국어로 답하세요. "
            "정보에 질문과 관련된 내용이 없으면 없다고 말하세요.",
        },
        {"role": "user", "content": f"카페 정보:\n{context}\n\n질문: {question}"},
    ]
```

- `context`가 없으면 질문 한 줄만 보냅니다. 모델은 자기 기억(학습 데이터)만으로 답해야 합니다.
- `context`가 있으면 두 가지를 더합니다.
  - **system 메시지**: 모델에게 역할을 지시합니다. "주어진 정보만 써라, 없으면 없다고 해라."
  - **user 메시지**: 카페 정보 전체를 붙이고, 그 뒤에 질문을 붙입니다.

이것이 RAG의 **A(Augmented, 증강)** 와 **G(Generation, 생성)** 입니다. 아직 **R(Retrieval, 검색)** 은 없습니다. 지금은 파일 전체를 통째로 붙이고 있기 때문입니다. 수업의 나머지는 "어떻게 필요한 부분만 골라서 붙일 것인가"를 다룹니다.

---

## 3. LLM을 호출하는 부분: `ask_llm()`

```python
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL", "https://api.x.ai/v1"),
)
MODEL = os.getenv("MODEL", "grok-3-mini")

def ask_llm(messages):
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content
```

- `openai` 패키지를 쓰지만 OpenAI 회사의 모델만 쓰는 것이 아닙니다. Groq, xAI 등 많은 회사가 **같은 요청 형식**(OpenAI 호환 API)을 지원합니다. 그래서 `BASE_URL`과 `MODEL`만 바꾸면 다른 회사의 모델로 바뀝니다.
- API 키는 코드에 적지 않고 `.env` 파일에 둡니다. `load_dotenv()`가 그 파일을 읽어 환경 변수로 올려 줍니다. `.env`는 `.gitignore`에 있어서 GitHub에 올라가지 않습니다.
- `response.choices[0].message.content`가 모델이 생성한 텍스트입니다.

---

## 4. 파일이 "시스템의 데이터"인 이유: `/info`

```python
INFO_FILE = Path(__file__).parent / "cafe_info.txt"   # 또는 cafe_info_long.txt

@app.get("/info")
def get_info():
    content, mtime = read_info()
    return jsonify(content=content, mtime=mtime)

@app.post("/info")
def save_info():
    content = request.get_json().get("content", "")
    INFO_FILE.write_text(content, encoding="utf-8")
    return jsonify(mtime=INFO_FILE.stat().st_mtime)
```

- 카페 정보의 원본은 **디스크의 파일**입니다. 브라우저의 영수증은 그 파일을 보여 주는 창일 뿐입니다.
- 브라우저는 2초마다 `GET /info`를 호출해 파일의 **수정 시각(mtime)** 을 확인합니다. 시각이 바뀌었으면 파일이 바뀐 것이므로 영수증을 새로 불러옵니다. 그래서 VS Code에서 파일을 고치고 저장하면 화면이 저절로 바뀝니다.
- "파일에 저장" 버튼은 반대 방향입니다. 영수증의 글을 `POST /info`로 보내면 서버가 파일에 씁니다.
- `INFO_FILE` 한 줄만 바꾸면 다른 파일을 기준 데이터로 쓸 수 있습니다. 긴 매뉴얼로 바꿔 보려면 `cafe_info_long.txt`로 바꾸고 서버를 다시 실행하세요.

실제 서비스라면 이 자리에 파일 하나가 아니라 문서 수천 개, 데이터베이스, 사내 위키가 옵니다. 구조는 같습니다. **시스템에 있는 데이터가 바뀌면 답이 바뀝니다.**

---

## 5. 화면 쪽 코드: `templates/index.html`

HTML 파일 하나에 CSS와 JavaScript가 함께 들어 있습니다. 서버 쪽만큼 중요하지는 않지만, 세 가지 함수만 알면 됩니다.

| 함수 | 하는 일 |
|---|---|
| `ask(mode)` | `/ask`에 fetch로 POST 요청을 보내고, 응답을 패널에 표시합니다. |
| `show(mode, text, kind)` | 답변 패널에 글을 넣습니다. 모델 답변은 Markdown으로 렌더링하고(`marked` + `DOMPurify`), "생각하는 중..." 같은 상태 메시지는 그대로 넣습니다. |
| `checkDisk()` | 2초마다 `/info`를 호출해 파일이 바뀌었는지 확인하고, 바뀌었으면 영수증을 갱신합니다. |

Jinja 템플릿 문법 `{{ cafe_info }}`, `{{ model }}`은 서버가 페이지를 처음 보낼 때 값을 채워 넣는 자리입니다.

`marked`는 모델이 보낸 Markdown(표, 굵은 글씨, 목록)을 HTML로 바꾸고, `DOMPurify`는 그 HTML에서 위험한 태그(script 등)를 걸러 냅니다. 모델이 생성한 텍스트를 화면에 그대로 `innerHTML`로 넣으면 안 되는 이유를 생각해 보세요.

---

## 6. 파일 구성 한눈에 보기

| 파일 | 역할 | 읽어야 하나? |
|---|---|---|
| `app.py` | Flask 서버. 프롬프트 조립, LLM 호출, 파일 읽기·쓰기 | 예, 전부 (약 100줄) |
| `templates/index.html` | 화면. 버튼, 패널, 파일 동기화 | `<script>` 부분만 |
| `cafe_info.txt` | 다섯 줄짜리 카페 규정. 모델이 알 수 없는 지어낸 정보 | 예 |
| `cafe_info_long.txt` | 같은 카페의 150줄짜리 운영 매뉴얼 | 훑어보기 |
| `.env.example` | API 키, 주소, 모델 이름 설정 예시 | 복사해서 `.env` 만들기 |
| `requirements.txt` | 필요한 패키지 3개: flask, openai, python-dotenv | 설치만 |

---

## 7. 직접 해 보기

1. **system 메시지 바꾸기.** `build_messages()`의 system 메시지에서 "정보에 질문과 관련된 내용이 없으면 없다고 말하세요"를 지우고 "무료 와이파이 있나요?"를 물어보세요. 무엇이 달라지나요?
2. **다른 모델 쓰기.** `.env`의 `MODEL`을 바꿔 보세요. Groq라면 `llama-3.3-70b-versatile` 같은 이름을 쓸 수 있습니다. 같은 프롬프트에 다른 모델이 어떻게 답하는지 비교하세요.
3. **프롬프트 형식 바꾸기.** user 메시지에서 카페 정보와 질문의 순서를 바꾸거나, 카페 정보를 `<정보>...</정보>` 태그로 감싸 보세요. 답의 품질이 달라지나요?
4. **긴 파일로 바꾸기.** `INFO_FILE`을 `cafe_info_long.txt`로 바꾸고 "전송된 프롬프트 보기"를 여세요. 질문 하나에 몇 글자가 들어가나요? 매뉴얼이 300쪽이면 어떻게 될까요?
5. **토큰 세기.** `ask_llm()`에서 `response.usage`를 출력해 보세요. 짧은 파일과 긴 파일에서 입력 토큰 수가 얼마나 차이 나나요? 이것이 다음 주제인 **검색(retrieval)** 이 필요한 이유입니다.

---

## 8. 자주 나오는 질문

**Q. 이게 정말 RAG인가요? 벡터 DB가 없는데요.**
RAG의 정의는 "생성 전에 외부 정보를 가져와 프롬프트에 넣는 것"입니다. 벡터 DB, 임베딩, 청킹은 그 "가져오는" 단계를 큰 데이터에서도 되게 만드는 도구이지 정의의 일부가 아닙니다. 이 데모는 데이터가 작아서 그 단계가 "파일 전체 읽기"로 끝났을 뿐입니다.

**Q. 모델이 카페 정보를 학습한 건가요?**
아닙니다. 모델의 가중치는 전혀 바뀌지 않았습니다. 매 요청마다 텍스트를 다시 보내고 있고, 요청이 끝나면 모델은 그 내용을 잊습니다. 파일을 고치면 바로 답이 바뀌는 것이 그 증거입니다. 학습(fine-tuning)이었다면 그렇게 즉시 바뀔 수 없습니다.

**Q. 모델이 카페 정보에 없는 내용을 지어내면요?**
그래서 system 메시지에 "없으면 없다고 말하라"고 지시합니다. 하지만 지시는 보장이 아닙니다. 실제 서비스에서는 답에 출처를 붙이게 하거나, 답을 다시 검증하는 단계를 둡니다. 이 데모에서는 "모델 혼자" 패널이 바로 그 지어내는 모습을 보여 주는 역할입니다.

**Q. `.env`에 키를 넣었는데 "Missing credentials" 오류가 나요.**
`.env` 파일 형식을 확인하세요. 한 줄에 `API_KEY=값` 형태여야 하고, 따옴표를 겹쳐 쓰면 python-dotenv가 그 줄을 읽지 못합니다. 서버를 실행했을 때 "could not parse statement" 경고가 나오면 그 줄 번호를 보세요.
