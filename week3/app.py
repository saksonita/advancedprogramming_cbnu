"""
app.py
고급 비즈니스 프로그래밍 · 3주차 라이브 데모 — 도구(Tool) 실습 웹 UI
Advanced Business Programming · Week 3 Live Demo — Tool Practices Web UI

tools.py · schemas.py · llm.py · evaluate.py 의 함수를 그대로 호출해서,
도구 호출 루프의 각 단계(판단 → 검증 → 승인 → 실행 → 결과 반환)를
브라우저 화면에서 한 단계씩 보여주는 얇은 웹 서버입니다.
A thin web server that calls the Week 3 modules as-is and replays every step of
the tool loop (think → validate → approve → execute → return) in the browser.

1주차 app.py 와 같이 표준 라이브러리만 사용합니다.
Standard library only, same as the Week 1 app.py.

실행 방법 (How to run):
    cd week3
    python3 app.py
    -> http://localhost:8600 접속 (open in a browser)

API 키 없이도 가짜 LLM(FakeClient)으로 전부 동작합니다.
진짜 LLM(Groq)은 화면에서 모드를 바꾸면 .env 의 GROQ_KEY 를 사용합니다.
"""

import json
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import agent_loop
from agent_loop import MAX_TURNS, SYSTEM_PROMPT, make_client, run_agent
from evaluate import CASES
from schemas import TOOLS, ValidationError, validate
from tools import DATA, FUNCS, INVENTORY, NEEDS_APPROVAL

WEB_DIR = Path(__file__).parent / "web"
PORT = 8600

# 진짜 클라이언트는 키가 필요하므로 처음 요청할 때 한 번만 만든다.
# The real client needs a key, so build it lazily and reuse it.
_REAL_CLIENT = None


def get_client(mode: str):
    global _REAL_CLIENT
    if mode == "real":
        if _REAL_CLIENT is None:
            _REAL_CLIENT = make_client(real=True)
        return _REAL_CLIENT
    return make_client(real=False)  # 가짜는 세션마다 새로 — call_001 부터 다시 시작


# ---------------------------------------------------------------------------
# 세션 — 승인 대기 중인 루프를 잠시 붙잡아 두는 곳
# Sessions: where a loop waits while the browser asks the user yes / no.
# ---------------------------------------------------------------------------
SESSIONS: dict[str, dict] = {}


def new_session(question: str, mode: str) -> dict:
    session = {
        "id": uuid.uuid4().hex[:8],
        "mode": mode,
        "client": get_client(mode),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "turn": 0,          # LLM 호출 횟수 — MAX_TURNS 로 제한 (safeguard 3)
        "queue": [],        # 아직 실행하지 않은 tool_calls (tool calls not yet run)
        "approvals": {},    # call_id → "yes" / "no"
        "trace": [],        # 호출 로그 (safeguard 4)
        "status": "running",
    }
    SESSIONS[session["id"]] = session
    return session


def _execute_call(session: dict, call: dict, events: list) -> dict | None:
    """
    도구 하나를 실행한다: 매핑 → 검증 → 승인 → 실행 → 로그.
    agent_loop.run_tool 과 같은 순서지만, 화면용 이벤트를 함께 남기고
    승인이 필요하면 None 을 돌려주어 루프를 잠시 멈춘다.
    Same order as agent_loop.run_tool, but emits UI events and returns None
    when it must pause for human approval.
    """
    call_id = call["id"]
    name = call["function"]["name"]
    raw_args = json.loads(call["function"]["arguments"])
    start = time.perf_counter()

    fn = FUNCS.get(name)  # 안전장치 1 — 이름 → 함수 매핑
    if fn is None:  # 안전장치 2 — 없는 도구도 오류를 결과로 돌려준다
        result = {"error": f"알 수 없는 도구: {name}. 사용 가능: {list(FUNCS)}"}
        events.append({"type": "validate", "call_id": call_id, "ok": False, "detail": result["error"]})
        return _finish_call(session, events, call_id, name, raw_args, result, start)

    try:
        args = validate(name, raw_args)  # 검증 후 실행 (validate, then run)
    except ValidationError as e:
        result = {"error": str(e)}
        events.append({"type": "validate", "call_id": call_id, "ok": False, "detail": str(e)})
        return _finish_call(session, events, call_id, name, raw_args, result, start)
    events.append({"type": "validate", "call_id": call_id, "ok": True, "args": args})

    if name in NEEDS_APPROVAL:  # 실습 4 — 되돌릴 수 없는 도구는 사람이 승인한다
        decision = session["approvals"].get(call_id)
        if decision is None:
            session["status"] = "needs_approval"
            session["pending"] = {"call_id": call_id, "tool": name, "args": args}
            events.append({"type": "approval_request", "call_id": call_id, "tool": name, "args": args})
            return None
        approved = decision.strip().lower() in {"y", "yes", "네"}
        events.append({"type": "approval", "call_id": call_id, "approved": approved})
        if not approved:
            result = {"error": "사용자가 실행을 거절했습니다. 다른 방법을 제안하세요."}
            return _finish_call(session, events, call_id, name, args, result, start)
    else:
        events.append({"type": "approval", "call_id": call_id, "skipped": True})

    result = fn(**args)
    return _finish_call(session, events, call_id, name, args, result, start)


