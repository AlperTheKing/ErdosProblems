#!/usr/bin/env python3
"""Independent exact verification of retained P98 witnesses and totals."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from component_core import audit, correction_V, score


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_row(row: dict[str, object]) -> None:
    if "delta" in row:
        fresh = audit(row["B"], int(row["h"]), int(row["b"]))
    else:
        fresh = score(row["B"], int(row["h"]))
    keys = [
        "p", "C_S", "T_F", "maximum_component_excess",
        "maximum_component_folds", "maximum_component_triangles",
    ]
    if "delta" in row:
        keys.append("delta")
    for key in keys:
        if int(fresh[key]) != int(row[key]):
            raise AssertionError((key, fresh[key], row[key]))
    if "V_b" in row:
        actual = correction_V(tuple(int(value) for value in row["B"]), int(row["h"]), int(row["b"]))
        if actual != int(row["V_b"]):
            raise AssertionError(("V_b", actual, row["V_b"]))
        excess = int(row["T_F"]) - int(row["C_S"]) - actual
        if excess != int(row["corrected_excess"]):
            raise AssertionError(("corrected_excess", excess, row["corrected_excess"]))


def walk_rows(obj: object) -> int:
    checked = 0
    if isinstance(obj, dict):
        if all(key in obj for key in ("B", "h", "b", "C_S", "T_F", "maximum_component_excess")):
            check_row(obj)
            checked += 1
        for value in obj.values():
            checked += walk_rows(value)
    elif isinstance(obj, list):
        for value in obj:
            checked += walk_rows(value)
    return checked


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = []
    checked = 0
    for path in args.inputs:
        payload = json.loads(path.read_text(encoding="ascii"))
        checked += walk_rows(payload)
        records.append({"path": str(path), "sha256": sha256(path)})
    result = {
        "status": "PASS",
        "arithmetic": "independent exact Python integer reconstruction",
        "retained_rows_checked": checked,
        "inputs": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
