#!/usr/bin/env python3
"""Exact P53/P75 equality and arbitrary-shift witness checks for P79."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from audit_outer_codegrees import (
    graph_statistics,
    literal_hole,
    outer_fold_graph,
    positive_differences,
    sum_pair_map,
)


ROOT = Path(__file__).resolve().parents[4]
P53 = ROOT / "problems/864/compute/p53/counterexample_p25_h494.json"
P75_SOURCE = ROOT / "problems/864/fanout/wave5/P75_hard_positive_defect_folds.md"
P75_B = (
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409, 501, 505, 519,
    631, 639, 689, 715, 775, 863, 883, 915, 931, 953, 977, 987,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def endpoint_record(
    name: str, values: tuple[int, ...], h: int, b: int | None,
) -> dict[str, object]:
    translation = values[0]
    normalized = tuple(value - translation for value in values)
    sums = sum_pair_map(normalized)
    differences = positive_differences(normalized)
    graph = outer_fold_graph(normalized, translation, h, sums)
    stats = graph_statistics(graph)
    p = len(values)
    record: dict[str, object] = {
        "name": name,
        "B": list(values),
        "p": p,
        "h": h,
        "C_S": stats["C_S"],
        "two_p_minus_one": 2 * p - 1,
        "left_max_codegree": stats["left_max_codegree"],
        "right_max_codegree": stats["right_max_codegree"],
        "two_sided_max_codegree": stats["two_sided_max_codegree"],
        "maximum_codegree_witnesses": stats["codegree_witnesses"],
        "contains_K4_4": stats["contains_K4_4"],
        "K4_4_witness": stats["K4_4_witness"],
        "maximum_balanced_biclique_order": stats["balanced_biclique_order_at_least_four"],
        "maximum_balanced_biclique_witness": stats[
            "maximum_balanced_biclique_witness_at_least_four"
        ],
    }
    if b is not None:
        record["b"] = b
        record["literal_hole"] = literal_hole(sums, differences, translation, b)
    return record


def arbitrary_shift_record() -> dict[str, object]:
    values = (0, 2, 3, 8, 12)
    h = 4
    sums = sum_pair_map(values)
    collisions = [
        {
            "low_sum": low,
            "low_pair": list(sums[low]),
            "high_sum": low + h,
            "high_pair": list(sums[low + h]),
        }
        for low in sorted(sums) if low + h in sums
    ]
    return {
        "name": "arbitrary-shift counterexample",
        "B": list(values),
        "p": len(values),
        "h": h,
        "width": values[-1] - values[0],
        "unordered_sum_count": len(sums),
        "C_S": len(collisions),
        "two_p_minus_one": 2 * len(values) - 1,
        "collisions": collisions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parent / "named_witness_audit.json",
    )
    args = parser.parse_args()

    p53 = json.loads(P53.read_text(encoding="ascii"))
    p53_values = tuple(int(value) for value in p53["hypotheses"]["B"])
    p53_record = endpoint_record("P53 p=25 equality", p53_values, 494, None)
    p75_record = endpoint_record("P75 p=26 equality and literal hole", P75_B, 988, 1)
    arbitrary = arbitrary_shift_record()

    assert p53_record["C_S"] == p53_record["two_p_minus_one"] == 49
    assert p75_record["C_S"] == p75_record["two_p_minus_one"] == 51
    assert p75_record["literal_hole"] is True
    assert p75_record["two_sided_max_codegree"] == 7
    assert arbitrary["unordered_sum_count"] == 15
    assert arbitrary["C_S"] == 10 > arbitrary["two_p_minus_one"] == 9

    payload = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "records": [p53_record, p75_record, arbitrary],
        "input_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (P53, P75_SOURCE)
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        record["name"]: {
            key: record[key] for key in (
                "p", "h", "C_S", "two_p_minus_one",
                "two_sided_max_codegree", "contains_K4_4",
                "maximum_balanced_biclique_order",
            ) if key in record
        }
        for record in payload["records"]
    }, indent=2))


if __name__ == "__main__":
    main()
