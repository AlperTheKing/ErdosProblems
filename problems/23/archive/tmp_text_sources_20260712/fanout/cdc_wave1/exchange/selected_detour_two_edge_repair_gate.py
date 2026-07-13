#!/usr/bin/env python3
"""Exact two-blue-edge repair hunt for the selected-detour fork core."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, SOFTCAP):
    sys.path.insert(0, str(path))

import global_softcap as soft
from selected_detour_closure_gate import (
    evaluate_rows,
    global_c5_payload,
    triangle_free,
)
from selected_detour_repair_gate import cut_sides, crosses
from unit_detour_core_gate import build_graph, edge


def task_record(task):
    n, blue, bad, bad_pair, repairs, max_row_product = task
    repaired_blue = frozenset(set(blue) | set(repairs))
    row_data = evaluate_rows(n, repaired_blue, bad, max_row_product)
    if not row_data.get("allEll5"):
        return {"status": "notEll5"}
    if row_data.get("status") != "EXHAUSTED":
        return {
            "status": "rowLimit",
            "badPair": list(bad_pair),
            "repairs": [list(item) for item in repairs],
            "rows": row_data,
        }
    lex_defect = row_data["lexMinimum"][1]
    c5 = None
    if lex_defect > 0:
        c5 = global_c5_payload(n, repaired_blue, bad, 1)
    return {
        "status": "exhausted",
        "badPair": list(bad_pair),
        "repairs": [list(item) for item in repairs],
        "rows": row_data,
        "globalC5": c5,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(32, os.cpu_count() or 1))
    parser.add_argument("--max-row-product", type=int, default=2_000_000)
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("workers must be in 1..64")

    n, blue, base_bad, protection = build_graph(6)
    windows = tuple(
        edge(path[i], path[i + 4])
        for path in protection
        for i in range(len(path) - 4)
    )
    sides = cut_sides(n, blue)
    nonedges = tuple(
        edge(x, y)
        for x in range(n)
        for y in range(x + 1, n)
        if sides[x] != sides[y]
        and edge(x, y) not in blue
        and edge(x, y) not in base_bad
        and edge(x, y) not in windows
    )

    tasks = []
    pair_audits = []
    raw_pairs = 0
    cut_repaired = 0
    triangle_free_count = 0
    for i, j in combinations(range(len(windows)), 2):
        bad = frozenset(set(base_bad) | {windows[i], windows[j]})
        ctx = soft.make_graph_context(n, blue, bad)
        sigma = tuple(ctx.sigma(mask) for mask in range(1 << (n - 1)))
        if min(sigma) != -1:
            raise AssertionError((i, j, min(sigma)))
        local_cut = 0
        local_tf = 0
        for repairs in combinations(nonedges, 2):
            raw_pairs += 1
            if any(
                value + int(crosses(mask, repairs[0])) +
                    int(crosses(mask, repairs[1])) < 0
                for mask, value in enumerate(sigma)
            ):
                continue
            cut_repaired += 1
            local_cut += 1
            repaired_blue = frozenset(set(blue) | set(repairs))
            if not triangle_free(n, repaired_blue, bad):
                continue
            triangle_free_count += 1
            local_tf += 1
            tasks.append(
                (n, blue, bad, (i, j), repairs, args.max_row_product)
            )
        pair_audits.append(
            {
                "badPair": [i, j],
                "rawRepairPairs": math.comb(len(nonedges), 2),
                "cutRepairPairs": local_cut,
                "triangleFreeCutRepairs": local_tf,
            }
        )

    if args.workers == 1:
        records = list(map(task_record, tasks))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            records = list(pool.map(task_record, tasks, chunksize=1))

    counts = {
        "windowPairs": math.comb(len(windows), 2),
        "nonedgeCandidates": len(nonedges),
        "rawRepairPairs": raw_pairs,
        "cutRepairPairs": cut_repaired,
        "triangleFreeCutRepairs": triangle_free_count,
        "allEll5Repairs": sum(
            r["status"] in ("exhausted", "rowLimit") for r in records
        ),
        "rowProductsExhausted": sum(r["status"] == "exhausted" for r in records),
        "rowProductLimits": sum(r["status"] == "rowLimit" for r in records),
        "positiveLexDefect": sum(
            r["status"] == "exhausted" and r["rows"]["lexMinimum"][1] > 0
            for r in records
        ),
        "positiveLexDefectWithoutGlobalC5": sum(
            r["status"] == "exhausted"
            and r["rows"]["lexMinimum"][1] > 0
            and r["globalC5"]["classes"] is None
            for r in records
        ),
    }
    payload = {
        "schema": "SELECTED_DETOUR_TWO_EDGE_REPAIR_V1",
        "arithmetic": (
            "integer exhaustive switch table; exact shortest-row enumeration; "
            "exact Dinic grouped flow; integer CP-SAT globalC5 only on positive defects"
        ),
        "n": n,
        "windows": windows,
        "pairAudits": pair_audits,
        "counts": counts,
        "records": records,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if counts["positiveLexDefectWithoutGlobalC5"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
