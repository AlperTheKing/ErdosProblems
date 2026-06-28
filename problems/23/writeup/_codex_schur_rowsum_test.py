"""Codex diagnostic: underload Schur row-sum lemma.

Let A = N I - K, K=P P^T, and O={v:T(v)>N}.  Let Q=V\\O.
Compute the Schur complement E = A_OO - A_OQ A_QQ^{-1} A_QO.

Since A is a symmetric Z-matrix, E is also a symmetric Z-matrix when A_QQ is
an M-matrix.  If every row sum of E is nonnegative, then E is diagonally
dominant and PSD.  Together with A_QQ PSD this would prove SPEC.

This script tests min row-sum(E) and min eig(E) numerically.
"""

import argparse
import subprocess

import numpy as np

from _h import GENG, blow, dec, loads


def p_matrix(info):
    n = info["n"]
    P = np.zeros((n, len(info["M"])))
    for j, f in enumerate(info["M"]):
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        for v, c in cnt.items():
            P[v, j] = c / den
    return P


def schur_stats(info):
    n = info["n"]
    P = p_matrix(info)
    K = P @ P.T
    A = n * np.eye(n) - K
    T = np.array([float(t) for t in info["T"]])
    O = [v for v in range(n) if T[v] > n + 1e-10]
    Q = [v for v in range(n) if v not in O]
    if not O:
        return {
            "has_O": False,
            "min_row": float("inf"),
            "min_eig": float("inf"),
            "min_Aqq": float("inf"),
            "O": O,
        }
    Aoo = A[np.ix_(O, O)]
    Aqq = A[np.ix_(Q, Q)]
    Aoq = A[np.ix_(O, Q)]
    min_Aqq = float(np.linalg.eigvalsh(Aqq).min()) if len(Q) else float("inf")
    if len(Q):
        X = np.linalg.solve(Aqq, Aoq.T)
        E = Aoo - Aoq @ X
    else:
        E = Aoo
    rows = E.sum(axis=1)
    return {
        "has_O": True,
        "min_row": float(rows.min()),
        "min_eig": float(np.linalg.eigvalsh(E).min()),
        "min_Aqq": min_Aqq,
        "O": O,
        "rows": rows,
        "E": E,
    }


def blowup_edges(n, edges, t):
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


def run_named():
    for g6, t in [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("J???E?pNu\\?", 2),
        ("I?AAD@wF_", 1),
    ]:
        n, e = dec(g6)
        if t != 1:
            n, e = blowup_edges(n, e, t)
        info = loads(n, e)
        s = schur_stats(info)
        print(
            f"{g6}[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} "
            f"O={s['O']} min_row={s['min_row']:+.6e} "
            f"min_eig={s['min_eig']:+.6e} min_Aqq={s['min_Aqq']:+.6e}",
            flush=True,
        )


def run_blowups():
    for t in range(1, 8):
        n, e = blow(t)
        info = loads(n, e)
        s = schur_stats(info)
        print(
            f"C5[{t}] N={n} Gamma={info['G']} |M|={len(info['M'])} "
            f"Osize={len(s['O'])} min_row={s['min_row']:+.6e} "
            f"min_eig={s['min_eig']:+.6e} min_Aqq={s['min_Aqq']:+.6e}",
            flush=True,
        )


def run_census(nmax=10, stride=1):
    count = 0
    bad_row = 0
    bad_eig = 0
    worst_row = None
    worst_eig = None
    for n in range(5, nmax + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(n)], capture_output=True, text=True
        ).stdout.split()[::stride]
        for g6 in graphs:
            nn, e = dec(g6)
            info = loads(nn, e)
            if info is None:
                continue
            count += 1
            s = schur_stats(info)
            if s["has_O"] and s["min_row"] < -1e-8:
                bad_row += 1
            if s["has_O"] and s["min_eig"] < -1e-8:
                bad_eig += 1
            item_r = (s["min_row"], g6, nn, s["O"], info["G"], len(info["M"]))
            item_e = (s["min_eig"], g6, nn, s["O"], info["G"], len(info["M"]))
            if worst_row is None or item_r[0] < worst_row[0]:
                worst_row = item_r
            if worst_eig is None or item_e[0] < worst_eig[0]:
                worst_eig = item_e
        print(f"N={n} done", flush=True)
    print(
        f"census count={count} bad_row={bad_row} bad_eig={bad_eig} "
        f"worst_row={worst_row} worst_eig={worst_eig}",
        flush=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["named", "blowups", "census", "all"], default="all")
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()
    if args.mode in ("named", "all"):
        print("=== named ===", flush=True)
        run_named()
    if args.mode in ("blowups", "all"):
        print("\n=== blowups ===", flush=True)
        run_blowups()
    if args.mode in ("census", "all"):
        print(f"\n=== census N<={args.nmax} stride={args.stride} ===", flush=True)
        run_census(args.nmax, args.stride)
