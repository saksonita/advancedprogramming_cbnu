# Advanced Business Programming (고급 비즈니스 프로그래밍)

Week-by-week live demo code for the course.

## Week 1 — Calculator Tool Agent (`agent.py`)

A minimal Observe → Think → Act agent loop, mirroring slides 12 and 16-17.

- **Observe** (`observe`) — take the raw user input.
- **Think** (`think`) — calls the Groq API (a real LLM) with the `TOOLS`
  spec so the model decides for itself whether/how to call `calculator`.
- **Act** (`act`) — run the tool (`calculator`) if needed, and format the
  response.

The `calculator` tool evaluates basic arithmetic expressions safely using
Python's `ast` module (never `eval()`).

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then put your real key in .env: GROQ_KEY=...
```

`.env` is gitignored — never commit your real API key.

### Run it (console)

```bash
python3 agent.py
```

### Run it (web UI)

A small browser UI visualizes the same Observe → Think → Act pipeline live,
so students can watch each step fill in with real data as they type a
question:

```bash
python3 app.py
```

Then open <http://localhost:8000>. `app.py` uses only `http.server` from the
standard library (no Flask/Django) and imports `observe`/`think`/`act`
directly from `agent.py` — it's a UI on top of the same functions the
console demo uses, not a separate implementation.

Try the example buttons, or type your own question:

- `(23 + 19) × 4는?` → tool call detected, `calculator` runs
- `100 / 4 - 5 계산해줘` → tool call detected
- `안녕하세요, 오늘 날씨 어때요?` → no expression found, no tool call
