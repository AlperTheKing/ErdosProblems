"""Parallel N=11 exact gate for the pure-K |O|=1 star bounds."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))

from _h import GENG, dec
from _angleD_O1 import gmin_sides
from _codex_stark1 import stark1


def check_g6(g6):
    n, E = dec(g6)
    adj, sides = gmin_sides(n, E)
    total = fails = k0fails = 0
    minr = None
    mink0r = None
    first = None
    firstk0 = None
    for side in sides:
        d = stark1(adj, side, n)
        if d is None:
            continue
        ok, ratio, D, lb, o, terms, k0 = d
        total += 1
        if not ok:
            fails += 1
            if first is None:
                first = (g6, "".join(map(str, side)), o, D, lb, k0, terms[:12])
        if D > 0:
            if minr is None or ratio < minr:
                minr = ratio
            k0r = k0 / D
            if mink0r is None or k0r < mink0r:
                mink0r = k0r
        if k0 < D:
            k0fails += 1
            if firstk0 is None:
                firstk0 = (g6, "".join(map(str, side)), o, D, lb, k0, terms[:12])
    return {
        "g6": g6,
        "total": total,
        "fails": fails,
        "k0fails": k0fails,
        "first": first,
        "firstk0": firstk0,
        "minr": minr,
        "mink0r": mink0r,
    }


def main():
    # Windows ProcessPoolExecutor caps max_workers at 61.
    workers = min(61, os.cpu_count() or 1)
    graphs = subprocess.run(
        [GENG, "-tc", "11"], capture_output=True, text=True, check=True
    ).stdout.split()
    acc = {
        "graphs": 0,
        "total": 0,
        "fails": 0,
        "k0fails": 0,
        "first": None,
        "firstk0": None,
        "minr": None,
        "minwit": None,
        "mink0r": None,
        "mink0wit": None,
    }
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(check_g6, g6) for g6 in graphs]
        for fut in as_completed(futures):
            r = fut.result()
            acc["graphs"] += 1
            acc["total"] += r["total"]
            acc["fails"] += r["fails"]
            acc["k0fails"] += r["k0fails"]
            if r["first"] is not None and acc["first"] is None:
                acc["first"] = r["first"]
            if r["firstk0"] is not None and acc["firstk0"] is None:
                acc["firstk0"] = r["firstk0"]
            if r["minr"] is not None and (
                acc["minr"] is None or r["minr"] < acc["minr"]
            ):
                acc["minr"] = r["minr"]
                acc["minwit"] = r["g6"]
            if r["mink0r"] is not None and (
                acc["mink0r"] is None or r["mink0r"] < acc["mink0r"]
            ):
                acc["mink0r"] = r["mink0r"]
                acc["mink0wit"] = r["g6"]

    print(f"workers {workers}")
    print(f"graphs {acc['graphs']}")
    print(f"cuts {acc['total']}")
    print(f"fails {acc['fails']}")
    print(f"k0fails {acc['k0fails']}")
    print(f"minratio {acc['minr']} minwit {acc['minwit']}")
    print(f"k0minratio {acc['mink0r']} k0minwit {acc['mink0wit']}")
    print(f"first {acc['first']}")
    print(f"firstk0 {acc['firstk0']}")


if __name__ == "__main__":
    main()
