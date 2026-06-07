# PDCA 단계별 체크리스트

> Checklist Design (https://www.checklist.design/) 패턴 적용. 각 단계 산출물 발행 전 quality-gate 스킬이 본 JSON을 로드해 검증.

## 사용법
1. 단계 종료 직전 `quality-gate` 스킬 호출
2. 스킬이 해당 단계 JSON을 로드하고 `must_pass=true` 항목 검증
3. `next_stage_blocker` 배열의 항목 중 1개라도 실패 → 다음 단계 진입 BLOCK

## 5개 단계
- `plan.json` — 트렌드/MD/라인시트
- `design.json` — 무드보드/컬러/디자인/스펙
- `do.json` — 테크팩/IMC/비주얼/카피
- `check.json` — 판매분석/수요예측/인사이트
- `act.json` — PDCA 반복/리테로/아카이빙

## CRITICAL 매핑
각 항목의 `critical_id` 필드는 CLAUDE.md 상단 5대 CRITICAL 원칙 번호와 연결됨:
1=BTA · 2=3B · 3=로고 · 4=프리셋 · 5=Evidence
