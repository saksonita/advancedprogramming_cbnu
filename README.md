# Advanced Business Programming (고급 비즈니스 프로그래밍)

Week-by-week live demo code for the course.

## Week 1 — Calculator Tool Agent (`agent.py`)

A minimal Observe → Think → Act agent loop, mirroring slides 12 and 16-17.

- **Observe** (`observe`) — take the raw user input.
- **Think** (`think`) — decide whether a tool call is needed. Since we
  haven't wired up a real LLM API yet (slide 15), this is simulated with a
  regex-based rule check today. In Week 2, a real LLM call replaces this
  function.
- **Act** (`act`) — run the tool (`calculator`) if needed, and format the
  response.

The `calculator` tool evaluates basic arithmetic expressions safely using
Python's `ast` module (never `eval()`).

### Run it

```bash
python3 agent.py
```

No external dependencies — standard library only (`ast`, `operator`, `re`).
