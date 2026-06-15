#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter
from tqdm import tqdm

from common import PROJECT_ROOT, ensure_output_dirs, load_yaml, output_path, read_json


LOVE_PALETTE = {
    "robe": (255, 217, 236, 255),
    "robe_dark": (190, 96, 162, 255),
    "trim": (255, 220, 92, 255),
    "hat": (255, 241, 247, 255),
    "staff": (221, 76, 145, 255),
    "aura": (255, 162, 203, 160),
    "line": (96, 48, 76, 255),
}

ANTILOVE_PALETTE = {
    "robe": (35, 28, 43, 255),
    "robe_dark": (10, 10, 16, 255),
    "trim": (196, 28, 91, 255),
    "hat": (20, 17, 25, 255),
    "staff": (116, 27, 92, 255),
    "aura": (139, 21, 91, 175),
    "line": (10, 8, 14, 255),
}


def prompt_sections(prompt_path: Path) -> tuple[str, str]:
    text = prompt_path.read_text(encoding="utf-8")
    positive = text.split("POSITIVE:", 1)[1].split("NEGATIVE:", 1)[0].strip()
    negative = text.split("NEGATIVE:", 1)[1].strip()
    return positive, negative


def draw_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: tuple, outline: tuple, width: int = 3) -> None:
    points = [
        (cx, cy + r),
        (cx - int(r * 1.35), cy - int(r * 0.2)),
        (cx - int(r * 0.75), cy - r),
        (cx, cy - int(r * 0.45)),
        (cx + int(r * 0.75), cy - r),
        (cx + int(r * 1.35), cy - int(r * 0.2)),
    ]
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill: tuple) -> None:
    draw.polygon([(cx, cy - r), (cx + r // 4, cy - r // 4), (cx + r, cy), (cx + r // 4, cy + r // 4), (cx, cy + r), (cx - r // 4, cy + r // 4), (cx - r, cy), (cx - r // 4, cy - r // 4)], fill=fill)


def draw_placeholder(path: Path, record: dict, size: int) -> None:
    palette = LOVE_PALETTE if record["alignment"] == "LOVE" else ANTILOVE_PALETTE
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    draw = ImageDraw.Draw(img)
    line = palette["line"]

    # Soft magical aura, similar to the transparent sample renders.
    for cx, cy, r in [(512, 500, 250), (655, 635, 165), (370, 650, 135)]:
        glow_draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=palette["aura"])
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(24)))

    # Staff with oversized heart head.
    draw.line((268, 245, 245, 830), fill=line, width=18)
    draw.line((268, 245, 245, 830), fill=palette["staff"], width=10)
    draw_heart(draw, 270, 210, 78, palette["staff"], line, 8)
    if record["alignment"] == "ANTILOVE":
        draw.line((250, 145, 292, 273), fill=line, width=7)
        for thorn_y in [355, 445, 545, 650]:
            draw.polygon([(253, thorn_y), (213, thorn_y + 28), (253, thorn_y + 18)], fill=line)

    # Familiar near the feet.
    familiar_fill = (255, 238, 244, 255) if record["alignment"] == "LOVE" else (17, 16, 23, 255)
    familiar_accent = (248, 91, 154, 255)
    draw.ellipse((166, 730, 292, 860), fill=familiar_fill, outline=line, width=8)
    draw.polygon([(180, 738), (205, 682), (230, 744)], fill=familiar_fill, outline=line)
    draw.polygon([(240, 740), (268, 684), (280, 750)], fill=familiar_fill, outline=line)
    draw.ellipse((198, 775, 214, 792), fill=line)
    draw.ellipse((244, 775, 260, 792), fill=line)
    draw_heart(draw, 232, 820, 18, familiar_accent, line, 3)

    # Wizard body and layered robe.
    skin = (248, 210, 190, 255)
    hair = (246, 210, 225, 255) if record["alignment"] == "LOVE" else (210, 186, 212, 255)
    draw.ellipse((378, 250, 650, 530), fill=hair, outline=line, width=9)
    draw.ellipse((410, 310, 618, 552), fill=skin, outline=line, width=7)
    draw.polygon([(370, 545), (653, 545), (725, 842), (301, 842)], fill=palette["robe"], outline=line)
    draw.polygon([(500, 545), (650, 842), (368, 842)], fill=palette["robe_dark"], outline=line)
    draw.polygon([(412, 560), (512, 842), (306, 842)], fill=palette["robe"], outline=line)
    draw.line((512, 560, 512, 835), fill=palette["trim"], width=13)
    draw.arc((405, 610, 620, 770), 10, 170, fill=palette["trim"], width=10)
    draw.rectangle((425, 832, 485, 902), fill=palette["robe_dark"], outline=line, width=7)
    draw.rectangle((555, 832, 615, 902), fill=palette["robe_dark"], outline=line, width=7)
    draw.ellipse((386, 886, 500, 925), fill=line)
    draw.ellipse((540, 886, 654, 925), fill=line)

    # Big sample-like hat with drooping tip.
    brim = [(284, 310), (390, 240), (570, 218), (738, 283), (645, 348), (426, 366)]
    draw.polygon(brim, fill=palette["hat"], outline=line)
    cone = [(374, 250), (508, 70), (640, 255), (570, 318), (446, 318)]
    draw.polygon(cone, fill=palette["hat"], outline=line)
    draw.line((470, 178, 568, 305), fill=palette["trim"], width=11)
    draw.arc((515, 48, 746, 265), 255, 40, fill=palette["hat"], width=42)
    draw_heart(draw, 525, 248, 34, palette["staff"], line, 5)

    # Face.
    eye = (75, 40, 72, 255) if record["alignment"] == "LOVE" else (218, 37, 100, 255)
    draw.ellipse((445, 390, 492, 450), fill=eye, outline=line, width=4)
    draw.ellipse((545, 390, 592, 450), fill=eye, outline=line, width=4)
    draw.ellipse((457, 402, 471, 419), fill=(255, 255, 255, 255))
    draw.ellipse((557, 402, 571, 419), fill=(255, 255, 255, 255))
    if record["alignment"] == "LOVE":
        draw.arc((476, 458, 562, 506), 15, 165, fill=(150, 55, 95, 255), width=5)
    else:
        draw.arc((475, 470, 560, 510), 200, 340, fill=(150, 35, 82, 255), width=5)
        draw.line((430, 382, 492, 365), fill=line, width=5)
        draw.line((545, 365, 607, 382), fill=line, width=5)

    # Textless charms, potion shapes, hearts, petals, and sample-like detail scatter.
    for cx, cy, r in [(742, 418, 28), (750, 565, 22), (342, 462, 24), (668, 185, 18)]:
        draw_heart(draw, cx, cy, r, palette["staff"], line, 4)
    for cx, cy in [(720, 760), (768, 808), (695, 866)]:
        draw.ellipse((cx - 22, cy - 30, cx + 22, cy + 30), fill=palette["staff"], outline=line, width=5)
        draw.rectangle((cx - 12, cy - 43, cx + 12, cy - 25), fill=palette["trim"], outline=line, width=4)
    for cx, cy, r in [(330, 180, 15), (755, 245, 13), (808, 500, 12), (360, 690, 10), (680, 700, 10)]:
        draw_star(draw, cx, cy, r, palette["trim"])

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
