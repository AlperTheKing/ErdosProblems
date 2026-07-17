#!/usr/bin/env python3
"""Exact-test complete-gate normalization at every hard cutoff."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
C34 = HERE.parent / "C34_image_dual_core"
sys.path.insert(0, str(C34))

from ground_core_lp import build_ground, solve  # noqa: E402
from lp_probe import admissible_pairs, allowed, hard_shape  # noqa: E402


INDEXED = re.compile(r"^(and_lo|and_l|and_r|or_lo)_(\d+)_(\d+)$")


def complete_rows(limit: int, selected_names: set[str]) -> tuple[set[str], dict]:
    indexed = {}
    or_hi = set()
    boundary = set()
    for name in selected_names:
        if name.startswith("q_lower_"):
            boundary.add(name)
        elif name.startswith("or_hi_"):
            or_hi.add(int(name.rsplit("_", 1)[1]))
        else:
            match = INDEXED.match(name)
            if match:
                kind, node, pair_index = match.groups()
                indexed.setdefault((int(node), int(pair_index)), set()).add(kind)

    kept = set(boundary)
    lower_count = 0
    for (node, pair_index), kinds in indexed.items():
        if "and_lo" in kinds and "or_lo" in kinds:
            kept.add(f"and_lo_{node}_{pair_index}")
            kept.add(f"or_lo_{node}_{pair_index}")
            lower_count += 1

    upper_count = 0
    for node in sorted(or_hi):
        pairs = admissible_pairs(node)
        choices = []
        for pair_index in range(len(pairs)):
            kinds = indexed.get((node, pair_index), set())
            sides = [kind for kind in ("and_l", "and_r") if kind in kinds]
            if len(sides) != 1:
                choices = []
                break
            choices.append((pair_index, sides[0]))
        if choices:
            kept.add(f"or_hi_{node}")
            kept.update(f"{side}_{node}_{pair_index}" for pair_index, side in choices)
            upper_count += 1
    return kept, {
        "boundary_count": len(boundary),
        "lower_gate_count": lower_count,
        "upper_gate_count": upper_count,
        "dropped_nonzero_row_count": len(selected_names - kept),
    }


def exact_audit(limit: int, kept: set[str]) -> dict:
    model, c_float, constant, _ = build_ground(limit)
    rows = {row.name: row for row in model.rows}
    row_coefficient = [0] * len(model.names)
    row_objective = 0
    for name in kept:
        row = rows[name]
        rhs = int(row.rhs)
        assert float(rhs) == row.rhs
        row_objective -= rhs
        for variable, coefficient_float in row.terms.items():
            coefficient = int(coefficient_float)
            assert float(coefficient) == coefficient_float
            row_coefficient[variable] -= coefficient

    dual_objective = row_objective
    bound_multipliers = {}
    for index, (name, coefficient_float) in enumerate(zip(model.names, c_float)):
        coefficient = int(coefficient_float)
        assert float(coefficient) == coefficient_float
        needed = coefficient - row_coefficient[index]
        if not needed:
            continue
        lo_float, hi_float = model.bounds[index]
        lo, hi = int(lo_float), int(hi_float)
        assert (float(lo), float(hi)) == (lo_float, hi_float)
        dual_objective += needed * (lo if needed > 0 else hi)
        bound_multipliers[name] = needed
        assert row_coefficient[index] + needed == coefficient

    required = int(constant)
    nonunit_nonground = []
    ground = set(build_ground(limit)[3]["ground"])
    for name, multiplier in bound_multipliers.items():
        if abs(multiplier) <= 1:
            continue
        if name.startswith("s_") and int(name[2:]) in ground:
            continue
        nonunit_nonground.append({"name": name, "multiplier": multiplier})
    return {
        "clean_dual_objective": dual_objective,
        "required": required,
        "passes": dual_objective >= required,
        "bound_count": len(bound_multipliers),
        "nonunit_nonground_bounds": nonunit_nonground,
    }


def test_cutoff(limit: int) -> dict:
    source = solve(limit, True)
    if source["status"] != 0:
        return {"limit": limit, "passes": False, "lp_status": source["status"]}
    nonzero = {
        row["name"]: row["dual"]
        for row in source["active_rows"]
        if abs(row["dual"]) >= 1e-8
    }
    nonunit = [
        {"name": name, "dual": dual}
        for name, dual in nonzero.items()
        if abs(dual + 1.0) > 1e-7
    ]
    if nonunit:
        return {
            "limit": limit,
            "passes": False,
            "reason": "nonunit LP row multiplier",
            "nonunit_rows": nonunit,
        }
    kept, counts = complete_rows(limit, set(nonzero))
    audit = exact_audit(limit, kept)
    return {
        "limit": limit,
        "lp_minimum": int(round(source["minimum_linear_part"])),
        **counts,
        **audit,
    }


def hard_cutoffs(stop: int) -> list[int]:
    return [
        value
        for value in range(4, stop + 1)
        if allowed(value) and hard_shape(value, admissible_pairs(value))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for cutoff in hard_cutoffs(args.stop):
        result = test_cutoff(cutoff)
        results.append(result)
        if not result.get("passes", False):
            break
    payload = {
        "schema_version": 1,
        "stop": args.stop,
        "tested": len(results),
        "all_pass": all(result.get("passes", False) for result in results),
        "first_failure": next(
            (result for result in results if not result.get("passes", False)), None
        ),
        "results": results,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "stop": args.stop,
                "tested": payload["tested"],
                "all_pass": payload["all_pass"],
                "first_failure": payload["first_failure"],
            }
        )
    )


if __name__ == "__main__":
    main()
