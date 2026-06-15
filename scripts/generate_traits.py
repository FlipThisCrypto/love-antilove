#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from collections import defaultdict

from common import (
    PROJECT_ROOT,
    alignment_for_edition,
    ensure_output_dirs,
    export_csv,
    load_yaml,
    name_for_edition,
    output_path,
    rarity_pool,
    write_json,
)


def build_attributes(traits_config: dict, rarity: str, rng: random.Random) -> list[dict[str, str]]:
    attributes = [{"trait_type": "Rarity", "value": rarity}]
    for trait_type, values in traits_config["traits"].items():
        attributes.append({"trait_type": trait_type, "value": rng.choice(values)})

    boosts = traits_config["rarity_boosts"][rarity]
    attributes.append({"trait_type": "Material", "value": rng.choice(boosts["materials"])})
    attributes.append({"trait_type": "Detail", "value": rng.choice(boosts["details"])})
    return attributes


def choose_background(rarity: str, rng: random.Random) -> str:
    backgrounds = load_yaml(PROJECT_ROOT / "config" / "backgrounds.yaml")
    tier = backgrounds["rarity_background_tiers"][rarity]
    return rng.choice(backgrounds["backgrounds"][tier])["name"]


def generate(love_count: int, antilove_count: int, seed: int, resume: bool) -> list[dict]:
    ensure_output_dirs()
    traits_path = output_path("reports", "traits.json")
    if resume and traits_path.exists():
        print(f"Resume enabled: keeping existing {traits_path}")
        return []

    rng = random.Random(seed)
    love_traits = load_yaml(PROJECT_ROOT / "config" / "traits_love.yaml")
    antilove_traits = load_yaml(PROJECT_ROOT / "config" / "traits_antilove.yaml")
    love_rarities = rarity_pool("LOVE", love_count, rng)
    antilove_rarities = rarity_pool("ANTILOVE", antilove_count, rng)

    rarity_index = defaultdict(int)
    editions = list(range(1, love_count + 1)) + list(range(445, 445 + antilove_count))
    rows = []
    for edition in editions:
        alignment = alignment_for_edition(edition)
        config = love_traits if alignment == "LOVE" else antilove_traits
        pool = love_rarities if alignment == "LOVE" else antilove_rarities
        rarity = pool[rarity_index[alignment]]
        rarity_index[alignment] += 1
        rows.append(
            {
                "edition": edition,
                "name": name_for_edition(edition),
                "alignment": alignment,
                "rarity": rarity,
                "attributes": build_attributes(config, rarity, rng)
                + [{"trait_type": "Background", "value": choose_background(rarity, rng)}],
            }
        )

    write_json(traits_path, rows)
    export_csv(output_path("reports", "traits.csv"), rows)
    print(f"Wrote {len(rows)} trait records to {traits_path}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate controlled LOVE // ANTILOVE trait records.")
    parser.add_argument("--love", type=int, default=444, help="Number of LOVE records to generate from #001.")
    parser.add_argument("--antilove", type=int, default=444, help="Number of ANTILOVE records to generate from #445.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed. Defaults to config seed.")
    parser.add_argument("--dry-run", action="store_true", help="Generate 3 LOVE and 3 ANTILOVE records.")
    parser.add_argument("--resume", action="store_true", help="Do not overwrite existing traits.json.")
    args = parser.parse_args()

    config = load_yaml(PROJECT_ROOT / "config" / "collection.yaml")
    seed = args.seed if args.seed is not None else int(config["collection"]["seed"])
    love_count = 3 if args.dry_run else args.love
    antilove_count = 3 if args.dry_run else args.antilove
    generate(love_count, antilove_count, seed, args.resume)


if __name__ == "__main__":
    main()
