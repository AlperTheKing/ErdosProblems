#!/usr/bin/env python3
"""Extract the exact C59 threshold tradeoff from a census artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def integer_cube_root(n: int) -> int:
    result = 0
    while (result + 1) ** 3 <= n:
        result += 1
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.artifact.read_text(encoding="ascii"))

    rows = []
    for shell in payload["shells"]:
        by_d = {row["D"]: row for row in shell["thresholds"]}
        sieve_d = integer_cube_root(shell["j"])
        harmonic_d = shell["j"]
        sieve = by_d[sieve_d]
        harmonic = by_d[harmonic_d]
        rows.append({
            "j": shell["j"],
            "X": shell["X"],
            "true_theta": shell["theta"],
            "capacity_over_parent": {
                "numerator": shell["actual_hole_capacity"],
                "denominator": shell["m_parent"],
            },
            "capacity_over_j_parent": {
                "numerator": shell["actual_hole_capacity"],
                "denominator": shell["j"] * shell["m_parent"],
            },
            "sieve_safe_D_floor_j_cuberoot": sieve_d,
            "sieve_safe_low_pair_hard": sieve["low_pair_hard"],
            "sieve_safe_theta_upper": sieve["finite_theta_upper"],
            "harmonic_D_j": harmonic_d,
            "harmonic_low_pair_hard": harmonic["low_pair_hard"],
            "harmonic_theta_upper": harmonic["finite_theta_upper"],
            "ap_hard_shape": shell["ap_hard_shape"],
            "ap_pairs_le_j": shell["ap_pairs_le_shell_index"],
            "ap_max_pairs": shell["ap_max_pairs"],
        })

    first_capacity_gt_j_parent = next(
        (
            {"j": row["j"], "X": row["X"]}
            for row in payload["shells"]
            if row["actual_hole_capacity"] > row["j"] * row["m_parent"]
        ),
        None,
    )
    result = {
        "schema_version": 1,
        "source": str(args.artifact),
        "sieve_safe_threshold": "floor(j^(1/3)); 1/3 < log(2)/2",
        "harmonic_threshold": "j = log_2 X",
        "first_actual_capacity_gt_j_times_parent": first_capacity_gt_j_parent,
        "rows": rows,
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=False) + "\n",
        encoding="ascii",
    )


if __name__ == "__main__":
    main()
