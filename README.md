# FPOF — 와키윌리 패션 하우스 시스템

> **Fashion PDCA Orchestration Framework v3.0**
>
> AI가 와키윌리(Wacky Willy) 브랜드의 시즌 기획부터 런칭·판매 분석까지를 함께 운영하는 패션 하우스 오케스트레이션 시스템입니다.
>
> 패션 실무자가 자연어로 지시하면, 브랜드 DNA와 전사 전략을 숙지한 AI 에이전시가 실무 산출물을 만들고 — 만든 것을 스스로 검증합니다.

---

## 📋 목차

1. [시스템 개요](#-시스템-개요)
2. [V3.0 하이라이트](#-v30-하이라이트)
3. [5대 CRITICAL 원칙](#-5대-critical-원칙)
4. [에이전시 & 스킬 아키텍처](#-에이전시--스킬-아키텍처)
5. [PDCA 워크플로우](#-pdca-워크플로우)
6. [운영(Operational) 체계](#-운영operational-체계)
7. [자동화 & 데이터 파이프라인](#-자동화--데이터-파이프라인)
8. [사용법](#-사용법)
9. [폴더 구조](#-폴더-구조)
10. [요약 통계](#-요약-통계)

---

## 🎯 시스템 개요

FPOF는 **2계층 스킬 아키텍처** 위에 6개 에이전시가 PDCA 사이클을 운영하는 구조입니다.

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: FPOF Domain Skills (system/skills/)                 │
│  ──────────────────────────────────────────────────────────  │
│  패션 실무 스킬 31개 (와키윌리 브랜드 DNA 내장)                │
│  + PM 프레임워크 스킬 50개 (Paweł Huryn PM-Skills 통합)        │
│  + 전용 엔진 3종 (comfyui · html-slide · supanova)            │
└──────────────────────────────────────────────────────────────┘
                              ↕
┌──────────────────────────────────────────────────────────────┐
│  Layer 2: Claude Universal Skills (.claude/skills/)           │
│  ──────────────────────────────────────────────────────────  │
│  범용 유틸리티 스킬 28개 — 문서 생성(pptx/docx/xlsx/pdf),     │
│  프론트엔드(frontend-slides·supanova), 검증(quality-gate·     │
│  webapp-testing), 디자인(canvas-design·theme-factory) 등      │
└──────────────────────────────────────────────────────────────┘
                              ↕
┌──────────────────────────────────────────────────────────────┐
│  Foundation: Presets & Guidelines (system/presets/)           │
│  ──────────────────────────────────────────────────────────  │
│  wacky-willy/ 브랜드 프리셋 11개 JSON — 단일 진실 공급원       │
│  bcave/ 전사 가이드라인 — BTA 전략·사업부 가이드·네이밍 규칙   │
└──────────────────────────────────────────────────────────────┘
```

### 브랜드 정보

| 항목 | 내용 |
|------|------|
| **브랜드명** | 와키윌리 (Wacky Willy) |
| **컨셉** | Kitsch Street & IP Universe |
| **코어 타겟** | 18~25세 트렌드리더 |
| **비전** | K-컬처 기반 글로벌 문화 브랜드 (2029 NO.1 K-Lifestyle Brand) |
| **프리셋** | `system/presets/wacky-willy/` — 브랜드 정보의 유일한 진실 |

---

## 🆕 V3.0 하이라이트

V2.2(PM-Skills 통합) 이후 시스템이 다음과 같이 진화했습니다.

| # | 변화 | 내용 |
|---|------|------|
| 1 | **system/ 재편** | 루트의 skills·agents·presets·scripts를 `system/` 하위로 통합 |
| 2 | **6대 핵심 스킬** | trend-radar · demand-optimizer · color-intelligence · design-generator · visual-factory · pattern-optimizer |
| 3 | **이미지 생성 엔진** | `/comfyui` — ComfyUI + ERNIE-Image(GGUF, 최소 11GB) 로컬 생성 |
| 4 | **마켓 인텔 자동화** | GitHub Actions 주간 크롤 — 무신사 랭킹·발매·트렌드 (매주 월 00:00 KST) |
| 5 | **전사 가이드라인** | `system/presets/bcave/` — BTA 상품구성 전략, 사업부 업무 가이드, 파일 네이밍 규칙 |
| 6 | **검증 강제 체계** | 5대 CRITICAL 원칙 3중 반복 + Evidence before Assertions (보고 전 Read 재확인) |
| 7 | **디자인 토큰 검증** | design-tokens.json 기반 quality-gate + 디자인 시스템 프리셋 72종(`design-systems/`) |
| 8 | **이중 트래킹** | 시즌 PDCA(전략 마일스톤)와 운영(주간/월간/대시보드)을 `.fpof-state.json`에서 분리 관리 |
| 9 | **내부 자료 보호** | `workspace/`·회의록·사내 데이터는 git 추적 제외 (로컬 전용) |
| 10 | **에이전트 팀 규칙** | 계획 승인 → 실행, 리드=Opus·팀원=Sonnet 모델 믹싱, 최소 인원 3~5명 |

---

## 🚨 5대 CRITICAL 원칙

모든 작업에 적용되는 절대 규칙입니다. 상세는 [CLAUDE.md](./CLAUDE.md) 참조.

| # | 원칙 | 한 줄 요약 |
|---|------|-----------|
| 1 | **BTA 구성 필수** | 상품/원가/물량 기획은 Basic/Trend/Accent 비율 명시 필수 |
| 2 | **3B 착장 금지** | Basic item/Basic color/Basic coordination 비주얼 전 채널 금지 |
| 3 | **로고 형태 변형 금지** | 원형 유지, 색상도 `visual-identity.json` 허용 범위 내에서만 |
| 4 | **프리셋이 진실** | 브랜드 정보를 지어내지 말고 `system/presets/wacky-willy/` JSON만 신뢰 |
| 5 | **결과 검증 강제** | 보고 전 산출물 Read 재확인 또는 "검증 불가" 명시 — 조작 금지 |

---

## 🏗️ 에이전시 & 스킬 아키텍처

### 6개 에이전시 (`system/agents/`)

| 에이전시 | 핵심 스킬 | PDCA |
|----------|----------|------|
| **전략기획실** (strategy-planning) | trend-research, brand-strategy, md-planning, line-sheet + PM 전략 프레임워크 | Plan |
| **크리에이티브 스튜디오** (creative-studio) | moodboard, **color-intelligence**, **design-generator**, pinterest-crawl, design-spec, visual-generation | Design |
| **프로덕트 랩** (product-lab) | techpack, costing-ve, **pattern-optimizer**, qr-process | Design/Do |
| **마케팅 쇼룸** (marketing-showroom) | imc-strategy, visual-content, **visual-factory**, copywriting, social-viral | Do |
| **데이터 인텔리전스** (data-intelligence) | **trend-radar**, **demand-optimizer**, sales-analysis, insight-archiving, market-intelligence, musinsa-ranking/release | Plan/Check |
| **QC 본부** (quality-control) | quality-gate, gap-analysis, completion-report, pdca-iteration | All |

### 패션 실무 스킬 31개 (`system/skills/`)

| 카테고리 | 스킬 |
|----------|------|
| `strategy/` (4) | brand-strategy, line-sheet, md-planning, trend-research |
| `creative/` (6) | color-intelligence, design-generator, design-spec, moodboard, pinterest-crawl, visual-generation |
| `product/` (4) | costing-ve, pattern-optimizer, qr-process, techpack |
| `marketing/` (5) | copywriting, imc-strategy, social-viral, visual-content, visual-factory |
| `data/` (7) | demand-optimizer, insight-archiving, market-intelligence, musinsa-ranking, musinsa-release, sales-analysis, trend-radar |
| `quality/` (4) | completion-report, gap-analysis, pdca-iteration, quality-gate |
| `task/` (1) | format-conversion |

### PM 프레임워크 스킬 50개 (`system/skills/pm-*/`)

| 카테고리 | 수 | 대표 스킬 |
|----------|----|----------|
| `pm-strategy/` | 10 | PESTLE, Porter's 5 Forces, Ansoff, BMC, Lean Canvas, Value Proposition |
| `pm-research/` | 4 | Customer Journey Map, Market Segments, User Personas |
| `pm-gtm/` | 3 | Beachhead Segment, Competitive Battlecard, ICP |
| `pm-discovery/` | 12 | OST, Brainstorm Ideas/Experiments, Assumptions, Interview |
| `pm-execution/` | 13 | OKRs, PRD, Roadmap, Stakeholder Map, Sprint, Retro |
| `pm-analytics/` | 3 | A/B Test, Cohort Analysis, SQL Queries |
| `pm-marketing/` | 1 | Product Name |
| `pm-toolkit/` | 4 | Grammar Check, NDA, Privacy Policy, Resume Review |

### 전용 엔진 스킬 3종

| 엔진 | 위치 | 용도 |
|------|------|------|
| **comfyui** | `system/skills/comfyui/` | ERNIE-Image 로컬 이미지 생성 — 룩북·무드보드·캠페인 비주얼 |
| **html-slide** | `system/skills/creative/html-slide/` | HTML 슬라이드 덱 생성 |
| **supanova** | `system/skills/design/supanova/` | 프리미엄 랜딩페이지 생성 |

### Claude 유니버설 스킬 28개 (`.claude/skills/`)

문서 생성(pptx·docx·xlsx·pdf·doc-coauthoring·executive-summary·internal-comms·md-to-image),
디자인(canvas-design·algorithmic-art·theme-factory·brand-guidelines·slack-gif-creator·image-prompt-builder·simple-ds-design),
웹(frontend-design·frontend-slides·supanova·supanova-redesign·web-artifacts-builder·webapp-testing),
구조화·개발(json-canvas·excalidraw-diagram·mcp-builder·skill-creator·claude-api·interview-analyzer·quality-gate)

---

## 🔄 PDCA 워크플로우

```
Plan (기획)        전략기획실 + 데이터 인텔리전스
  ↓  trend-radar → trend-research → brand-strategy → md-planning → line-sheet
  ↓  Quality Gate 1 (QG1)
Design (디자인)    크리에이티브 + 프로덕트 랩
  ↓  moodboard → color-intelligence → design-generator → design-spec
  ↓  → visual-generation + costing-ve / pattern-optimizer
  ↓  Quality Gate 2 (QG2)
Do (실행)          프로덕트 랩 + 마케팅 쇼룸
  ↓  techpack + imc-strategy → visual-content / visual-factory
  ↓  → copywriting → social-viral
  ↓  Quality Gate 3 (QG3)
Check (분석)       데이터 인텔리전스 + QC 본부
  ↓  demand-optimizer → sales-analysis → insight-archiving
  ↓  + gap-analysis → completion-report
  ↓  Quality Gate 4 (QG4)
Act (개선)         QC 본부
  ↓  pdca-iteration (Match Rate < 90% 시 자동 루프)
```

| 게이트 | 전환 | 통과 조건 |
|-------|------|----------|
| **QG1** | Plan → Design | 트렌드 브리프·브랜드 전략·MD 전략·라인시트·경영목표 정합성 |
| **QG2** | Design → Do | 무드보드·컬러 전략·디자인 스펙·원가 검증·비주얼 에셋 |
| **QG3** | Do → Check | 테크팩·캠페인 브리프·콘텐츠 기획·카피·런칭 시퀀스 |
| **QG4** | Check → Next | Match Rate ≥ 90% → COMPLETE / < 90% → Act 루프 |

---

## 📊 운영(Operational) 체계

시즌 PDCA(전략 마일스톤)와 별개로, 일상 운영 산출물은 `.fpof-state.json`의 `operational` 섹션에서 독립 추적합니다.

| 영역 | 산출물 | 주기 |
|------|--------|------|
| **주간 리뷰** | `workspace/[시즌]/weekly/` — 부서/임원 요약, 주간 덱 | 매주 |
| **판매 대시보드** | board_master-review_new · board_season-planning_new (`dashboard - sales/`) | 매주 데이터 갱신 |
| **주간·월간 대시보드** | board_weekly(6탭) · board_monthly(7탭) | 매주/매월 |
| **비즈니스 플로우** | board_overview — 발주→입고→출고→판매→재고 2-트랙 드릴다운 | 매주 |
| **대표 보고** | 월간 리뷰 덱 (본장 + 데이터 근거 상세장, 재현 파이프라인 포함) | 매월 |

모든 운영 산출물은 `workspace/`(로컬 전용, git 제외)에 저장하며, 파일명은
`system/presets/bcave/file-naming-convention.json` 규칙을 따릅니다:

```
PDCA: [plan|design|do|check|act]_[description][_YYYY-MM-DD][_vN].[ext]
운영: [review|meeting|deck|board|sheet|report|data]_[description][_YYYY-MM-DD][_vN].[ext]
```

---

## 🤖 자동화 & 데이터 파이프라인

| 파이프라인 | 구성 | 스케줄 |
|-----------|------|--------|
| **마켓 트렌드 주간 수집** | `.github/workflows/market-trend-weekly.yml` + `system/scripts/market-trend-builder.py` | 매주 월 00:00 KST |
| **무신사 크롤러 3종** | `system/scripts/musinsa-crawler` · `musinsa-release-crawler` · `musinsa-trend-crawler` (+ MCP 서버) | 워크플로우/수동 |
| **마켓 인텔 로컬 수집** | `system/launchd/com.fpof.market-intel.plist` (macOS launchd) | 로컬 스케줄 |
| **Google Workspace 연동** | `system/integrations/gws` | 수동 |
| **보고서 생성기** | `system/scripts/` PPT 생성 스크립트 (주간/전략/사용자 매뉴얼) | 수동 |

수집 데이터는 `system/data/market-intel/`(gitignore)에 적재되고 `trend-radar`·`market-intelligence` 스킬이 소비합니다.

---

## 🚀 사용법

### 자연어 라우팅

의도를 파악해 적합한 스킬로 자동 라우팅합니다 (`.claude/instructions.md` 라우팅 테이블).

```
"요즘 뭐가 유행이야?"        → trend-radar / trend-research
"컬러 전략 잡아줘"           → color-intelligence
"디자인 시안 뽑아줘"         → design-generator
"리오더 타이밍 알려줘"       → demand-optimizer
"룩북 이미지 만들어줘"       → /comfyui (ERNIE-Image)
"매출 분석해줘"              → sales-analysis
"세상이 어떻게 변하고 있어?"  → pestle-analysis
```

원칙: **패션/브랜드 → FPOF 스킬**, 범용 비즈니스(HR/법무/재무/영업) → KW 플러그인. 2개 이상 겹치면 질문.

### KW 플러그인 이중 라우팅

FPOF 도메인 스킬과 별개로 **Knowledge Work 플러그인**(engineering·data·marketing·sales·legal·finance·HR 등 도메인별)이 활성화되어 있어, 범용 비즈니스 요청은 해당 도메인 스킬로 라우팅됩니다. 상세: [docs/guide/plugin-routing-guide.md](./docs/guide/plugin-routing-guide.md)

### Telegram 채널

Telegram 봇으로 모바일에서 세션에 지시·보고받을 수 있습니다 (telegram 플러그인). 설정: [docs/guide/telegram-setup-guide.md](./docs/guide/telegram-setup-guide.md)

### 슬래시 명령어 (49개)

| 그룹 | 명령어 |
|------|--------|
| **FPOF 운영** | `/status` `/brief` `/review` `/next` `/team` `/export` |
| **문서 생성** | `/deck` `/pdf` `/sheet` `/doc` |
| **6대 핵심** | `/trend-radar` `/demand-optimizer` `/color-intelligence` `/design-generator` `/visual-factory` `/pattern-optimizer` |
| **데이터 수집** | `/musinsa-ranking` `/musinsa-release` `/market-intel` `/pinterest` `/comfyui` |
| **PM 전략** | `/market-scan` `/pricing` `/business-model` `/strategy-canvas` `/value-prop` `/competitive` `/battlecard` `/growth` `/launch` `/north-star` |
| **디스커버리** | `/discover` `/brainstorm` `/interview` `/research-users` `/analyze-feedback` `/triage` |
| **실행 관리** | `/okrs` `/prd` `/roadmap` `/stakeholders` `/sprint` `/pre-mortem` `/metrics` |
| **데이터·유틸** | `/ab-test` `/cohorts` `/marketing` `/meeting` `/proofread` |

### 빠른 시작

```
# 1. 현재 상태 확인 (시즌·PDCA 단계·산출물)
/status

# 2. 자연어로 작업 시작
"26FW 트렌드 레이더 돌려줘"

# 3. 비주얼 생성
/comfyui            # ERNIE-Image 로컬 이미지 생성

# 4. 품질 검수 & 단계 전환
/review             # Quality Gate 검수
/next               # 다음 PDCA 단계
```

---

## 📁 폴더 구조

```
FPOF V3.0/
├── README.md                        # 이 파일
├── CLAUDE.md                        # 시스템 운영 규칙 (5대 CRITICAL 포함)
├── ONBOARDING.md                    # 신규 팀원 온보딩 가이드
├── .fpof-state.json                 # 시즌/PDCA/운영 상태 (이중 트래킹)
│
├── .claude/                         # Claude Code 설정
│   ├── skills/                      # 유니버설 스킬 28개
│   ├── commands/                    # 슬래시 명령어 49개
│   ├── hooks/                       # route-skill·check-output·validate-filename·team-* (배선: hooks.json + settings.json)
│   ├── instructions.md              # 자연어 → 스킬 라우팅 테이블
│   └── settings.json
│
├── system/                          # FPOF 코어
│   ├── agents/                      # 6개 에이전시 (README + references/checklists)
│   ├── presets/
│   │   ├── wacky-willy/             # 브랜드 프리셋 11개 JSON (진실 공급원)
│   │   └── bcave/                   # 전사 가이드라인 (BTA·사업부·네이밍)
│   ├── skills/                      # 패션 31 + PM 50 + 엔진 3 (comfyui·html-slide·supanova)
│   ├── skills-universal/            # 어댑터 & 브릿지
│   ├── scripts/                     # 무신사 크롤러 3종·MCP 서버·market-intel·PPT 생성기
│   ├── integrations/gws/            # Google Workspace CLI
│   ├── launchd/                     # macOS 로컬 스케줄러
│   ├── apple-neural-engine/         # ANE CLI 스킬
│   ├── converter/                   # 문서 포맷 변환기
│   ├── knowledge/                   # 지식 인덱스
│   └── data/                        # market-intel 수집 데이터 (gitignore)
│
├── design-systems/                  # 디자인 시스템 프리셋 72종 (frontend-slides 연동)
│
├── docs/                            # 문서
│   ├── guide/                       # 퀵스타트·사용자 매뉴얼·플러그인 라우팅
│   ├── reference/                   # 아키텍처·네이밍·브랜드 운영 플랜
│   ├── workshop/                    # 워크샵 가이드 16종
│   ├── generated/                   # 생성된 보고서·덱
│   └── (meeting notes·qr process·education — 로컬 전용, git 제외)
│
└── workspace/                       # 시즌 산출물 (로컬 전용, git 제외)
    ├── 26SS/ · 26FW/ · 27SS/        # 시즌별: 대시보드·주간·전략·프로젝트
    └── [수집 데이터·무드보드·회의록]
```

---

## 📌 요약 통계

| 항목 | V2.2 | V3.0 |
|------|------|------|
| **패션 실무 스킬** | 21개 | **31개** (6대 핵심 + 무신사·마켓인텔 추가) |
| **PM 프레임워크 스킬** | 65개* | 50개 (정비·통합) |
| **전용 엔진 스킬** | - | **3개** (comfyui·html-slide·supanova) |
| **Claude 유니버설 스킬** | 19개 | **28개** |
| **슬래시 명령어** | 40+개 | **49개** |
| **브랜드 프리셋 JSON** | 7개 | **11개** (+design-tokens·component-library·pmf·operation) |
| **전사 가이드라인** | - | **6개** (bcave) |
| **디자인 시스템 프리셋** | - | **72종** |
| **자동 수집 파이프라인** | - | **무신사 3종 + 마켓 트렌드 주간 크롤** |
| **총 스킬** | 105개 | **112개** |

\* V2.2 문서 기준 수치 — V3.0에서 실파일 기준으로 재집계

---

## 📖 추가 참고자료

- [CLAUDE.md](./CLAUDE.md) — 운영 규칙·5대 CRITICAL 원칙·에이전트 팀 규칙
- [ONBOARDING.md](./ONBOARDING.md) — 신규 팀원 온보딩
- [docs/guide/quickstart-guide.md](./docs/guide/quickstart-guide.md) — 5분 퀵스타트
- [docs/guide/user-manual.md](./docs/guide/user-manual.md) — 전체 사용자 매뉴얼
- [docs/reference/fpof-architecture.md](./docs/reference/fpof-architecture.md) — 아키텍처 상세
- [docs/guide/plugin-routing-guide.md](./docs/guide/plugin-routing-guide.md) — FPOF ↔ KW 플러그인 라우팅
- [docs/guide/telegram-setup-guide.md](./docs/guide/telegram-setup-guide.md) — Telegram 채널 설정

---

**버전**: 3.0.0
**최종 업데이트**: 2026-06-07
**PM-Skills**: Paweł Huryn (MIT License) 기반 와키윌리 커스터마이징
**라이선스**: Copyright © 2026 Wacky Willy. All rights reserved.
