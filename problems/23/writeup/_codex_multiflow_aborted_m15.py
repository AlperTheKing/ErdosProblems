"""Resolve the four m=15 local-obstruction searches that hit the default DFS cap."""

from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _claude_d3_local_obstruction as d3
from _codex_multiflow_footprint_gate import adjacency_masks, tw2_order_cached


CASES = (
    "N?????????????}?O~o",
    "N?????????O?O?N_[N?",
    "N?????????O?O?No[F?",
    "N?????????O?O?}?C~?",
)

def init_worker() -> None:
    d3.NODE_CAP = 100_000_000


def main() -> None:
    with Pool(len(CASES), initializer=init_worker) as pool:
        results = pool.map(d3.check_F, [(g6,) for g6 in CASES])

    rows = []
    for g6, (result, aborted, npairs) in zip(CASES, results):
        witness_g6 = result[0] if result is not None else None
        rows.append({
            "g6": g6,
            "aborted": aborted,
            "distance4Pairs": npairs,
            "hasWitness": result is not None,
            "witnessSeriesParallel": (
                None if witness_g6 is None
                else tw2_order_cached(adjacency_masks(witness_g6)) is not None
            ),
        })
    assert all(not row["aborted"] for row in rows)
    print(json.dumps(rows, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
