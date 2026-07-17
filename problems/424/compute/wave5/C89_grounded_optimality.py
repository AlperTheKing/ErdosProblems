#!/usr/bin/env python3
"""Compare every C23 image optimum with the grounded fixed point."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
C78_PATH = ROOT / "problems/424/compute/wave5/C78_minimal_image_audit.py"
SPEC = importlib.util.spec_from_file_location("c78", C78_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load C78")
C78 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C78)


def scan(stop: int, workers: int, seconds: float) -> dict:
    rows = []
    first_difference = None
    equality_count = 0
    for cutoff in range(2, stop + 1):
        if not C78.allowed(cutoff) or not C78.hard_shape(cutoff):
            continue
        pairs = {
            value: C78.admissible_pairs(value)
            for value in range(2, cutoff + 1)
            if C78.allowed(value)
        }
        grounded = C78.grounded_set(cutoff, pairs)
        hard, boundary = C78.hard_holes_and_boundaries(
            grounded, cutoff, pairs
        )
        grounded_excess = len(hard) - len(boundary)
        optimum = C78.optimize_transition_variant(
            cutoff, "image", workers, seconds
        )
        if optimum["status"] != "OPTIMAL":
            raise RuntimeError((cutoff, optimum["status"]))
        maximum_excess = int(optimum["objective_violation"])
        row = {
            "cutoff": cutoff,
            "maximum_image_excess": maximum_excess,
            "grounded_excess": grounded_excess,
            "grounded_is_optimal": maximum_excess == grounded_excess,
        }
        rows.append(row)
        if row["grounded_is_optimal"]:
            equality_count += 1
        elif first_difference is None:
            first_difference = row
    return {
        "stop": stop,
        "tested_hard_cutoffs": len(rows),
        "grounded_optimal_count": equality_count,
        "first_difference": first_difference,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop", type=int, default=1000)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    result = scan(args.stop, args.workers, args.seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"tested={result['tested_hard_cutoffs']} "
        f"grounded_optimal={result['grounded_optimal_count']} "
        f"first_difference={result['first_difference']}"
    )


if __name__ == "__main__":
    main()
