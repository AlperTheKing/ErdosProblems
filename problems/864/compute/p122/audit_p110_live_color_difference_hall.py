#!/usr/bin/env python3
"""Exact P122 Hall audit on every live translation of the P110 seeds.

For an endpoint-normalized seed A with h_0=A[-1]+1, test
    B=A+gamma, h=h_0+gamma, 0 <= gamma < delta(A,h_0).
The literal-hole test is done with exact bitsets before reconstructing the
fold system.  The arm graph and Hall matching depend on B,h, not on b, so one
matching is evaluated for each translation that passes the b=1 or b=2 gate.
"""

from __future__ import annotations

import argparse
import hashlib
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


p122 = load(
    "p122_live_translation_audit",
    ROOT / "problems/864/compute/p122/audit_color_excess_difference_hall.py",
)


def support_masks(values: tuple[int, ...]) -> tuple[int, int]:
    sums = {left + right for index, left in enumerate(values) for right in values[index:]}
    differences = {
        right - left for index, left in enumerate(values) for right in values[index + 1 :]
    }
    return sum(1 << value for value in sums), sum(1 << value for value in differences)


def literal_hole(sum_mask: int, difference_mask: int, gamma: int, b: int) -> bool:
    """For A+gamma, test Delta+(A) intersect (A+A+2gamma+b)."""

    return (difference_mask & (sum_mask << (2 * gamma + b))) == 0


def scan(max_seeds: int | None) -> dict[str, object]:
    payload = json.loads(
        (ROOT / "problems/864/compute/p110/dimension_falsifiers.json").read_text(
            encoding="ascii"
        )
    )
    seeds = payload["failures"]
    if max_seeds is not None:
        seeds = seeds[:max_seeds]

    digest = hashlib.sha256()
    result: dict[str, object] = {
        "schema_version": 1,
        "arithmetic": "exact Python integers, bitset hole gate, augmenting-path matching",
        "source": "problems/864/compute/p110/dimension_falsifiers.json failures",
        "seeds": len(seeds),
        "positive_translations": 0,
        "b1_gate_rows": 0,
        "b2_gate_rows": 0,
        "union_gate_rows": 0,
        "matching_calls": 0,
        "positive_excess_rows": 0,
        "maximum_positive_color_excess": 0,
        "maximum_T_F": 0,
        "maximum_deficit": 0,
        "first_failure": None,
        "per_seed": [],
    }

    for seed_id, seed in enumerate(seeds):
        source = tuple(seed["B"])
        h0 = int(seed["h"])
        p = len(source)
        delta0 = (3 * p * p - p + 2) // 2 - h0
        sum_mask, difference_mask = support_masks(source)
        seed_rows = seed_b1 = seed_b2 = seed_positive = 0

        for gamma in range(delta0):
            gate_b1 = literal_hole(sum_mask, difference_mask, gamma, 1)
            gate_b2 = literal_hole(sum_mask, difference_mask, gamma, 2)
            if not (gate_b1 or gate_b2):
                continue

            values = tuple(value + gamma for value in source)
            h = h0 + gamma
            # Folds, arm arcs, and their difference labels do not use b.
            b = 1 if gate_b1 else 2
            row = p122.score(values, h, b)
            assert int(row["delta"]) > 0
            assert bool(row["literal_hole"])

            compact = (
                seed_id,
                gamma,
                gate_b1,
                gate_b2,
                row["C_S"],
                row["T_F"],
                row["positive_color_excess"],
                row["matching"],
                row["deficit"],
            )
            digest.update((repr(compact) + "\n").encode("ascii"))
            seed_rows += 1
            seed_b1 += gate_b1
            seed_b2 += gate_b2
            seed_positive += int(row["positive_color_excess"]) > 0
            result["positive_translations"] = int(result["positive_translations"]) + 1
            result["b1_gate_rows"] = int(result["b1_gate_rows"]) + gate_b1
            result["b2_gate_rows"] = int(result["b2_gate_rows"]) + gate_b2
            result["matching_calls"] = int(result["matching_calls"]) + 1
            result["positive_excess_rows"] = int(result["positive_excess_rows"]) + (
                int(row["positive_color_excess"]) > 0
            )
            result["maximum_positive_color_excess"] = max(
                int(result["maximum_positive_color_excess"]),
                int(row["positive_color_excess"]),
            )
            result["maximum_T_F"] = max(int(result["maximum_T_F"]), int(row["T_F"]))
            result["maximum_deficit"] = max(
                int(result["maximum_deficit"]), int(row["deficit"])
            )
            if int(row["deficit"]) > 0 and result["first_failure"] is None:
                result["first_failure"] = {
                    "seed_id": seed_id,
                    "gamma": gamma,
                    "gate_b1": gate_b1,
                    "gate_b2": gate_b2,
                    **row,
                }

        result["per_seed"].append(
            {
                "seed_id": seed_id,
                "p": p,
                "delta0": delta0,
                "union_gate_rows": seed_rows,
                "b1_gate_rows": seed_b1,
                "b2_gate_rows": seed_b2,
                "positive_excess_rows": seed_positive,
            }
        )

    result["decision_sha256"] = digest.hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-seeds", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = scan(args.max_seeds)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="ascii")
    print(rendered, end="")


if __name__ == "__main__":
    main()
