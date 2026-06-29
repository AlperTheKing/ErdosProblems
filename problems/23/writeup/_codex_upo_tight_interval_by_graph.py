"""Per-graph positive-tight interval counts for UPO interval Hall."""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

from _h import GENG
from _codex_upo_tight_interval_stats import graph_probe


def one(g6: str):
    ctr, examples = graph_probe(g6)
    return g6, ctr.get(("tight_positive",), 0), examples[:3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--n", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    rows = []
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for g6, count, examples in ex.map(one, graphs, chunksize=args.chunksize):
                if count:
                    rows.append((g6, count, examples))
    else:
        for g6 in graphs:
            count_row = one(g6)
            if count_row[1]:
                rows.append(count_row)
    print("N", args.n, "num_graphs", len(rows), "total", sum(count for _g, count, _ex in rows))
    for g6, count, examples in rows:
        print(repr(g6), count)
        for ex in examples:
            print("  ", ex)


if __name__ == "__main__":
    main()
