---
name: comfyui
description: Local ComfyUI + Baidu ERNIE-Image(8B DiT, Apache 2.0) 엔진으로 텍스트-투-이미지 생성. Turbo(8step/빠름)·Pro(50step/고품질)·Custom(20step/하이브리드) 3모드. "이미지 만들어줘", "비주얼 생성", "/comfyui" 등 모든 이미지 생성 요청에 사용. 범용 엔진이며 브랜드 미적용.
---

# ComfyUI — ERNIE-Image 엔진

오픈소스 텍스트-투-이미지 1등(현재)인 바이도 ERNIE-Image(8B DiT, Apache 2.0) 기반 **로컬 이미지 생성 엔진**. 본 스킬은 **범용 엔진**이며 와키윌리 브랜드 토큰은 자동 주입하지 않는다. 브랜드 적용이 필요하면 상위 스킬(`visual-factory`, `design-generator`)이 프롬프트를 조립해 이 엔진에 넘긴다.

## 3가지 모드

| 모드 | 모델 | 스텝 | CFG | 특징 | 용도 |
|------|------|------|-----|------|------|
| `turbo` | ernie-image-turbo | 8 | 1.0 | DMD/RL 최적화, ~5초/장(MPS) | 초안·테스트 |
| `pro` | ernie-image | 50 | 4.0 | 최고품질, 1~2분/장 | 최종 컷 |
| `custom` | 두 모델 순차 | 20 (0→2 Turbo, 2→20 Pro) | 4.0 | 구도=Turbo, 디테일=Pro | 품질·속도 밸런스 |

공통: sampler `euler`, scheduler `simple`, 기본 해상도 960×1280.

## 사전 준비 (1회성)

### 1) ComfyUI 설치 — `~/ComfyUI/`
이미 설치됨(2026-04-21 기준). 재설치 필요 시:
```bash
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
cd ~/ComfyUI && uv venv --python 3.12 .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install torch torchvision torchaudio  # MPS
```

### 2) 모델 파일 (~47GB)
`references/model-paths.json`의 HuggingFace URL에서 다운로드. 저장 위치:
- `~/ComfyUI/models/diffusion_models/ernie-image.safetensors`
- `~/ComfyUI/models/diffusion_models/ernie-image-turbo.safetensors`
- `~/ComfyUI/models/text_encoders/ministral-3-3b.safetensors`
- `~/ComfyUI/models/text_encoders/ernie-image-prompt-enhancer.safetensors`
- `~/ComfyUI/models/vae/flux2-vae.safetensors`

간편 다운로드:
```bash
python system/skills/comfyui/scripts/comfyui_client.py --download-models
```

### 3) API 포맷 워크플로우 변환 (최초 1회)
워크플로우 JSON 3개는 ComfyUI UI 그래프 포맷이라 API 제출 불가. 변환:
```bash
python system/skills/comfyui/scripts/comfyui_client.py --export-api
```
→ `system/skills/comfyui/api/*.json` 생성.

UI에서 수동 변환도 가능: ComfyUI UI에서 JSON 로드 → 우상단 **Save (API Format)** → `system/skills/comfyui/api/<원본이름>_api.json`으로 저장.

### 4) ComfyUI 서버 기동
```bash
cd ~/ComfyUI && .venv/bin/python main.py --listen 127.0.0.1 --port 8188
```
- MPS 자동 감지 (macOS)
- 서버 주소: http://127.0.0.1:8188/
- 스킬이 서버 상태를 자동 체크하므로 **생성 전 켜둘 것**

## 실행 절차 (Claude가 수행)

사용자가 `/comfyui ...` 호출하면:

### 1단계 — 서버 헬스 체크
```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8188/
```
- `200` → 다음 단계
- 그 외 → **중단**. 사용자에게 "ComfyUI 서버를 먼저 켜주세요: `cd ~/ComfyUI && .venv/bin/python main.py`" 안내.

### 2단계 — 인수 파싱
슬래시 커맨드의 `$ARGUMENTS`에서 추출:
- `mode`: `turbo` / `pro` / `custom` (기본 `turbo`)
- `prompt`: 따옴표로 감싼 문자열 (필수)
- `--width <int>`: 기본 960
- `--height <int>`: 기본 1280
- `--seed <int>`: 기본 -1(랜덤)
- `--no-enhance`: 프롬프트 인헨서 끄기 (기본 ON)
- `--out <path>`: 출력 디렉토리 (기본 `workspace/[현재시즌]/visuals/`; 시즌은 `.fpof-state.json`에서)
- `--count <int>`: 배치 크기 (기본 1)

