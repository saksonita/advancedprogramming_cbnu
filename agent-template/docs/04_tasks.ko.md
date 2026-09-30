# 과제 목록

한 번에 과제 **하나만** 합니다. Part 1은 팀이 직접 생각하고 쓰는 부분입니다. AI 어시스턴트도 코드도 쓰지 않습니다.

AI 어시스턴트에게 줄 프롬프트 (Part 2에서만 사용):
> Read AGENTS.md. Then do Task N from docs/04_tasks.md using docs/03_tool_spec.md. Only touch the files needed.

## Part 0 — 준비
- [ ] **0. 공통 파일 복사.** `README.ko.md`의 "준비" 단계를 따릅니다. 확인: `python -m pytest tests/test_tool_format.py`가 실행되고, `test_team_has_four_new_tools`만 실패합니다.

## Part 1 — 설계 (코드 없음)
- [ ] **1. 브리프.** `docs/01_brief.md`를 채웁니다. 확인: 다른 팀 친구가 읽고, 사용자가 누구이며 에이전트가 무엇을 하는지 말할 수 있습니다.
- [ ] **2. 데이터.** `data/*.json` 파일을 직접 만듭니다. 현실적인 항목을 5–10개 넣습니다. `docs/02_architecture.md`의 "Data files"에 파일 목록을 적습니다.
- [ ] **3. 도구 지도.** `docs/03_tool_spec.md`의 "도구 지도" 표를 채웁니다. `ASSIGNMENT.ko.md`의 요구 사항을 확인하고 이름만 바꾸기 테스트를 해 봅니다.
- [ ] **4. 도구 명세.** 팀원마다 자신이 맡은 도구의 명세를 `docs/03_tool_spec.md`에 씁니다. 모든 오류에는 힌트가 있어야 합니다.
- [ ] **5. 시나리오.** `tests/scenarios.md`를 채웁니다. 도구 3개 연결, 오류 회복, write 전 확인이 들어가야 합니다.

## Part 2 — 구현 (프롬프트 하나에 도구 하나)
- [ ] **6. 시스템 프롬프트.** `prompts/system_prompt.md`를 채웁니다.
- [ ] **7. 도구 1:** `<이름>`. 구현하고, 스키마를 쓰고, `src/tools/__init__.py`에 등록하고, `tests/test_tools.py`에 정상 테스트 하나와 오류 테스트 하나를 추가합니다. 확인: `python -m pytest tests -k <이름>`.
- [ ] **8. 도구 2:** `<이름>`. 같은 순서.
- [ ] **9. 도구 3:** `<이름>`. 같은 순서.
- [ ] **10. 도구 4:** `<이름>`. 같은 순서.
- [ ] **11. 추가 도구 (선택).** 같은 순서.

## Part 3 — 검증
- [ ] **12. 형식 검사.** `python -m pytest tests`가 실패 없이 통과합니다.
- [ ] **13. 시나리오.** `python -m src.main`으로 모든 시나리오를 실행합니다. 에이전트가 엉뚱한 도구를 고르거나 오류 한 번에 포기하면 도구 설명, 오류 힌트, 시스템 프롬프트를 고칩니다. 에이전트 코드는 고치지 않습니다.
- [ ] **14. 발표.** `ASSIGNMENT.ko.md`의 3분 발표를 연습합니다. 모든 팀원이 자신이 맡은 도구를 설명할 수 있어야 합니다.
