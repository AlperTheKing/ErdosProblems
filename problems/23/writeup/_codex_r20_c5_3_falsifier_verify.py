"""Independent exact verifier for the C5[3] two-row-exchange falsifier."""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations, product

from _codex_r19_global_base_census import evaluate_rows
from _codex_r20_c5_blowup_local_min_gate import (
    balanced_c5,
    rows_of,
    verify_graph,
)
from _codex_r20_two_row_exchange_gate import obligation_score


WITNESS = (12, 16, 11, 1, 5, 6, 26, 18, 22)


def best_for_subset(args):
    subset, choice = args
    t = 3
    n = 15
    _, info, families = balanced_c5(t)
    family_size = len(families[0])
    old = obligation_score(n, info, rows_of(families, choice))
    best = (old, choice)
    domains = [tuple(r for r in range(family_size) if r != choice[i]) for i in subset]
    checked = 0
    for replacements in product(*domains):
        candidate = list(choice)
        for i, replacement in zip(subset, replacements):
            candidate[i] = replacement
        candidate = tuple(candidate)
        value = obligation_score(n, info, rows_of(families, candidate))
        checked += 1
        if (value, candidate) < best:
            best = (value, candidate)
    return {
        "subset": list(subset),
        "checked": checked,
        "bestScore": best[0],
        "bestChoice": list(best[1]),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    parser.add_argument("--max-k", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 61:
        parser.error("--workers must be between 1 and 61 on Windows")
    if not 1 <= args.max_k <= len(WITNESS):
        parser.error("--max-k out of range")
    return args


def main():
    args = parse_args()
    layers, info, families = balanced_c5(3)
    graph_check = verify_graph(3, layers, info, families)
    rows = rows_of(families, WITNESS)
    score = obligation_score(15, info, rows)
    kind, _, matching_detail = evaluate_rows(
        "C5[3]-explicit", 15, info, rows, "row-reserved"
    )
    assert kind == "fail"
    by_k = {}
    first_descent_k = None
    best_descent = None
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for k in range(1, args.max_k + 1):
            jobs = [(subset, WITNESS) for subset in combinations(range(9), k)]
            results = list(pool.map(best_for_subset, jobs, chunksize=1))
            best = min(results, key=lambda r: (r["bestScore"], r["bestChoice"], r["subset"]))
            by_k[str(k)] = {
                "subsets": len(results),
                "neighborsChecked": sum(r["checked"] for r in results),
                "best": best,
            }
            if first_descent_k is None and best["bestScore"] < score:
                first_descent_k = k
                best_descent = best
    payload = {
        "graphCheck": graph_check,
        "choice": list(WITNESS),
        "rows": [list(row) for row in rows],
        "score": score,
        "matchingFailure": matching_detail,
        "byK": by_k,
        "firstDescentK": first_descent_k,
        "bestDescent": best_descent,
        "verdict": "TWO_ROW_THEOREM_FALSIFIED",
    }
    if best_descent is not None:
        payload["descentRows"] = [
            list(row) for row in rows_of(families, tuple(best_descent["bestChoice"]))
        ]
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
