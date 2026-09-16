// script.js
// 3주차 도구 데모 — 서버(app.py)가 돌려준 이벤트를 화면에서 한 단계씩 재생합니다.
// Week 3 tool demo — replays the events returned by app.py one step at a time.
//
// 서버는 루프를 끝까지(또는 승인이 필요한 곳까지) 돌리고 이벤트 목록을 돌려줍니다.
// 여기서는 그 목록을 STEP_DELAY_MS 간격으로 재생해 학생들이 흐름을 눈으로 따라오게 합니다.
// The server runs the loop to the end (or to an approval request) and returns a
// list of events; this file replays them with a delay so students can follow.

const STEP_DELAY_MS = 650;

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const pretty = (obj) => JSON.stringify(obj, null, 2);
const compact = (obj) => JSON.stringify(obj);

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.error) throw new Error(data.error || `서버 오류 (server error): ${res.status}`);
  return data;
}

// ---------------------------------------------------------------------------
// 탭 (tabs)
// ---------------------------------------------------------------------------
$$(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    $$(".tab").forEach((b) => b.classList.toggle("active", b === btn));
    $$(".panel").forEach((p) => p.classList.toggle("active", p.id === `tab-${btn.dataset.tab}`));
  });
});

// ---------------------------------------------------------------------------
// 탭 1 · 도구 호출 루프 (tool loop)
// ---------------------------------------------------------------------------
const questionInput = $("#question");
const runBtn = $("#run-btn");
const hint = $("#hint");
const turnBadge = $("#turn-badge");
const loopBack = $("#loop-back");
const finalAnswer = $("#final-answer");
const finalText = $("#final-text");
const messagesEl = $("#messages");
const traceBody = $("#trace tbody");
const modal = $("#approval-modal");
const approvalCall = $("#approval-call");

const stage = (name) => $(`.stage[data-stage="${name}"]`);
const stageOut = (name) => $(`.stage-output[data-out="${name}"]`);

let currentSession = null;
let maxTurns = 5;

$$(".preset").forEach((btn) => {
  btn.addEventListener("click", () => {
    questionInput.value = btn.dataset.q;
    hint.textContent = btn.dataset.hint;
    hint.hidden = false;
    runQuestion();
  });
});
runBtn.addEventListener("click", runQuestion);
questionInput.addEventListener("keydown", (e) => { if (e.key === "Enter") runQuestion(); });
questionInput.addEventListener("input", () => { hint.hidden = true; });

function currentMode() {
  return $('input[name="mode"]:checked').value;
}

function resetLoop() {
  for (const name of ["user", "llm", "validate", "approve", "execute"]) {
    const s = stage(name);
    s.dataset.active = "false";
    s.dataset.state = "";
    s.dataset.stale = "false";
    stageOut(name).textContent = "—";
  }
  turnBadge.textContent = `턴 0 / ${maxTurns}`;
  turnBadge.classList.remove("limit");
  loopBack.classList.remove("active");
  finalAnswer.hidden = true;
  finalAnswer.classList.remove("limit");
  messagesEl.innerHTML = "";
  traceBody.innerHTML = "";
}

// 새 턴이 시작되면 이전 턴의 도구 단계는 지우지 않고 흐리게 남긴다 — 모델이 무엇을 보고 판단했는지 보이도록
// On a new turn, dim (don't erase) the previous tool stages so students see what the model reacted to.
function dimToolStages() {
  for (const name of ["validate", "approve", "execute"]) {
    stage(name).dataset.active = "false";
    stage(name).dataset.stale = "true";
  }
}

function setActive(name) {
  $$(".stage").forEach((s) => (s.dataset.active = "false"));
  stage(name).dataset.active = "true";
}

function setStage(name, text, state) {
  stage(name).dataset.active = "false";
  stage(name).dataset.stale = "false";
  stage(name).dataset.state = state || "";
  stageOut(name).textContent = text;
}

