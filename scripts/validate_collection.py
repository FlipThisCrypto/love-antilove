#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter

from common import output_path, read_json


REQUIRED_FIELDS = {
    "name",
    "description",
    "image",
    "edition",
    "alignment",
    "attributes",
    "collection",
    "rewards note",
}


def expected_editions(expected: int) -> list[int]:
    if expected == 888:
        return list(range(1, 889))
    love = min(expected // 2, 444)
    anti = max(0, expected - love)
    return list(range(1, love + 1)) + list(range(445, 445 + anti))


def validate(expected: int) -> list[str]:
    errors: list[str] = []
    metadata_files = sorted(output_path("metadata").glob("*.json"))
    image_files = sorted(output_path("images").glob("*.png"))
    if len(metadata_files) != expected:
        errors.append(f"Expected {expected} metadata JSON files, found {len(metadata_files)}")
    if len(image_files) != expected:
        errors.append(f"Expected {expected} image PNG files, found {len(image_files)}")

    names = []
    seen_editions = []
    for path in metadata_files:
        data = read_json(path)
        missing = REQUIRED_FIELDS - data.keys()
        if missing:
            errors.append(f"{path.name} missing fields: {', '.join(sorted(missing))}")
        edition = int(data.get("edition", -1))
        seen_editions.append(edition)
        names.append(data.get("name"))
        expected_alignment = "LOVE" if 1 <= edition <= 444 else "ANTILOVE"
        if data.get("alignment") != expected_alignment:
            errors.append(f"{path.name} has wrong alignment {data.get('alignment')} for edition {edition}")
        expected_name = f"{expected_alignment} Wizard #{edition:03d}"
        if data.get("name") != expected_name:
            errors.append(f"{path.name} has wrong name {data.get('name')} expected {expected_name}")
        if data.get("alignment") == "LOVE" and not (1 <= edition <= 444):
            errors.append(f"{path.name} LOVE edition outside 1-444")
        if data.get("alignment") == "ANTILOVE" and not (445 <= edition <= 888):
            errors.append(f"{path.name} ANTILOVE edition outside 445-888")

    duplicates = [name for name, count in Counter(names).items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate names found: {', '.join(duplicates)}")

    expected_set = set(expected_editions(expected))
    missing_editions = sorted(expected_set - set(seen_editions))
    extra_editions = sorted(set(seen_editions) - expected_set)
    if missing_editions:
        errors.append(f"Missing editions: {missing_editions[:20]}")
    if extra_editions:
        errors.append(f"Unexpected editions: {extra_editions[:20]}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate LOVE // ANTILOVE output files.")
    parser.add_argument("--expected", type=int, default=888)
    args = parser.parse_args()
    errors = validate(args.expected)
    report_path = output_path("reports", "validation.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if errors:
        report_path.write_text("FAILED\n" + "\n".join(errors) + "\n", encoding="utf-8")
        print(f"Validation failed with {len(errors)} issue(s). See {report_path}")
        raise SystemExit(1)
    report_path.write_text("PASSED\n", encoding="utf-8")
    print(f"Validation passed. See {report_path}")


if __name__ == "__main__":
    main()