### 3단계 — Python 스크립트 호출
```bash
python "system/skills/comfyui/scripts/comfyui_client.py" \
  --mode <mode> \
  --prompt "<prompt>" \
  --width <w> --height <h> \
  --seed <seed> \
  --enhance <true|false> \
  --out "<out_dir>" \
  --count <n>
```

### 4단계 — 결과 검증 (**CRITICAL**: CLAUDE.md 원칙 #5·#7)
스크립트가 저장했다고 **주장**하는 파일을 **직접 Read로 확인**:
- 이미지 파일 존재 여부
- 메타데이터 JSON의 `status: success` 확인
- 실패 시 스크립트 stderr 그대로 보고 ("검증 불가 / 실패"를 숨기지 말 것)

### 5단계 — 사용자 보고
- 저장 경로 (상대·절대)
- 사용한 시드·모드·스텝·CFG
- 생성 소요 시간
- 인헨서 ON인 경우 enhanced prompt 발췌 (중국어일 수 있음)

## 출력 포맷

- **이미지**: PNG, `<out>/<YYYYMMDD-HHMMSS>_<mode>_<seed>.png`
- **메타**: 같은 basename의 `.json`:
  ```json
  {
    "prompt": "...",
    "enhanced_prompt": "... (中文 가능)",
    "seed": 123,
    "mode": "turbo",
    "model": "ernie-image-turbo.safetensors",
    "width": 960, "height": 1280,
    "steps": 8, "cfg": 1.0,
    "sampler": "euler", "scheduler": "simple",
    "duration_ms": 4721,
    "status": "success",
    "comfyui_version": "0.3.64"
  }
  ```

## 브랜드 통합 — 경계 명시

이 스킬은 **엔진 레이어**다. 의도적으로 브랜드 중립:
- 와키윌리 visual-identity·tone-manner 토큰 **자동 주입 안 함**
- `--brand wacky-willy` 같은 플래그 **없음**
- 상위 스킬(`visual-factory`, `design-generator`, `moodboard`)이 프롬프트 조립 후 이 엔진에 위임

이 경계 덕에 향후 Wacky-Willy가 아닌 다른 브랜드·범용 콘텐츠 생성에도 쓸 수 있다.

## 트러블슈팅

| 증상 | 원인·해결 |
|------|----------|
| `Connection refused` / 헬스체크 실패 | 서버 미기동. `cd ~/ComfyUI && .venv/bin/python main.py` |
| `model not found: ernie-image*.safetensors` | 모델 파일 누락. `--download-models` 실행 |
| API 포맷 워크플로우 없음 | `--export-api` 실행 또는 UI에서 수동 Save (API Format) |
| 프롬프트 인헨서 중국어 출력 | 정상(Ernie는 중국 모델). 그대로 사용 가능 |
| MPS 메모리 부족 | `--width 512 --height 768`로 내리거나 `--count 1` |
| 10분 이상 멈춤 (block attention issue) | ComfyUI 서버 재시작 |
| 샘플러/노드 타입 누락 에러 | 커스텀 노드 필요. `ComfyUI-Manager` 설치 후 누락 노드 자동 인스톨 |

## 참고 자료

- `scripts/comfyui_client.py` — 헬스체크·워크플로우 mutate·API 제출·폴링·저장 전체
- `scripts/ui_to_api.py` — UI 그래프 → API 포맷 변환 (제한적; 대부분 Ernie 워크플로우 처리)
- `references/model-paths.json` — 파일 ↔ 경로 ↔ HF URL 맵
- `references/setup-guide.md` — 최초 설치·모델 다운로드 상세
- 튜토리얼 영상: <https://www.youtube.com/watch?v=H6SbNBEtPFU>
- 공식: <https://github.com/baidu/ernie-image> / <https://huggingface.co/Comfy-Org/ERNIE-Image> / <https://docs.comfy.org/tutorials/image/ernie-image/ernie-image>
