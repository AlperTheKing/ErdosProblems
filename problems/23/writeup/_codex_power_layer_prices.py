"""Codex diagnostic: power-family layer prices.

For A[f,i]=sum_{v in I_i(f)} p_f(v) S(v), set
  c[f,i] = A[f,i]^theta / sum_j A[f,j]^theta, b=1/c.
This automatically has sum_i c[f,i]=1.  Scan theta and report the max
vertex-budget minus N.

This is a float diagnostic only; a passing theta would need exact follow-up.
"""

import subprocess
import argparse

from _h import GENG, dec, loads
from _layerprice import layers_of


def pfs_and_S(info):
    pfs = {}
    S = [0.0] * info["n"]
    for f in info["M"]:
        paths = info["cyc"][f]
        den = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: c / den for v, c in cnt.items()}
        pfs[f] = pf
        for v, val in pf.items():
            S[v] += val
    return pfs, S


def max_gap(info, theta):
    n = info["n"]
    pfs, S = pfs_and_S(info)
    budget = [0.0] * n
    for f in info["M"]:
        lay, _, h = layers_of(info, f)
        pf = pfs[f]
        A = [sum(pf[v] * S[v] for v in lay[i]) for i in range(h + 1)]
        denom = sum(a**theta for a in A)
        for i, a in enumerate(A):
            c = (a**theta) / denom
            b = 1.0 / c
            for v in lay[i]:
                budget[v] += b * pf[v]
    return max(budget) - n


def blowup_edges(n, edges, t):
    out = []
    for a, b in edges:
        for i in range(t):
            for j in range(t):
                out.append((a * t + i, b * t + j))
    return n * t, out


def load_case(g6, t=1):
    n, e = dec(g6)
    if t != 1:
        n, e = blowup_edges(n, e, t)
    return n, loads(n, e)


def scan_case(label, info, grid):
    vals = [(max_gap(info, th), th) for th in grid]
    best = min(vals)
    interval = [th for gap, th in vals if gap <= 1e-8]
    print(
        f"{label} N={info['n']} |M|={len(info['M'])} "
        f"best_gap={best[0]:+.6f}@theta={best[1]:.3f} "
        f"pass_range={(min(interval), max(interval)) if interval else None}",
        flush=True,
    )
    return best, interval


def run_named():
    grid = [i / 100 for i in range(0, 301)]
    for g6, t in [
        ("I?BD@g]Qo", 1),
        ("I?ABCc]}?", 1),
        ("J?`@C_W{Ck?", 1),
        ("J?AA@AW^?}?", 1),
        ("J???E?pNu\\?", 2),
        ("I?AAD@wF_", 1),
    ]:
        _, info = load_case(g6, t)
        scan_case(f"{g6}[{t}]", info, grid)


def run_census(nmax=10, stride=1):
    grid = [i / 20 for i in range(0, 61)]
    global_worst = None
    for n in range(5, nmax + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(n)], capture_output=True, text=True
        ).stdout.split()[::stride]
        for g6 in graphs:
            nn, e = dec(g6)
            info = loads(nn, e)
            if info is None:
                continue
            best, interval = scan_case(g6, info, grid)
            if global_worst is None or best[0] > global_worst[0]:
                global_worst = (best[0], g6, nn, best[1], bool(interval))
        print(f"N={n} done", flush=True)
    print(f"global_worst={global_worst}", flush=True)


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
