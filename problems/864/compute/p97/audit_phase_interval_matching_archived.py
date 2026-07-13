#!/usr/bin/env python3
"""Audit phase-hull matching on archived translations and insertions."""

from __future__ import annotations

import argparse
import heapq
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "problems/864/compute/p86"))
import dense_loose_search as p86


def fold_system(values, h):
    folds, _ = p86.fold_edges(values, h)
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles = []
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None not in ids and len(set(ids)) == 3:
                triangles.append(ids)
    return folds, triangles


def greedy_matches_all(intervals, slots):
    intervals = sorted(intervals)
    heap = []
    index = matched = 0
    for point in sorted(slots):
        while index < len(intervals) and intervals[index][0] <= point:
            heapq.heappush(heap, intervals[index][1]); index += 1
        if heap and heap[0] < point:
            return False
        if heap:
            heapq.heappop(heap); matched += 1
    return matched == len(intervals)


def matching_ok(values, h, b):
    folds, triangles = fold_system(values, h)
    if not triangles:
        return True, len(folds), 0
    labels = [a + c + b for a, c, _u, _v in folds]
    intervals = [
        (min(labels[i] for i in triangle), max(labels[i] for i in triangle))
        for triangle in triangles
    ]
    return greedy_matches_all(intervals, labels), len(folds), len(triangles)


def translation_worker(values):
    z = tuple(values)
    p, width = len(z), z[-1]
    baseline = (3 * p * p - p + 2) // 2
    max_gamma = min(width - 1, baseline - width - 2)
    if max_gamma < 0:
        return 0, 0, None
    sum_mask, difference_mask = p86.masks_for_ruler(z)
    holes = failures = 0
    witness = None
    for gamma in range(max_gamma + 1):
        h = width + gamma + 1
        if (sum_mask & (sum_mask >> h)).bit_count() == 0:
            continue
        for b in (1, 2):
            if ((sum_mask << (2 * gamma + b)) & difference_mask) != 0:
                continue
            holes += 1
            B = tuple(x + gamma for x in z)
            ok, folds, triangles = matching_ok(B, h, b)
            if not ok:
                failures += 1
                witness = witness or {"B": B, "h": h, "b": b, "C_S": folds, "T_F": triangles}
    return holes, failures, witness


def insertion_worker(values):
    z = tuple(values)
    p, width = len(z), z[-1]
    baseline = (3 * (p + 1) ** 2 - (p + 1) + 2) // 2
    max_g = min(width, (baseline - 1) // 2 - width)
    if max_g < 1:
        return 0, 0, None
    holes = failures = 0
    witness = None
    for g in range(1, max_g + 1):
        c_base = tuple(value + g for value in z)
        h0 = width + g
        existing = set(p86.unordered_sum_map(c_base))
        occupied = set(c_base)
        for x in range(1, h0):
            if x in occupied or not p86.insertion_is_sidon(c_base, existing, x):
                continue
            c = tuple(sorted(c_base + (x,)))
            B = tuple(2 * value - 1 for value in c)
            h = 2 * h0
            holes += 1
            ok, folds, triangles = matching_ok(B, h, 1)
            if not ok:
                failures += 1
                witness = witness or {"B": B, "h": h, "b": 1, "C_S": folds, "T_F": triangles}
    return holes, failures, witness


def run(worker, payloads, workers):
    if workers == 1:
        return [worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, payloads, chunksize=1))


def summarize(rows):
    return {
        "literal_holes": sum(row[0] for row in rows),
        "matching_failures": sum(row[1] for row in rows),
        "first_failure": next((row[2] for row in rows if row[2] is not None), None),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bases, _ = p86.load_archives()
    translations = run(translation_worker, [base.values for base in bases], args.workers)
    insertion_bases = [
        base for base in bases
        if len(base.values) <= 40 and any("/p46/" in source or "/p53/" in source for source in base.sources)
    ]
    insertions = run(insertion_worker, [base.values for base in insertion_bases], args.workers)
    result = {"translations": summarize(translations), "insertions": summarize(insertions)}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
