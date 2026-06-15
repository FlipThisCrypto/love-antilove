#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw
from tqdm import tqdm

from common import PROJECT_ROOT, ensure_output_dirs, load_yaml, output_path, read_json


LOVE_PALETTE = {
    "robe": (255, 214, 232, 255),
    "trim": (255, 220, 92, 255),
    "hat": (255, 245, 248, 255),
    "staff": (255, 116, 176, 255),
    "aura": (255, 162, 203, 160),
}

ANTILOVE_PALETTE = {
    "robe": (45, 30, 60, 255),
    "trim": (180, 32, 74, 255),
    "hat": (18, 18, 26, 255),
    "staff": (128, 36, 160, 255),
    "aura": (94, 38, 140, 170),
}


def prompt_sections(prompt_path: Path) -> tuple[str, str]:
    text = prompt_path.read_text(encoding="utf-8")
    positive = text.split("POSITIVE:", 1)[1].split("NEGATIVE:", 1)[0].strip()
    negative = text.split("NEGATIVE:", 1)[1].strip()
    return positive, negative


def draw_placeholder(path: Path, record: dict, size: int) -> None:
    palette = LOVE_PALETTE if record["alignment"] == "LOVE" else ANTILOVE_PALETTE
    scale = size // 128
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def rect(coords, color):
        draw.rectangle([v * scale for v in coords], fill=color)

    # Pixel-sprite placeholder: centered, full-body, transparent background.
    rect((46, 23, 82, 35), palette["hat"])
    rect((39, 35, 89, 42), palette["hat"])
    rect((52, 42, 76, 66), (255, 220, 185, 255))
    rect((49, 66, 79, 98), palette["robe"])
    rect((43, 74, 51, 93), palette["robe"])
    rect((77, 74, 85, 93), palette["robe"])
    rect((52, 98, 62, 112), palette["robe"])
    rect((66, 98, 76, 112), palette["robe"])
    rect((49, 66, 79, 72), palette["trim"])
    rect((62, 66, 66, 98), palette["trim"])
    rect((86, 45, 90, 102), palette["staff"])
    rect((82, 42, 94, 54), palette["staff"])
    if record["alignment"] == "LOVE":
        rect((57, 52, 61, 56), (80, 30, 55, 255))
        rect((69, 52, 73, 56), (80, 30, 55, 255))
        rect((60, 58, 70, 62), (190, 75, 115, 255))
        rect((25, 48, 31, 54), palette["aura"])
        rect((96, 68, 104, 76), palette["aura"])
    else:
        rect((56, 52, 61, 56), (230, 230, 240, 255))
        rect((70, 52, 75, 56), (230, 230, 240, 255))
        rect((60, 60, 72, 63), (150, 30, 70, 255))
        rect((24, 46, 34, 56), palette["aura"])
        rect((94, 67, 106, 79), palette["aura"])

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def queue_comfy(prompt: str, negative: str, seed: int, output_prefix: str, size: int) -> None:
    config = load_yaml(PROJECT_ROOT / "config" / "collection.yaml")
    workflow_path = PROJECT_ROOT / config["generation"]["comfyui_workflow"]
    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))["api_workflow"]
    packed = json.dumps(workflow)
    packed = packed.replace('"POSITIVE_PROMPT"', json.dumps(prompt))
    packed = packed.replace('"NEGATIVE_PROMPT"', json.dumps(negative))
    packed = packed.replace('"SEED"', str(seed))
    packed = packed.replace('"WIDTH"', str(size))
    packed = packed.replace('"HEIGHT"', str(size))
    packed = packed.replace('"OUTPUT_PREFIX"', json.dumps(output_prefix))
    payload = {"prompt": json.loads(packed)}
    response = requests.post(f'{config["generation"]["comfyui_url"]}/prompt', json=payload, timeout=30)
    response.raise_for_status()


def generate(mode: str, resume: bool) -> None:
    ensure_output_dirs()
    config = load_yaml(PROJECT_ROOT / "config" / "collection.yaml")
    size = int(config["generation"]["image_size"])
    traits = read_json(output_path("reports", "traits.json"))

    for record in tqdm(traits, desc="Images"):
        edition = int(record["edition"])
        image_path = output_path("images", f"{edition:03d}.png")
        if resume and image_path.exists():
            continue
        prompt_path = output_path("prompts", f"{edition:03d}.txt")
        positive, negative = prompt_sections(prompt_path)
        if mode == "placeholder":
            draw_placeholder(image_path, record, size)
        elif mode == "comfyui":
            output_prefix = f"love_antilove/{edition:03d}"
            queue_comfy(positive, negative, edition + int(config["collection"]["seed"]), output_prefix, size)
            print(f"Queued ComfyUI job for {edition:03d}. Copy final PNG into {image_path}")
            time.sleep(0.15)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
    print(f"Image step complete. Mode: {mode}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or queue NFT images.")
    parser.add_argument("--mode", choices=["placeholder", "comfyui"], default="placeholder")
    parser.add_argument("--resume", action="store_true", help="Skip images that already exist.")
    args = parser.parse_args()
    generate(args.mode, args.resume)


if __name__ == "__main__":
    main()
