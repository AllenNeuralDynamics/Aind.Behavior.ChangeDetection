#!/usr/bin/env python
"""Parse Bonsai debug LogEvent rows from passive DoC image-loading diagnostics."""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_DEFAULT = [
    "imk00459.tiff",
    "imk00895.tiff",
    "imk00942.tiff",
    "imk01057.tiff",
    "imk01097.tiff",
    "imk01220.tiff",
    "imk01378.tiff",
    "imk01643.tiff",
]


def read_expected(folder: str | None) -> list[str]:
    if not folder:
        return EXPECTED_DEFAULT
    p = Path(folder)
    if not p.exists():
        return EXPECTED_DEFAULT
    return sorted(x.name for x in p.glob("*.tiff"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("event_log", help="Path to bonsai_event_log.csv")
    ap.add_argument("--expected-folder", default=None, help="Folder containing expected .tiff images")
    args = ap.parse_args()

    event_log = Path(args.event_log)
    expected = read_expected(args.expected_folder)

    stages = defaultdict(list)
    stage_rows = Counter()
    count_values = defaultdict(list)
    samples = {}

    dbg_pat = re.compile(r"DBG_([A-Z_]+):?\s*(.*)", re.I)
    img_pat = re.compile(r"([^\\/,\s\)]+\.tiff)", re.I)
    count_pat = re.compile(r"(-?\d+)")

    with event_log.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        text = " | ".join("" if v is None else str(v) for v in row.values())
        m = dbg_pat.search(text)
        if not m:
            continue

        stage = m.group(1).upper()
        rest = m.group(2)
        stage_rows[stage] += 1
        samples.setdefault(stage, text[:600])

        mi = img_pat.search(rest)
        if mi:
            stages[stage].append(mi.group(1))

        if stage.endswith("_COUNT"):
            mc = count_pat.search(rest)
            if mc:
                count_values[stage].append(int(mc.group(1)))

    print(f"Event log: {event_log}")
    print(f"Expected images ({len(expected)}): {', '.join(expected)}")
    print()

    all_stages = [
        "ENUM", "LOAD", "CONCAT", "SELECTED", "PERMUTE", "CLOSE",
        "ENUM_COUNT", "LOAD_COUNT", "CONCAT_COUNT", "SELECTED_COUNT",
    ]
    print("Debug stage summary:")
    for stage in all_stages:
        row_count = stage_rows[stage]
        imgs = stages.get(stage, [])
        counts = count_values.get(stage, [])
        if row_count == 0 and not imgs and not counts:
            continue

        print(f"\nDBG_{stage}")
        print(f"  debug rows: {row_count}")
        if counts:
            print(f"  count values: {counts}")
        if imgs:
            unique = sorted(set(imgs))
            missing = [x for x in expected if x not in set(imgs)]
            print(f"  image rows: {len(imgs)}")
            print(f"  unique images: {len(unique)}")
            print(f"  missing expected: {missing if missing else 'none'}")
            print(f"  first 16 images: {imgs[:16]}")
        if not imgs and not counts:
            print(f"  sample: {samples.get(stage, '')}")

    print("\nInterpretation guide:")
    print("  ENUM_COUNT=8 and LOAD_COUNT=7 -> LoadImages/input mapping is dropping one item.")
    print("  LOAD_COUNT=8 and CONCAT_COUNT=7 -> Concat/replay boundary is dropping one item.")
    print("  CONCAT_COUNT=8 and SELECTED/PERMUTE=7 -> SelectedImages/replay/scheduling boundary is dropping one item.")
    print("  PERMUTE=7 and CLOSE=7 unique -> Permutation/CloseCycle are downstream of the loss.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
