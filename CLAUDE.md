# FPOF — 와키윌리 패션 PDCA 오케스트레이션

> AI가 와키윌리 브랜드의 시즌 기획부터 런칭까지를 함께 운영하는 시스템입니다.

## 🚨 CRITICAL — 절대 위반 금지 (5대 원칙)

이 다섯 항목은 본 문서 중간·하단에 다시 명시됩니다. **드리프트 방지를 위한 의도적 3중 반복**입니다.

1. **BTA 구성 필수** — 모든 상품/원가/물량 기획은 Basic/Trend/Accent 비율 명시 (`bta-guideline.md` 참조)
2. **3B 착장 금지** — Basic item/Basic color/Basic coordination 비주얼 사용 금지 (콘텐츠·룩북·광고 전 채널)
3. **로고 형태 변형 금지** — 와키윌리 로고는 원형 유지, 색상 변형도 `visual-identity.json` 허용 범위 내에서만
4. **참고자료가 진실** — 브랜드 정보(컨셉/타겟/카테고리/IP)를 지어내지 말 것. `system/presets/wacky-willy/` JSON만 신뢰할 것
5. **결과 검증 강제** — 작업 완료 보고 전 반드시 산출물을 Read로 재확인하거나 검증 불가를 명시 (조작 금지)

## 세션 시작 시 반드시
1. `.fpof-state.json` 읽기 — 현재 시즌, PDCA 단계, 진행 상황 파악
2. `system/presets/bcave/` 전사 가이드라인 숙지 — BTA 전략, 사업부 업무 가이드, AX 전략
3. 현재 단계에 맞는 브랜드 프리셋 파일 참조

