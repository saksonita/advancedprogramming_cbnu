"""왜 RAG인가? — 빈 브릿지 카페 수업 도입용 데모.

같은 질문을 LLM에게 두 번 보냅니다:
  1. 카페 정보 없이 (모델이 추측해야 함)
  2. cafe_info.txt를 프롬프트에 붙여 넣고 (RAG의 핵심 아이디어)

cafe_info.txt는 디스크의 파일이 기준입니다. 에디터로 파일을 고치면 화면의
영수증이 자동으로 갱신되고, 화면에서 고친 내용은 "파일에 저장"으로 디스크에 씁니다.

/pdf 페이지에서는 학생이 직접 PDF를 올리고 그 문서와 대화합니다. 네 가지 방식을
화면에서 바꿔 가며 비교합니다 (수업 3~5단계 순서 그대로):
  - 전체 붙여 넣기: 뽑은 글자를 통째로 프롬프트에 (짧은 문서만 가능)
  - 키워드 검색:   문단으로 자른 뒤(청킹) TF-IDF로 비슷한 청크 3개만 (로컬, API 키 불필요)
  - 의미 검색:     같은 구조, 벡터만 임베딩 서버(bge-m3)의 뜻 벡터로 교체
  - 검색+리랭커:   임베딩으로 후보 10개 추린 뒤 리랭커(bge-reranker)가 정독해 재정렬
  - 에이전트:      retrieve를 search_documents 도구로 감싸 모델이 스스로 호출

OpenAI 호환 API라면 어떤 것이든 동작합니다 (xAI Grok, Groq, OpenAI...).
.env 파일에 API_KEY, BASE_URL, MODEL을 설정하세요 (.env.example 참고).
"""
import json
import os
import re
import unicodedata
import uuid
from pathlib import Path

import httpx
import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL", "https://api.x.ai/v1"),
)
MODEL = os.getenv("MODEL", "grok-3-mini")
# Qwen3처럼 '생각' 과정을 먼저 길게 쓰는 모델은 .env에 DISABLE_THINKING=1을 주면 바로 답합니다 (vLLM 전용 옵션).
CHAT_EXTRA = {"chat_template_kwargs": {"enable_thinking": False}} if os.getenv("DISABLE_THINKING") == "1" else {}
INFO_FILE = Path(__file__).parent / "cafe_info.txt"

# ---- PDF 채팅 설정 --------------------------------------------------------
# 업로드한 문서는 서버 메모리에만 둡니다 (서버를 재시작하면 사라짐).
# "전체 붙여 넣기"에서 프롬프트에 넣을 최대 글자 수. Groq 무료 등급은 분당 8,000 토큰이 한도라
# 한국어 기준 약 10,000자를 넘기면 413 오류가 납니다 (그게 바로 ①의 한계입니다). xAI 등은 더 올려도 됩니다.
MAX_PDF_CHARS = int(os.getenv("MAX_PDF_CHARS", "10000"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))          # 문단이 이보다 길면 이 길이로 자름
TOP_K = int(os.getenv("TOP_K", "3"))                      # 검색에서 고를 청크 수
# 검색 ③④에 쓰는 임베딩/리랭커 서버 (OpenAI 호환 /v1/embeddings, vLLM /v1/rerank). 비어 있으면 그 모드는 꺼집니다.
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
RERANK_BASE_URL = os.getenv("RERANK_BASE_URL", "")
RERANK_MODEL = os.getenv("RERANK_MODEL", "bge-reranker-v2-m3")
RERANK_CANDIDATES = int(os.getenv("RERANK_CANDIDATES", "10"))   # ④에서 임베딩으로 먼저 추리는 후보 수
embed_client = OpenAI(api_key=os.getenv("EMBED_API_KEY") or os.getenv("API_KEY"), base_url=EMBED_BASE_URL) if EMBED_BASE_URL else None
MAX_PDF_BYTES = 20 * 1024 * 1024
DOCS = {}   # doc_id -> {"name", "pages", "text", "chunks", "tfidf", "embeddings"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_PDF_BYTES
app.json.ensure_ascii = False   # JSON 응답의 한글을 \uXXXX 로 바꾸지 않고 그대로 보냄 (curl, 개발자 도구에서 읽기 좋게)


def build_messages(question, context=None):
    """질문만 보내거나, 질문 + 카페 정보(= 증강된 프롬프트)를 보냅니다."""
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


