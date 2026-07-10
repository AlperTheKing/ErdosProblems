"""Exact series-parallel classification of local-obstruction footprints."""

from __future__ import annotations

import json
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _claude_d3_local_obstruction import GENG, check_F
from _codex_multiflow_footprint_gate import adjacency_masks, tw2_order_cached


def classify_m(m: int, workers: int) -> dict[str, object]:
    edge_count = m - 1
    graph_count = 0
    witness_graphs: list[str] = []
    aborted = 0
    aborted_graphs: list[str] = []

    for n in range(5, edge_count + 2):
        proc = subprocess.run(
            [GENG, "-q", "-c", "-b", str(n), f"{edge_count}:{edge_count}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode not in (0, 1):
            raise RuntimeError(
                f"geng failed for n={n}, e={edge_count}: {proc.stderr.strip()}"
            )
        lines = [line for line in proc.stdout.splitlines() if line.strip()]
        graph_count += len(lines)
        if not lines:
            continue
        chunksize = max(1, len(lines) // (workers * 4) or 1)
        with Pool(workers) as pool:
            for line, (result, was_aborted, _npairs) in zip(
                lines,
                pool.imap(
                check_F, [(line,) for line in lines], chunksize=chunksize
                ),
            ):
                aborted += int(was_aborted)
                if was_aborted:
                    aborted_graphs.append(line)
                if result is not None:
                    witness_graphs.append(result[0])

    witness_graphs.sort()
    non_sp = [
        g6 for g6 in witness_graphs
        if tw2_order_cached(adjacency_masks(g6)) is None
    ]
    return {
        "m": m,
        "graphs": graph_count,
        "witnesses": len(witness_graphs),
        "seriesParallel": len(witness_graphs) - len(non_sp),
        "nonSeriesParallel": len(non_sp),
        "nonSeriesParallelG6": non_sp,
        "aborted": aborted,
        "abortedG6": sorted(aborted_graphs),
    }


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: script M [WORKERS]")
    m = int(sys.argv[1])
    workers = int(sys.argv[2]) if len(sys.argv) == 3 else 60
    if not 1 <= workers <= 60:
        raise SystemExit("Windows multiprocessing pool requires 1..60 workers")
    print(json.dumps(classify_m(m, workers), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
