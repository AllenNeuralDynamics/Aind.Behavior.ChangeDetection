"""Summarize image identities presented in a Bonsai passive DoC event log.

Usage
-----
python scripts/check_bonsai_event_log_images.py path/to/bonsai_event_log.csv --expected-count 8

This script is deliberately post hoc only: it does not change or stop the Bonsai workflow.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

IMAGE_RE = re.compile(r"([^\\/\s,;]+\.tiff)", re.IGNORECASE)


def extract_images(log_path: Path) -> list[str]:
    images: list[str] = []
    with log_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "Value" not in (reader.fieldnames or []):
            raise ValueError(
                f"Expected a Bonsai event log with a 'Value' column; "
                f"found columns: {reader.fieldnames}"
            )
        for row in reader:
            value = row.get("Value", "") or ""
            match = IMAGE_RE.search(value)
            if match:
                images.append(match.group(1))
    return images


def collapse_blocks(images: list[str]) -> list[tuple[str, int]]:
    blocks: list[tuple[str, int]] = []
    for image in images:
        if not blocks or blocks[-1][0] != image:
            blocks.append((image, 1))
        else:
            name, count = blocks[-1]
            blocks[-1] = (name, count + 1)
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event_log", type=Path, help="Path to bonsai_event_log.csv")
    parser.add_argument(
        "--expected-count",
        type=int,
        default=8,
        help="Expected number of unique image identities; use 0 to skip this check.",
    )
    parser.add_argument(
        "--expected-folder",
        type=Path,
        default=None,
        help="Optional folder containing the expected *.tiff files.",
    )
    args = parser.parse_args()

    images = extract_images(args.event_log)
    counts = Counter(images)
    unique = sorted(counts)
    blocks = collapse_blocks(images)

    print(f"Event log: {args.event_log}")
    print(f"Image presentation rows: {len(images)}")
    print(f"Unique presented images: {len(unique)}")
    print()

    if unique:
        print("Counts by image:")
        for image in unique:
            print(f"  {image}: {counts[image]}")
    else:
        print("No .tiff image presentations found in the Value column.")

    expected_names: set[str] = set()
    if args.expected_folder is not None:
        expected_names = {p.name for p in args.expected_folder.glob("*.tiff")}
    elif args.expected_count:
        # Count-only mode: no names available.
        expected_names = set()

    if expected_names:
        missing = sorted(expected_names - set(unique))
        extra = sorted(set(unique) - expected_names)
        print()
        print(f"Expected images from folder: {len(expected_names)}")
        print("Missing expected images: " + (", ".join(missing) if missing else "none"))
        print("Unexpected images: " + (", ".join(extra) if extra else "none"))

    if args.expected_count:
        print()
        if len(unique) == args.expected_count:
            print(f"PASS: found expected unique image count ({args.expected_count}).")
        else:
            print(
                f"WARNING: expected {args.expected_count} unique images, "
                f"but found {len(unique)}."
            )

    if blocks:
        print()
        print("First 20 image blocks:")
        for i, (image, n) in enumerate(blocks[:20]):
            print(f"  {i:02d}: {image} x {n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
