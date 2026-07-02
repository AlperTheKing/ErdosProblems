"""Random active-5 debt/eta ratio stress for quotient seeds."""

from __future__ import annotations

import argparse
import contextlib
import io
import random
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_active_size_quotient_fast import (
        EQ,
        SIB,
        loads_for,
        side_data,
    )
    from _codex_c5lift_weighted_quotient_gate import (
        qcut_value,
        qmaxcut_value,
        sides_to_scan,
    )
    from _codex_c5rs_inspect import fmt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--samples", type=int, default=20000)
    ap.add_argument("--max-weight", type=int, default=100)
    ap.add_argument("--seed", type=int, default=230702)
    args = ap.parse_args()

    g6 = EQ if args.graph == "eq" else SIB
    rng = random.Random(args.seed)
    n = 10
    side_cache = {}
    max_ratio = None
    max_rec = None
    checked_rows = 0
    qmax_cuts = 0
    active5_rows = 0

    for _ in range(args.samples):
        weights = [rng.randint(1, args.max_weight) for _ in range(n)]
        best = qmaxcut_value(g6, weights)
        N = sum(weights)
        for side in sides_to_scan(g6):
            if qcut_value(g6, side, weights) != best:
                continue
            qmax_cuts += 1
            if side not in side_cache:
                side_cache[side] = side_data(g6, side)
            sn, _E, M, paths, rows = side_cache[side]
            m = sum(weights[a] * weights[b] for a, b in M)
            eta = F(N * N, 25) - m
            if eta <= 0:
                continue
            tau = F(5 * m, N)
            loads = loads_for(sn, M, paths, weights)
            for f, row in rows:
                if len(row) != 5:
                    continue
                checked_rows += 1
                s = [loads[v] for v in row]
                active = [i for i, x in enumerate(s) if x > tau]
                if len(active) != 5:
                    continue
                active5_rows += 1
                row_sum = sum(s, F(0))
                debt = row_sum - N
                if debt <= 0:
                    continue
                ratio = debt / eta
                if max_ratio is None or ratio > max_ratio:
                    max_ratio = ratio
                    max_rec = {
                        "weights": tuple(weights),
                        "side": side,
                        "f": f,
                        "row": tuple(row),
                        "N": N,
                        "m": m,
                        "eta": eta,
                        "tau": tau,
                        "s": tuple(s),
                        "row_sum": row_sum,
                        "debt": debt,
                        "ratio": ratio,
                    }

    print("graph", args.graph)
    print("samples", args.samples)
    print("max_weight", args.max_weight)
    print("qmax_cuts", qmax_cuts)
    print("checked_rows", checked_rows)
    print("active5_rows", active5_rows)
    print("max_ratio", None if max_ratio is None else fmt(max_ratio))
    if max_rec:
        for k, v in max_rec.items():
            if isinstance(v, F):
                v = fmt(v)
            elif isinstance(v, tuple):
                v = tuple(fmt(x) if isinstance(x, F) else x for x in v)
            print(k, v)


if __name__ == "__main__":
    main()
