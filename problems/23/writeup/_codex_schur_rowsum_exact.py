"""Exact Fraction test of the Schur row-sum candidate.

This avoids forming the full Schur complement.  Let O={T>N}, Q=V\\O,
A=N I-K, and r=N-T.  If h solves A_QQ h = r_Q, then row sums of the
Schur complement on O are

  r_o - A_oQ h = (N-T(o)) + sum_{q in Q} K[o,q] h(q).

The candidate says these quantities are all nonnegative.
"""

from fractions import Fraction as F
import argparse
import subprocess

from _h import GENG, dec, loads


def exact_pfs(info):
    pfs = {}
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pfs[f] = {v: F(c, den) for v, c in cnt.items()}
    return pfs


def exact_K_T(info):
    n = info["n"]
    K = [[F(0) for _ in range(n)] for _ in range(n)]
    T = [F(0) for _ in range(n)]
    pfs = exact_pfs(info)
    for f, pf in pfs.items():
        ell = F(info["ell"][f])
        for v, pv in pf.items():
            T[v] += ell * pv
            for w, pw in pf.items():
                K[v][w] += pv * pw
    return K, T


def solve_fraction(M, b):
    n = len(M)
    if n == 0:
        return []
    A = [row[:] + [b[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        if piv != col:
            A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(n):
            if r == col:
                continue
            fac = A[r][col]
            if fac:
                A[r] = [A[r][c] - fac * A[col][c] for c in range(n + 1)]
    return [A[i][n] for i in range(n)]


def check_info(info):
    n = info["n"]
    K, T = exact_K_T(info)
    r = [F(n) - T[v] for v in range(n)]
    O = [v for v in range(n) if r[v] < 0]
    Q = [v for v in range(n) if r[v] >= 0]
    if not O:
        return F(10**9), None, O, None, None, None
    Aqq = []
    for v in Q:
        row = []
        for w in Q:
            row.append((F(n) if v == w else F(0)) - K[v][w])
        Aqq.append(row)
    h = solve_fraction(Aqq, [r[v] for v in Q])
    if h is None:
        return None, "singular", O, None, None, None
    min_h = min(h) if h else F(0)
    max_h = max(h) if h else F(0)
    worst = None
    for o in O:
        val = r[o] + sum(K[o][q] * h[j] for j, q in enumerate(Q))
        item = (val, o)
        if worst is None or item[0] < worst[0]:
            worst = item
    return worst[0], worst[1], O, min_h, max_h, h


def run_named():
    for g6 in [
        "I?BD@g]Qo",
        "I?ABCc]}?",
        "J?`@C_W{Ck?",
        "J?AA@AW^?}?",
        "I?AAD@wF_",
    ]:
        n, e = dec(g6)
        info = loads(n, e)
        val, o, O, min_h, max_h, _ = check_info(info)
        print(
            f"{g6} N={n} Gamma={info['G']} O={O} "
            f"min_row={val} ({float(val):+.6f}) at={o} "
            f"h_range=({min_h},{max_h})",
            flush=True,
        )


def run_census(nmax=10, stride=1):
    count = 0
    bad = 0
    singular = 0
    worst = None
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
            val, o, O, min_h, max_h, _ = check_info(info)
            if val is None:
                singular += 1
                continue
            if val < 0:
                bad += 1
            item = (val, g6, nn, o, O, min_h, max_h, info["G"], len(info["M"]))
            if worst is None or item[0] < worst[0]:
                worst = item
        print(f"N={n} done", flush=True)
    print(
        f"census count={count} bad={bad} singular={singular} worst={worst}",
        flush=True,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["named", "census"], default="named")
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()
    if args.mode == "named":
        run_named()
    else:
        run_census(args.nmax, args.stride)