def _finish_call(session, events, call_id, name, args, result, start) -> dict:
    seconds = round(time.perf_counter() - start, 3)
    entry = {"call_id": call_id, "tool": name, "args": args, "result": result, "seconds": seconds}
    session["trace"].append(entry)
    events.append({"type": "tool_result", **entry})
    # 같은 id 를 붙여 결과를 돌려준다 (슬라이드 12) — return the result under the same id
    session["messages"].append(
        {"role": "tool", "tool_call_id": call_id, "content": json.dumps(result, ensure_ascii=False)}
    )
    return result


def step_session(session: dict) -> list[dict]:
    """
    루프를 돌린다: 최종 답변이 나오거나, 승인이 필요하거나, 한도에 닿을 때까지.
    Run the loop until a final answer, an approval request, or the turn limit.
    """
    events: list[dict] = []
    session["status"] = "running"
    session.pop("pending", None)

    while True:
        # 1) 실행 대기 중인 도구 호출이 있으면 먼저 처리한다
        while session["queue"]:
            call = session["queue"][0]
            if _execute_call(session, call, events) is None:
                return events  # 승인 대기 — 브라우저가 답을 주면 다시 온다
            session["queue"].pop(0)

        # 2) 안전장치 3 — 반복 한도
        if session["turn"] >= MAX_TURNS:
            session["status"] = "done"
            answer = f"반복 한도({MAX_TURNS}회)에 도달해 중단했습니다."
            events.append({"type": "limit", "max_turns": MAX_TURNS, "answer": answer})
            return events

        # 3) LLM 에게 묻는다 — 도구를 부를지, 답을 낼지
        session["turn"] += 1
        started = time.perf_counter()
        message = session["client"].chat(session["messages"], TOOLS)
        usage = message.pop("usage", None)
        session["messages"].append(message)
        calls = message.get("tool_calls") or []
        events.append(
            {
                "type": "llm",
                "turn": session["turn"],
                "max_turns": MAX_TURNS,
                "seconds": round(time.perf_counter() - started, 3),
                "usage": usage,
                "message": message,
            }
        )

        if not calls:  # 도구가 더 필요 없다 → 최종 답변
            session["status"] = "done"
            events.append({"type": "final", "answer": message.get("content", "")})
            return events

        session["queue"] = list(calls)


# ---------------------------------------------------------------------------
# 실습 2 — 스키마 검증 놀이터: 어느 층에서 걸리는지 보여준다
# Practice 2 playground: show WHICH layer rejects the input.
# ---------------------------------------------------------------------------
LAYERS = ["syntax", "shape", "type", "value", "fact"]


def _layer_of(message: str) -> str:
    """validate() 의 오류 메시지를 슬라이드 14 의 네 층에 대응시킨다."""
    if "object여야" in message or "알 수 없는 도구" in message:
        return "syntax"
    if "누락" in message or "알 수 없는 인자" in message:
        return "shape"
    if "타입 오류" in message or "정수여야" in message:
        return "type"
    return "value"


def check_arguments(tool: str, raw_text: str) -> dict:
    layers = {name: {"status": "skip"} for name in LAYERS}

    try:  # ① 구문 — JSON 이 파싱되는가
        args = json.loads(raw_text)
    except json.JSONDecodeError as e:
        layers["syntax"] = {"status": "fail", "detail": f"JSON 구문 오류: {e.msg} (위치 {e.pos})"}
        return {"layers": layers, "tool": tool}
    layers["syntax"] = {"status": "ok", "detail": "JSON 으로 읽었습니다"}

    try:  # ② 형태 ③ 타입 ④ 값 — schemas.validate()
        checked = validate(tool, args)
    except ValidationError as e:
        failed = _layer_of(str(e))
        for name in ["shape", "type", "value"]:
            if name == failed:
                layers[name] = {"status": "fail", "detail": str(e)}
                break
            layers[name] = {"status": "ok"}
        return {"layers": layers, "tool": tool}
    for name in ["shape", "type", "value"]:
        layers[name] = {"status": "ok"}
    layers["value"]["detail"] = f"기본값 채운 인자: {json.dumps(checked, ensure_ascii=False)}"

    # ⑤ 사실 — 스키마를 통과해도 존재하지 않을 수 있다 (실습 2 의 핵심)
    if tool in NEEDS_APPROVAL:
        layers["fact"] = {
            "status": "skip",
            "detail": "create_order 는 되돌릴 수 없어 여기서는 실행하지 않습니다. '도구 호출 루프' 탭에서 승인과 함께 시험하세요.",
        }
        return {"layers": layers, "tool": tool, "args": checked}

    result = FUNCS[tool](**checked)
    if "error" in result:
        layers["fact"] = {"status": "fail", "detail": result["error"]}
    else:
        layers["fact"] = {"status": "ok", "detail": json.dumps(result, ensure_ascii=False)}
    return {"layers": layers, "tool": tool, "args": checked, "result": result}


