"""Parallel N=11 exact gate for an aggregate moment lemma implying STAR-K1.

For a singleton overload O={o}, put
  D = T[o] - N, a_q = K[o,q], R_q = N - T[q],
  s = sum_{R_q=0} a_q, B = N - K[o,o] - s.

Let A = sum_{R_q>0} a_q and M = sum_{R_q>0} a_q^2/R_q.

Candidate moment dominance:
  D * M <= B * A.

This implies STAR-K1 by Jensen/convexity:
  sum a_q^2/(a_q+R_q)
    = sum a_q * (a_q/R_q)/(1+a_q/R_q)
    <= A * m/(1+m),  m = M/A <= B/D,
so the positive-deficit contribution is at most B. The saturated
contribution is exactly s, hence the diagonal Schur term is <= s+B.
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
    total = fails = 0
    minratio = None
    first = None
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
        sat = sum(
            K[o][q]
            for q in range(n)
            if q != o and K[o][q] > 0 and F(n) - T[q] == 0
        )
        B = F(n) - K[o][o] - sat
        A = F(0)
        M = F(0)
        total += 1
        for q in range(n):
            if q == o:
                continue
            a = K[o][q]
            R = F(n) - T[q]
            if a > 0 and R > 0:
                A += a
                M += a * a / R
        lhs = D * M
        rhs = B * A
        if lhs > rhs:
            fails += 1
            first = (
                g6,
                "".join(map(str, side)),
                o,
                D,
                K[o][o],
                sat,
                B,
                A,
                M,
                lhs - rhs,
                T,
            )
            return {
                "g6": g6,
                "total": total,
                "fails": fails,
                "first": first,
                "minratio": minratio,
            }
        if lhs > 0:
            ratio = rhs / lhs
            if minratio is None or ratio < minratio:
                minratio = ratio
    return {
        "g6": g6,
        "total": total,
        "fails": fails,
        "first": first,
        "minratio": minratio,
    }


def main():
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run(
        [GENG, "-tc", "11"], capture_output=True, text=True, check=True
    ).stdout.split()
    acc = {
        "graphs": 0,
        "total": 0,
        "fails": 0,
        "first": None,
        "minratio": None,
        "minwit": None,
    }
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            r = fut.result()
            acc["graphs"] += 1
            acc["total"] += r["total"]
            acc["fails"] += r["fails"]
            if r["first"] is not None and acc["first"] is None:
                acc["first"] = r["first"]
            if r["minratio"] is not None and (
                acc["minratio"] is None or r["minratio"] < acc["minratio"]
            ):
                acc["minratio"] = r["minratio"]
                acc["minwit"] = r["g6"]

    print(f"workers {workers}")
    print(f"graphs {acc['graphs']}")
    print(f"cuts {acc['total']}")
    print(f"fails {acc['fails']}")
    print(f"minratio {acc['minratio']} minwit {acc['minwit']}")
    print(f"first {acc['first']}")


if __name__ == "__main__":
    main()
