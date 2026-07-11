"""Exact sharded canonical-minimum Hall gate for one graph6 instance.

The graph and row families are initialized once per worker.  Mixed-radix
row choices are split into bounded chunks.  Pass one finds the exact minimum
obligation score; pass two checks every minimizing tuple with the corrected
active-scoped owner flow.  This removes the per-graph serialization exposed
by the order-12 preflight.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor

from _codex_r19_global_base_census import dec, loads
from _codex_r20_two_row_exchange_gate import obligation_score, shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_score,
    full_owner_flow,
)

_G6 = None
_N = None
_INFO = None
_FAMILIES = None
_SIZES = None
_SCORE_MODE = None


def initialize(g6, score_mode="global"):
    global _G6, _N, _INFO, _FAMILIES, _SIZES, _SCORE_MODE
    _G6 = g6
    _N, edges = dec(g6)
    _INFO = loads(_N, edges)
    if _INFO is None or any(length != 5 for length in _INFO["ell"].values()):
        raise ValueError("graph is not an eligible all-ell=5 instance")
    _FAMILIES = shortest_row_families(_INFO)
    _SIZES = tuple(len(family) for family in _FAMILIES)
    _SCORE_MODE = score_mode


def score_of(rows):
    if _SCORE_MODE == "global":
        return obligation_score(_N, _INFO, rows)
    return active_scoped_obligation_score(
        _N, set(_INFO["Bset"]), set(_INFO["Mset"]), rows
    )


def choice_at(index):
    values = [0] * len(_SIZES)
    for position in range(len(_SIZES) - 1, -1, -1):
        values[position] = index % _SIZES[position]
        index //= _SIZES[position]
    assert index == 0
    return tuple(values)


def rows_at(index):
    choice = choice_at(index)
    return choice, tuple(_FAMILIES[i][choice[i]] for i in range(len(choice)))


def score_chunk(bounds):
    start, stop = bounds
    minimum = None
    count = 0
    for index in range(start, stop):
        _, rows = rows_at(index)
        score = score_of(rows)
        if minimum is None or score < minimum:
            minimum = score
            count = 1
        elif score == minimum:
            count += 1
    return minimum, count


def flow_chunk(task):
    start, stop, minimum = task
    minimizing = 0
    failures = 0
    first = None
    for index in range(start, stop):
        choice, rows = rows_at(index)
        if score_of(rows) != minimum:
            continue
        minimizing += 1
        if _SCORE_MODE == "scoped" and minimum == 0:
            continue
        record = full_owner_flow(
            _N, set(_INFO["Bset"]), set(_INFO["Mset"]), rows, _G6,
            require_full=False, quiet=True, scope="active", include_outside=False,
        )
        if not record["full"]:
            failures += 1
            if first is None:
                first = {
                    "index": index, "choice": choice,
                    "rows": rows, "flow": record,
                }
    return minimizing, failures, first


def chunks(total, size):
    return [(start, min(total, start + size)) for start in range(0, total, size)]


def positive(value):
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("g6")
    parser.add_argument("--workers", type=positive, default=min(61, os.cpu_count() or 1))
    parser.add_argument("--chunk", type=positive, default=256)
    parser.add_argument("--score-mode", choices=("global", "scoped"), default="global")
    args = parser.parse_args()
    if args.workers > 61:
        parser.error("Windows ProcessPoolExecutor supports at most 61 workers")

    initialize(args.g6, args.score_mode)
    total = math.prod(_SIZES)
    bounds = chunks(total, args.chunk)
    with ProcessPoolExecutor(
        max_workers=args.workers, initializer=initialize,
        initargs=(args.g6, args.score_mode),
    ) as pool:
        score_rows = list(pool.map(score_chunk, bounds, chunksize=1))
        minimum = min(value for value, _ in score_rows)
        minimizing_from_scores = sum(count for value, count in score_rows if value == minimum)
        flow_rows = list(pool.map(
            flow_chunk, ((a, b, minimum) for a, b in bounds), chunksize=1
        ))
    minimizing = sum(row[0] for row in flow_rows)
    failures = sum(row[1] for row in flow_rows)
    first = next((row[2] for row in flow_rows if row[2] is not None), None)
    assert minimizing == minimizing_from_scores
    payload = {
        "g6": args.g6, "order": _N, "workers": args.workers,
        "familySizes": _SIZES, "tuples": total, "minimumScore": minimum,
        "scoreMode": args.score_mode,
        "minimizingTuples": minimizing, "failingMinimizers": failures,
        "firstFailure": first,
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
