#!/usr/bin/env python3
"""ComfyUI ERNIE-Image 클라이언트.

서브커맨드:
  --download-models   모델 5종을 ~/ComfyUI/models/ 에 다운로드
  --export-api        UI 워크플로우 → API 포맷 변환
  --check-setup       서버·모델·워크플로우 상태 점검
  --mode X --prompt Y 이미지 생성 (메인 경로)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REFERENCES_DIR = SKILL_DIR / "references"
API_DIR = SKILL_DIR / "api"
COMFYUI_ROOT = Path.home() / "ComfyUI"
SERVER_URL = "http://127.0.0.1:8188"

# UI widget → API input 매핑. "__skip__" = UI 전용, API에는 포함 안 함.
WIDGET_INPUTS: dict[str, list[str]] = {
    "PrimitiveInt": ["value", "__skip__"],
    "PrimitiveFloat": ["value", "__skip__"],
    "PrimitiveString": ["value"],
    "PrimitiveStringMultiline": ["value"],
    "PrimitiveBoolean": ["value"],
    "PrimitiveAny": ["value"],
    "String": ["value"],
    "KSampler": ["seed", "__skip__", "steps", "cfg", "sampler_name", "scheduler", "denoise"],
    "KSamplerAdvanced": [
        "add_noise", "noise_seed", "__skip__", "steps", "cfg",
        "sampler_name", "scheduler", "start_at_step", "end_at_step",
        "return_with_leftover_noise",
    ],
    "UNETLoader": ["unet_name", "weight_dtype"],
    "VAELoader": ["vae_name"],
    "CLIPLoader": ["clip_name", "type", "device"],
    "DualCLIPLoader": ["clip_name1", "clip_name2", "type", "device"],
    # city96/ComfyUI-GGUF 커스텀 노드 (GGUF 양자화 로더)
    "UnetLoaderGGUF": ["unet_name"],
    "UnetLoaderGGUFAdvanced": ["unet_name", "dequant_dtype", "patch_dtype", "patch_on_device"],
    "CLIPLoaderGGUF": ["clip_name", "type"],
    "DualCLIPLoaderGGUF": ["clip_name1", "clip_name2", "type"],
    "TripleCLIPLoaderGGUF": ["clip_name1", "clip_name2", "clip_name3"],
    "QuadrupleCLIPLoaderGGUF": ["clip_name1", "clip_name2", "clip_name3", "clip_name4"],
    "CheckpointLoaderSimple": ["ckpt_name"],
    "ModelSamplingSD3": ["shift"],
    "CLIPTextEncode": ["text"],
    "ConditioningZeroOut": [],
    "EmptyLatentImage": ["width", "height", "batch_size"],
    "EmptyFlux2LatentImage": ["width", "height", "batch_size"],
    "EmptySD3LatentImage": ["width", "height", "batch_size"],
    "VAEDecode": [],
    "VAEEncode": [],
    "SaveImage": ["filename_prefix"],
    "PreviewImage": [],
    "PreviewAny": [],
    "CLIPSetLastLayer": ["stop_at_clip_layer"],
    "LoraLoader": ["lora_name", "strength_model", "strength_clip"],
    # ComfyUI StringReplace 실제 schema: ["string", "find", "replace"]
    "StringReplace": ["string", "find", "replace"],
    "ComfySwitchNode": ["switch"],
    # TextGenerate (프롬프트 인헨서) — 실측 schema 기반:
    # required: clip(link), prompt(link), max_length, sampling_mode
    # nested under sampling_mode=on: temperature, top_k, top_p, min_p, repetition_penalty
    # optional: thinking, use_default_template
    "TextGenerate": [
        "prompt", "max_length", "sampling_mode",
        "temperature", "top_k", "top_p", "min_p", "repetition_penalty",
        "seed", "__skip__",   # [8]=seed, [9]=control_after_generate(UI-only)
        "thinking", "use_default_template",
    ],
}

MODES: dict[str, dict] = {
    "turbo": {
        "ui_json": "53_1_Ernie Image Turbo.json",
        "api_json": "53_1_Ernie Image Turbo_api.json",
        "steps": 8, "cfg": 1.0,
    },
    "pro": {
        "ui_json": "53_2_Ernie Image.json",
        "api_json": "53_2_Ernie Image_api.json",
        "steps": 50, "cfg": 4.0,
    },
    "custom": {
        "ui_json": "53_3_Ernie Image Custom.json",
        "api_json": "53_3_Ernie Image Custom_api.json",
        "steps": 20, "cfg": 4.0,
    },
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def http_get(url: str, timeout: float = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "fpof-comfyui-client/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def http_post_json(url: str, data: dict, timeout: float = 30) -> dict:
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "fpof-comfyui-client/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="replace")
        except Exception:
            detail = ""
        raise RuntimeError(f"HTTP {e.code} on POST {url}\n{detail}") from e


def server_health() -> bool:
    try:
        req = urllib.request.Request(f"{SERVER_URL}/")
        with urllib.request.urlopen(req, timeout=3) as r:
            return 200 <= r.status < 400
    except Exception:
        return False


def ui_to_api(ui: dict) -> tuple[dict, set[str]]:
    """UI 포맷 워크플로우 → API 포맷 dict.

    반환: (api_workflow, unknown_class_types)
    """
    link_map: dict[int, list] = {}
    for link in ui.get("links") or []:
        if isinstance(link, list) and len(link) >= 5:
            link_id, src_node, src_slot = link[0], link[1], link[2]
            # ComfyUI API requires string node IDs in link references (prompt dict is keyed by str).
            link_map[link_id] = [str(src_node), src_slot]

    api: dict[str, dict] = {}
    unknown: set[str] = set()

    for node in ui.get("nodes") or []:
        node_id = str(node["id"])
        class_type = node["type"]
        inputs: dict = {}

        # 1) 위젯 디폴트 먼저 — 매핑 없는 클래스는 위젯 있을 때만 unknown으로 신고
        widget_names = WIDGET_INPUTS.get(class_type)
        widgets = node.get("widgets_values") or []
        if widget_names is None:
            if widgets:
                unknown.add(class_type)
        else:
            for i, name in enumerate(widget_names):
                if i < len(widgets) and name != "__skip__":
                    inputs[name] = widgets[i]

        # 2) 링크가 있으면 위젯 덮어쓰기 — 링크 우선
        for inp in node.get("inputs") or []:
            name = inp.get("name")
            link_id = inp.get("link")
            if name and link_id is not None and link_id in link_map:
                inputs[name] = link_map[link_id]

        api[node_id] = {
            "inputs": inputs,
            "class_type": class_type,
            "_meta": {"title": node.get("title") or class_type},
        }

    return api, unknown


def cmd_export_api(args) -> int:
    API_DIR.mkdir(exist_ok=True, parents=True)
    any_unknown: set[str] = set()
    for mode, spec in MODES.items():
        src = SKILL_DIR / spec["ui_json"]
        dst = API_DIR / spec["api_json"]
        if not src.exists():
            eprint(f"[skip] {mode}: source not found {src}")
            continue
        with open(src) as f:
            ui = json.load(f)
        api, unknown = ui_to_api(ui)
        any_unknown |= unknown
        with open(dst, "w") as f:
            json.dump(api, f, indent=2, ensure_ascii=False)
        print(f"[ok] {mode}: {src.name} → api/{dst.name}  ({len(api)} nodes)")

    if any_unknown:
        eprint()
        eprint(f"[warning] Unknown node types — widget inputs may be missing:")
        for t in sorted(any_unknown):
            eprint(f"  - {t}")
        eprint("If ComfyUI complains about missing inputs, open the workflow in ComfyUI UI")
        eprint("and save again via File → Save (API Format). Overwrite files under api/.")
    return 0


def cmd_download_models(args) -> int:
    paths_file = REFERENCES_DIR / "model-paths.json"
    with open(paths_file) as f:
        cfg = json.load(f)
    try:
        from huggingface_hub import hf_hub_download  # type: ignore
    except ImportError:
        eprint("Installing huggingface_hub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub"])
        from huggingface_hub import hf_hub_download  # type: ignore

    models_dir = COMFYUI_ROOT / "models"
    models_dir.mkdir(exist_ok=True, parents=True)

    # 필수 파일과 선택 파일 구분
    required_files = [s for s in cfg["files"] if s.get("required", True)]
    optional_files = [s for s in cfg["files"] if not s.get("required", True)]

    specs = required_files[:]
    if getattr(args, "include_optional", False):
        specs += optional_files
        print(f"[info] Including optional files ({len(optional_files)}개): "
              f"{', '.join(Path(s['local_path']).name for s in optional_files)}")
    else:
        if optional_files:
            names = ", ".join(Path(s["local_path"]).name for s in optional_files)
            eprint(f"[info] Skipping optional files: {names}")
            eprint(f"       Add --include-optional to download them too.")
            eprint()

    total_gb = sum(s.get("approximate_size_gb", 0) for s in specs)
    print(f"[plan] {len(specs)}개 파일, 약 {total_gb:.1f} GB\n")

    for spec in specs:
        repo = spec.get("hf_repo")
        if not repo:
            eprint(f"[skip] {spec['local_path']}: no hf_repo specified")
            continue

        local_path = COMFYUI_ROOT / spec["local_path"]
        local_path.parent.mkdir(exist_ok=True, parents=True)

        if local_path.exists():
            size_gb = local_path.stat().st_size / (1024 ** 3)
            print(f"[skip] {spec['local_path']} ({size_gb:.2f} GB, already present)")
            continue

        approx = spec.get("approximate_size_gb", "?")
        print(f"[download] {repo}/{spec['hf_path']} → {spec['local_path']} (~{approx} GB)")
        # hf_hub_download은 repo 구조를 그대로 local_dir 밑에 복제하므로
        # 우리 원하는 위치로 가려면 download 후 이동 or local_dir를 섬세하게 설정.
        # 간단히: local_dir을 local_path의 부모로 하고 filename을 basename으로.
        # 하지만 hf_path 자체가 subfolder 포함이라 repo 구조 유지 후 이동이 단순.
        downloaded = hf_hub_download(
            repo_id=repo,
            filename=spec["hf_path"],
            local_dir=str(models_dir),
        )
        # 요청 위치가 실제 다운로드 위치와 다르면 이동
        actual = Path(downloaded)
        if actual != local_path:
            local_path.parent.mkdir(exist_ok=True, parents=True)
            actual.replace(local_path)
            print(f"  moved: {actual.name} → {local_path}")
        else:
            print(f"  saved: {downloaded}")

    print("\n[ok] Download complete.")
    return 0


def cmd_check_setup(args) -> int:
    ok = True
    print("=== ComfyUI setup check ===")
    print(f"ComfyUI root   : {COMFYUI_ROOT} — {'OK' if COMFYUI_ROOT.exists() else 'MISSING'}")
    if not COMFYUI_ROOT.exists():
        ok = False

    venv = COMFYUI_ROOT / ".venv" / "bin" / "python"
    print(f"Python venv    : {venv} — {'OK' if venv.exists() else 'MISSING'}")
    if not venv.exists():
        ok = False

    print(f"Server         : {SERVER_URL} — {'UP' if server_health() else 'DOWN'}")

    print()
    print("Custom nodes:")
    ggufnodes = COMFYUI_ROOT / "custom_nodes" / "ComfyUI-GGUF"
    print(f"  ComfyUI-GGUF: {'OK' if ggufnodes.exists() else 'MISSING'}  ({ggufnodes})")
    if not ggufnodes.exists():
        ok = False

    print()
    print("Models:")
    paths_file = REFERENCES_DIR / "model-paths.json"
    if paths_file.exists():
        with open(paths_file) as f:
            cfg = json.load(f)
        for spec in cfg["files"]:
            p = COMFYUI_ROOT / spec["local_path"]
            required = spec.get("required", True)
            tag = "[req]" if required else "[opt]"
            if p.exists():
                status = f"OK ({p.stat().st_size/(1024**3):.2f} GB)"
            else:
                status = "MISSING"
                if required:
                    ok = False
            print(f"  {tag} {spec['local_path']:<55} {status}")

    print()
    print("API workflows:")
    for mode, spec in MODES.items():
        p = API_DIR / spec["api_json"]
        status = "OK" if p.exists() else "MISSING (run --export-api)"
        print(f"  {mode:<7}  {spec['api_json']:<50} {status}")
        if not p.exists():
            ok = False

    print()
    print("Overall:", "READY" if ok else "NOT READY")
    return 0 if ok else 1


def find_node_by_class(api_wf: dict, class_type: str) -> str | None:
    for nid, node in api_wf.items():
        if node.get("class_type") == class_type:
            return nid
    return None


def find_node_by_title(api_wf: dict, title_substr: str, class_type: str | None = None) -> str | None:
    for nid, node in api_wf.items():
        meta_title = (node.get("_meta") or {}).get("title", "")
        if title_substr.lower() in meta_title.lower():
            if class_type is None or node.get("class_type") == class_type:
                return nid
    return None


def normalize_model_paths(api_wf: dict) -> None:
    """튜토리얼 워크플로우는 'Ernie Image\\\\*.safetensors' 같은 서브폴더·백슬래시 경로를 쓴다.

    ComfyUI의 표준 flat 구조에 맞춰 백슬래시 → forward slash 치환,
    'Ernie Image/'·'Flux2/' 접두사 스트립.
    """
    rules = {
        "UNETLoader": ["unet_name"],
        "UnetLoaderGGUF": ["unet_name"],
        "UnetLoaderGGUFAdvanced": ["unet_name"],
        "VAELoader": ["vae_name"],
        "CLIPLoader": ["clip_name"],
        "CLIPLoaderGGUF": ["clip_name"],
        "DualCLIPLoader": ["clip_name1", "clip_name2"],
        "DualCLIPLoaderGGUF": ["clip_name1", "clip_name2"],
        "CheckpointLoaderSimple": ["ckpt_name"],
    }
    prefixes = ("Ernie Image/", "Flux2/")
    for node in api_wf.values():
        names = rules.get(node.get("class_type"))
        if not names:
            continue
        for inp_name in names:
            val = node["inputs"].get(inp_name)
            if not isinstance(val, str):
                continue
            v = val.replace("\\", "/")
            for pref in prefixes:
                if v.startswith(pref):
                    v = v[len(pref):]
                    break
            node["inputs"][inp_name] = v


# UNETLoader safetensors 파일 → GGUF 파일 매핑 (model-paths.json과 동기)
GGUF_SUBSTITUTIONS: dict[str, str] = {
    "ernie-image-turbo.safetensors": "ernie-image-turbo-Q4_K_M.gguf",
    "ernie-image.safetensors": "ernie-image-Q4_K_M.gguf",
}


def swap_unet_to_gguf(api_wf: dict) -> int:
    """모든 UNETLoader 노드를 UnetLoaderGGUF로 치환하고 파일명을 GGUF로 변경.

    ComfyUI-GGUF (city96) 노드를 요구. 모델은 ~/ComfyUI/models/unet/ 에 위치.
    반환: 치환된 노드 수.
    """
    swapped = 0
    for node in api_wf.values():
        if node.get("class_type") != "UNETLoader":
            continue
        unet_name = node["inputs"].get("unet_name", "")
        gguf_name = GGUF_SUBSTITUTIONS.get(unet_name)
        if not gguf_name:
            # 매핑 없으면 확장자만 바꾸는 휴리스틱
            if unet_name.endswith(".safetensors"):
                gguf_name = unet_name[:-len(".safetensors")] + "-Q4_K_M.gguf"
            else:
                continue
        node["class_type"] = "UnetLoaderGGUF"
        node["inputs"] = {"unet_name": gguf_name}
        (node.setdefault("_meta", {}))["title"] = node["_meta"].get("title") or "UNETLoader (GGUF)"
        swapped += 1
    return swapped


def prune_enhance_branch(api_wf: dict) -> int:
    """enhance=false 일 때 프롬프트 인헨서 브랜치 전체 제거.

    제거 대상: StringReplace, TextGenerate, ComfySwitchNode(프롬프트 분기), CLIPLoader(PE),
    PreviewAny, PrimitiveBoolean(enhance toggle)
    재배선: CLIPTextEncode.text 입력을 직접 PrimitiveStringMultiline(유저 프롬프트)으로 연결.

    이유: TextGenerate 노드의 sampling_mode는 COMFY_DYNAMICCOMBO_V3로 nested 스키마라
    flat 위젯 매핑으로 validation 통과가 안 됨. enhance=false면 어차피 실행 안 되므로
    그래프에서 완전히 제거.
    """
    prompt_node_id = None
    for nid, node in api_wf.items():
        if node.get("class_type") == "PrimitiveStringMultiline":
            prompt_node_id = nid
            break
    if not prompt_node_id:
        return 0

    switch_node_ids = [
        nid for nid, n in api_wf.items() if n.get("class_type") == "ComfySwitchNode"
    ]

    # CLIPTextEncode(positive)의 text 입력이 스위치 출력이면 유저 프롬프트로 직결
    for nid, node in api_wf.items():
        if node.get("class_type") != "CLIPTextEncode":
            continue
        t = node["inputs"].get("text")
        if isinstance(t, list) and t[0] in switch_node_ids:
            node["inputs"]["text"] = [prompt_node_id, 0]

    to_remove: set[str] = set()
    for nid, node in api_wf.items():
        ct = node.get("class_type")
        if ct in ("StringReplace", "TextGenerate", "ComfySwitchNode", "PreviewAny"):
            to_remove.add(nid)
        elif ct == "CLIPLoader" and "prompt-enhancer" in str(node["inputs"].get("clip_name", "")):
            to_remove.add(nid)
        elif ct == "PrimitiveBoolean":
            to_remove.add(nid)

    for nid in to_remove:
        del api_wf[nid]
    return len(to_remove)


def patch_missing_clip_files(api_wf: dict) -> None:
    """PE encoder 파일이 없으면 CLIPLoader clip_name을 ministral로 치환.

    ComfyUI는 inactive 브랜치(ComfySwitchNode on_false)도 validation 단계에서 검사하므로
    모델 파일 존재 여부를 체크한다. PE 파일을 다운로드하지 않은 경우
    해당 CLIPLoader가 '파일 없음' 에러를 낸다.

    해결: clip_name을 실제 존재하는 파일(ministral)로 치환. 노드 자체는 enhance=false 경로에서
    실행되지 않으므로 실제 로드는 발생하지 않는다 (validation만 통과시킴).
    """
    pe_path = COMFYUI_ROOT / "models" / "text_encoders" / "ernie-image-prompt-enhancer.safetensors"
    mistral_path = COMFYUI_ROOT / "models" / "text_encoders" / "ministral-3-3b.safetensors"
    if pe_path.exists():
        return  # 실제 파일 있으면 그대로 사용
    if not mistral_path.exists():
        return  # 대체할 파일도 없으면 손 못 댐
    for node in api_wf.values():
        if node.get("class_type") in ("CLIPLoader", "CLIPLoaderGGUF"):
            cname = node["inputs"].get("clip_name")
            if isinstance(cname, str) and "prompt-enhancer" in cname:
                node["inputs"]["clip_name"] = "ministral-3-3b.safetensors"
                (node.setdefault("_meta", {}))["title"] = (
                    (node.get("_meta") or {}).get("title", "") + " [PE missing — substituted]"
                )


def mutate_workflow(api_wf: dict, args) -> tuple[dict, int]:
    """프롬프트·시드·해상도·인헨서 값을 API 워크플로우에 주입.

    기본: UNETLoader → UnetLoaderGGUF 치환(GGUF 파일 사용).
    `--safetensors` 플래그로 끌 수 있음(원본 FP16 safetensors 사용).
    """
    normalize_model_paths(api_wf)
    patch_missing_clip_files(api_wf)
    if not getattr(args, "enhance", True):
        pruned = prune_enhance_branch(api_wf)
        if pruned:
            eprint(f"[info] --enhance false → removed {pruned} enhance-branch node(s)")
    if getattr(args, "use_gguf", True):
        n = swap_unet_to_gguf(api_wf)
        if n == 0:
            eprint("[warn] GGUF mode requested but no UNETLoader found to swap")

    prompt_id = find_node_by_class(api_wf, "PrimitiveStringMultiline")
    width_id = find_node_by_title(api_wf, "Width", "PrimitiveInt")
    height_id = find_node_by_title(api_wf, "Height", "PrimitiveInt")
    enhance_id = find_node_by_class(api_wf, "PrimitiveBoolean")

    if prompt_id:
        api_wf[prompt_id]["inputs"]["value"] = args.prompt
    else:
        eprint("[warn] No PrimitiveStringMultiline node found — prompt not injected")

    if width_id:
        api_wf[width_id]["inputs"]["value"] = args.width
    if height_id:
        api_wf[height_id]["inputs"]["value"] = args.height

    if enhance_id is not None:
        api_wf[enhance_id]["inputs"]["value"] = bool(args.enhance)

    seed_val = args.seed if args.seed >= 0 else random.randint(1, 2**31 - 1)
    for nid, node in api_wf.items():
        ct = node.get("class_type")
        if ct == "KSampler":
            node["inputs"]["seed"] = seed_val
        elif ct == "KSamplerAdvanced":
            node["inputs"]["noise_seed"] = seed_val

    return api_wf, seed_val


def submit_and_wait(api_wf: dict, timeout: float = 600) -> tuple[str, dict]:
    client_id = hashlib.md5(str(time.time()).encode()).hexdigest()
    resp = http_post_json(f"{SERVER_URL}/prompt", {"prompt": api_wf, "client_id": client_id})
    prompt_id = resp.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"No prompt_id returned: {resp}")

    start = time.time()
    while time.time() - start < timeout:
        try:
            raw = http_get(f"{SERVER_URL}/history/{prompt_id}", timeout=10)
            hist = json.loads(raw)
            if prompt_id in hist:
                entry = hist[prompt_id]
                status = entry.get("status", {})
                if status.get("completed") or status.get("status_str") == "success":
                    return prompt_id, entry.get("outputs") or {}
                if status.get("status_str") == "error":
                    msgs = status.get("messages") or []
                    raise RuntimeError(f"Generation error: {json.dumps(msgs, ensure_ascii=False)[:500]}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Server unreachable during polling: {e}") from e
        time.sleep(1.5)

    raise TimeoutError(f"Generation exceeded {timeout}s")


def download_outputs(outputs: dict, out_dir: Path, basename: str) -> list[Path]:
    saved: list[Path] = []
    for node_id, node_out in outputs.items():
        for idx, img in enumerate(node_out.get("images") or []):
            params = urllib.parse.urlencode({
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            })
            url = f"{SERVER_URL}/view?{params}"
            data = http_get(url, timeout=180)

            ext = Path(img["filename"]).suffix or ".png"
            suffix = "" if len(saved) == 0 else f"_{len(saved)}"
            out_file = out_dir / f"{basename}{suffix}{ext}"
            out_file.write_bytes(data)
            saved.append(out_file)
    return saved


def cmd_generate(args) -> int:
    if args.mode not in MODES:
        eprint(f"[error] Unknown mode: {args.mode}")
        return 2
    spec = MODES[args.mode]

    if not server_health():
        eprint(f"[error] ComfyUI server not reachable at {SERVER_URL}")
        eprint(f"Start it: cd ~/ComfyUI && .venv/bin/python main.py --listen 127.0.0.1 --port 8188")
        return 3

    api_path = API_DIR / spec["api_json"]
    if not api_path.exists():
        eprint(f"[info] API workflow missing, exporting first: {api_path.name}")
        cmd_export_api(args)
    if not api_path.exists():
        eprint(f"[error] Cannot produce API workflow. Export manually via ComfyUI UI.")
        return 4

    with open(api_path) as f:
        api_wf = json.load(f)

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(exist_ok=True, parents=True)

    t0 = time.time()
    api_wf, seed = mutate_workflow(api_wf, args)

    try:
        prompt_id, outputs = submit_and_wait(api_wf, timeout=args.timeout)
    except Exception as e:
        eprint(f"[error] {e}")
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        fail = {
            "status": "failed",
            "error": str(e),
            "mode": args.mode,
            "prompt": args.prompt,
            "seed": seed,
            "duration_ms": int((time.time() - t0) * 1000),
        }
        fail_file = out_dir / f"{ts}_{args.mode}_{seed}_FAILED.json"
        fail_file.write_text(json.dumps(fail, indent=2, ensure_ascii=False))
        eprint(f"[meta] {fail_file}")
        return 5

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    basename = f"{ts}_{args.mode}_{seed}"
    saved = download_outputs(outputs, out_dir, basename)

    duration_ms = int((time.time() - t0) * 1000)
    meta = {
        "status": "success" if saved else "success_no_image",
        "mode": args.mode,
        "prompt": args.prompt,
        "enhance": bool(args.enhance),
        "seed": seed,
        "width": args.width,
        "height": args.height,
        "steps": spec["steps"],
        "cfg": spec["cfg"],
        "sampler": "euler",
        "scheduler": "simple",
        "duration_ms": duration_ms,
        "prompt_id": prompt_id,
        "images": [str(p) for p in saved],
        "comfyui_server": SERVER_URL,
        "timestamp": datetime.now().isoformat(),
    }
    meta_file = out_dir / f"{basename}.json"
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"[ok] {len(saved)} image(s) in {out_dir}")
    for p in saved:
        print(f"  {p}")
    print(f"  meta: {meta_file}")
    print(f"  seed: {seed}   duration: {duration_ms/1000:.1f}s")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="ComfyUI ERNIE-Image client")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--download-models", action="store_true")
    g.add_argument("--export-api", action="store_true")
    g.add_argument("--check-setup", action="store_true")

    p.add_argument("--mode", choices=list(MODES.keys()))
    p.add_argument("--prompt", type=str, default="")
    p.add_argument("--width", type=int, default=960)
    p.add_argument("--height", type=int, default=1280)
    p.add_argument("--seed", type=int, default=-1)
    p.add_argument("--enhance", type=lambda v: str(v).lower() in {"true", "1", "yes"}, default=True)
    p.add_argument("--out", type=str, default="./comfyui-out")
    p.add_argument("--timeout", type=float, default=600)
    p.add_argument("--include-optional", action="store_true",
                   help="--download-models 시 optional(Base·PE) 파일도 포함")
    p.add_argument("--safetensors", dest="use_gguf", action="store_false", default=True,
                   help="GGUF 대신 원본 safetensors UNETLoader 사용 (모델 파일 필요)")

    args = p.parse_args()

    if args.download_models:
        return cmd_download_models(args)
    if args.export_api:
        return cmd_export_api(args)
    if args.check_setup:
        return cmd_check_setup(args)
    if args.mode and args.prompt:
        return cmd_generate(args)

    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
