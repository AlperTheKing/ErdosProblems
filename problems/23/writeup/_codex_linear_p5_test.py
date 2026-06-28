"""Exact diagnostic for the linear sufficient condition under P5.

For a singleton overload O={o}, P5 follows from

    sum_q K[o,q] * (N - T[q]) >= N * (T[o] - N),

because each denominator N - 4 K[o,q] is at most N.

This script only tests that stronger linear inequality; it is not a proof.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _h import GENG, dec
from _angleD_O1 import gmin_sides
from _test_fullg import build_K


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = 0
    first = None
    minratio = None
    for side in sides:
        r = build_K(adj, side, n)
        if r is None:
            continue
        K, T = r
        O = [v for v in range(n) if T[v] > n]
        if len(O) != 1:
            continue
        o = O[0]
        D = T[o] - n
        lhs = sum(
            K[o][q] * (F(n) - T[q])
            for q in range(n)
            if q != o and T[q] < n
        )
        rhs = F(n) * D
        total += 1
        if lhs < rhs:
            first = (g6, "".join(map(str, side)), o, D, lhs, rhs, T, K[o])
            break
        ratio = lhs / rhs
        if minratio is None or ratio < minratio:
            minratio = ratio
    return {"g6": g6, "total": total, "first": first, "minratio": minratio}


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run(
        [GENG, "-tc", "11"], capture_output=True, text=True, check=True
    ).stdout.split()
    total = 0
    first = None
    minratio = None
    minwit = None
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            r = fut.result()
            done += 1
            total += r["total"]
            if r["first"] is not None and first is None:
                first = r["first"]
                break
            if r["minratio"] is not None and (
                minratio is None or r["minratio"] < minratio
            ):
                minratio = r["minratio"]
                minwit = r["g6"]

    print(f"workers {workers}")
    print(f"done_graphs {done}")
    print(f"cuts {total}")
    print(f"first {first}")
    print(f"minratio {minratio} minwit {minwit}")


if __name__ == "__main__":
    main()
