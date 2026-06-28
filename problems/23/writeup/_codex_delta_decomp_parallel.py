from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
import time
from fractions import Fraction as F

from _h import GENG, dec, loads
from _schur_spec import pf_exact


def check_graph(args):
    g6, mode = args
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
    r = [F(n) - T[v] for v in range(n)]
    W = {q: sum(K[q][q2] * r[q2] for q2 in Q) for q in Q}
    psi = {q: F(n) * r[q] + W[q] for q in Q}

    worst = None
    for o in O:
        S = sum(P[fi].get(o, F(0)) for fi in range(len(M)))
        raw = F(0)
        delta = F(0)
        for fi, e in enumerate(M):
            a = P[fi].get(o, F(0))
            if not a:
                continue
            H = sum(P[fi].get(q, F(0)) * psi[q] for q in Q)
            raw += a * H
            delta += a * (H - F(n * n) * (ell[e] - 4))
        if mode == "positive-delta":
            lhs = delta
            rhs = F(n * n) * max(F(0), 4 * S - F(n))
        elif mode == "half-baseline":
            lhs = raw
            rhs = F(n * n) * sum(
                P[fi].get(o, F(0)) * (ell[e] - 4) for fi, e in enumerate(M)
            ) / 2
        else:
            raise ValueError(mode)
        margin = lhs - rhs
        data = dict(n=n, o=o, S=S, T=T[o], lhs=lhs, rhs=rhs, margin=margin)
        if worst is None or margin < worst["margin"]:
            worst = data
        if margin < 0:
            return ("bad", g6, data)

    return ("ok", g6, worst)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("--mode", choices=["positive-delta", "half-baseline"], default="positive-delta")
    parser.add_argument("--workers", type=int, default=60)
    parser.add_argument("--chunksize", type=int, default=32)
    args = parser.parse_args()

    graphs = subprocess.run(
        [GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True
    ).stdout.split()

    t0 = time.time()
    count = skip = bad = 0
    worst = None
    first_bad = None

    with mp.Pool(processes=args.workers) as pool:
        for done, (status, g6, data) in enumerate(
            pool.imap_unordered(
                check_graph,
                [(g6, args.mode) for g6 in graphs],
                chunksize=args.chunksize,
            ),
            1,
        ):
            if status == "skip":
                skip += 1
            elif status == "ok":
                count += 1
                if worst is None or data["margin"] < worst[0]:
                    worst = (data["margin"], g6, data)
            else:
                bad += 1
                if first_bad is None:
                    first_bad = (g6, data)

            if done % 5000 == 0:
                print(
                    "done=%d/%d count=%d skip=%d bad=%d elapsed=%.1fs worst=%s first_bad=%s"
                    % (done, len(graphs), count, skip, bad, time.time() - t0, worst, first_bad),
                    flush=True,
                )
                if first_bad is not None:
                    break

    print(
        "FINAL n=%d mode=%s graphs=%d count=%d skip=%d bad=%d elapsed=%.1fs worst=%s first_bad=%s"
        % (args.n, args.mode, len(graphs), count, skip, bad, time.time() - t0, worst, first_bad),
        flush=True,
    )


if __name__ == "__main__":
    main()
