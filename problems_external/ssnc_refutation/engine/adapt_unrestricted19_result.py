#!/usr/bin/env python3
"""Project an engine result/checkpoint to one strict verifier input schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence


class AdapterError(ValueError):
    pass


class DuplicateKeyError(AdapterError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def locate_candidate(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AdapterError("result root must be an object")
    if "n" in value or "out_neighbors" in value:
        candidate = value
    elif "candidate" in value:
        candidate = value["candidate"]
        if not isinstance(candidate, dict):
            raise AdapterError("candidate field must be an object")
    else:
        raise AdapterError("result contains no candidate adjacency")
    if "n" not in candidate or "out_neighbors" not in candidate:
        raise AdapterError("candidate is partial: n and out_neighbors are required")
    return candidate


def validate_rows(candidate: dict[str, object]) -> tuple[int, list[list[int]]]:
    n = candidate["n"]
    rows = candidate["out_neighbors"]
    if type(n) is not int or not (1 <= n <= 63):
        raise AdapterError("n must be an integer in [1,63]")
    if not isinstance(rows, list) or len(rows) != n:
        raise AdapterError("out_neighbors must contain exactly n rows")
    normalized: list[list[int]] = []
    for source, row in enumerate(rows):
        if not isinstance(row, list):
            raise AdapterError(f"row {source} is not a list")
        if any(type(target) is not int for target in row):
            raise AdapterError(f"row {source} has a non-integer target")
        if row != sorted(set(row)):
            raise AdapterError(f"row {source} is not sorted and unique")
        if any(not (0 <= target < n) for target in row):
            raise AdapterError(f"row {source} has an out-of-range target")
        if source in row:
            raise AdapterError(f"row {source} contains a loop")
        normalized.append(row.copy())
    row_sets = [set(row) for row in normalized]
    for a in range(n):
        for b in row_sets[a]:
            if a in row_sets[b]:
                raise AdapterError(f"digon on pair {min(a,b)},{max(a,b)}")
    return n, normalized


def adapt(value: object, target: str) -> dict[str, object]:
    candidate = locate_candidate(value)
    n, rows = validate_rows(candidate)
    if target == "legacy":
        return {"n": n, "out_neighbors": rows}
    if target == "oracle":
        return {
            "schema": "ssnc-oriented-graph-v1",
            "n": n,
            "out_neighbors": rows,
        }
    raise AdapterError(f"unknown target schema {target!r}")


def read_json(path: Path) -> object:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AdapterError("input is not UTF-8") from exc
    try:
        return json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise AdapterError("input is not one complete JSON value") from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--target", choices=("legacy", "oracle"), required=True)
    args = parser.parse_args(argv)
    try:
        value = adapt(read_json(args.input), args.target)
    except (OSError, AdapterError) as exc:
        print(json.dumps({"status": "ADAPTER_REJECT", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
