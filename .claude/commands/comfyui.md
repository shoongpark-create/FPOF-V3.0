# ComfyUI 이미지 생성 (ERNIE-Image)

로컬 ComfyUI + 바이도 ERNIE-Image 모델로 텍스트-투-이미지 생성. Turbo(빠름)·Pro(고품질)·Custom(밸런스) 3 모드.

## 사용법
`/comfyui [모드] "<프롬프트>" [옵션]` — 모드 생략 시 `turbo`.

## 모드
- `turbo` — 8스텝, ~5초/장, 초안·테스트용 (기본값)
- `pro` — 50스텝, 고품질, 1~2분/장
- `custom` — Turbo→Pro 하이브리드, 20스텝, 품질·속도 밸런스

## 옵션
- `--width 960 --height 1280` — 해상도 (기본 960×1280, 16 배수)
- `--seed 12345` — 고정 시드 (생략 시 랜덤)
- `--no-enhance` — 프롬프트 인헨서 끄기 (기본 ON)
- `--out workspace/26SS/moodboard` — 출력 디렉토리 (기본 `workspace/[시즌]/visuals/`)
- `--count 3` — 배치 크기

## 예시
```
/comfyui turbo "Seoul street fashion editorial, neon backdrop"
/comfyui pro "urban nightlife, Korean signage, cinematic" --width 1280 --height 1280
/comfyui custom "soft wellness fabric texture, natural light" --no-enhance --seed 42
/comfyui turbo "minimalist product photography, white background" --count 4
```

## 절차

1. `system/skills/comfyui/SKILL.md` 스킬 파일 읽어 실행 절차 확인
2. ComfyUI 서버 헬스 체크 (127.0.0.1:8188) — 실패 시 안내 후 중단
3. `$ARGUMENTS`에서 모드·프롬프트·옵션 파싱
4. `.fpof-state.json`에서 현재 시즌 조회 (`--out` 미지정 시 `workspace/[시즌]/visuals/`)
5. `scripts/comfyui_client.py` 호출
6. 결과 파일을 **Read로 직접 확인**한 뒤 사용자에게 경로·시드·메타 요약 보고 (CLAUDE.md 원칙 #5 검증 강제)

## 주의
- **범용 엔진이라 브랜드 자동 적용 안 됨**. 와키윌리 브랜드 비주얼이 필요하면 `/visual-factory` 또는 `/design-generator`를 거쳐 호출할 것.
- 최초 사용 전 `python system/skills/comfyui/scripts/comfyui_client.py --export-api`로 API 포맷 워크플로우 생성 필요.

## 인수
$ARGUMENTS
