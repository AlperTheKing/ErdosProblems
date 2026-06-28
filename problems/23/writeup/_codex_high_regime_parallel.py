from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
import time
from fractions import Fraction as F

from _h import GENG, dec, loads
from _schur_spec import pf_exact


def check_graph(g6: str):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return ("skip", g6, None)

    P, M, ell, n = pf_exact(info)
    if not M:
        return ("skip", g6, None)

    K = [[F(0)] * n for _ in range(n)]
    for pd in P:
        items = list(pd.items())
        for va, pa in items:
            for vb, pb in items:
                K[va][vb] += pa * pb

    T = [sum(K[v][w] for w in range(n)) for v in range(n)]
    O = [v for v in range(n) if T[v] > n]
    if not O:
        return ("skip", g6, None)

    Q = [v for v in range(n) if T[v] <= n]
    u = {q: F(n) - T[q] for q in Q}
    W = {q: sum(K[q][q2] * u[q2] for q2 in Q) for q in Q}

    rows = []
    for o in O:
        S = sum(P[fi].get(o, F(0)) for fi in range(len(M)))
        one = sum(K[o][q] * u[q] for q in Q) / F(n)
        two = sum(K[o][q] * W[q] for q in Q) / F(n * n)
        deficit = T[o] - n
        margin = one + two - deficit
        k1_gap = deficit - one
        high = T[o] + 4 * S > 2 * n
        surplus_unit = (T[o] + 4 * S - 2 * n) / F(n)
        rows.append(
            dict(
                o=o,
                S=S,
                T=T[o],
                margin=margin,
                k1_gap=k1_gap,
                two=two,
                surplus_unit=surplus_unit,
                gap_margin=surplus_unit - k1_gap,
                two_margin=two - surplus_unit,
                high=high,
            )
        )

    high_rows = [r for r in rows if r["high"]]
    low_rows = [r for r in rows if not r["high"]]
    worst_high = min(high_rows, key=lambda r: r["margin"]) if high_rows else None
    worst_k1_high = max(high_rows, key=lambda r: r["k1_gap"]) if high_rows else None
    worst_gap_margin = min(high_rows, key=lambda r: r["gap_margin"]) if high_rows else None
    worst_two_margin = min(high_rows, key=lambda r: r["two_margin"]) if high_rows else None
    worst_low = min(low_rows, key=lambda r: r["margin"]) if low_rows else None
    return (
        "ok",
        g6,
        dict(
            n=n,
            total=len(rows),
            high=len(high_rows),
            low=len(low_rows),
            worst_high=worst_high,
            worst_k1_high=worst_k1_high,
            worst_gap_margin=worst_gap_margin,
            worst_two_margin=worst_two_margin,
            worst_low=worst_low,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("--workers", type=int, default=60)
    parser.add_argument("--chunksize", type=int, default=32)
    args = parser.parse_args()

    graphs = subprocess.run(
        [GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True
    ).stdout.split()

    t0 = time.time()
    graph_count = skip = 0
    total_o = high_o = low_o = 0
    worst_high = None
    worst_low = None
    worst_k1_high = None
    worst_gap_margin = None
    worst_two_margin = None

    with mp.Pool(processes=args.workers) as pool:
        for done, (status, g6, data) in enumerate(
            pool.imap_unordered(check_graph, graphs, chunksize=args.chunksize), 1
        ):
            if status == "skip":
                skip += 1
            else:
                graph_count += 1
                total_o += data["total"]
                high_o += data["high"]
                low_o += data["low"]
                if data["worst_high"] is not None:
                    wh = data["worst_high"]
                    if worst_high is None or wh["margin"] < worst_high[0]:
                        worst_high = (wh["margin"], g6, wh)
                if data["worst_k1_high"] is not None:
                    wk = data["worst_k1_high"]
                    if worst_k1_high is None or wk["k1_gap"] > worst_k1_high[0]:
                        worst_k1_high = (wk["k1_gap"], g6, wk)
                if data["worst_gap_margin"] is not None:
                    wg = data["worst_gap_margin"]
                    if worst_gap_margin is None or wg["gap_margin"] < worst_gap_margin[0]:
                        worst_gap_margin = (wg["gap_margin"], g6, wg)
                if data["worst_two_margin"] is not None:
                    wt = data["worst_two_margin"]
                    if worst_two_margin is None or wt["two_margin"] < worst_two_margin[0]:
                        worst_two_margin = (wt["two_margin"], g6, wt)
                if data["worst_low"] is not None:
                    wl = data["worst_low"]
                    if worst_low is None or wl["margin"] < worst_low[0]:
                        worst_low = (wl["margin"], g6, wl)

            if done % 5000 == 0:
                print(
                    "done=%d/%d graphs=%d skip=%d total_o=%d high=%d low=%d worst_high=%s worst_low=%s worst_k1_high=%s worst_gap_margin=%s worst_two_margin=%s elapsed=%.1fs"
                    % (
                        done,
                        len(graphs),
                        graph_count,
                        skip,
                        total_o,
                        high_o,
                        low_o,
                        worst_high,
                        worst_low,
                        worst_k1_high,
                        worst_gap_margin,
                        worst_two_margin,
                        time.time() - t0,
                    ),
                    flush=True,
                )

    print(
        "FINAL n=%d graphs=%d withO=%d skip=%d total_o=%d high=%d low=%d worst_high=%s worst_low=%s worst_k1_high=%s worst_gap_margin=%s worst_two_margin=%s elapsed=%.1fs"
        % (
            args.n,
            len(graphs),
            graph_count,
            skip,
            total_o,
            high_o,
            low_o,
            worst_high,
            worst_low,
            worst_k1_high,
            worst_gap_margin,
            worst_two_margin,
            time.time() - t0,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