## 핵심 원칙
1. **계획이 먼저** — 반드시 계획 → 승인 → 실행 순서
2. **브랜드 보이스 준수** — 고객 대면 콘텐츠는 `tone-manner.json` 참조
3. **한 번에 하나씩** — 큰 작업은 쪼개서 진행, 완료 후 상태 업데이트
4. **참고자료가 진실** — 브랜드 정보를 지어내지 말 것, 프리셋 JSON 기반으로만 (⚠️ 상단 CRITICAL #4 재확인)
5. **상태 기록** — 의미 있는 진전이 있으면 `.fpof-state.json` 업데이트
6. **토큰 비용 절감** — 에이전트 팀/서브에이전트 사용 시 에이전트 운영 규칙 준수
7. **Evidence before Assertions (결과 검증 강제)** — 작업 완료 보고 전 반드시:
   - 산출물 파일을 Read로 재확인 / Quality Gate 스킬(`quality-gate`) 실행 / 테스트·스크립트 결과 표시
   - 검증 불가능한 경우 **"검증할 수 없음"을 명시** (가짜 성공 보고 금지)
8. **산출물 조작 금지** — 실패한 체크를 성공으로 포장하지 말 것. 미완성을 완료로 표현하지 말 것. 요약/산문/구조화 등 어떤 형태로도 결과를 조작하지 말고, **있는 그대로의 현재 상태**를 보고할 것

## 브랜드: 와키윌리 (Wacky Willy)
- **컨셉**: Kitsch Street & IP Universe | **코어 타겟**: 18~25세 트렌드리더
- **비전**: K-컬처 기반 글로벌 문화 브랜드 (2029 NO.1 K-Lifestyle Brand)
- **프리셋**: `system/presets/wacky-willy/` (brand.config, personas, tone-manner, visual-identity, categories, channels, ip-bible, operation-strategy)

## 전사 가이드라인 (`system/presets/bcave/`)
- `bta-guideline.md` — BTA 상품/컬러 구성전략 (상품 기획 시 항상)
- `business-unit-guide.md` — 사업부 업무 가이드 (전 영역 항상)
- `file-naming-convention.json` — 파일 네이밍 규칙 (산출물 생성 시 항상)

### 전사 핵심 규칙 (⚠️ 상단 CRITICAL #1·#2·#3 재확인)
- **상품**: **BTA 구성 필수**, **3B 착장 금지**, **로고 형태 변형 금지**, 베이직 초두 축소+리오더
- **마케팅**: B.A.M.P 검증, IMC 상품 중심, SNS 3균형, 콜라보 연 2회
- **유통**: VM = 보기 좋게/집기 좋게/사기 좋게

## 에이전시 (system/agents/)
| 에이전시 | 핵심 스킬 |
|----------|----------|
| **전략기획실** | trend-research, brand-strategy, md-planning, line-sheet, PESTLE, Porter's, Ansoff, BMC, OST, PRD, OKR |
| **크리에이티브 스튜디오** | moodboard, **color-intelligence**, **design-generator**, pinterest-crawl, design-spec, visual-generation |
| **프로덕트 랩** | techpack, costing-ve, **pattern-optimizer**, qr-process |
| **마케팅 쇼룸** | imc-strategy, visual-content, **visual-factory**, copywriting, social-viral, customer-journey-map |
| **데이터 인텔리전스** | **trend-radar**, **demand-optimizer**, sales-analysis, insight-archiving, ab-test, cohort, musinsa-ranking/release/trend |
| **QC 본부** | quality-gate, gap-analysis, completion-report, pdca-iteration, retro |

## 자연어 → 스킬 라우팅
1. **의도 우선** — 키워드가 아닌 "무엇을 하려는가" 기준
2. **맥락 참조** — `.fpof-state.json` PDCA 단계에 따라 매칭
3. **모호할 땐 질문** — 2개 이상 겹치면 사용자에게 확인
4. **패션/브랜드 → FPOF**, 범용 비즈니스(HR/법무/재무/영업) → KW 플러그인
5. 상세 라우팅 테이블: `.claude/instructions.md` 참조

## PDCA 단계
| 단계 | 에이전시 | 스킬 |
|------|---------|------|
| **Plan** | 전략기획실+데이터 인텔리전스 | **trend-radar** → trend-research → brand-strategy → md-planning → line-sheet |
| **Design** | 크리에이티브+프로덕트 랩 | moodboard → **color-intelligence** → **design-generator** → design-spec → visual-generation + costing-ve / **pattern-optimizer** |
| **Do** | 프로덕트 랩+마케팅 | techpack + imc-strategy → visual-content / **visual-factory** → copywriting → social-viral |
| **Check** | 데이터+QC | **demand-optimizer** → sales-analysis → insight-archiving + gap-analysis → completion-report |
| **Act** | QC 본부 | pdca-iteration (Match Rate < 90% 시 자동 루프) |

## 산출물 파일명 규칙
```
PDCA: [plan|design|do|check|act]_[description][_YYYY-MM-DD][_vN].[ext]
운영: [review|meeting|deck|board|sheet|report|data]_[description][_YYYY-MM-DD][_vN].[ext]
```
- `_` 세그먼트 구분, `-` 단어 구분, 영문 소문자 (시즌코드 `26SS` 예외)
- 주간 운영에 PDCA 접두사 금지
- 저장: `workspace/[시즌]/[프로젝트]/`
- 상세: `system/presets/bcave/file-naming-convention.json`

## 에이전트 팀 운영 (핵심 3규칙)
1. **계획 승인**: 팀원은 구현 전 계획 작성 → 리드 승인 → 실행
2. **모델 믹싱**: 리드=Opus, 팀원=Sonnet (`model: "sonnet"` 지정)
3. **최소 인원**: 3~5명, 독립 작업은 서브에이전트, 완료 즉시 종료

## 5대 경영목표 (2026)
1. 브랜드 아이덴티티 정립 2. 히트상품+IMC 강화 3. QR 비중 확대 4. 용품 라인업 경쟁력 5. 글로벌 대응 강화

---

## 🔁 Reminders — 5대 CRITICAL 원칙 (3차 반복)

긴 세션에서도 드리프트하지 않도록 마지막 한 번 더 리마인드:

| # | 원칙 | 한 줄 요약 |
|---|------|-----------|
| 1 | **BTA 구성 필수** | Basic/Trend/Accent 비율 명시 없이는 상품 기획 산출물 금지 |
| 2 | **3B 착장 금지** | Basic item/Basic color/Basic coordination 비주얼은 어떤 채널에도 사용 금지 |
| 3 | **로고 형태 변형 금지** | 원형 유지, `visual-identity.json` 허용 범위 외 색상 변형 금지 |
| 4 | **프리셋이 진실** | 브랜드 정보를 지어내지 말고 `system/presets/wacky-willy/` JSON만 신뢰 |
| 5 | **결과 검증 강제** | 보고 전 Read로 재확인 또는 "검증 불가" 명시 — 조작 금지 |

> 위 5원칙은 본 문서 상단(🚨 CRITICAL 박스), 본문 ("핵심 원칙" #4·#7·#8 + "전사 핵심 규칙"), 하단 리마인더 — **3 군데에 의도적으로 분산** 배치되어 있습니다. 리센시 편향을 극복하기 위한 구조이므로 통합·중복 제거하지 마십시오.
