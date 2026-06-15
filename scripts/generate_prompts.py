#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import PROJECT_ROOT, ensure_output_dirs, output_path, read_json, read_text


STYLE_PRESETS = {
    "default": "",
    "8bit": (
        "8-bit retro pixel art, NES and Game Boy Color inspired sprite, chunky visible pixels, "
        "very limited color palette, tile-like shading, strong black outline, simplified readable shapes, "
        "low-resolution fantasy RPG character aesthetic. "
    ),
    "16bit": (
        "16-bit retro pixel art, Super Nintendo and Sega Genesis inspired RPG sprite, visible pixels, "
        "limited but richer color palette, crisp dithering, clean outline, readable chibi fantasy details, "
        "classic JRPG character aesthetic. "
    ),
    "32bit": (
        "32-bit retro pixel art, PlayStation and Game Boy Advance era RPG sprite, visible pixel clusters, "
        "rich but controlled palette, crisp outline, more detailed shading and ornamentation, "
        "premium collectible retro fantasy character aesthetic. "
    ),
    "64bit": (
        "64-bit high-detail pixel art, late retro RPG character sprite, subtle visible pixel clusters, "
        "large controlled color palette, crisp outline, refined shading and ornate readable accessories, "
        "premium high-resolution retro fantasy collectible aesthetic. "
    ),
}


def trait_sentence(record: dict) -> str:
    pieces = []
    for attr in record["attributes"]:
        if attr["trait_type"] != "Rarity":
            pieces.append(f'{attr["trait_type"]}: {attr["value"]}')
    return ", ".join(pieces)


def rarity_sentence(record: dict) -> str:
    rarity = record["rarity"]
    if rarity == "Common":
        return "simple readable pixel details, clean silhouette"
    if rarity == "Uncommon":
        return "extra accent pixels, richer accessory detail"
    if rarity == "Rare":
        return "ornate magical accents, brighter aura treatment"
    if rarity == "Epic":
        return "dramatic aura, premium detail density, standout silhouette"
    return "mythic centerpiece quality, unique aura, strongest collectible presence"


def generate(resume: bool, style_preset: str) -> None:
    ensure_output_dirs()
    traits = read_json(output_path("reports", "traits.json"))
    love_template = read_text(PROJECT_ROOT / "prompts" / "love_prompt_template.txt")
    antilove_template = read_text(PROJECT_ROOT / "prompts" / "antilove_prompt_template.txt")
    negative = read_text(PROJECT_ROOT / "prompts" / "negative_prompt.txt")

    for record in traits:
        prompt_path = output_path("prompts", f'{record["edition"]:03d}.txt')
        if resume and prompt_path.exists():
            continue
        template = love_template if record["alignment"] == "LOVE" else antilove_template
        positive = template.format(
            trait_sentence=trait_sentence(record),
            rarity_sentence=rarity_sentence(record),
        )
        prefix = STYLE_PRESETS[style_preset]
        if prefix:
            positive = prefix + positive
        prompt_path.write_text(
            f"POSITIVE:\n{positive}\n\nNEGATIVE:\n{negative}\n",
            encoding="utf-8",
        )
    print(f"Wrote prompts for {len(traits)} records to {output_path('prompts')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate image prompts from metadata traits.")
    parser.add_argument("--resume", action="store_true", help="Skip prompt files that already exist.")
    parser.add_argument("--style-preset", choices=sorted(STYLE_PRESETS), default="default")
    args = parser.parse_args()
    generate(args.resume, args.style_preset)


if __name__ == "__main__":
    main()