def read_info():
    """디스크에 있는 cafe_info.txt의 내용과 수정 시각을 읽어 옵니다."""
    return INFO_FILE.read_text(encoding="utf-8"), INFO_FILE.stat().st_mtime


@app.route("/")
def index():
    content, _ = read_info()
    return render_template("index.html", cafe_info=content, model=MODEL)


@app.get("/info")
def get_info():
    """화면이 주기적으로 호출해 파일이 바뀌었는지 확인합니다 (VS Code 등으로 편집한 경우)."""
    content, mtime = read_info()
    return jsonify(content=content, mtime=mtime)


@app.post("/info")
def save_info():
    """화면에서 편집한 내용을 cafe_info.txt에 저장합니다."""
    content = request.get_json().get("content", "")
    INFO_FILE.write_text(content, encoding="utf-8")
    return jsonify(mtime=INFO_FILE.stat().st_mtime)


@app.post("/ask")
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode")  # "plain" 또는 "rag"
    if not question:
        return jsonify(error="먼저 질문을 입력하세요."), 400

    context = data.get("context", "") if mode == "rag" else None
    messages = build_messages(question, context)
    try:
        answer = ask_llm(messages)
    except Exception as exc:  # 서버가 죽는 대신 API 문제를 화면에 보여 줌
        return jsonify(error=api_error_message(exc)), 502

    prompt_text = "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)
    return jsonify(answer=answer, prompt=prompt_text)


# ===========================================================================
# PDF 채팅: 청킹 -> 검색 -> 증강 -> (에이전트)
#
# 수업 순서 그대로입니다.
#   1. chunk      문서를 문단 단위로 자른다                 -> chunk_pages()
#   2. retrieve   질문과 가장 비슷한 청크 2~3개를 고른다      -> retrieve_keyword() / retrieve_embedding() / retrieve_rerank()
#   3. augment    고른 청크를 프롬프트에 붙여 넣는다           -> build_chat_messages()
#   5. tool       retrieve를 도구로 감싸 모델이 직접 호출하게 -> run_agent()
# 검색 방식을 바꿔도 retrieve 함수 하나만 바뀝니다. 나머지는 그대로입니다.
# ===========================================================================

def strip_think(text):
    """Qwen3 등이 답 앞에 붙이는 <think>...</think> 생각 과정을 떼어 냅니다."""
    return re.sub(r"<think>.*?</think>\s*", "", text or "", flags=re.S).strip()


def ask_llm(messages):
    response = client.chat.completions.create(model=MODEL, messages=messages, extra_body=CHAT_EXTRA)
    return strip_think(response.choices[0].message.content)


def api_error_message(exc):
    """API 오류를 학생이 읽을 수 있는 말로 바꿉니다. 특히 '프롬프트가 너무 큼'은 수업의 핵심 장면입니다."""
    text = str(exc)
    if ("413" in text or "rate_limit_exceeded" in text or "too large" in text.lower()
            or "maximum context length" in text or "context length" in text.lower()):
        m = re.search(r"Limit (\d+), Requested (\d+)", text)
        detail = f" 요청 {int(m.group(2)):,} 토큰, 한도 {int(m.group(1)):,} 토큰." if m else ""
        m = re.search(r"maximum context length is (\d+) tokens.*?(\d+) tokens", text, flags=re.S)
        detail = detail or (f" 모델 문맥 한도 {int(m.group(1)):,} 토큰, 요청 {int(m.group(2)):,} 토큰." if m else "")
        return ("프롬프트가 너무 커서 API가 거절했습니다." + detail +
                "\n이게 바로 '전체 붙여 넣기'의 한계입니다. ② 키워드 검색이나 ③ 의미 검색으로 바꾸면 "
                "관련 청크만 보내므로 프롬프트가 작아집니다. (또는 .env의 MAX_PDF_CHARS를 줄이거나 대화를 지우세요.)")
    return f"API 호출 실패: {exc}"


def clean_text(text):
    """PDF에서 뽑은 글자를 정리합니다.

    - NFC 정규화: 맥에서 만든 PDF는 한글이 자모로 풀려 나올 때가 있음 ('한' -> 'ㅎ','ㅏ','ㄴ')
    - 글꼴에 유니코드 표가 없을 때 pypdf가 남기는 (cid:123) 표시와 제어 문자 제거
    """
    text = unicodedata.normalize("NFC", text or "")
    text = re.sub(r"\(cid:\d+\)", "", text)
    text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    return text.strip()


