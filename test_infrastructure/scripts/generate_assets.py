#!/usr/bin/env python3
"""Создаёт локальные тестовые модели, изображения и файлы одинакового размера."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "test_assets"
MODELS = ASSETS / "models"
BACKGROUNDS = ASSETS / "backgrounds"
SCREENSAVERS = ASSETS / "screensavers"
DOWNLOADS = ASSETS / "downloads"
MANIFESTS = ASSETS / "manifests"

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415408d763f8cfc000000301010018dd8db00000000049454e44ae426082"
)


def svg(name: str, color: str, label: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <rect width="640" height="360" fill="{color}"/>
  <text x="40" y="190" fill="#0f172a" font-size="42" font-family="sans-serif">{label}</text>
</svg>
"""


MODELS_DATA = [
    {
        "id": "pulse-circle",
        "name": "Pulse Circle",
        "type": "css",
        "shape": "circle",
        "previewColor": "#38BDF8",
        "stageBackground": "#0EA5E9",
        "use3d": False,
    },
    {
        "id": "rotate-square",
        "name": "Rotate Square",
        "type": "css",
        "shape": "square",
        "previewColor": "#A78BFA",
        "stageBackground": "#7C3AED",
        "use3d": False,
    },
    {
        "id": "slide-square",
        "name": "Slide Square",
        "type": "css",
        "shape": "square",
        "previewColor": "#34D399",
        "stageBackground": "#10B981",
        "use3d": False,
    },
    {
        "id": "fade-circle",
        "name": "Fade Circle",
        "type": "css",
        "shape": "circle",
        "previewColor": "#FBBF24",
        "stageBackground": "#F59E0B",
        "use3d": False,
    },
    {
        "id": "bounce-square",
        "name": "Bounce Square",
        "type": "css",
        "shape": "square",
        "previewColor": "#F472B6",
        "stageBackground": "#DB2777",
        "use3d": False,
    },
    {
        "id": "cube-3d",
        "name": "CSS Cube",
        "type": "css",
        "shape": "cube",
        "previewColor": "#22D3EE",
        "stageBackground": "#1D4ED8",
        "use3d": True,
    },
]


BACKGROUNDS_DATA = [
    {"id": "sunset-orange", "name": "Sunset Orange", "tags": ["sunset", "orange", "warm"], "file": "sunset-orange.svg"},
    {"id": "sunset-beach", "name": "Sunset Beach", "tags": ["sunset", "beach"], "file": "sunset-beach.svg"},
    {"id": "aurora-green", "name": "Aurora Green", "tags": ["aurora", "night"], "file": "aurora-green.svg"},
    {"id": "broken-bg", "name": "Broken Background", "tags": ["broken"], "file": "broken.svg"},
    {"id": "missing-bg", "name": "Missing Background", "tags": ["missing"], "file": "does-not-exist.svg"},
]

SCREENSAVERS_DATA = [
    {"id": "aurora-stars", "name": "Aurora Stars", "tags": ["aurora", "night", "stars"], "file": "aurora-stars.svg"},
    {"id": "sunset-stars", "name": "Sunset Stars", "tags": ["sunset", "night"], "file": "sunset-stars.svg"},
    {"id": "broken-saver", "name": "Broken Saver", "tags": ["broken"], "file": "broken-saver.svg"},
    {"id": "missing-saver", "name": "Missing Saver", "tags": ["missing"], "file": "does-not-exist.svg"},
]


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for folder in (MODELS, BACKGROUNDS, SCREENSAVERS, DOWNLOADS, MANIFESTS):
        folder.mkdir(parents=True, exist_ok=True)

    for model in MODELS_DATA:
        write_json(MODELS / f"{model['id']}.json", model)
    write_json(MANIFESTS / "models.json", MODELS_DATA)

    backgrounds = []
    for item in BACKGROUNDS_DATA:
        if item["file"] == "broken.svg":
            (BACKGROUNDS / item["file"]).write_text("NOT_AN_IMAGE", encoding="utf-8")
        elif item["id"] != "missing-bg":
            (BACKGROUNDS / item["file"]).write_text(svg(item["id"], "#fb923c", item["name"]), encoding="utf-8")
        backgrounds.append(
            {
                "id": item["id"],
                "name": item["name"],
                "tags": item["tags"],
                "url": f"/test_assets/backgrounds/{item['file']}",
            }
        )
    write_json(MANIFESTS / "backgrounds.json", backgrounds)

    savers = []
    for item in SCREENSAVERS_DATA:
        if item["file"] == "broken-saver.svg":
            (SCREENSAVERS / item["file"]).write_text("NOT_AN_IMAGE", encoding="utf-8")
        elif item["id"] != "missing-saver":
            (SCREENSAVERS / item["file"]).write_text(svg(item["id"], "#38bdf8", item["name"]), encoding="utf-8")
        savers.append(
            {
                "id": item["id"],
                "name": item["name"],
                "tags": item["tags"],
                "url": f"/test_assets/screensavers/{item['file']}",
            }
        )
    write_json(MANIFESTS / "screensavers.json", savers)

    chunk = b"MOTION-PLAYGROUND-DOWNLOAD"
    payload = (chunk * ((256 * 1024 // len(chunk)) + 1))[: 256 * 1024]
    for name in ("payload.bin", "payload-copy.bin"):
        (DOWNLOADS / name).write_bytes(payload)
    (DOWNLOADS / "tiny.png").write_bytes(PNG_1X1)
    print(f"Assets generated in {ASSETS}")


if __name__ == "__main__":
    main()
