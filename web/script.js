// script.js
// Observe -> Think -> Act 파이프라인을 화면에서 순서대로 재생합니다.
// Replays the Observe -> Think -> Act pipeline on screen, step by step.
//
// 서버(app.py)는 세 단계를 전부 실행한 뒤 결과를 한 번에 돌려주므로,
// 여기서는 그 결과를 STEP_DELAY_MS 간격으로 하나씩 "재생"해서
// 학생들이 각 단계를 눈으로 따라올 수 있게 합니다.
// The server (app.py) runs all three steps and returns the result at once;
// this file "replays" that result one step at a time so students can
// follow each stage visually.

const STEP_DELAY_MS = 700;

const questionInput = document.getElementById("question");
const runBtn = document.getElementById("run-btn");
const consoleLog = document.getElementById("console-log");
const finalAnswer = document.getElementById("final-answer");
const finalText = document.getElementById("final-text");

const stages = {
  observe: document.getElementById("stage-observe"),
  think: document.getElementById("stage-think"),
  act: document.getElementById("stage-act"),
};
const outputs = {
  observe: document.getElementById("out-observe"),
  think: document.getElementById("out-think"),
  act: document.getElementById("out-act"),
};

document.querySelectorAll(".preset").forEach((btn) => {
  btn.addEventListener("click", () => {
    questionInput.value = btn.dataset.q;
    runPipeline();
  });
});

runBtn.addEventListener("click", runPipeline);
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runPipeline();
});

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function log(line) {
  consoleLog.textContent += line + "\n";
  consoleLog.scrollTop = consoleLog.scrollHeight;
}

function resetStages() {
  for (const key of Object.keys(stages)) {
    stages[key].dataset.active = "false";
    stages[key].dataset.done = "false";
    outputs[key].textContent = "—";
  }
  finalAnswer.hidden = true;
  consoleLog.textContent = "";
}

function setActive(stageKey) {
  stages[stageKey].dataset.active = "true";
}

function setDone(stageKey, text) {
  stages[stageKey].dataset.active = "false";
  stages[stageKey].dataset.done = "true";
  outputs[stageKey].textContent = text;
}

async function runPipeline() {
  const input = questionInput.value.trim();
  if (!input) {
    questionInput.focus();
    return;
  }

  runBtn.disabled = true;
  resetStages();

  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input }),
    });
    if (!res.ok) throw new Error(`서버 오류 (server error): ${res.status}`);
    const data = await res.json();

    // STEP 3: Observe
    setActive("observe");
    log(`[Observe] 사용자 입력 (user input): "${data.observe.input}"`);
    await sleep(STEP_DELAY_MS);
    setDone("observe", data.observe.input);

    // STEP 4: Think
    setActive("think");
    await sleep(200);
    if (data.think.tool_needed) {
      const line = `[Think]   수식 감지 → 도구 호출: ${data.think.tool}("${data.think.expression}")`;
      log(line);
      await sleep(STEP_DELAY_MS);
      setDone("think", `도구 호출 필요 (tool call needed)\n${data.think.tool}("${data.think.expression}")`);
    } else {
      log("[Think]   수식 없음 → 도구 호출 불필요 (no tool call needed)");
      await sleep(STEP_DELAY_MS);
      setDone("think", "도구 호출 불필요\n(no tool call needed)");
    }

    // STEP 5: Act
    setActive("act");
    await sleep(200);
    log(`[Act]     응답 (response): ${data.act.response}`);
    await sleep(STEP_DELAY_MS);
    setDone("act", data.act.response);

    finalText.textContent = data.act.response;
    finalAnswer.hidden = false;
  } catch (err) {
    log(`[Error] ${err.message}`);
  } finally {
    runBtn.disabled = false;
  }
}
