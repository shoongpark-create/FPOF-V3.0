# ComfyUI 이미지 생성 (ERNIE-Image)

로컬 ComfyUI + 바이도 ERNIE-Image 모델로 텍스트-투-이미지 생성. Turbo(빠름)·Pro(고품질)·Custom(밸런스) 3 모드.

## 사용법

### 직접 프롬프트 모드
`/comfyui [모드] "<프롬프트>" [옵션]` — 모드 생략 시 `turbo`.

### 인터랙티브 모드 (한국어 의도 수집)
`/comfyui` 만 입력하거나 `/comfyui [모드]`처럼 **프롬프트 없이 호출하면 AskUserQuestion으로 한국어 인터뷰** 진행 후 생성한다. 한국어로 의도만 알려주면 스킬이 알아서 프롬프트를 조립·영어 확장·생성까지 연쇄 처리.

## 모드
- `turbo` — 8스텝, ~5초/장, 초안·테스트용 (기본값)
- `pro` — 50스텝, 고품질, 1~2분/장
- `custom` — Turbo→Pro 하이브리드, 20스텝, 품질·속도 밸런스

## 옵션
- `--width 960 --height 1280` — 해상도 (기본 960×1280, 16 배수)
- `--seed 12345` — 고정 시드 (생략 시 랜덤)
- `--no-enhance` — 프롬프트 인헨서 끄기 (기본 ON, 영어 확장 출력)
- `--out workspace/26SS/moodboard` — 출력 디렉토리 (기본 `workspace/[시즌]/visuals/`)
- `--safetensors` — GGUF 대신 원본 safetensors 쓰기 (기본은 GGUF Q4_K_M)

## 예시
```
/comfyui                                                # 인터랙티브 (한국어 인터뷰)
/comfyui turbo                                          # 인터랙티브 (turbo 모드 고정)
/comfyui turbo "Seoul street fashion editorial, neon backdrop"
/comfyui pro "urban nightlife, Korean signage, cinematic" --width 1280 --height 1280
/comfyui custom "soft wellness fabric texture" --no-enhance --seed 42
/comfyui turbo "한강 야경, 네온, 시네마틱"             # 한국어 프롬프트 OK (인헨서가 영어로 확장)
```

## 절차 (Claude가 수행)

### Step 0 — 인자 파싱
`$ARGUMENTS`에서 다음 추출:
- `mode`: turbo/pro/custom (없으면 turbo)
- `prompt`: 따옴표로 감싼 텍스트 (없을 수 있음 → 인터랙티브 분기)
- 플래그들(`--width`, `--height`, `--seed`, `--no-enhance`, `--out`, `--safetensors`)

### Step 1A — 인터랙티브 분기 (prompt가 비었거나 매우 짧음<5글자)
**AskUserQuestion**을 사용해 사용자 의도를 한국어로 수집. 한 번에 한 질문씩 (multiSelect=false가 기본). 질문 묶음은 상황에 맞게 줄여도 됨:

1. **"무엇을 담고 싶으신가요?"**
   - options: 인물 / 제품·오브젝트 / 풍경·도시 / 일러스트·포스터 / 추상·패턴
   - open=true (자유 기입 허용)

2. **"어떤 스타일·무드인가요?"** (multiSelect=true)
   - options: 실사 사진 / 시네마틱 / 만화·애니 / 미니멀 / 빈티지·레트로 / 글로시 광고 / 따뜻한 파스텔 / 차가운 모노톤

3. **"꼭 들어가야 할 요소가 있나요?"** (자유 기입)
   - 예: 배경·색상·소품·시간대·카메라 앵글·텍스트 등. "없음"도 허용.

4. **(선택) "해상도·시드 지정할까요?"**
   - 해상도 옵션: 960×1280(세로) / 1280×960(가로) / 1024×1024(정방) / 직접 입력
   - 시드: 랜덤 / 숫자 입력

수집한 답변을 한국어 1문장으로 조립:
```
[주제], [스타일·무드 콤마 나열], [구체 요소]
```
예: `한강 야경 속 젊은 여성, 시네마틱 실사 사진 · 따뜻한 파스텔, 네온·주황 가로등 섞인 저녁 분위기, 캐주얼 아우터`

조립한 프롬프트를 Step 2로 전달.

> **왜 한국어 그대로?** Mistral-3 인코더가 다국어 대응. 인헨서 시스템 프롬프트에 "MUST respond in English" 내장되어 있어 한국어 입력도 영어 확장문으로 변환된 뒤 이미지 생성에 쓰임.

### Step 1B — 직접 분기 (prompt 있음)
그대로 Step 2로 이동.

### Step 2 — 선행 조건
1. `system/skills/comfyui/SKILL.md` 스킬 파일 읽어 최신 절차 확인
2. ComfyUI 서버 헬스 체크 (`http://127.0.0.1:8188`) — 실패 시 안내(`cd ~/ComfyUI && .venv/bin/python main.py`) 후 중단
3. `.fpof-state.json` 읽어 현재 시즌 조회 (`--out` 미지정 시 `workspace/[시즌]/visuals/`)

### Step 3 — 실행
`scripts/comfyui_client.py`를 Bash로 호출:
```
python "/Users/sherman/00. FPOF V3.0 Claude -main/system/skills/comfyui/scripts/comfyui_client.py" \
  --mode <mode> \
  --prompt "<조립된 또는 사용자 프롬프트>" \
  --width <w> --height <h> \
  --seed <seed> \
  --enhance <true|false> \
  --out "<out_dir>"
```

### Step 4 — 검증·보고 (CLAUDE.md 원칙 #5 강제)
- 결과 파일 경로가 실제 존재하는지 **Read로 확인**
- 메타 JSON의 `status: success` 확인
- 실패 시 stderr 그대로 보고 ("검증 불가" 숨기지 말 것)
- 성공 시: 경로·시드·모드·소요시간·인헨서 영어 프롬프트 발췌 보고

## 주의
- **범용 엔진이라 브랜드 자동 적용 안 됨**. 와키윌리 브랜드 비주얼이 필요하면 `/visual-factory` 또는 `/design-generator`를 거쳐 호출할 것.
- 최초 사용 전 모델 다운로드·서버 기동 필요. `python system/skills/comfyui/scripts/comfyui_client.py --check-setup`로 준비 상태 확인.
- AskUserQuestion 도중 사용자가 답 일부를 건너뛰거나 "랜덤·추천"이라 답하면, 해당 항목은 프롬프트 조립 시 생략하고 인헨서에 맡기면 됨.

## 인수
$ARGUMENTS
