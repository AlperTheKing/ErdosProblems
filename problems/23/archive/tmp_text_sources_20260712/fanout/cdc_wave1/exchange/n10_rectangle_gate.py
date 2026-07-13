#!/usr/bin/env python3
"""Exact catalogue of the N10 corrected exchanges that genuinely need two rows."""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, WRITEUP, SOFTCAP):
    sys.path.insert(0, str(path))

from _codex_r19_global_base_census import dec, loads  # noqa: E402
from _codex_r20_two_row_exchange_gate import shortest_row_families  # noqa: E402
import global_softcap as soft  # noqa: E402
from exchange_gate import (  # noqa: E402
    build_metric,
    exchange_decomposition,
    one_neighbors,
    rows_for_choice,
    two_neighbors,
)


G6 = "I?rFf_{N?"


def columns_preserved(families, old, new):
    changed = [index for index in range(len(old)) if old[index] != new[index]]
    if len(changed) != 2:
        return False
    left, right = changed
    old_left = families[left][old[left]]
    old_right = families[right][old[right]]
    new_left = families[left][new[left]]
    new_right = families[right][new[right]]
    return all(
        sorted((old_left[position], old_right[position]))
        == sorted((new_left[position], new_right[position]))
        for position in range(5)
    )


def main():
    n, edges = dec(G6)
    info = loads(n, edges)
    if info is None:
        raise AssertionError("missing canonical cut")
    families = shortest_row_families(info)
    sizes = tuple(len(family) for family in families)
    choices = tuple(product(*(range(size) for size in sizes)))
    ctx = soft.make_graph_context(n, info["Bset"], info["Mset"])
    metrics = {
        choice: build_metric(
            ctx, rows_for_choice(families, choice), p4_scope="unscoped"
        )
        for choice in choices
    }

    two_only = []
    rectangle_count = 0
    first = None
    for old in choices:
        old_metric = metrics[old]
        if old_metric["defect"] == 0:
            continue
        one = [
            new for new in one_neighbors(old, sizes)
            if metrics[new]["collision"] <= old_metric["collision"]
            and metrics[new]["defect"] < old_metric["defect"]
        ]
        if one:
            continue
        candidates = [
            new for new in two_neighbors(old, sizes)
            if metrics[new]["collision"] <= old_metric["collision"]
            and metrics[new]["defect"] < old_metric["defect"]
        ]
        if not candidates:
            raise AssertionError(("no two-row descent", old))
        rectangles = [new for new in candidates if columns_preserved(families, old, new)]
        two_only.append(old)
        rectangle_count += bool(rectangles)
        if first is None and rectangles:
            new = min(
                rectangles,
                key=lambda choice: (
                    metrics[choice]["collision"], metrics[choice]["defect"], choice
                ),
            )
            old_full = build_metric(
                ctx,
                rows_for_choice(families, old),
                force_full=True,
                p4_scope="unscoped",
            )
            new_full = build_metric(
                ctx,
                rows_for_choice(families, new),
                force_full=True,
                p4_scope="unscoped",
            )
            first = {
                "oldChoice": list(old),
                "newChoice": list(new),
                "oldRows": [list(row) for row in rows_for_choice(families, old)],
                "newRows": [list(row) for row in rows_for_choice(families, new)],
                "oldCollisionUnits": old_metric["collision"],
                "newCollisionUnits": metrics[new]["collision"],
                "oldDefect": old_metric["defect"],
                "newDefect": metrics[new]["defect"],
                "decomposition": exchange_decomposition(ctx, old_full, new_full),
            }

    payload = {
        "schema": "CDC_WAVE1_N10_RECTANGLE_EXCHANGE_V1",
        "arithmetic": "Python integers only; exact integral Dinic max flow",
        "graph6": G6,
        "rowFamilySizes": list(sizes),
        "tuples": len(choices),
        "twoRowOnlyFailures": len(two_only),
        "withColumnPreservedRectangle": rectangle_count,
        "firstRectangle": first,
        "verdict": (
            "ALL_TWO_ROW_ONLY_HAVE_RECTANGLE"
            if rectangle_count == len(two_only)
            else "RECTANGLE_INCOMPLETE"
        ),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if rectangle_count == len(two_only) else 1


if __name__ == "__main__":
    raise SystemExit(main())
