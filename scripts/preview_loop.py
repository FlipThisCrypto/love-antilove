#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from common import PROJECT_ROOT, output_path


def run_step(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def clean_preview_outputs() -> None:
    targets = [
        output_path("images"),
        output_path("metadata"),
        output_path("prompts"),
        output_path("reports"),
    ]
    for folder in targets:
        folder.mkdir(parents=True, exist_ok=True)
        for path in folder.iterdir():
            if path.is_file():
                path.unlink()


def sample_paths(reference_dir: Path) -> list[Path]:
    paths = []
    for index in range(1, 9):
        for extension in ("png", "jpg", "jpeg"):
            candidate = reference_dir / f"sample{index}.{extension}"
            if candidate.exists():
                paths.append(candidate)
                break
    return paths


def paste_thumb(sheet: Image.Image, path: Path, box: tuple[int, int, int, int], label: str) -> None:
    x, y, width, height = box
    tile = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    image = Image.open(path).convert("RGBA")
    image.thumbnail((width - 24, height - 54), Image.Resampling.LANCZOS)
    px = (width - image.width) // 2
    py = 12 + ((height - 54) - image.height) // 2
    tile.alpha_composite(image, (px, py))
    draw = ImageDraw.Draw(tile)
    draw.text((12, height - 32), label, fill=(0, 0, 0, 255))
    sheet.paste(tile.convert("RGB"), (x, y))


def make_contact_sheet(reference_dir: Path, iteration: int) -> Path:
    references = sample_paths(reference_dir)
    previews = sorted(output_path("images").glob("*.png"))
    columns = 4
    tile_w = 260
    tile_h = 300
    rows = ((len(references) + columns - 1) // columns) + ((len(previews) + columns - 1) // columns)
    sheet = Image.new("RGB", (columns * tile_w, max(1, rows) * tile_h), (230, 230, 230))

    for idx, path in enumerate(references):
        x = (idx % columns) * tile_w
        y = (idx // columns) * tile_h
        paste_thumb(sheet, path, (x, y, tile_w, tile_h), f"reference {path.stem}")

    offset = ((len(references) + columns - 1) // columns) * columns
    for idx, path in enumerate(previews):
        slot = offset + idx
        x = (slot % columns) * tile_w
        y = (slot // columns) * tile_h
        paste_thumb(sheet, path, (x, y, tile_w, tile_h), f"preview {path.name}")

    out_dir = output_path("reports", "preview_loop")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"iteration_{iteration:02d}_sheet.jpg"
    sheet.save(out_path, quality=95)
    return out_path


def run_iteration(iteration: int, args: argparse.Namespace) -> Path:
    clean_preview_outputs()
    seed = args.seed + iteration - 1
    run_step(
        [
            sys.executable,
            "scripts/generate_traits.py",
            "--love",
            str(args.love),
            "--antilove",
            str(args.antilove),
            "--seed",
            str(seed),
        ]
    )
    prompt_command = [sys.executable, "scripts/generate_prompts.py"]
    if args.style_preset is not None:
        prompt_command.extend(["--style-preset", args.style_preset])
    run_step(prompt_command)
    image_command = [sys.executable, "scripts/generate_images.py", "--mode", args.image_mode]
    if args.size is not None:
        image_command.extend(["--size", str(args.size)])
    if args.pixel_size is not None:
        image_command.extend(["--pixel-size", str(args.pixel_size)])
    if args.palette_colors is not None:
        image_command.extend(["--palette-colors", str(args.palette_colors)])
    run_step(image_command)
    run_step([sys.executable, "scripts/create_metadata.py"])
    run_step([sys.executable, "scripts/rarity_report.py"])
    run_step(
        [
            sys.executable,
            "scripts/validate_collection.py",
            "--expected",
            str(args.love + args.antilove),
        ]
    )
    sheet = make_contact_sheet(args.reference_dir, iteration)
    print(f"Preview sheet: {sheet}")
    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Run small visual preview batches until the style is approved.")
    parser.add_argument("--iterations", type=int, default=1, help="Number of preview batches to run.")
    parser.add_argument("--love", type=int, default=3, help="LOVE previews per iteration.")
    parser.add_argument("--antilove", type=int, default=3, help="ANTILOVE previews per iteration.")
    parser.add_argument("--seed", type=int, default=888, help="Base seed. Each iteration increments it by 1.")
    parser.add_argument("--image-mode", choices=["placeholder", "comfyui"], default="placeholder")
    parser.add_argument("--style-preset", choices=["default", "8bit", "16bit", "32bit", "64bit"], default=None)
    parser.add_argument("--size", type=int, default=None, help="Override square image size for this run.")
    parser.add_argument("--pixel-size", type=int, default=None, help="Postprocess pixel block size.")
    parser.add_argument("--palette-colors", type=int, default=None, help="Quantize final image to this many colors.")
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=PROJECT_ROOT.parent,
        help="Folder containing sample1.png through sample8.png.",
    )
    args = parser.parse_args()

    sheets = [run_iteration(iteration, args) for iteration in range(1, args.iterations + 1)]
    print("Generated preview sheets:")
    for sheet in sheets:
        print(f"- {sheet}")


if __name__ == "__main__":
    main()
