# ComfyUI + ERNIE-Image 설치 가이드

최초 1회 진행. 이미 완료했다면 스킵.

## 1. ComfyUI 클론 및 환경 구성

```bash
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
cd ~/ComfyUI
uv venv --python 3.12 .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

# PyTorch — macOS(MPS) 기준
.venv/bin/python -m pip install torch torchvision torchaudio
```

## 2. (권장) ComfyUI-Manager 설치
커스텀 노드 자동 설치용. Ernie 워크플로우에 필요한 노드가 기본 포함인지 확실치 않으면 설치해두는 게 안전.
```bash
cd ~/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git
```

## 3. ERNIE-Image 모델 다운로드 (~47GB)

### 옵션 A — 자동 (hf_hub_download)
```bash
python system/skills/comfyui/scripts/comfyui_client.py --download-models
```
스크립트가 `references/model-paths.json` 참조해 5개 파일을 `~/ComfyUI/models/` 하위 경로에 배치.

### 옵션 B — 수동 (HuggingFace CLI)
```bash
pip install -U "huggingface_hub[cli]"
cd ~/ComfyUI/models

huggingface-cli download Comfy-Org/ERNIE-Image \
  diffusion_models/ernie-image.safetensors \
  diffusion_models/ernie-image-turbo.safetensors \
  text_encoders/ministral-3-3b.safetensors \
  text_encoders/ernie-image-prompt-enhancer.safetensors \
  vae/flux2-vae.safetensors \
  --local-dir . --local-dir-use-symlinks False
```

## 4. 서버 실행

```bash
cd ~/ComfyUI && .venv/bin/python main.py --listen 127.0.0.1 --port 8188
```
- 첫 기동 시 모델 로드로 1~2분 소요
- `http://127.0.0.1:8188/` 접속 가능한지 확인

**백그라운드 상시 실행** (선택):
```bash
cd ~/ComfyUI
nohup .venv/bin/python main.py --listen 127.0.0.1 --port 8188 > ~/comfyui.log 2>&1 &
echo $! > ~/.comfyui.pid
```
중지: `kill $(cat ~/.comfyui.pid)`

## 5. API 포맷 워크플로우 생성

워크플로우 3개 모두 UI 포맷이라 `/prompt` 엔드포인트에서 거부된다. 변환 방법:

### 옵션 A — 스크립트 자동 변환
```bash
python system/skills/comfyui/scripts/comfyui_client.py --export-api
```
→ `system/skills/comfyui/api/{53_1,53_2,53_3}_api.json` 생성.

### 옵션 B — ComfyUI UI 수동 저장
1. ComfyUI UI(`localhost:8188`) 열기
2. 각 워크플로우 JSON 드래그앤드롭해서 로드
3. 우상단 메뉴 → **Workflow** → **Save (API Format)**
4. 파일명을 원래 이름 + `_api.json`으로 저장
5. 3개 파일 모두 `system/skills/comfyui/api/` 폴더에 이동

## 6. 스모크 테스트

```bash
python system/skills/comfyui/scripts/comfyui_client.py \
  --mode turbo \
  --prompt "test photo, a cat sitting on grass" \
  --out /tmp/comfyui-smoke \
  --count 1
```

성공 시:
- `/tmp/comfyui-smoke/*.png` 생성
- 같은 폴더에 `.json` 메타 파일
- 메타 `status: success` + `duration_ms` 표시

## 트러블슈팅

- **MPS/Metal 에러**: PyTorch 2.3+ 필요. `pip install -U torch torchvision torchaudio`.
- **`ERROR: Missing node type 'EmptyFlux2LatentImage'`**: ComfyUI 최신 아닐 때. `cd ~/ComfyUI && git pull`.
- **디스크 부족**: Klein 4B·과거 Flux 모델이 남아 있을 수 있음. `du -sh ~/ComfyUI/models/*` 로 확인.
- **메모리 부족 (64GB 이하)**: 해상도 내리기(960→512) 또는 `--lowvram` 플래그 추가.
