# ComfyUI + ERNIE-Image (GGUF) 설치 가이드

최초 1회 진행. 이미 완료했다면 스킵.

## 1. ComfyUI 클론 및 환경 구성

```bash
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
cd ~/ComfyUI
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt

# PyTorch — macOS(MPS) 기준
uv pip install --python .venv/bin/python torch torchvision torchaudio
```

## 2. ComfyUI-GGUF 커스텀 노드 설치 (필수)

GGUF 양자화 모델 로더. `UnetLoaderGGUF`·`CLIPLoaderGGUF` 노드 제공.
```bash
cd ~/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git
uv pip install --python ~/ComfyUI/.venv/bin/python gguf sentencepiece protobuf
```

## 3. (선택) ComfyUI-Manager
커스텀 노드 자동 설치 UI. 이 스킬에선 필수 아님.
```bash
cd ~/ComfyUI/custom_nodes
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git
```

## 4. 모델 다운로드 (GGUF Q4_K_M, 최소 ~11GB)

### 옵션 A — 자동 (권장)
최소셋 (turbo 모드만):
```bash
python system/skills/comfyui/scripts/comfyui_client.py --download-models
```
풀세트 (pro·custom + 프롬프트 인헨서):
```bash
python system/skills/comfyui/scripts/comfyui_client.py --download-models --include-optional
```

스크립트가 `references/model-paths.json` 참조해:
- `unsloth/ERNIE-Image-Turbo-GGUF` → `~/ComfyUI/models/unet/ernie-image-turbo-Q4_K_M.gguf`
- `Comfy-Org/ERNIE-Image` → `~/ComfyUI/models/text_encoders/` + `vae/`

### 옵션 B — 수동 (HuggingFace CLI)
```bash
uv pip install --python ~/ComfyUI/.venv/bin/python "huggingface_hub[cli]"
cd ~/ComfyUI/models

# GGUF 디퓨전 모델 (필수 turbo / 선택 base)
huggingface-cli download unsloth/ERNIE-Image-Turbo-GGUF \
  ernie-image-turbo-Q4_K_M.gguf --local-dir ./unet
huggingface-cli download unsloth/ERNIE-Image-GGUF \
  ernie-image-Q4_K_M.gguf --local-dir ./unet   # optional

# 텍스트 인코더·VAE (safetensors)
huggingface-cli download Comfy-Org/ERNIE-Image \
  text_encoders/ministral-3-3b.safetensors \
  vae/flux2-vae.safetensors \
  --local-dir .
# 인헨서 쓸 때만 추가 다운로드
huggingface-cli download Comfy-Org/ERNIE-Image \
  text_encoders/ernie-image-prompt-enhancer.safetensors \
  --local-dir .
```

## 5. 서버 실행

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

## 6. API 포맷 워크플로우 생성

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

## 7. 스모크 테스트

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

- **MPS/Metal 에러**: PyTorch 2.3+ 필요. `uv pip install --python ~/ComfyUI/.venv/bin/python -U torch torchvision torchaudio`.
- **`Unknown node type 'UnetLoaderGGUF'`**: ComfyUI-GGUF 커스텀 노드 미설치. Step 2 수행.
- **`Unknown node type 'EmptyFlux2LatentImage'`**: ComfyUI 구버전. `cd ~/ComfyUI && git pull`.
- **디스크 부족**: 과거 모델 잔존 가능. `du -sh ~/ComfyUI/models/*` 로 확인 후 불필요한 파일 삭제.
- **메모리 부족 (64GB 이하)**: 해상도 내리기(960→512) 또는 `--lowvram` 플래그 추가. Q4_K_M GGUF는 대략 VRAM 7GB 전후 요구.
- **GGUF 품질이 기대 이하**: Q4_K_M → Q5_K_M 또는 Q6_K로 교체. `references/model-paths.json`의 파일명만 바꾸면 됨.
