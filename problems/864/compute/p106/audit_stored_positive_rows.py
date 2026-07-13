#!/usr/bin/env python3
"""Audit RM97 on every stored positive-defect endpoint row in P98-P105."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106s = load("p106_stored_audit", ROOT / "problems/864/compute/p106/search_positive_defect_rm_falsifier.py")


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def is_sidon(values):
    sums = set()
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in sums:
                return False
            sums.add(total)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    files = []
    for number in range(98, 106):
        directory = ROOT / f"problems/864/compute/p{number}"
        if directory.exists():
            files.extend(directory.glob("*.json"))
    seen = set()
    rows = []
    for path in files:
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        for record in walk(payload):
            B, h = record.get("B"), record.get("h")
            if not isinstance(B, list) or not B or not isinstance(h, int):
                continue
            values = tuple(B)
            if values[-1] != h - 1 or not is_sidon(values):
                continue
            p = len(values)
            delta = (3 * p * p - p + 2) // 2 - h
            if delta <= 0:
                continue
            phases = (int(record["b"]),) if record.get("b") in (1, 2) else (1, 2)
            for b in phases:
                key = (values, h, b)
                if key in seen:
                    continue
                seen.add(key)
                row = p106s.audit(values, h, b)
                rows.append({
                    "source": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "p": p, "h": h, "b": b, "delta": delta,
                    **row,
                })
    failures = [row for row in rows if row["RM97_failure"]]
    closest = max(
        rows,
        key=lambda row: (
            row["intervals"] - row["matched"],
            row["intervals"] - row["slots"], row["T_F"],
        ),
        default=None,
    )
    result = {
        "json_files_scanned": len(files),
        "distinct_positive_defect_phase_rows": len(rows),
        "RM97_failures": len(failures),
        "first_failure": failures[0] if failures else None,
        "closest_row": closest,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
