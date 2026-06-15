#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import PROJECT_ROOT, ensure_output_dirs, export_csv, load_yaml, output_path, read_json, write_json


def create(resume: bool) -> None:
    ensure_output_dirs()
    config = load_yaml(PROJECT_ROOT / "config" / "collection.yaml")
    collection = config["collection"]
    traits = read_json(output_path("reports", "traits.json"))
    metadata_rows = []

    for record in traits:
        edition = int(record["edition"])
        metadata_path = output_path("metadata", f"{edition:03d}.json")
        if resume and metadata_path.exists():
            metadata_rows.append(read_json(metadata_path))
            continue
        description = (
            collection["description_love"]
            if record["alignment"] == "LOVE"
            else collection["description_antilove"]
        )
        metadata = {
            "name": record["name"],
            "description": description,
            "image": f'{collection["image_base_uri"]}/{edition:03d}{collection["image_extension"]}',
            "edition": edition,
            "alignment": record["alignment"],
            "attributes": record["attributes"],
            "collection": collection["name"],
            "rewards note": collection["rewards_note"],
        }
        write_json(metadata_path, metadata)
        metadata_rows.append(metadata)

    export_csv(output_path("reports", "collection.csv"), metadata_rows)
    print(f"Wrote {len(metadata_rows)} metadata files and CSV export.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create NFT metadata JSON and CSV export.")
    parser.add_argument("--resume", action="store_true", help="Skip metadata files that already exist.")
    args = parser.parse_args()
    create(args.resume)


if __name__ == "__main__":
    main()
