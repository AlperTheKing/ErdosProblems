"""Slack diagnostics for the {1,2} fractional split certificate.

For each bad edge f with L=ell(f), write
  E = A_0 + A_{L-1}
  U = A_1 + A_{L-2}
  C = A_2 + ... + A_{L-3}.

The {1,2} fractional certificate is equivalent to:
  if U >= 2N/L:  E <= 2N/L and C <= (L-4)N/L;
  if U <= 2N/L:  E+U <= 4N/L and U+C <= (L-2)N/L.

This script reports exact worst slacks on the selected loads() cut.
"""
from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads
from _layerprice import layers_of


def exact_pf_and_s(info):
    pfs = {}
    s = [F(0) for _ in range(info["n"])]
    for f in info["M"]:
        paths = info["cyc"][f]
        nf = len(paths)
        cnt = {}
        for path in paths:
            for v in path:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, nf) for v, c in cnt.items()}
        pfs[f] = pf
        for v, x in pf.items():
            s[v] += x
    return pfs, s


KEYS = ["hi_E", "hi_C", "lo_EU", "lo_UC", "U_bal"]


def graph_probe(g6):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None:
        return None
    pfs, s = exact_pf_and_s(info)
    counts = {"rows": 0, "hi": 0, "lo": 0}
    worst = {k: (F(-10**9), None) for k in KEYS}
    for f in info["M"]:
        lay, _, h = layers_of(info, f)
        L = h + 1
        if L < 5:
            continue
        pf = pfs[f]
        A = [sum(pf[v] * s[v] for v in lay[i]) for i in range(L)]
        E = A[0] + A[-1]
        U = A[1] + A[-2]
        C = sum(A[2:-2])
        threshold = F(2 * n, L)
        counts["rows"] += 1
        ubal = U - threshold
        if ubal > worst["U_bal"][0]:
            worst["U_bal"] = (ubal, (g6, n, f, L, E, U, C, tuple(A)))
        if U >= threshold:
            counts["hi"] += 1
            gap = E - threshold
            if gap > worst["hi_E"][0]:
                worst["hi_E"] = (gap, (g6, n, f, L, E, U, C, tuple(A)))
            gap = C - F((L - 4) * n, L)
            if gap > worst["hi_C"][0]:
                worst["hi_C"] = (gap, (g6, n, f, L, E, U, C, tuple(A)))
        if U <= threshold:
            counts["lo"] += 1
            gap = E + U - F(4 * n, L)
            if gap > worst["lo_EU"][0]:
                worst["lo_EU"] = (gap, (g6, n, f, L, E, U, C, tuple(A)))
            gap = U + C - F((L - 2) * n, L)
            if gap > worst["lo_UC"][0]:
                worst["lo_UC"] = (gap, (g6, n, f, L, E, U, C, tuple(A)))
    return counts, worst


def merge(acc_counts, acc_worst, res):
    if res is None:
        return
    counts, worst = res
    for k, v in counts.items():
        acc_counts[k] += v
    for k in KEYS:
        if worst[k][0] > acc_worst[k][0]:
            acc_worst[k] = worst[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    counts = {"rows": 0, "hi": 0, "lo": 0}
    worst = {k: (F(-10**9), None) for k in KEYS}
    for nn in range(5, args.max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        if args.workers > 1:
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for res in ex.map(graph_probe, out, chunksize=32):
                    merge(counts, worst, res)
        else:
            for g6 in out:
                merge(counts, worst, graph_probe(g6))
        print(f"N<={nn}: counts={counts}", flush=True)
    print("=== FINAL ===")
    print(f"counts={counts}")
    for k in KEYS:
        print(f"{k}: {worst[k]}")


if __name__ == "__main__":
    main()
