"""Exact graph-derived M-exchange gate for active-scoped obligation score."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WRITEUP = ROOT / "problems" / "23" / "writeup"
sys.path.insert(0, str(WRITEUP))

from _codex_r19_global_base_census import dec, graph6_for_orders, loads
from _codex_r20_two_row_exchange_gate import shortest_row_families
from _codex_r23_outside_attachment_full_obligation_gate import (
    active_scoped_obligation_score,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(info, rows) -> int:
    return active_scoped_obligation_score(
        info["n"], set(info["Bset"]), set(info["Mset"]), rows
    )


def first_falsifier(min_n: int, max_n: int):
    stats = {"graphs": 0, "eligible": 0, "tuples": 0, "axiomTests": 0}
    for n in range(min_n, max_n + 1):
        for g6 in graph6_for_orders(n, n)[0]:
            stats["graphs"] += 1
            nv, edges = dec(g6)
            info = loads(nv, edges)
            if info is None or any(ell != 5 for ell in info["ell"].values()):
                continue
            families = shortest_row_families(info)
            if not families or all(len(f) == 1 for f in families):
                continue
            stats["eligible"] += 1
            choices = list(itertools.product(*(range(len(f)) for f in families)))
            rows = {
                c: tuple(families[i][c[i]] for i in range(len(families)))
                for c in choices
            }
            values = {c: score(info, rows[c]) for c in choices}
            stats["tuples"] += len(choices)
            # Partition-base M-convex exchange: choose u in supp(x)\supp(y).
            # Its block forces the unique v in supp(y)\supp(x), hence swap i.
            for x_index, x in enumerate(choices):
                for y in choices[x_index + 1:]:
                    for i in range(len(families)):
                        if x[i] == y[i]:
                            continue
                        xs = x[:i] + (y[i],) + x[i + 1:]
                        ys = y[:i] + (x[i],) + y[i + 1:]
                        lhs = values[x] + values[y]
                        rhs = values[xs] + values[ys]
                        stats["axiomTests"] += 1
                        if lhs < rhs:
                            return stats, {
                                "n": n, "g6": g6, "edges": sorted(map(list, edges)),
                                "familySizes": list(map(len, families)), "coordinate": i,
                                "x": list(x), "y": list(y), "xSwap": list(xs),
                                "ySwap": list(ys), "scores": {
                                    "x": values[x], "y": values[y],
                                    "xSwap": values[xs], "ySwap": values[ys],
                                    "lhs": lhs, "rhs": rhs,
                                },
                                "rows": {k: [list(r) for r in rows[v]] for k, v in
                                         [("x", x), ("y", y), ("xSwap", xs), ("ySwap", ys)]},
                            }
    return stats, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    stats, falsifier = first_falsifier(args.min_n, args.max_n)
    payload = {"exactInteger": True, "stats": stats, "falsifier": falsifier}
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
