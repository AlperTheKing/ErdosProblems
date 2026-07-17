#!/usr/bin/env python3
"""Exact replay of C113 boundary-prefix token inequalities."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def weight(q: int, j: int) -> int:
    root = math.isqrt(q)
    return min(root if root * root == q else root + 1, j)


def update_failure(current, condition: bool, row: dict[str, object]):
    return row if current is None and condition else current


def run(payload: dict[str, object]) -> dict[str, object]:
    bins: dict[int, list[dict[str, int]]] = {}
    for raw in payload["vulnerable_boundary_certificates"]:
        row = {key: int(raw[key]) for key in ("root", "j", "q", "source", "endpoint")}
        bins.setdefault(row["j"], []).append(row)
    failures = {"moving_sqrt": None, "linear": None, "full_cap": None}
    minimum_sqrt_slack = None
    cap_violable_prefixes = 0
    tested_prefixes = 0
    for j, roots in sorted(bins.items()):
        roots.sort(key=lambda row: row["root"])
        sqrt_prefix = linear_prefix = cap_prefix = 0
        for index, row in enumerate(roots):
            if index == 0:
                continue
            tested_prefixes += 1
            sqrt_prefix += weight(row["q"], j)
            linear_prefix += row["q"]
            cap_prefix += j
            rhs = row["root"] - (1 << j)
            common = {
                "X": int(payload["limit"]),
                "j": j,
                "root": row["root"],
                "index": index + 1,
                "rhs": rhs,
            }
            failures["moving_sqrt"] = update_failure(
                failures["moving_sqrt"], sqrt_prefix > rhs, {**common, "lhs": sqrt_prefix}
            )
            failures["linear"] = update_failure(
                failures["linear"], linear_prefix > rhs, {**common, "lhs": linear_prefix}
            )
            failures["full_cap"] = update_failure(
                failures["full_cap"], cap_prefix > rhs, {**common, "lhs": cap_prefix}
            )
            cap_violable_prefixes += cap_prefix > rhs
            slack_row = {**common, "lhs": sqrt_prefix, "slack": rhs - sqrt_prefix}
            if minimum_sqrt_slack is None or slack_row["slack"] < minimum_sqrt_slack["slack"]:
                minimum_sqrt_slack = slack_row
    return {
        "schema": "C113-boundary-prefix-replay-v1",
        "arithmetic": "exact integers only",
        "input_schema": payload["schema"],
        "limit": int(payload["limit"]),
        "boundary_certificates": sum(len(rows) for rows in bins.values()),
        "bins": len(bins),
        "tested_nontrivial_prefixes": tested_prefixes,
        "first_failures": failures,
        "minimum_moving_sqrt_slack": minimum_sqrt_slack,
        "full_cap_violable_boundary_prefixes": cap_violable_prefixes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    payload = run(json.loads(raw))
    payload["input_sha256"] = hashlib.sha256(raw).hexdigest()
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("ascii")
    args.output.write_bytes(encoded)
    print(hashlib.sha256(encoded).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
