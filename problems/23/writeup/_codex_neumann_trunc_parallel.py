from __future__ import annotations

import argparse
import multiprocessing as mp
import subprocess
import time
from fractions import Fraction as F

from _h import GENG, dec, loads
import _schur_spec as schur


def test_g6(args):
    g6, steps = args
    n, E = dec(g6)
    info = loads(n, E)
    if info is None:
        return ("skip", g6, None)

    P, M, ell, n = schur.pf_exact(info)
    if not M:
        return ("skip", g6, None)

    K = [[F(0)] * n for _ in range(n)]
    for pd in P:
        items = list(pd.items())
        for va, pa in items:
            for vb, pb in items:
                K[va][vb] += pa * pb

    T = [
        sum(ell[M[fi]] * P[fi].get(v, F(0)) for fi in range(len(M)))
        for v in range(n)
    ]
    O = [v for v in range(n) if T[v] > n]
    if not O:
        return ("skip", g6, None)
    Q = [v for v in range(n) if T[v] <= n]

    # g_steps = sum_{t=0}^{steps-1} (K_QQ/N)^t (N-T)_Q/N.
    term = [(F(n) - T[q]) / F(n) for q in Q]
    g = term[:]
    for _ in range(1, steps):
        term = [
            sum(K[q][Q[j]] * term[j] for j in range(len(Q))) / F(n)
            for q in Q
        ]
        g = [g[i] + term[i] for i in range(len(Q))]

    margins = [
        F(n) - T[o] + sum(K[o][Q[i]] * g[i] for i in range(len(Q)))
        for o in O
    ]
    min_margin = min(margins)
    if min_margin < 0:
        return (
            "bad",
            g6,
            dict(n=n, O=O, min_margin=min_margin, T=T, margins=margins),
        )
    return ("ok", g6, dict(n=n, O=O, min_margin=min_margin))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--steps", type=int, default=2)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=16)
    ns = ap.parse_args()

    out = subprocess.run(
        [GENG, "-tc", str(ns.n)], capture_output=True, text=True, check=True
    ).stdout.split()
    t0 = time.time()
    count = skip = bad = 0
    worst = None
    first_bad = None

    with mp.Pool(processes=ns.workers) as pool:
        for done, (st, g6, data) in enumerate(
            pool.imap_unordered(
                test_g6, [(g6, ns.steps) for g6 in out], chunksize=ns.chunksize
            ),
            1,
        ):
            if st == "skip":
                skip += 1
            elif st == "ok":
                count += 1
                val = data["min_margin"]
                if worst is None or val < worst[0]:
                    worst = (val, g6, data["n"], data["O"])
            else:
                bad += 1
                if first_bad is None:
                    first_bad = (g6, data)

            if done % 5000 == 0:
                print(
                    f"done={done}/{len(out)} count={count} skip={skip} bad={bad} "
                    f"elapsed={time.time()-t0:.1f}s worst={worst}",
                    flush=True,
                )
                if first_bad is not None:
                    print("FIRST_BAD", first_bad, flush=True)
                    break

    print(
        f"FINAL n={ns.n} steps={ns.steps} graphs={len(out)} count={count} "
        f"skip={skip} bad={bad} elapsed={time.time()-t0:.1f}s "
        f"worst={worst} first_bad={first_bad}",
        flush=True,
    )


if __name__ == "__main__":
    main()

