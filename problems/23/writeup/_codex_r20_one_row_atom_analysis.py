"""Classify strict one-row descents in the R20 collision-matching gate."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from _codex_r19_global_base_census import dec, evaluate_rows, graph6_for_orders, loads
from _codex_r20_two_row_atom_analysis import score_detail
from _codex_r20_two_row_exchange_gate import shortest_row_families


def contiguous(indices):
    return not indices or indices == tuple(range(indices[0], indices[-1] + 1))


def analyze_graph(g6):
    n, graph_edges = dec(g6)
    info = loads(n, graph_edges)
    if info is None or any(length != 5 for length in info["ell"].values()):
        return None
    families = shortest_row_families(info)
    sizes = tuple(map(len, families))
    choices = list(product(*(range(size) for size in sizes)))
    scores = {}
    failures = []
    for choice in choices:
        rows = tuple(families[i][choice[i]] for i in range(len(choice)))
        scores[choice] = score_detail(n, info, rows)
        kind, _, _ = evaluate_rows(g6, n, info, rows, "row-reserved")
        if kind == "fail":
            failures.append(choice)

    counts = Counter()
    signatures = Counter()
    examples = {}
    for choice in failures:
        old_score = scores[choice]
        descents = []
        for index, size in enumerate(sizes):
            old_row = families[index][choice[index]]
            for replacement in range(size):
                if replacement == choice[index]:
                    continue
                neighbor = choice[:index] + (replacement,) + choice[index + 1:]
                new_score = scores[neighbor]
                if new_score[0] >= old_score[0]:
                    continue
                new_row = families[index][replacement]
                changed = tuple(i for i in range(5) if old_row[i] != new_row[i])
                is_contiguous = contiguous(changed)
                is_monotone = (
                    new_score[1] <= old_score[1]
                    and new_score[2] <= old_score[2]
                )
                descents.append((
                    is_contiguous,
                    is_monotone,
                    changed,
                    new_score[1] - old_score[1],
                    new_score[2] - old_score[2],
                    index,
                    replacement,
                ))
        if not descents:
            counts["noOneRowDescent"] += 1
            continue
        counts["oneRowDescent"] += 1
        flags = {
            "hasContiguous": any(d[0] for d in descents),
            "hasMonotone": any(d[1] for d in descents),
            "hasContiguousMonotone": any(d[0] and d[1] for d in descents),
        }
        counts.update(key for key, value in flags.items() if value)
        preferred = [d for d in descents if d[0] and d[1]] or descents
        best = min(preferred, key=lambda d: (2 * d[3] + 2 * d[4], len(d[2]), d))
        signature = (
            ("changedPositions", best[2]),
            ("collisionDelta", best[3]),
            ("activeDelta", best[4]),
            ("contiguous", best[0]),
            ("monotone", best[1]),
        )
        signatures[signature] += 1
        examples.setdefault(signature, {
            "g6": g6,
            "choice": choice,
            "rowIndex": best[5],
            "replacement": best[6],
        })
    if not failures:
        return None
    return counts, signatures, examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-order", type=int, default=5)
    parser.add_argument("--max-order", type=int, default=11)
    parser.add_argument("--workers", type=int, default=min(61, os.cpu_count() or 1))
    args = parser.parse_args()
    if not (1 <= args.workers <= 61):
        parser.error("--workers must be between 1 and 61 on Windows")
    graph6, generated = graph6_for_orders(args.min_order, args.max_order)
    counts = Counter()
    signatures = Counter()
    examples = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(analyze_graph, graph6, chunksize=8):
            if result is None:
                continue
            local_counts, local_signatures, local_examples = result
            counts.update(local_counts)
            signatures.update(local_signatures)
            for signature, example in local_examples.items():
                examples.setdefault(signature, example)
    rendered = []
    for signature, count in signatures.most_common():
        item = dict(signature)
        item["count"] = count
        item["example"] = examples[signature]
        rendered.append(item)
    print(json.dumps({
        "orders": [args.min_order, args.max_order],
        "workers": args.workers,
        "generatedByOrder": generated,
        "counts": dict(sorted(counts.items())),
        "signatureCount": len(signatures),
        "signatures": rendered,
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
