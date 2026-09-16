"""Thin wrapper around the OpenAI-compatible chat API (Groq or xAI).

TODO (Task 1):
- Create an OpenAI client with API_KEY and BASE_URL from config.
- Implement chat(messages, tools=None) -> the assistant message object
  (response.choices[0].message). Only pass `tools` when it is not None.
- Add a __main__ block that sends [{"role": "user", "content": "Hello"}] and prints the reply.
"""


def chat(messages: list[dict], tools: list[dict] | None = None):
    """Send messages (and optional tool schemas) to the LLM and return the assistant message."""
    raise NotImplementedError("Task 1")
