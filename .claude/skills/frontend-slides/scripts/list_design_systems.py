#!/usr/bin/env python3
"""List project design systems for the frontend-slides skill.

The script intentionally prints compact metadata so Codex can choose a design
system without loading every DESIGN.md into the context window.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


def find_project_root(start: Path) -> Path | None:
    candidates = [Path.cwd(), start, *start.parents, *Path.cwd().parents]
    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "design-systems").is_dir():
            return candidate
    return None


def read_metadata(design_file: Path) -> dict[str, str]:
    text = design_file.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    title = design_file.parent.name
    category = "Uncategorized"
    summary = ""

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            title = re.sub(r"^Design System Inspired by\s+", "", title)
            break

    for index, line in enumerate(lines[:12]):
        if line.startswith("> Category:"):
            category = line.split(":", 1)[1].strip() or category
            for follow in lines[index + 1 : index + 5]:
                if follow.startswith(">") and not follow.startswith("> Category:"):
                    summary = follow.lstrip("> ").strip()
                    break
            break

    if not summary:
        for line in lines[:24]:
            clean = line.strip().lstrip("> ").strip()
            if clean and not clean.startswith("#") and not clean.startswith("Category:"):
                summary = clean
                break

    return {
        "slug": design_file.parent.name,
        "title": title,
        "category": category,
        "summary": summary,
        "path": str(design_file),
    }


def matches(item: dict[str, str], query: str) -> bool:
    haystack = " ".join(
        item[key] for key in ("slug", "category", "title", "summary")
    ).lower()
    tokens = set(re.split(r"[^a-z0-9]+", haystack))
    terms = [term.lower() for term in re.split(r"\s+", query.strip()) if term.strip()]
    return any(term in tokens if len(term) <= 2 else term in haystack for term in terms)


def main() -> int:
    parser = argparse.ArgumentParser(description="List design-systems/*/DESIGN.md metadata.")
    parser.add_argument("--query", help="Filter by words across slug, category, title, and summary.")
    parser.add_argument("--slug", help="Print one exact design system slug.")
    parser.add_argument("--root", help="Project root containing design-systems/.")
    args = parser.parse_args()

    if args.root:
        root = Path(args.root).expanduser().resolve()
    else:
        root = find_project_root(Path(__file__).resolve())

    if root is None:
        print("ERROR: Could not find a design-systems directory from cwd or script path.", file=sys.stderr)
        return 2

    design_root = root / "design-systems"
    files = sorted(design_root.glob("*/DESIGN.md"))
    items = [read_metadata(path) for path in files]

    if args.slug:
        items = [item for item in items if item["slug"] == args.slug]
    if args.query:
        items = [item for item in items if matches(item, args.query)]

    if not items:
        print("No matching design systems found.")
        return 1

    for item in items:
        print(f"{item['slug']}\t{item['category']}\t{item['title']}\t{item['summary']}\t{item['path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