def extract_pdf_pages(file_obj):
    """PDF의 모든 페이지에서 글자를 뽑아 쪽별 문자열 리스트로 돌려줍니다."""
    reader = PdfReader(file_obj)
    return [clean_text(page.extract_text()) for page in reader.pages]


def join_pages(pages):
    return "\n\n".join(f"[{n}쪽]\n{text}" for n, text in enumerate(pages, start=1))


# ---- 1. chunk ---------------------------------------------------------------

def chunk_pages(pages, size=CHUNK_SIZE):
    """문서를 문단(빈 줄 기준)으로 자릅니다. 너무 긴 문단은 size 글자씩 더 자릅니다.

    수업 코드의 `open("policy.txt").read().split("\\n\\n")` 와 같은 일입니다.
    PDF는 빈 줄이 거의 없을 때가 많아서 긴 문단을 한 번 더 자르는 단계가 붙었습니다.
    각 청크에 몇 쪽에서 왔는지 기록해 두면 화면에서 보여 주기 좋습니다.
    """
    chunks = []
    for page_no, page_text in enumerate(pages, start=1):
        for para in page_text.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            for i in range(0, len(para), size):
                chunks.append({"id": len(chunks), "page": page_no, "text": para[i:i + size]})
    return chunks


# ---- 2. retrieve ------------------------------------------------------------