function addMessage(role, body, opts = {}) {
  const div = document.createElement("div");
  div.className = `msg msg-${role}${opts.error ? " error" : ""}`;
  const idTag = opts.id ? `<span class="msg-id">${opts.id}</span>` : "";
  div.innerHTML = `<span class="msg-role">${role}</span>${idTag}<pre></pre>`;
  div.querySelector("pre").textContent = body;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addTraceRow(entry) {
  const isError = entry.result && "error" in entry.result;
  const tr = document.createElement("tr");
  tr.className = `new-row${isError ? " fail" : ""}`;
  tr.innerHTML = `
    <td><code>${entry.call_id}</code></td>
    <td><code>${entry.tool}</code></td>
    <td><code></code></td>
    <td><code class="result"></code></td>
    <td>${entry.seconds.toFixed(3)}s</td>`;
  tr.children[2].firstChild.textContent = compact(entry.args);
  tr.children[3].firstChild.textContent = compact(entry.result);
  traceBody.appendChild(tr);
}

function describeCalls(calls) {
  return calls
    .map((c) => `${c.function.name}(${c.function.arguments})\n  id=${c.id}`)
    .join("\n");
}

async function playEvents(events) {
  for (const ev of events) {
    switch (ev.type) {
      case "llm": {
        if (ev.turn > 1) {
          loopBack.classList.add("active");
          await sleep(STEP_DELAY_MS * 0.6);
          dimToolStages();
        }
        turnBadge.textContent = `턴 ${ev.turn} / ${ev.max_turns}`;
        setActive("llm");
        await sleep(STEP_DELAY_MS);
        loopBack.classList.remove("active");
        const calls = ev.message.tool_calls || [];
        const timing = ev.usage ? `\n(${ev.seconds}s · ${ev.usage} tokens)` : `\n(${ev.seconds}s)`;
        if (calls.length) {
          setStage("llm", `tool_calls ${calls.length}건:\n${describeCalls(calls)}${timing}`, "wait");
          addMessage("assistant", pretty({ content: ev.message.content, tool_calls: calls }));
        } else {
          setStage("llm", `도구 불필요 → 최종 답변${timing}\n${ev.message.content}`, "ok");
          addMessage("assistant", pretty({ content: ev.message.content }));
        }
        break;
      }
      case "validate": {
        setActive("validate");
        await sleep(STEP_DELAY_MS);
        if (ev.ok) {
          setStage("validate", `✓ FUNCS 에서 함수 찾음\n✓ 스키마 통과 (기본값 채움)\n${compact(ev.args)}`, "ok");
        } else {
          setStage("validate", `✗ ${ev.detail}\n→ 예외 대신 오류를 결과로 돌려준다`, "fail");
        }
        break;
      }
      case "approval_request": {
        setActive("approve");
        await sleep(STEP_DELAY_MS);
        setStage("approve", `⏸ ${ev.tool} 는 되돌릴 수 없다\n사용자 승인 대기 중… (yes / no)`, "wait");
        stage("approve").dataset.active = "true";
        break;
      }
      case "approval": {
        setActive("approve");
        await sleep(STEP_DELAY_MS * 0.7);
        if (ev.skipped) {
          setStage("approve", "— 인식·계산 도구는 승인 없이 실행", "skip");
        } else if (ev.approved) {
          setStage("approve", "✓ 사용자가 yes 를 입력했다 → 실행", "ok");
        } else {
          setStage("approve", "✗ 사용자가 거절했다\n→ 실행하지 않고, 거절도 결과로 모델에게 알린다", "fail");
        }
        break;
      }
      case "tool_result": {
        setActive("execute");
        await sleep(STEP_DELAY_MS);
        const isError = "error" in ev.result;
        setStage("execute", `${isError ? "✗ 오류를 결과로" : "✓ 결과"} (${ev.seconds}s)\n${pretty(ev.result)}`, isError ? "fail" : "ok");
        addMessage("tool", compact(ev.result), { id: `tool_call_id=${ev.call_id}`, error: isError });
        addTraceRow(ev);
        break;
      }
      case "final": {
        await sleep(STEP_DELAY_MS * 0.5);
        finalText.textContent = ev.answer;
        finalAnswer.hidden = false;
        break;
      }
      case "limit": {
        turnBadge.classList.add("limit");
        finalText.textContent = `⛔ ${ev.answer} (안전장치 3)`;
        finalAnswer.classList.add("limit");
        finalAnswer.hidden = false;
        break;
      }
    }
  }
}

async function runQuestion() {
  const question = questionInput.value.trim();
  if (!question) { questionInput.focus(); return; }

  runBtn.disabled = true;
  resetLoop();
  addMessage("system", "너는 사내 헬프데스크 에이전트다. 재고·가격·주문 질문에 답한다. …");
  setActive("user");
  await sleep(STEP_DELAY_MS * 0.6);
  setStage("user", question, "ok");
  addMessage("user", question);

  try {
    const data = await postJSON("/api/ask", { question, mode: currentMode() });
    await handleSession(data);
  } catch (err) {
    setStage("llm", `⚠ ${err.message}`, "fail");
    runBtn.disabled = false;
  }
}

async function handleSession(data) {
  maxTurns = data.max_turns;
  await playEvents(data.events);
  if (data.status === "needs_approval") {
    currentSession = data.session_id;
    approvalCall.textContent = `${data.pending.tool}(${pretty(data.pending.args)})\n\ncall id: ${data.pending.call_id}`;
    modal.hidden = false;
  } else {
    currentSession = null;
    runBtn.disabled = false;
  }
}

async function answerApproval(answer) {
  modal.hidden = true;
  if (!currentSession) return;
  try {
    const data = await postJSON("/api/approve", { session_id: currentSession, answer });
    await handleSession(data);
  } catch (err) {
    setStage("approve", `⚠ ${err.message}`, "fail");
    runBtn.disabled = false;
  }
}
$("#approve-yes").addEventListener("click", () => answerApproval("yes"));
$("#approve-no").addEventListener("click", () => answerApproval("no"));

// ---------------------------------------------------------------------------
// 탭 2 · 스키마 검증 놀이터 (validation playground)
// ---------------------------------------------------------------------------
const vTool = $("#v-tool");
const vArgs = $("#v-args");
const vCallout = $("#v-callout");
const LAYER_ORDER = ["syntax", "shape", "type", "value", "fact"];
let validationRun = 0; // 빠르게 연달아 눌러도 이전 애니메이션이 덮어쓰지 않게 (cancel stale replays)

$$(".vpreset").forEach((btn) => {
  btn.addEventListener("click", () => {
    vTool.value = btn.dataset.tool;
    vArgs.value = btn.dataset.args;
    runValidation();
  });
});
$("#v-run").addEventListener("click", runValidation);

function layerEl(name) { return $(`.layer[data-layer="${name}"]`); }

async function runValidation() {
  const run = ++validationRun;
  for (const name of LAYER_ORDER) {
    const el = layerEl(name);
    el.dataset.status = "";
    el.dataset.active = "false";
    el.querySelector(".layer-detail").textContent = "—";
  }
  vCallout.hidden = true;

  let data;
  try {
    data = await postJSON("/api/validate", { tool: vTool.value.trim(), args: vArgs.value });
    if (run !== validationRun) return;
  } catch (err) {
    vCallout.textContent = `⚠ ${err.message}`;
    vCallout.className = "callout fail";
    vCallout.hidden = false;
    return;
  }

  let failedAt = null;
  for (const name of LAYER_ORDER) {
    const info = data.layers[name];
    const el = layerEl(name);
    el.dataset.active = "true";
    await sleep(STEP_DELAY_MS * 0.55);
    if (run !== validationRun) return;
    el.dataset.active = "false";
    el.dataset.status = info.status;
    const detail = info.detail || (info.status === "ok" ? "통과" : info.status === "skip" ? "(검사하지 않음)" : "");
    el.querySelector(".layer-detail").textContent = detail;
    if (info.status === "fail") { failedAt = name; break; }
  }

  const LABEL = { syntax: "① 구문", shape: "② 형태", type: "③ 타입", value: "④ 값", fact: "⑤ 사실" };
  if (failedAt === "fact") {
    vCallout.textContent = "★ 스키마(①~④)는 모두 통과했지만 실행하면 오류입니다. 형식 검사와 사실 검사는 다른 층입니다 — 스키마는 형식만 보장합니다. 이 오류도 예외가 아니라 결과로 돌려주어, 모델이 읽고 고치거나 사용자에게 알릴 수 있습니다.";
    vCallout.className = "callout fail";
  } else if (failedAt) {
    vCallout.textContent = `${LABEL[failedAt]} 층에서 거절되었습니다. 루프는 이 메시지를 {"error": ...} 로 모델에게 돌려주고, 모델은 인자를 고쳐 다시 시도할 수 있습니다. 함수는 실행되지 않았습니다.`;
    vCallout.className = "callout fail";
  } else if (data.layers.fact.status === "skip") {
    vCallout.textContent = data.layers.fact.detail;
    vCallout.className = "callout";
  } else {
    vCallout.textContent = "다섯 층 모두 통과 — 이 결과가 tool 메시지로 모델에게 돌아갑니다.";
    vCallout.className = "callout ok";
  }
  vCallout.hidden = false;
}

// ---------------------------------------------------------------------------
// 탭 3 · 평가 (evaluation)
// ---------------------------------------------------------------------------
const evalBtn = $("#eval-run");
const evalSpinner = $("#eval-spinner");

evalBtn.addEventListener("click", async () => {
  const mode = $('input[name="eval-mode"]:checked').value;
  evalBtn.disabled = true;
  evalSpinner.hidden = false;
  evalSpinner.textContent = mode === "real" ? "진짜 LLM 으로 6개 케이스 실행 중… (수십 초)" : "실행 중…";
  try {
    const data = await postJSON("/api/evaluate", { mode });
    renderEvaluation(data);
  } catch (err) {
    evalSpinner.textContent = `⚠ ${err.message}`;
    evalBtn.disabled = false;
    return;
  }
  evalSpinner.hidden = true;
  evalBtn.disabled = false;
});

function renderEvaluation(data) {
  const pct = (x) => `${Math.round(x * 100)}%`;
  const set = (key, text, good) => {
    const el = $(`.score-value[data-score="${key}"]`);
    el.textContent = text;
    el.className = `score-value ${good === undefined ? "" : good ? "good" : "bad"}`;
  };
  set("selection", pct(data.selection), data.selection === 1);
  set("arguments", pct(data.arguments), data.arguments === 1);
  set("task", pct(data.task), data.task === 1);
  set("avg_seconds", `${data.avg_seconds.toFixed(2)}초`);
  set("avg_calls", `${data.avg_calls.toFixed(1)}회`);
  $("#scores").hidden = false;

  const tbody = $("#eval-table tbody");
  tbody.innerHTML = "";
  for (const row of data.rows) {
    const tr = document.createElement("tr");
    if (row.layer) tr.className = "fail";
    const mark = (ok) => `<td class="${ok ? "ok" : "bad"}">${ok ? "✓" : "✗"}</td>`;
    tr.innerHTML = `
      <td>${row.q}${row.layer ? `<br><small style="color:var(--fail)">✗ ${row.layer} 층에서 실패</small>` : ""}</td>
      <td><code>${row.expected_tools.join(" → ") || "(없음)"}</code></td>
      <td><code>${row.used_tools.join(" → ") || "(없음)"}</code></td>
      ${mark(row.selection)}${mark(row.arguments)}${mark(row.task)}
      <td class="answer"></td>
      <td>${row.seconds.toFixed(2)}s · ${row.calls}회</td>`;
    tr.querySelector(".answer").textContent = row.answer;
    tbody.appendChild(tr);
  }
  $("#eval-table-card").hidden = false;
}

// ---------------------------------------------------------------------------
// 탭 4 · 참고 (reference) — 서버에서 도구 명세와 데이터를 받아 그린다
// ---------------------------------------------------------------------------
async function loadReference() {
  const res = await fetch("/api/reference");
  const ref = await res.json();
  maxTurns = ref.max_turns;
  turnBadge.textContent = `턴 0 / ${maxTurns}`;

  const toolsEl = $("#ref-tools");
  toolsEl.innerHTML = "";
  for (const t of ref.tools) {
    const fn = t.function;
    const needs = ref.needs_approval.includes(fn.name);
    const div = document.createElement("div");
    div.className = "tool-spec";
    div.innerHTML = `
      <h4><code>${fn.name}</code>
        <span class="badge ${needs ? "approval" : "read"}">${needs ? "행동 도구 · 승인 필요" : "인식/계산 도구"}</span></h4>
      <p class="tool-desc"></p>
      <pre></pre>`;
    div.querySelector(".tool-desc").textContent = `description: ${fn.description}`;
    div.querySelector("pre").textContent = pretty(fn.parameters);
    toolsEl.appendChild(div);
  }

  const invBody = $("#ref-inventory tbody");
  invBody.innerHTML = "";
  for (const row of ref.inventory) {
    const tr = document.createElement("tr");
    tr.className = row.stock === 0 ? "out" : row.stock < row.safety_stock ? "low" : "";
    tr.innerHTML = `<td><code>${row.product_id}</code></td><td>${row.name}</td>
      <td class="num">${row.price.toLocaleString()}원</td>
      <td class="num">${row.stock}${row.stock === 0 ? " (품절)" : ""}</td>
      <td class="num">${row.safety_stock}</td>`;
    invBody.appendChild(tr);
  }
  $("#ref-policy").textContent = ref.policy;
  $("#ref-system").textContent = ref.system_prompt;
}

loadReference().catch((err) => console.error("reference load failed", err));
