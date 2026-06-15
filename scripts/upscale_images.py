#!/usr/bin/env python3
from __future__ import annotations

import argparse

from PIL import Image
from tqdm import tqdm

from common import output_path


def upscale(factor: int, resume: bool) -> None:
    source_dir = output_path("images")
    target_dir = output_path("images", f"upscaled_{factor}x")
    target_dir.mkdir(parents=True, exist_ok=True)
    images = sorted(source_dir.glob("*.png"))
    for image_path in tqdm(images, desc="Upscale"):
        target = target_dir / image_path.name
        if resume and target.exists():
            continue
        with Image.open(image_path) as img:
            resized = img.resize((img.width * factor, img.height * factor), Image.Resampling.NEAREST)
            resized.save(target)
    print(f"Upscaled {len(images)} images into {target_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Nearest-neighbor upscale for pixel art PNGs.")
    parser.add_argument("--factor", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    upscale(args.factor, args.resume)


if __name__ == "__main__":
    main()
