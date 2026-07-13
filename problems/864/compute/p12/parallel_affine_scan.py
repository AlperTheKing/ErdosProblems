"""Parallel exact affine-cut scan for Singer reflected constructions."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path

from algebraic_scan import (
    analyze_lift,
    cyclic_lifts,
    reflected_admissibility,
    singer,
    unit_multipliers,
)


def scan_unit(task: tuple[int, tuple[int, ...], int]) -> dict[str, object]:
    modulus, residues, multiplier = task
    transformed = tuple((multiplier * x) % modulus for x in residues)
    best: dict[str, object] | None = None
    lifts = 0
    candidates = 0
    for lift, base, cut_gap in cyclic_lifts(transformed, modulus):
        lifts += 1
        record = analyze_lift(lift)
        center = record["candidate_center"]
        if center is None:
            continue
        candidates += 1
        record = {
            **record,
            "affine_multiplier": multiplier,
            "cut_base": base,
            "cut_gap": cut_gap,
            "hole_offset_above_2span": int(center) - 2 * int(record["span"]),
        }
        key = (int(center), int(record["span"]), tuple(record["points"]))
        if best is None or key < (
            int(best["candidate_center"]),
            int(best["span"]),
            tuple(best["points"]),
        ):
            best = record
    return {
        "multiplier": multiplier,
        "lifts": lifts,
        "candidates": candidates,
        "best": best,
    }


def run(parameter: int, unit_limit: int, workers: int) -> dict[str, object]:
    modulus, residues, metadata = singer(parameter)
    units = unit_multipliers(modulus, unit_limit)
    tasks = [(modulus, residues, unit) for unit in units]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        records = list(pool.map(scan_unit, tasks, chunksize=1))

    candidates = [row["best"] for row in records if row["best"] is not None]
    if not candidates:
        best = None
        check = None
    else:
        best = min(
            candidates,
            key=lambda row: (
                int(row["candidate_center"]),
                int(row["span"]),
                tuple(row["points"]),
            ),
        )
        check = reflected_admissibility(
            best["points"], int(best["candidate_center"])
        )
        if not check["admissible"]:
            raise AssertionError("literal reflected verification failed")

    return {
        "family": "singer",
        "parameter": parameter,
        "modulus": modulus,
        "residue_size": len(residues),
        "metadata": metadata,
        "workers": workers,
        "unit_limit": unit_limit,
        "unit_classes_total": len(unit_multipliers(modulus, None)),
        "unit_classes_scanned": len(units),
        "lifts_scanned": sum(int(row["lifts"]) for row in records),
        "candidate_lifts": sum(int(row["candidates"]) for row in records),
        "best_candidate": best,
        "best_candidate_check": check,
        "best_center_over_p2": (
            str(Fraction(int(best["candidate_center"]), len(residues) ** 2))
            if best is not None
            else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameter", type=int, required=True)
    parser.add_argument("--unit-limit", type=int, default=512)
    parser.add_argument("--workers", type=int, default=60)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 61:
        parser.error("--workers must be in [1,61] on Windows")

    result = run(args.parameter, args.unit_limit, args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, sort_keys=True) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "parameter": result["parameter"],
                "p": result["residue_size"],
                "units": result["unit_classes_scanned"],
                "lifts": result["lifts_scanned"],
                "candidate_lifts": result["candidate_lifts"],
                "best_center_over_p2": result["best_center_over_p2"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
