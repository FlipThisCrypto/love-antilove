#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from common import PROJECT_ROOT, output_path


PRESETS = {
    "8bit": {"pixel_size": 10, "palette_colors": 32},
    "16bit": {"pixel_size": 6, "palette_colors": 96},
    "32bit": {"pixel_size": 4, "palette_colors": 192},
    "64bit": {"pixel_size": 3, "palette_colors": 256},
}


def run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def copy_outputs(preset: str) -> None:
    target_root = output_path("variants", preset)
    if target_root.exists():
        shutil.rmtree(target_root)
    for folder in ["images", "metadata", "prompts", "reports"]:
        source = output_path(folder)
        target = target_root / folder
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate 8-bit, 16-bit, 32-bit, and 64-bit 512px preview variants.")
    parser.add_argument("--love", type=int, default=3)
    parser.add_argument("--antilove", type=int, default=3)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=900)
    parser.add_argument("--image-mode", choices=["placeholder", "comfyui"], default="comfyui")
    parser.add_argument("--background-mode", choices=["composite", "prompt"], default="composite")
    parser.add_argument("--presets", nargs="+", choices=sorted(PRESETS), default=["8bit", "16bit", "32bit"])
    args = parser.parse_args()

    for index, preset in enumerate(args.presets):
        settings = PRESETS[preset]
        run(
            [
                sys.executable,
                "scripts/preview_loop.py",
                "--iterations",
                "1",
                "--love",
                str(args.love),
                "--antilove",
                str(args.antilove),
                "--image-mode",
                args.image_mode,
                "--size",
                str(args.size),
                "--pixel-size",
                str(settings["pixel_size"]),
                "--palette-colors",
                str(settings["palette_colors"]),
                "--style-preset",
                preset,
                "--background-mode",
                args.background_mode,
                "--seed",
                str(args.seed + index),
            ]
        )
        copy_outputs(preset)
        print(f"Saved {preset} outputs to {output_path('variants', preset)}")


if __name__ == "__main__":
    main()
