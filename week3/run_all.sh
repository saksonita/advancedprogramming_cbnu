#!/usr/bin/env bash
# 오프라인 실습을 한 번에 실행합니다 (API 키 불필요).
# Runs every offline practice in order. No API key needed.
set -e
cd "$(dirname "$0")"
echo "=== 실습 1 · 도구 함수 ==============================="; python3 tools.py
echo; echo "=== 실습 2 · 스키마와 검증 ==========================="; python3 schemas.py
echo; echo "=== 실습 1–2 · 단위 테스트 ==========================="; python3 test_tools.py
echo; echo "=== 실습 3–4 · 루프와 승인 (가짜 LLM) ================"; python3 agent_loop.py
echo; echo "=== 실습 6 · 직렬 vs 병렬 ============================"; python3 parallel_calls.py
echo; echo "=== 실습 7 · 실패와 재시도 ==========================="; python3 reliability.py
echo; echo "=== 실습 8 · 평가 (가짜 LLM) ========================="; python3 evaluate.py
