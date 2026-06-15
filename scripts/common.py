from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def output_path(*parts: str) -> Path:
    config = load_yaml(PROJECT_ROOT / "config" / "collection.yaml")
    return PROJECT_ROOT / config["generation"]["output_root"] / Path(*parts)


def ensure_output_dirs() -> None:
    for folder in ["images", "metadata", "prompts", "reports"]:
        output_path(folder).mkdir(parents=True, exist_ok=True)


def alignment_for_edition(edition: int) -> str:
    return "LOVE" if edition <= 444 else "ANTILOVE"


def name_for_edition(edition: int) -> str:
    alignment = alignment_for_edition(edition)
    return f"{alignment} Wizard #{edition:03d}"


def edition_range(limit: int | None = None, love: int | None = None, antilove: int | None = None) -> list[int]:
    if love is not None or antilove is not None:
        love_count = 444 if love is None else love
        antilove_count = 444 if antilove is None else antilove
        return list(range(1, love_count + 1)) + list(range(445, 445 + antilove_count))
    if limit is None:
        return list(range(1, 889))
    love_count = min(limit, 444)
    remaining = max(0, limit - love_count)
    return list(range(1, love_count + 1)) + list(range(445, 445 + min(remaining, 444)))


def rarity_pool(alignment: str, limit: int | None = None, rng: random.Random | None = None) -> list[str]:
    rng = rng or random.Random()
    rarity = load_yaml(PROJECT_ROOT / "config" / "rarity.yaml")
    pool: list[str] = []
    for tier in rarity["rarity_order"]:
        pool.extend([tier] * int(rarity["rarity_counts"][alignment][tier]))
    if limit is not None:
        pool = pool[:limit]
    rng.shuffle(pool)
    return pool


def export_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    trait_keys = sorted({attr["trait_type"] for row in rows for attr in row["attributes"]})
    fieldnames = ["edition", "name", "alignment", "rarity"] + trait_keys
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            rarity = row.get("rarity")
            if rarity is None:
                rarity = next(
                    (
                        attr["value"]
                        for attr in row["attributes"]
                        if attr["trait_type"] == "Rarity"
                    ),
                    "",
                )
            flat = {
                "edition": row["edition"],
                "name": row["name"],
                "alignment": row["alignment"],
                "rarity": rarity,
            }
            for attr in row["attributes"]:
                flat[attr["trait_type"]] = attr["value"]
            writer.writerow(flat)
