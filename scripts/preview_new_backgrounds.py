#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw

from common import PROJECT_ROOT
from generate_images import (
    draw_background,
    load_background_style,
    pixelate_image,
    remove_corner_background,
)


STYLE_NAMES = [
    "Blockchain Ember Grid",
    "Tangerine Chainlink",
    "Tang Gang Flame Wall",
    "Tang Gang Crown",
]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def latest_raw_for_edition(edition: int) -> Path:
    output_dir = PROJECT_ROOT.parent / "ComfyUI" / "output" / "love_antilove"
    matches = sorted(
        output_dir.glob(f"{edition:03d}_*.png"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError(f"No ComfyUI raw output found for edition {edition:03d}")
    return matches[0]


def apply_style(raw_path: Path, style_name: str, target: Path, pixel_size: int, palette_colors: int) -> None:
    style = load_background_style(style_name)
    if not style:
        raise ValueError(f"Unknown background style: {style_name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw_path.read_bytes())
    remove_corner_background(target)
    character = Image.open(target).convert("RGBA")
    background = draw_background(style, character.width)
    background.alpha_composite(character)
    background.putalpha(255)
    background.save(target)
    pixelate_image(target, pixel_size, palette_colors)


def make_sheet(paths: list[tuple[str, Path]], output_path: Path) -> None:
    cols = 4
    tile_w, tile_h = 280, 330
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tile_w, rows * tile_h), (232, 232, 232))
    for idx, (label, path) in enumerate(paths):
        tile = Image.new("RGBA", (tile_w, tile_h), (255, 255, 255, 255))
        image = Image.open(path).convert("RGBA")
        image.thumbnail((tile_w - 20, tile_h - 58), Image.Resampling.NEAREST)
        tile.alpha_composite(image, ((tile_w - image.width) // 2, 10 + (tile_h - 58 - image.height) // 2))
        draw = ImageDraw.Draw(tile)
        draw.text((12, tile_h - 38), label, fill=(0, 0, 0, 255))
        sheet.paste(tile.convert("RGB"), ((idx % cols) * tile_w, (idx // cols) * tile_h))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview new blockchain and Tang Gang background styles.")
    parser.add_argument("--editions", nargs="+", type=int, default=[1, 2, 445, 446])
    parser.add_argument("--pixel-size", type=int, default=3)
    parser.add_argument("--palette-colors", type=int, default=256)
    args = parser.parse_args()

    output_root = PROJECT_ROOT / "outputs" / "background_previews"
    rendered: list[tuple[str, Path]] = []
    for style_name, edition in zip(STYLE_NAMES, args.editions):
        raw = latest_raw_for_edition(edition)
        target = output_root / slug(style_name) / f"{edition:03d}.png"
        apply_style(raw, style_name, target, args.pixel_size, args.palette_colors)
        rendered.append((f"{style_name} #{edition:03d}", target))
        print(target)

    sheet = PROJECT_ROOT / "outputs" / "reports" / "new_background_preview_sheet.jpg"
    make_sheet(rendered, sheet)
    print(sheet)


if __name__ == "__main__":
    main()
