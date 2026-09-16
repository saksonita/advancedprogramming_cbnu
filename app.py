"""
app.py
고급 비즈니스 프로그래밍 · 1주차 라이브 데모 — 계산기 에이전트 웹 UI
Advanced Business Programming · Week 1 Live Demo — Calculator Agent Web UI

agent.py에 있는 Observe → Think → Act 세 함수를 그대로 호출해서,
각 단계의 입력/출력을 브라우저 화면에 순서대로 보여주는 아주 얇은 웹 서버입니다.
A thin web server that calls agent.py's Observe -> Think -> Act functions
as-is and shows each step's input/output on screen, in order.

agent.py처럼 표준 라이브러리만 사용합니다 (아직 프레임워크를 정하지 않았으므로).
Standard library only, same as agent.py (no framework has been chosen yet).

실행 방법 (How to run):
    python3 app.py
    -> http://localhost:8000 접속 (open in a browser)
"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agent import act, observe, think

WEB_DIR = Path(__file__).parent / "web"
PORT = 8500


class AgentDemoHandler(BaseHTTPRequestHandler):
    # 브라우저가 보낼 수 있는 정적 파일만 화이트리스트로 서빙합니다.
    # Only serve a small whitelist of static files the browser will request.
    _STATIC_FILES = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css; charset=utf-8"),
        "/script.js": ("script.js", "application/javascript; charset=utf-8"),
    }

    def log_message(self, fmt, *args):
        pass  # 데모용 서버라 콘솔에 접속 로그는 생략합니다 (skip access logs for the demo)

    def do_GET(self):
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
        if self.path != "/api/run":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        user_input = body.get("input", "")

        result = self._run_agent_pipeline(user_input)

        payload = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    @staticmethod
    def _run_agent_pipeline(user_input: str) -> dict:
        """agent.py의 STEP 3~5를 그대로 실행하고, 각 단계 결과를 화면용으로 정리합니다.
        Runs agent.py's STEP 3-5 as-is and packages each step's result for display."""

        # STEP 3: Observe
        perceived = observe(user_input)

        # STEP 4: Think
        decision = think(perceived)

        # STEP 5: Act
        response = act(decision, perceived)

        return {
            "observe": {
                "input": perceived,
            },
            "think": {
                "tool_needed": decision is not None,
                "tool": decision["tool"] if decision else None,
                "expression": decision["arguments"]["expression"] if decision else None,
            },
            "act": {
                "response": response,
            },
        }


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), AgentDemoHandler)
    print(f"에이전트 데모 서버 실행 중 (Agent demo server running): http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
