"""왜 RAG인가? — 빈 브릿지 카페 수업 도입용 데모.

같은 질문을 LLM에게 두 번 보냅니다:
  1. 카페 정보 없이 (모델이 추측해야 함)
  2. cafe_info.txt를 프롬프트에 붙여 넣고 (RAG의 핵심 아이디어)

cafe_info.txt는 디스크의 파일이 기준입니다. 에디터로 파일을 고치면 화면의
영수증이 자동으로 갱신되고, 화면에서 고친 내용은 "파일에 저장"으로 디스크에 씁니다.

OpenAI 호환 API라면 어떤 것이든 동작합니다 (xAI Grok, Groq, OpenAI...).
.env 파일에 API_KEY, BASE_URL, MODEL을 설정하세요 (.env.example 참고).
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL", "https://api.x.ai/v1"),
)
MODEL = os.getenv("MODEL", "grok-3-mini")
INFO_FILE = Path(__file__).parent / "cafe_info_long.txt"

app = Flask(__name__)


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


def ask_llm(messages):
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content


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
        return jsonify(error=f"API 호출 실패: {exc}"), 502

    prompt_text = "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)
    return jsonify(answer=answer, prompt=prompt_text)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
