"""Parallel N=11 exact gate for GPT-Pro's P5-DEFICIT lemma.

For singleton overload O={o}, define
  D = T[o] - N, a_q = K[o,q], R_q = N - T[q].

Candidate P5-DEFICIT:
  sum_{q != o, a_q>0, R_q>0} a_q R_q / (N - 4 a_q) >= D.

This implies STAR-K1 because h_q=T(q)-a_q >= 4a_q follows from
ell(f)>=5 and 0<=p_f(o)<=1, so
  a_q + R_q = N - h_q <= N - 4a_q.
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
        lb = F(0)
        terms = []
        total += 1
        for q in range(n):
            if q == o:
                continue
            a = K[o][q]
            R = F(n) - T[q]
            if a > 0 and R > 0:
                den = F(n) - 4 * a
                if den <= 0:
                    first = (
                        g6,
                        "".join(map(str, side)),
                        o,
                        q,
                        D,
                        a,
                        R,
                        den,
                        T,
                    )
                    return {
                        "g6": g6,
                        "total": total,
                        "fails": 1,
                        "first": first,
                        "minratio": minratio,
                    }
                term = a * R / den
                lb += term
                terms.append((q, a, R, den, term))
        if lb < D:
            fails += 1
            first = (
                g6,
                "".join(map(str, side)),
                o,
                D,
                lb,
                terms,
                T,
            )
            return {
                "g6": g6,
                "total": total,
                "fails": fails,
                "first": first,
                "minratio": minratio,
            }
        if D > 0:
            ratio = lb / D
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
