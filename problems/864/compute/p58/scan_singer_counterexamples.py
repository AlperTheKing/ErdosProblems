#!/usr/bin/env python3
"""Exact affine-cut scan for clean-fold Singer P58 counterexamples."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
ALGEBRAIC_SCAN = ROOT / "problems/864/compute/p12/algebraic_scan.py"


def load_algebraic_scan():
    spec = importlib.util.spec_from_file_location("p12_algebraic_scan", ALGEBRAIC_SCAN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the P12 algebraic generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def supports(values: tuple[int, ...]) -> tuple[set[int], set[int]]:
    sums = {
        left + right
        for i, left in enumerate(values)
        for right in values[i:]
    }
    differences = {left - right for left in values for right in values}
    return sums, differences


def scan(q: int) -> dict[str, object]:
    source = load_algebraic_scan()
    h, residues, metadata = source.singer(q)
    p = len(residues)
    baseline = (3 * p * p - p + 2) // 2
    seen: set[tuple[int, ...]] = set()
    holes = []

    for multiplier in source.unit_multipliers(h, None):
        transformed = tuple((multiplier * value) % h for value in residues)
        for lift, cut_base, cut_gap in source.cyclic_lifts(transformed, h):
            width = lift[-1]
            gamma = h - 1 - width
            values = tuple(gamma + value for value in lift)
            if values in seen:
                continue
            seen.add(values)

            sums, differences = supports(values)
            assert len(sums) == p * (p + 1) // 2
            assert len(differences) == p * (p - 1) + 1
            c_s = len(sums) - len({value % h for value in sums})
            c_d = len(differences) - len({value % h for value in differences})
            assert c_s == c_d == 0

            for b in (1, 2):
                if any(s + d == -b for s in sums for d in differences):
                    continue
                delta = baseline - h
                excess = max(delta - 5 * (c_s + c_d), 0)
                holes.append(
                    {
                        "multiplier": multiplier,
                        "cut_base": cut_base,
                        "cut_gap": cut_gap,
                        "B": list(values),
                        "p": p,
                        "h": h,
                        "b": b,
                        "gamma": gamma,
                        "width": width,
                        "C_S": c_s,
                        "C_D": c_d,
                        "delta": delta,
                        "positive_excess": excess,
                        "candidate_lhs": excess * excess,
                        "candidate_rhs": 4 * p**3,
                        "candidate_fails": excess * excess > 4 * p**3,
                    }
                )

    holes.sort(key=lambda row: (row["B"], row["b"]))
    return {
        "arithmetic": "exact integers",
        "family": "Singer perfect difference set",
        "q": q,
        "p": p,
        "h": h,
        "metadata": metadata,
        "unit_classes": len(source.unit_multipliers(h, None)),
        "distinct_affine_top_lifts": len(seen),
        "b_values_per_lift": 2,
        "profiles_checked": 2 * len(seen),
        "hole_count": len(holes),
        "counterexample_count": sum(row["candidate_fails"] for row in holes),
        "holes": holes,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=13)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p58/singer_q13_scan.json"),
    )
    args = parser.parse_args()
    result = scan(args.q)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {key: result[key] for key in (
                "q",
                "p",
                "h",
                "unit_classes",
                "distinct_affine_top_lifts",
                "profiles_checked",
                "hole_count",
                "counterexample_count",
            )},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
