#!/usr/bin/env python3
"""Sharded exact adversarial search for BC108."""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable, Sequence

from bc108_core import (
    gated_score,
    sidon_rulers_with_first,
    structure_score,
    unordered_sums,
    positive_differences,
)


ROOT = Path(__file__).resolve().parents[4]


def canonical_bytes(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def better(row: dict[str, object] | None, old: dict[str, object] | None):
    if row is None:
        return old
    if old is None:
        return row
    key = (
        int(row["bc108_residual"]), int(row["positive_color_excess"]),
        int(row["T_F"]), -int(row["p"]), -int(row["h"]), row["B"],
    )
    old_key = (
        int(old["bc108_residual"]), int(old["positive_color_excess"]),
        int(old["T_F"]), -int(old["p"]), -int(old["h"]), old["B"],
    )
    return row if key > old_key else old


def compact(row: dict[str, object], source: str) -> dict[str, object]:
    return {
        "source": source,
        "B": row["B"], "p": row["p"], "h": row["h"], "b": row.get("b"),
        "delta": row["delta"], "C_S": row["C_S"], "T_F": row["T_F"],
        "positive_color_excess": row["positive_color_excess"],
        "bc108_residual": row["bc108_residual"],
        "literal_hole": row.get("literal_hole"),
        "colors": row["colors"],
    }


def scan_translation_family(
    base: Sequence[int], source: str, digest: hashlib._Hash,
) -> dict[str, object]:
    width = base[-1]
    p = len(base)
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = baseline - width - 2
    counts = {
        "rulers": 1,
        "direct_positive_candidates": 0,
        "direct_literal_holes": 0,
        "direct_triangle_rows": 0,
        "direct_bc108_failures": 0,
        "parity_lift_candidates": 0,
        "parity_lift_positive_defect": 0,
        "parity_lift_triangle_rows": 0,
        "parity_lift_bc108_failures": 0,
    }
    worst = failure = parity_worst = parity_failure = None
    if max_gamma < 0:
        digest.update(canonical_bytes([list(base), "no-positive-translation"]))
        return {**counts, "worst": None, "failure": None,
                "parity_worst": None, "parity_failure": None}

    base_sums = tuple(unordered_sums(base))
    differences = positive_differences(base)
    for gamma in range(max_gamma + 1):
        values = tuple(gamma + value for value in base)
        h = gamma + width + 1
        holes = []
        for b in (1, 2):
            counts["direct_positive_candidates"] += 1
            hole = all(total + 2 * gamma + b not in differences for total in base_sums)
            digest.update(canonical_bytes([list(base), gamma, b, int(hole)]))
            if hole:
                holes.append(b)
                counts["direct_literal_holes"] += 1
        parity_positive = baseline - 2 * h > 0
        counts["parity_lift_candidates"] += 1
        counts["parity_lift_positive_defect"] += int(parity_positive)
        if not holes and not parity_positive:
            continue

        structure = structure_score(values, h)
        if holes and int(structure["T_F"]) > 0:
            counts["direct_triangle_rows"] += len(holes)
        for b in holes:
            row = {**structure, "b": b, "literal_hole": True}
            row = compact(row, source + f"/gamma={gamma}/b={b}")
            worst = better(row, worst)
            if int(row["bc108_residual"]) > 0:
                counts["direct_bc108_failures"] += 1
                failure = better(row, failure)

        if parity_positive:
            lifted_values = tuple(2 * value + 1 for value in values)
            lifted = structure_score(lifted_values, 2 * h)
            if int(lifted["T_F"]) > 0:
                counts["parity_lift_triangle_rows"] += 1
            lifted = compact(
                {**lifted, "b": 1, "literal_hole": True},
                source + f"/gamma={gamma}/q2-parity",
            )
            parity_worst = better(lifted, parity_worst)
            if int(lifted["bc108_residual"]) > 0:
                counts["parity_lift_bc108_failures"] += 1
                parity_failure = better(lifted, parity_failure)
    return {
        **counts,
        "worst": worst,
        "failure": failure,
        "parity_worst": parity_worst,
        "parity_failure": parity_failure,
    }


def scan_shard(task: tuple[int, int]) -> dict[str, object]:
    width, first = task
    digest = hashlib.sha256()
    totals: dict[str, int] = {}
    worst = failure = parity_worst = parity_failure = None
    for ruler in sidon_rulers_with_first(width, first):
        row = scan_translation_family(ruler, f"w={width}/first={first}", digest)
        for key, value in row.items():
            if isinstance(value, int):
                totals[key] = totals.get(key, 0) + value
        worst = better(row["worst"], worst)
        failure = better(row["failure"], failure)
        parity_worst = better(row["parity_worst"], parity_worst)
        parity_failure = better(row["parity_failure"], parity_failure)
    return {
        "width": width,
        "first_internal_mark": first,
        **totals,
        "decision_sha256": digest.hexdigest(),
        "worst": worst,
        "failure": failure,
        "parity_worst": parity_worst,
        "parity_failure": parity_failure,
    }


def aggregate(shards: Sequence[dict[str, object]]) -> dict[str, object]:
    totals: dict[str, int] = {}
    worst = failure = parity_worst = parity_failure = None
    digest = hashlib.sha256()
    for shard in sorted(shards, key=lambda row: (row["width"], row["first_internal_mark"])):
        digest.update(canonical_bytes([
            shard["width"], shard["first_internal_mark"], shard["decision_sha256"]
        ]))
        for key, value in shard.items():
            if isinstance(value, int) and key not in ("width", "first_internal_mark"):
                totals[key] = totals.get(key, 0) + value
        worst = better(shard.get("worst"), worst)
        failure = better(shard.get("failure"), failure)
        parity_worst = better(shard.get("parity_worst"), parity_worst)
        parity_failure = better(shard.get("parity_failure"), parity_failure)
    return {
        **totals,
        "aggregate_decision_sha256": digest.hexdigest(),
        "worst": worst,
        "failure": failure,
        "parity_worst": parity_worst,
        "parity_failure": parity_failure,
        "shards": list(shards),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-width", type=int, default=31)
    parser.add_argument("--max-width", type=int, default=40)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        raise ValueError("workers must be in [1,64]")
    if not 3 <= args.min_width <= args.max_width:
        raise ValueError("invalid width range")
    tasks = [
        (width, first)
        for width in range(args.min_width, args.max_width + 1)
        for first in range(0, width)
    ]
    if args.workers == 1:
        shards = [scan_shard(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            shards = list(pool.map(scan_shard, tasks, chunksize=1))
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "candidate": "sum_u max(0,t_u-n_u) <= p",
        "domain": {
            "min_width": args.min_width,
            "max_width": args.max_width,
            "orientations": "all endpoint-normalized Sidon rulers, including the two-mark ruler",
            "translations": "all gamma with direct delta>0",
            "phases": [1, 2],
            "parity_lifts": "B -> 2B+1, h -> 2h, b=1 whenever lifted delta>0",
        },
        "source_manifest": {
            "bc108_core.py": sha256_file(Path(__file__).with_name("bc108_core.py")),
            "search_bc108.py": sha256_file(Path(__file__)),
        },
        "result": aggregate(shards),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "domain": result["domain"],
        "totals": {k: v for k, v in result["result"].items() if isinstance(v, int)},
        "aggregate_decision_sha256": result["result"]["aggregate_decision_sha256"],
        "failure": result["result"]["failure"],
        "parity_failure": result["result"]["parity_failure"],
        "worst": result["result"]["worst"],
    }, indent=2))


if __name__ == "__main__":
    main()
