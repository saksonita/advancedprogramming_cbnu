"""Why RAG? — hook demo for the Bean Bridge Cafe.

Sends the same question to the LLM twice:
  1. without any cafe information (the model has to guess)
  2. with cafe_info.txt pasted into the prompt (the core idea of RAG)

Works with any OpenAI-compatible API (xAI Grok, Groq, OpenAI...).
Set API_KEY, BASE_URL and MODEL in a .env file (see .env.example).
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
INFO_FILE = Path(__file__).parent / "cafe_info.txt"

app = Flask(__name__)


def build_messages(question, context=None):
    """Plain question, or question + cafe information (= augmented prompt)."""
    if context is None:
        return [{"role": "user", "content": question}]
    return [
        {
            "role": "system",
            "content": "Answer using only the cafe information below. "
            "If the information does not cover the question, say so.",
        },
        {"role": "user", "content": f"Cafe information:\n{context}\n\nQuestion: {question}"},
    ]


def ask_llm(messages):
    response = client.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content


@app.route("/")
def index():
    return render_template("index.html", cafe_info=INFO_FILE.read_text(encoding="utf-8"), model=MODEL)


@app.post("/ask")
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode")  # "plain" or "rag"
    if not question:
        return jsonify(error="Type a question first."), 400

    context = data.get("context", "") if mode == "rag" else None
    messages = build_messages(question, context)
    try:
        answer = ask_llm(messages)
    except Exception as exc:  # show API problems in the UI instead of crashing
        return jsonify(error=f"API call failed: {exc}"), 502

    prompt_text = "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)
    return jsonify(answer=answer, prompt=prompt_text)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
