#!/usr/bin/env python3
"""Replay the archived C5[3] two-row falsifier under corrected grouped flow."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import json
import os
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
SOFTCAP = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
for path in (HERE, WRITEUP, SOFTCAP):
    sys.path.insert(0, str(path))

from _codex_r20_c5_blowup_local_min_gate import (  # noqa: E402
    balanced_c5,
    rows_of,
    verify_graph,
)
import global_softcap as soft  # noqa: E402
from exchange_gate import build_metric, exchange_decomposition  # noqa: E402


T = 3
CENTER = (12, 16, 11, 1, 5, 6, 26, 18, 22)
LAYERS, INFO, FAMILIES = balanced_c5(T)
CTX = soft.make_graph_context(5 * T, INFO["Bset"], INFO["Mset"])
RADIX = T**3


def metric_tuple(state):
    metric = build_metric(
        CTX, rows_of(FAMILIES, state), p4_scope="unscoped"
    )
    return tuple(state), metric["collision"], metric["defect"], metric["flow"]


def neighborhood(center):
    states = {tuple(center)}
    for index in range(len(center)):
        for replacement in range(RADIX):
            if replacement != center[index]:
                state = list(center)
                state[index] = replacement
                states.add(tuple(state))
    for left, right in combinations(range(len(center)), 2):
        for left_replacement in range(RADIX):
            if left_replacement == center[left]:
                continue
            for right_replacement in range(RADIX):
                if right_replacement == center[right]:
                    continue
                state = list(center)
                state[left] = left_replacement
                state[right] = right_replacement
                states.add(tuple(state))
    return tuple(sorted(states))


def compact(record):
    return {
        "state": list(record[0]),
        "collisionUnits": record[1],
        "flowDefect": record[2],
        "maximumFlow": record[3],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("workers must be in 1..64")

    graph_check = verify_graph(T, LAYERS, INFO, FAMILIES)
    states = neighborhood(CENTER)
    if args.workers == 1:
        records = list(map(metric_tuple, states))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            records = list(executor.map(metric_tuple, states, chunksize=16))
    by_state = {record[0]: record for record in records}
    old = by_state[CENTER]
    descents = [
        record for record in records
        if record[0] != CENTER
        and record[1] <= old[1]
        and record[2] < old[2]
    ]
    zero_descents = [record for record in descents if record[2] == 0]
    best = min(descents, key=lambda item: (item[1], item[2], item[0])) if descents else None
    decomposition = None
    if best is not None:
        old_full = build_metric(
            CTX, rows_of(FAMILIES, CENTER), force_full=True, p4_scope="unscoped"
        )
        new_full = build_metric(
            CTX, rows_of(FAMILIES, best[0]), force_full=True, p4_scope="unscoped"
        )
        decomposition = exchange_decomposition(CTX, old_full, new_full)

    distance = lambda record: sum(x != y for x, y in zip(CENTER, record[0]))
    payload = {
        "schema": "CDC_WAVE1_C5_3_CORRECTED_EXCHANGE_V1",
        "arithmetic": "Python integers only; exact integral Dinic max flow",
        "graphCheck": graph_check,
        "center": compact(old),
        "statesExhausted": len(records),
        "distanceHistogram": dict(sorted(Counter(map(distance, records)).items())),
        "defectHistogram": dict(sorted(Counter(record[2] for record in records).items())),
        "descentCount": len(descents),
        "descentDistanceHistogram": dict(
            sorted(Counter(map(distance, descents)).items())
        ),
        "zeroDescentCount": len(zero_descents),
        "bestDescent": compact(best) if best is not None else None,
        "bestDecomposition": decomposition,
        "verdict": "EXCHANGE_EXISTS" if best is not None else "NO_TWO_ROW_EXCHANGE",
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if best is None else 0


if __name__ == "__main__":
    raise SystemExit(main())
