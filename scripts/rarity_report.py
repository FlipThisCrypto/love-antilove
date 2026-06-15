#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from common import output_path, read_json


def report() -> str:
    metadata_files = sorted(output_path("metadata").glob("*.json"))
    rarity_by_alignment = defaultdict(Counter)
    traits = defaultdict(Counter)
    for path in metadata_files:
        data = read_json(path)
        alignment = data["alignment"]
        for attr in data["attributes"]:
            if attr["trait_type"] == "Rarity":
                rarity_by_alignment[alignment][attr["value"]] += 1
            else:
                traits[(alignment, attr["trait_type"])][attr["value"]] += 1

    lines = ["# LOVE // ANTILOVE Rarity Report", ""]
    lines.append("## Rarity Counts")
    for alignment in ["LOVE", "ANTILOVE"]:
        lines.append(f"### {alignment}")
        for rarity, count in rarity_by_alignment[alignment].most_common():
            lines.append(f"- {rarity}: {count}")
        lines.append("")

    lines.append("## Trait Counts")
    for (alignment, trait_type), counts in sorted(traits.items()):
        lines.append(f"### {alignment} - {trait_type}")
        for value, count in counts.most_common():
            lines.append(f"- {value}: {count}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Markdown rarity report.")
    parser.parse_args()
    text = report()
    path = output_path("reports", "rarity_report.md")
    path.write_text(text, encoding="utf-8")
    print(f"Wrote rarity report to {path}")


if __name__ == "__main__":
    main()