def index_keyword(chunks):
    """TF-IDF: 어떤 글자 조각이 어느 청크에 많이 나오는지 센 표. API 키 없이 로컬에서 돕니다.

    한국어는 '대관은', '대관을'처럼 조사가 붙어 단어가 매번 달라지므로
    단어 대신 글자 2~3개짜리 조각(n-gram)으로 셉니다.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 3)).fit(c["text"] for c in chunks)
    return vec, vec.transform(c["text"] for c in chunks)


def retrieve_keyword(doc, question, k=TOP_K):
    """키워드 검색: 질문과 글자 조각이 많이 겹치는 청크 k개 (코사인 유사도)."""
    from sklearn.metrics.pairwise import cosine_similarity
    vec, chunk_vecs = doc["tfidf"]
    scores = cosine_similarity(vec.transform([question]), chunk_vecs)[0]
    top = scores.argsort()[::-1][:k]
    return [dict(doc["chunks"][i], score=round(float(scores[i]), 3)) for i in top]


def embed(texts):
    """문장 리스트를 임베딩 서버에 보내 뜻 벡터(길이 1로 정규화)로 받아 옵니다."""
    if embed_client is None:
        raise RuntimeError("EMBED_BASE_URL이 설정되지 않았습니다. .env를 확인하세요.")
    out = []
    for i in range(0, len(texts), 64):  # 한 번에 너무 많이 보내지 않도록 64개씩
        res = embed_client.embeddings.create(model=EMBED_MODEL, input=texts[i:i + 64])
        out.extend(d.embedding for d in res.data)
    vecs = np.array(out, dtype=np.float32)
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def retrieve_embedding(doc, question, k=TOP_K):
    """의미 검색: 단어가 달라도 뜻이 비슷한 청크 k개. retrieve_keyword()와 모양이 같습니다.

    바뀐 것은 '비교하는 벡터를 누가 만드느냐' 뿐입니다.
    TF-IDF는 글자를 세고, 임베딩 모델(bge-m3)은 문장의 뜻을 숫자 벡터로 바꿉니다.
    """
    if doc.get("embeddings") is None:  # 문서당 한 번만 계산해 둠
        doc["embeddings"] = embed([c["text"] for c in doc["chunks"]])
    q = embed([question])[0]
    scores = doc["embeddings"] @ q      # 정규화했으므로 내적 = 코사인 유사도
    top = scores.argsort()[::-1][:k]
    return [dict(doc["chunks"][i], score=round(float(scores[i]), 3)) for i in top]


def retrieve_rerank(doc, question, k=TOP_K):
    """검색 + 리랭커: 임베딩으로 후보 10개를 빨리 추린 뒤, 리랭커가 질문과 후보를 한 쌍씩 정독해서 다시 순위를 매깁니다.

    임베딩 검색은 빠르지만 대략적이고, 리랭커는 느리지만 정확합니다. 그래서 둘을 이어 씁니다.
    """
    if not RERANK_BASE_URL:
        raise RuntimeError("RERANK_BASE_URL이 설정되지 않았습니다. .env를 확인하세요.")
    candidates = retrieve_embedding(doc, question, k=RERANK_CANDIDATES)
    res = httpx.post(f"{RERANK_BASE_URL.rstrip('/')}/rerank", timeout=60,
                     headers={"Authorization": f"Bearer {os.getenv('RERANK_API_KEY') or os.getenv('API_KEY')}"},
                     json={"model": RERANK_MODEL, "query": question, "documents": [c["text"] for c in candidates]})
    res.raise_for_status()
    ranked = sorted(res.json()["results"], key=lambda r: -r["relevance_score"])[:k]
    return [dict(candidates[r["index"]], score=round(float(r["relevance_score"]), 3)) for r in ranked]


RETRIEVERS = {"keyword": retrieve_keyword, "embedding": retrieve_embedding, "rerank": retrieve_rerank}


# ---- 3. augment -------------------------------------------------------------

def build_chat_messages(context, history, question, note=""):
    """문서(전체 또는 고른 청크)를 system에 넣고, 지금까지의 대화와 새 질문을 이어 붙입니다.

    build_messages()와 같은 아이디어입니다. 다른 점은 둘뿐입니다:
      - 카페 정보 대신 PDF의 글자(전체 또는 검색된 청크)가 들어감
      - 이전 대화(history)를 함께 보내서 이어서 질문할 수 있음 (모델은 기억이 없음)
    """
    system = (
        "아래 문서 내용만 근거로 한국어로 답하세요. "
        "문서에 없는 내용은 문서에 없다고 말하세요. 질문의 언어가 다르면 그 언어로 답해도 됩니다.\n"
        f"{note}\n"
        f"=== 문서 시작 ===\n{context}\n=== 문서 끝 ==="
    )
    messages = [{"role": "system", "content": system}]
    for turn in history:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})
    return messages


def format_chunks(chunks):
    return "\n---\n".join(f"[청크 {c['id']}, {c['page']}쪽]\n{c['text']}" for c in chunks)


# ---- 5. tool: retrieve를 도구로 감싸기 ----------------------------------------

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_documents",
        "description": "업로드된 문서에서 질문과 관련된 부분을 찾아 돌려줍니다. 문서 내용이 필요하면 반드시 먼저 호출하세요.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "검색어 (질문의 핵심 단어들)"}},
            "required": ["query"],
        },
    },
}


def run_agent(doc, history, question, retriever=retrieve_keyword, max_rounds=4):
    """1주차 계산기 에이전트와 같은 구조. 도구가 숫자 대신 문서 조각을 돌려줄 뿐입니다.

    모델이 search_documents를 부르면 retrieve()를 실행해 결과를 돌려주고,
    모델이 도구 없이 답을 내놓을 때까지 반복합니다.
    """
    messages = [{"role": "system", "content":
                 "당신은 업로드된 문서에 대해 답하는 비서입니다. 문서 내용이 필요하면 search_documents 도구로 "
                 "검색한 뒤 그 결과만 근거로 한국어로 답하세요. 검색 결과에 없는 내용은 없다고 말하세요."}]
    for turn in history:
        if turn.get("role") in ("user", "assistant") and turn.get("content"):
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": question})

    trace, used = [], []
    for _ in range(max_rounds):
        msg = client.chat.completions.create(model=MODEL, messages=messages, tools=[SEARCH_TOOL],
                                             extra_body=CHAT_EXTRA).choices[0].message
        content = strip_think(msg.content)
        if not msg.tool_calls:                       # 도구 없이 최종 답변
            messages.append({"role": "assistant", "content": content})
            return content, messages, trace, used
        messages.append({"role": "assistant", "content": content, "tool_calls": [
            {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
            for tc in msg.tool_calls]})
        for tc in msg.tool_calls:                    # 도구 실행 = retrieve()
            query = json.loads(tc.function.arguments or "{}").get("query", question)
            found = retriever(doc, query)
            used.extend(found)
            trace.append({"query": query, "chunks": [c["id"] for c in found]})
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": format_chunks(found)})
    messages.append({"role": "assistant", "content": "(도구 호출 횟수 제한에 걸려 답을 만들지 못했습니다.)"})
    return messages[-1]["content"], messages, trace, used


def messages_to_text(messages):
    lines = []
    for m in messages:
        if m.get("tool_calls"):
            calls = ", ".join(f"{tc['function']['name']}({tc['function']['arguments']})" for tc in m["tool_calls"])
            lines.append(f"[assistant -> 도구 호출]\n{calls}")
        elif m["role"] == "tool":
            lines.append(f"[tool 결과]\n{m['content']}")
        else:
            lines.append(f"[{m['role']}]\n{m['content']}")
    return "\n\n".join(lines)


# ---- PDF 채팅 라우트 ---------------------------------------------------------

@app.route("/pdf")
def pdf_page():
    return render_template("pdf.html", model=MODEL, max_chars=MAX_PDF_CHARS, top_k=TOP_K, chunk_size=CHUNK_SIZE)


@app.post("/pdf/upload")
def pdf_upload():
    """PDF를 받아 글자를 뽑고 청크로 자른 뒤 doc_id를 돌려줍니다. 화면은 이 id로 질문합니다."""
    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify(error="PDF 파일을 선택하세요."), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify(error="PDF 파일만 올릴 수 있습니다."), 400
    try:
        pages = extract_pdf_pages(file.stream)
    except Exception as exc:
        return jsonify(error=f"PDF를 읽지 못했습니다: {exc}"), 400
    if not any(pages):
        return jsonify(error="이 PDF에서 글자를 찾지 못했습니다. 스캔 이미지 PDF라면 OCR이 필요합니다."), 400

    chunks = chunk_pages(pages)
    doc_id = uuid.uuid4().hex
    name = unicodedata.normalize("NFC", file.filename)
    DOCS[doc_id] = {"name": name, "pages": pages, "text": join_pages(pages),
                    "chunks": chunks, "tfidf": index_keyword(chunks), "embeddings": None}
    text = DOCS[doc_id]["text"]
    return jsonify(doc_id=doc_id, name=name, pages=len(pages), chars=len(text),
                   truncated=len(text) > MAX_PDF_CHARS, chunks=chunks)


@app.post("/pdf/chat")
def pdf_chat():
    data = request.get_json()
    doc = DOCS.get(data.get("doc_id", ""))
    if doc is None:
        return jsonify(error="먼저 PDF를 올리세요. (서버를 재시작했다면 다시 올려야 합니다.)"), 400
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify(error="먼저 질문을 입력하세요."), 400
    history = data.get("history") or []
    mode = data.get("mode", "full")   # full | keyword | embedding | rerank | agent

    try:
        if mode == "agent":
            answer, messages, trace, used = run_agent(doc, history, question)
            return jsonify(answer=answer, prompt=messages_to_text(messages), retrieved=used, trace=trace,
                           prompt_chars=len(messages_to_text(messages)))

        if mode in RETRIEVERS:
            retrieved = RETRIEVERS[mode](doc, question)
            context = format_chunks(retrieved)
            note = f"(전체 {len(doc['chunks'])}개 청크 중 검색으로 고른 {len(retrieved)}개만 포함)"
        else:
            retrieved = None
            context = doc["text"][:MAX_PDF_CHARS]
            note = f"(앞 {MAX_PDF_CHARS:,}자만 포함, 뒷부분은 잘림)" if len(doc["text"]) > MAX_PDF_CHARS else ""
        messages = build_chat_messages(context, history, question, note)
        answer = ask_llm(messages)
    except RuntimeError as exc:   # 임베딩/리랭커 서버가 .env에 없음
        return jsonify(error=str(exc)), 501
    except Exception as exc:
        return jsonify(error=api_error_message(exc)), 502

    prompt_text = messages_to_text(messages)
    return jsonify(answer=answer, prompt=prompt_text, retrieved=retrieved, trace=None, prompt_chars=len(prompt_text))


if __name__ == "__main__":
    # 로컬: python app.py -> http://127.0.0.1:5000
    # 배포(Render 등)는 PORT 환경변수를 주므로 모든 주소에서 받고 디버그를 끕니다.
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=os.getenv("PORT") is None, host="0.0.0.0" if os.getenv("PORT") else "127.0.0.1", port=port)
