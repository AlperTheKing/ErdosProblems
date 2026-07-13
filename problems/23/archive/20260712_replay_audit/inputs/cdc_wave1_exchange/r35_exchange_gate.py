#!/usr/bin/env python3
"""Exact Hamming-two corrected exchange gate on the real R35 N24 cage."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import importlib.util
from itertools import combinations
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R35_PATH = ROOT / "tmp" / "fanout" / "r35_24_trade" / "evaluate_trade.py"
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, SOFTCAP):
    sys.path.insert(0, str(path))

import global_softcap as soft  # noqa: E402
from exchange_gate import build_metric, exchange_decomposition  # noqa: E402


def load_r35():
    spec = importlib.util.spec_from_file_location("cdc_exchange_r35", R35_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(R35_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R35 = load_r35()
CTX = soft.make_graph_context(R35.N, R35.BLUE, R35.BAD)
FAMILIES = tuple(tuple(row) for row in R35.ROW_FAMILIES)
RADICES = tuple(R35.RADICES)


def rows_for_state(state):
    return tuple(FAMILIES[index][choice] for index, choice in enumerate(state))


def metric_tuple(state):
    metric = build_metric(CTX, rows_for_state(state), p4_scope="unscoped")
    return tuple(state), metric["collision"], metric["defect"], metric["flow"]


def neighborhood(center):
    states = {tuple(center)}
    for index, radix in enumerate(RADICES):
        for replacement in range(radix):
            if replacement != center[index]:
                state = list(center)
                state[index] = replacement
                states.add(tuple(state))
    for left, right in combinations(range(len(center)), 2):
        for left_replacement in range(RADICES[left]):
            if left_replacement == center[left]:
                continue
            for right_replacement in range(RADICES[right]):
                if right_replacement == center[right]:
                    continue
                state = list(center)
                state[left] = left_replacement
                state[right] = right_replacement
                states.add(tuple(state))
    return tuple(sorted(states))


def compact(state, collision, defect, flow):
    return {
        "state": list(state),
        "collisionUnits": collision,
        "flowDefect": defect,
        "maximumFlow": flow,
    }


def analyze_center(center, workers):
    states = neighborhood(center)
    if workers == 1:
        records = list(map(metric_tuple, states))
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            records = list(executor.map(metric_tuple, states, chunksize=16))
    by_state = {record[0]: record for record in records}
    old_record = by_state[tuple(center)]
    old_collision, old_defect = old_record[1], old_record[2]
    descents = [
        record for record in records
        if record[0] != tuple(center)
        and record[1] <= old_collision
        and record[2] < old_defect
    ]
    zero_descents = [record for record in descents if record[2] == 0]
    best = min(descents, key=lambda item: (item[1], item[2], item[0])) if descents else None

    decomposition = None
    if best is not None:
        old_full = build_metric(
            CTX, rows_for_state(center), force_full=True, p4_scope="unscoped"
        )
        new_full = build_metric(
            CTX, rows_for_state(best[0]), force_full=True, p4_scope="unscoped"
        )
        decomposition = exchange_decomposition(CTX, old_full, new_full)

    distance_histogram = Counter(
        sum(x != y for x, y in zip(center, record[0])) for record in records
    )
    descent_distance_histogram = Counter(
        sum(x != y for x, y in zip(center, record[0])) for record in descents
    )
    zero_distance_histogram = Counter(
        sum(x != y for x, y in zip(center, record[0])) for record in zero_descents
    )
    defect_histogram = Counter(record[2] for record in records)
    return {
        "center": compact(*old_record),
        "statesExhausted": len(records),
        "distanceHistogram": dict(sorted(distance_histogram.items())),
        "descentDistanceHistogram": dict(sorted(descent_distance_histogram.items())),
        "zeroDescentDistanceHistogram": dict(sorted(zero_distance_histogram.items())),
        "defectHistogram": dict(sorted(defect_histogram.items())),
        "descentCount": len(descents),
        "zeroDescentCount": len(zero_descents),
        "bestDescent": compact(*best) if best is not None else None,
        "bestDecomposition": decomposition,
        "verdict": "EXCHANGE_EXISTS" if best is not None else "NO_TWO_ROW_EXCHANGE",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument(
        "--center",
        choices=("displayed", "one-row-minimum"),
        default="one-row-minimum",
    )
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("workers must be in 1..64")

    if args.center == "displayed":
        center = tuple(R35.DISPLAYED)
    else:
        center = tuple(R35.DISPLAYED)
        center = center[:9] + (0,) + center[10:]
    result = analyze_center(center, args.workers)
    payload = {
        "schema": "CDC_WAVE1_R35_HAMMING_TWO_EXCHANGE_V1",
        "arithmetic": "Python integers only; exact integral Dinic max flow",
        "order": R35.N,
        "rowFamilySizes": list(RADICES),
        "centerKind": args.center,
        "result": result,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if result["verdict"] == "NO_TWO_ROW_EXCHANGE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