# ---------------------------------------------------------------------------
# 실습 8 — 평가: evaluate.CASES 를 돌려 케이스별 결과까지 화면에 보낸다
# Practice 8: run evaluate.CASES and return per-case rows for the table.
# ---------------------------------------------------------------------------
def run_evaluation(mode: str) -> dict:
    client = get_client(mode)
    rows = []
    for case in CASES:
        agent_loop.TRACE.clear()
        start = time.perf_counter()
        answer = run_agent(case["q"], client, auto_approve="yes")
        elapsed = time.perf_counter() - start

        used_tools = [t["tool"] for t in agent_loop.TRACE]
        used_args = {k: v for t in agent_loop.TRACE for k, v in t["args"].items()}
        ok_selection = used_tools == case["tools"]           # 선택 (selection)
        ok_arguments = all(used_args.get(k) == v for k, v in case["args"].items())  # 인자
        ok_task = case["answer"] in answer                    # 과제 (task)

        rows.append(
            {
                "q": case["q"],
                "expected_tools": case["tools"],
                "used_tools": used_tools,
                "expected_args": case["args"],
                "used_args": used_args,
                "expected_answer": case["answer"],
                "answer": answer,
                "selection": ok_selection,
                "arguments": ok_arguments,
                "task": ok_task,
                "layer": None
                if ok_selection and ok_arguments and ok_task
                else "선택" if not ok_selection else "인자" if not ok_arguments else "과제",
                "seconds": round(elapsed, 3),
                "calls": len(agent_loop.TRACE),
            }
        )

    n = len(rows)
    return {
        "mode": mode,
        "n": n,
        "selection": sum(r["selection"] for r in rows) / n,
        "arguments": sum(r["arguments"] for r in rows) / n,
        "task": sum(r["task"] for r in rows) / n,
        "avg_seconds": sum(r["seconds"] for r in rows) / n,
        "avg_calls": sum(r["calls"] for r in rows) / n,
        "rows": rows,
    }


def reference() -> dict:
    return {
        "tools": TOOLS,
        "needs_approval": sorted(NEEDS_APPROVAL),
        "max_turns": MAX_TURNS,
        "system_prompt": SYSTEM_PROMPT,
        "inventory": [{"product_id": pid, **row} for pid, row in INVENTORY.items()],
        "policy": (DATA / "order_policy.md").read_text(encoding="utf-8"),
    }


# ---------------------------------------------------------------------------
# HTTP 핸들러 (HTTP handler)
# ---------------------------------------------------------------------------
class ToolDemoHandler(BaseHTTPRequestHandler):
    _STATIC_FILES = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css; charset=utf-8"),
        "/script.js": ("script.js", "application/javascript; charset=utf-8"),
    }

    def log_message(self, fmt, *args):
        pass  # 데모용 — 접속 로그 생략 (skip access logs)

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/reference":
            self._send_json(reference())
            return
        entry = self._STATIC_FILES.get(self.path)
        if entry is None:
            self.send_error(404, "Not Found")
            return
        filename, content_type = entry
        content = (WEB_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        try:
            if self.path == "/api/ask":
                session = new_session(body.get("question", ""), body.get("mode", "fake"))
                events = step_session(session)
                self._send_json(self._session_view(session, events))
            elif self.path == "/api/approve":
                session = SESSIONS.get(body.get("session_id", ""))
                if session is None or session.get("status") != "needs_approval":
                    self._send_json({"error": "승인 대기 중인 세션이 없습니다."}, 400)
                    return
                session["approvals"][session["pending"]["call_id"]] = body.get("answer", "no")
                events = step_session(session)
                self._send_json(self._session_view(session, events))
            elif self.path == "/api/validate":
                self._send_json(check_arguments(body.get("tool", ""), body.get("args", "")))
            elif self.path == "/api/evaluate":
                self._send_json(run_evaluation(body.get("mode", "fake")))
            else:
                self.send_error(404, "Not Found")
        except KeyError as e:  # 대개 GROQ_KEY 가 없을 때 (usually a missing GROQ_KEY)
            self._send_json({"error": f"환경변수 {e} 가 없습니다. week3/.env 에 GROQ_KEY 를 넣어 주세요."}, 500)
        except Exception as e:  # noqa: BLE001 — 데모 UI 에는 오류를 그대로 보여준다
            self._send_json({"error": f"{type(e).__name__}: {e}"}, 500)

    @staticmethod
    def _session_view(session: dict, events: list) -> dict:
        view = {
            "session_id": session["id"],
            "status": session["status"],
            "turn": session["turn"],
            "max_turns": MAX_TURNS,
            "events": events,
            "trace": session["trace"],
        }
        if session["status"] == "needs_approval":
            view["pending"] = session["pending"]
        else:
            SESSIONS.pop(session["id"], None)  # 끝난 세션은 정리한다
        return view


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ToolDemoHandler)
    print(f"3주차 도구 데모 서버 실행 중 (Week 3 tool demo running): http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
