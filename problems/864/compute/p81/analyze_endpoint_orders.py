#!/usr/bin/env python3
"""Test monotone-subsequence mechanisms on the exact P79 K_5,5 witness."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "problems/864/compute/p79/outer_codegree_audit.json"
OUTPUT = ROOT / "problems/864/compute/p81/p79_k55_endpoint_orders.json"


def direction(values: Sequence[int]) -> str | None:
    if all(left < right for left, right in zip(values, values[1:])):
        return "increasing"
    if all(left > right for left, right in zip(values, values[1:])):
        return "decreasing"
    return None


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    record = data["domains"]["p20_all_translations"][
        "maximum_balanced_biclique_witness"
    ]
    witness = record["witness"]
    left = witness["left"]
    right = witness["right"]
    edges = {
        tuple(edge["edge"]): tuple(edge["inner_edge"])
        for edge in witness["edges"]
    }
    if set(edges) != set(itertools.product(left, right)):
        raise AssertionError("stored edges are not the complete product")

    matrices = {
        "inner_low": [[edges[(a, v)][0] for v in right] for a in left],
        "inner_high": [[edges[(a, v)][1] for v in right] for a in left],
    }
    result: dict[str, object] = {
        "schema_version": 1,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_id": record["source_id"],
        "left": left,
        "right": right,
        "matrices": matrices,
        "tests": {},
    }

    tests: dict[str, object] = {}
    for name, matrix in matrices.items():
        row_triples = []
        shared: dict[tuple[tuple[int, ...], str], list[int]] = {}
        for row_index, row in enumerate(matrix):
            witnesses = []
            for columns in itertools.combinations(range(len(right)), 3):
                sign = direction([row[column] for column in columns])
                if sign is None:
                    continue
                item = {
                    "columns": [right[column] for column in columns],
                    "direction": sign,
                    "values": [row[column] for column in columns],
                }
                witnesses.append(item)
                shared.setdefault((columns, sign), []).append(row_index)
            row_triples.append(
                {
                    "left_vertex": left[row_index],
                    "count": len(witnesses),
                    "witnesses": witnesses,
                }
            )
        shared_rows = [
            {
                "columns": [right[column] for column in columns],
                "direction": sign,
                "rows": [left[row] for row in rows],
            }
            for (columns, sign), rows in shared.items()
            if len(rows) >= 3
        ]

        aligned = []
        for row_indices in itertools.combinations(range(len(left)), 3):
            for column_indices in itertools.combinations(range(len(right)), 3):
                for row_sign in ("increasing", "decreasing"):
                    if not all(
                        direction([matrix[row][column] for column in column_indices])
                        == row_sign
                        for row in row_indices
                    ):
                        continue
                    for column_sign in ("increasing", "decreasing"):
                        if all(
                            direction([matrix[row][column] for row in row_indices])
                            == column_sign
                            for column in column_indices
                        ):
                            aligned.append(
                                {
                                    "rows": [left[row] for row in row_indices],
                                    "columns": [right[column] for column in column_indices],
                                    "row_direction": row_sign,
                                    "column_direction": column_sign,
                                    "values": [
                                        [matrix[row][column] for column in column_indices]
                                        for row in row_indices
                                    ],
                                }
                            )
        tests[name] = {
            "row_monotone_triples": row_triples,
            "shared_triples_on_at_least_three_rows": shared_rows,
            "aligned_3x3_count": len(aligned),
            "aligned_3x3_examples": aligned[:20],
        }

    paired_aligned = []
    low_aligned = tests["inner_low"]["aligned_3x3_examples"]
    high_aligned = tests["inner_high"]["aligned_3x3_examples"]
    high_shapes = {
        (tuple(item["rows"]), tuple(item["columns"])) for item in high_aligned
    }
    for item in low_aligned:
        shape = (tuple(item["rows"]), tuple(item["columns"]))
        if shape in high_shapes:
            paired_aligned.append(
                {"rows": list(shape[0]), "columns": list(shape[1])}
            )
    tests["same_shape_aligned_for_both_endpoints_among_first_20"] = paired_aligned
    result["tests"] = tests
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "row_triple_counts_low": [
                    row["count"] for row in tests["inner_low"]["row_monotone_triples"]
                ],
                "row_triple_counts_high": [
                    row["count"] for row in tests["inner_high"]["row_monotone_triples"]
                ],
                "shared_low": len(
                    tests["inner_low"]["shared_triples_on_at_least_three_rows"]
                ),
                "shared_high": len(
                    tests["inner_high"]["shared_triples_on_at_least_three_rows"]
                ),
                "aligned_low": tests["inner_low"]["aligned_3x3_count"],
                "aligned_high": tests["inner_high"]["aligned_3x3_count"],
                "paired_first20": len(paired_aligned),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
