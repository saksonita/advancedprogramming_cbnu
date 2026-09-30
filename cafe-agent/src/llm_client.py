"""Thin wrapper around the OpenAI-compatible chat API (Groq or xAI)."""
from openai import OpenAI

from src.config import API_KEY, BASE_URL, MODEL

_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat(messages: list[dict], tools: list[dict] | None = None):
    """Send messages (and optional tool schemas) to the LLM and return the assistant message."""
    kwargs = {"model": MODEL, "messages": messages}
    if tools is not None:
        kwargs["tools"] = tools
    response = _client.chat.completions.create(**kwargs)
    return response.choices[0].message


if __name__ == "__main__":
    reply = chat([{"role": "user", "content": "Hello"}])
    print(reply.content)
