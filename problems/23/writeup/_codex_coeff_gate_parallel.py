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
    psi = {q: F(n) * u[q] + W[q] for q in Q}

    c_min = None
    needed_max = None
    records = []
    for o in O:
        S = sum(P[fi].get(o, F(0)) for fi in range(len(M)))
        B = T[o] - 4 * S
        if B <= 0:
            continue
        raw = F(0)
        for fi in range(len(M)):
            a = P[fi].get(o, F(0))
            if not a:
                continue
            H = sum(P[fi].get(q, F(0)) * psi[q] for q in Q)
            raw += a * H
        c = raw / (F(n * n) * B)
        needed = (T[o] - n) / B
        rec = dict(o=o, S=S, T=T[o], B=B, raw=raw, c=c, needed=needed)
        records.append(rec)
        if c_min is None or c < c_min["c"]:
            c_min = rec
        if needed_max is None or needed > needed_max["needed"]:
            needed_max = rec

    if not records:
        return ("skip", g6, None)
    return ("ok", g6, dict(n=n, count=len(records), c_min=c_min, needed_max=needed_max))


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
    count = skip = total = 0
    c_min = None
    needed_max = None
    worst_gap = None

    with mp.Pool(processes=args.workers) as pool:
        for done, (status, g6, data) in enumerate(
            pool.imap_unordered(check_graph, graphs, chunksize=args.chunksize), 1
        ):
            if status == "skip":
                skip += 1
            else:
                count += 1
                total += data["count"]
                cm = data["c_min"]
                nm = data["needed_max"]
                if c_min is None or cm["c"] < c_min[0]:
                    c_min = (cm["c"], g6, cm)
                if needed_max is None or nm["needed"] > needed_max[0]:
                    needed_max = (nm["needed"], g6, nm)
                gap = cm["c"] - nm["needed"]
                if worst_gap is None or gap < worst_gap[0]:
                    worst_gap = (gap, g6, cm, nm)

            if done % 5000 == 0:
                print(
                    "done=%d/%d graphs=%d skip=%d total=%d c_min=%s needed_max=%s worst_gap=%s elapsed=%.1fs"
                    % (
                        done,
                        len(graphs),
                        count,
                        skip,
                        total,
                        c_min,
                        needed_max,
                        worst_gap,
                        time.time() - t0,
                    ),
                    flush=True,
                )

    print(
        "FINAL n=%d graphs=%d withBpos=%d skip=%d total=%d c_min=%s needed_max=%s worst_gap=%s elapsed=%.1fs"
        % (args.n, len(graphs), count, skip, total, c_min, needed_max, worst_gap, time.time() - t0),
        flush=True,
    )


if __name__ == "__main__":
    main()
