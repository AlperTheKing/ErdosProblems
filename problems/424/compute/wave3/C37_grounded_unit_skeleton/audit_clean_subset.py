#!/usr/bin/env python3
"""Audit the complete-gate subset of each exact C34 grounded dual."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
C34 = HERE.parent / "C34_image_dual_core"
sys.path.insert(0, str(C34))

from ground_core_lp import grounded_core  # noqa: E402
from lp_probe import admissible_pairs, allowed, hard_shape  # noqa: E402


ENDPOINTS = (54, 74, 186, 362, 500, 1000, 2000, 5000, 10000)
INDEXED = re.compile(r"^(and_lo|and_l|and_r|or_lo)_(\d+)_(\d+)$")


def audit(limit: int) -> dict:
    values = [value for value in range(2, limit + 1) if allowed(value)]
    pairs = {value: admissible_pairs(value) for value in values}
    ground = grounded_core(values, pairs)
    hard = {value for value in values if hard_shape(value, pairs[value])}
    cert = json.loads((C34 / f"ground_dual_{limit}.json").read_text(encoding="ascii"))

    boundary = set()
    selected = defaultdict(lambda: defaultdict(set))
    for name in cert["row_duals"]:
        if name.startswith("q_lower_"):
            boundary.add(int(name.rsplit("_", 1)[1]))
        elif name.startswith("or_hi_"):
            selected[int(name.rsplit("_", 1)[1])]["or_hi"].add(0)
        else:
            match = INDEXED.match(name)
            if match:
                kind, node, pair_index = match.groups()
                selected[int(node)][kind].add(int(pair_index))

    lower = set()
    upper = {}
    for node, kinds in selected.items():
        for pair_index in kinds["and_lo"] & kinds["or_lo"]:
            lower.add((node, pair_index))
        if not kinds["or_hi"]:
            continue
        choices = []
        complete = True
        for pair_index in range(len(pairs[node])):
            sides = []
            if pair_index in kinds["and_l"]:
                sides.append(0)
            if pair_index in kinds["and_r"]:
                sides.append(1)
            if len(sides) != 1:
                complete = False
                break
            choices.append(sides[0])
        if complete:
            upper[node] = choices

    lower_count = defaultdict(int)
    upper_count = defaultdict(int)
    for node, pair_index in lower:
        left, right = pairs[node][pair_index]
        lower_count[left] += 1
        lower_count[right] += 1
    for node, choices in upper.items():
        for pair, side in zip(pairs[node], choices):
            upper_count[pair[side]] += 1

    score = -len(lower)
    source_bounds = {}
    for value in values:
        needed = lower_count[value] - upper_count[value]
        source_bounds[value] = needed
        if value in ground:
            score += needed
        elif needed < 0:
            score += needed

    f_bounds = {}
    for value in values:
        residual = (
            int(value in hard)
            + int(value in boundary)
            - int(2 * value - 1 in boundary)
            - sum((value, pair_index) in lower for pair_index in range(len(pairs[value])))
            + int(value in upper)
        )
        f_bounds[value] = residual
        if value in (2, 3):
            score += residual
        elif pairs[value] and residual < 0:
            score += residual

    nonunit_bounds = [
        {"kind": "s", "node": node, "coefficient": coefficient}
        for node, coefficient in source_bounds.items()
        if node not in ground and abs(coefficient) > 1
    ] + [
        {"kind": "f", "node": node, "coefficient": coefficient}
        for node, coefficient in f_bounds.items()
        if abs(coefficient) > 1
    ]
    return {
        "limit": limit,
        "required": len(hard),
        "clean_subset_score": score,
        "passes": score >= len(hard),
        "boundary_count": len(boundary),
        "lower_gate_count": len(lower),
        "upper_gate_count": len(upper),
        "dropped_or_hi_count": sum(
            bool(kinds["or_hi"]) for node, kinds in selected.items() if node not in upper
        ),
        "nonunit_nonground_bounds": nonunit_bounds,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {"schema_version": 1, "results": [audit(limit) for limit in ENDPOINTS]}
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload["results"]))


if __name__ == "__main__":
    main()
