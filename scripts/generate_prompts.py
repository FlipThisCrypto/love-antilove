#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import PROJECT_ROOT, ensure_output_dirs, load_yaml, output_path, read_json, read_text


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


BACKGROUND_PROMPTS = {
    "Amber Wash": "Background: warm amber orange pixel gradient backdrop, simple clean collectible NFT background, no text.",
    "Apricot Glow": "Background: soft apricot orange radial glow behind the character, clean pixel backdrop, no text.",
    "Peach Pixel Mist": "Background: peach orange pixel mist with tiny square dithering, clean retro backdrop, no text.",
    "Sunset Flat": "Background: sunset orange flat dithered pixel backdrop, warm and simple, no text.",
    "Blood Orange Bloom": "Background: blood orange radial bloom, warm circular glow and darker orange corners, no text.",
    "Tangerine Sparks": "Background: tangerine orange backdrop with small pixel sparkles, collectible retro NFT background, no text.",
    "Coral Heatwave": "Background: coral orange heatwave pixel pattern with warm dithered texture, no text.",
    "Ember Halo": "Background: rare ember orange halo with subtle sunburst rays behind the character, no text.",
    "Molten Rose": "Background: rare molten rose orange and dark red pixel pattern, dramatic warm backdrop, no text.",
    "Pumpkin Eclipse": "Background: rare pumpkin orange eclipse circle with dark burnt orange outer ring, no text.",
    "Infernal Gold": "Background: epic infernal orange and gold radial rays, premium rare NFT backdrop, no text.",
    "Solar Blood Moon": "Background: legendary solar blood moon aura, deep red orange gold pixel radiance, no text.",
    "Blockchain Ember Grid": "Background: rare blockchain ember grid, orange node network and subtle chain geometry behind the character, no text.",
    "Tangerine Chainlink": "Background: rare tangerine chainlink pattern, orange blockchain links and node grid, no text.",
    "Tang Gang Flame Wall": "Background: epic Tang Gang flame wall, dark blood orange with rising orange flames and premium pixel sparks, no text.",
    "Tang Gang Crown": "Background: legendary Tang Gang crown backdrop, dark blood orange aura with golden crown geometry and flame accents, no text.",
}


def trait_sentence(record: dict) -> str:
    pieces = []
    for attr in record["attributes"]:
        if attr["trait_type"] != "Rarity":
            pieces.append(f'{attr["trait_type"]}: {attr["value"]}')
    return ", ".join(pieces)


def attr_value(record: dict, trait_type: str) -> str | None:
    for attr in record.get("attributes", []):
        if attr.get("trait_type") == trait_type:
            return attr.get("value")
    return None


def background_sentence(record: dict) -> str:
    background = attr_value(record, "Background")
    if not background:
        return "Background: warm orange pixel-art collectible backdrop, no text."
    return BACKGROUND_PROMPTS.get(background, f"Background: {background}, orange pixel-art collectible backdrop, no text.")


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
            background_sentence=background_sentence(record),
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
