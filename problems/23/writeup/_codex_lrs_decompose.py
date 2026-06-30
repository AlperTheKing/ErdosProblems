"""Decompose the LRS margin in exact small configurations.

LRS is

    sum T^2 - N*Gamma <= Gamma * (N^2/25 - m).

This script reports:
  overload = sum_v T(v)*(T(v)-N)
  reserve = Gamma*(N^2/25 - m)
  length_excess = Gamma - 25m
  threshold_deficit = N^2/25 - m

The goal is to see what a proof should charge.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads


def decomp(info):
    n = info["n"]
    m = len(info["M"])
    gamma = info["G"]
    t = info["T"]
    overload = sum(x * (x - F(n)) for x in t)
    threshold_deficit = F(n * n, 25) - F(m)
    reserve = gamma * threshold_deficit
    length_excess = gamma - 25 * m
    return overload, reserve, threshold_deficit, length_excess


def probe(g6: str):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or not info["M"]:
        return None
    overload, reserve, threshold_deficit, length_excess = decomp(info)
    margin = reserve - overload
    return {
        "margin": margin,
        "g6": g6,
        "n": info["n"],
        "m": len(info["M"]),
        "Gamma": info["G"],
        "overload": overload,
        "reserve": reserve,
        "threshold_deficit": threshold_deficit,
        "length_excess": length_excess,
        "Tmin": min(info["T"]),
        "Tmax": max(info["T"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=61)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()

    for nn in range(5, args.max_n + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(nn)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        rows = []
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for row in ex.map(probe, graphs, chunksize=args.chunksize):
                if row is not None:
                    rows.append(row)
        rows.sort(key=lambda r: (r["margin"], r["g6"]))
        print(f"N={nn} rows={len(rows)}", flush=True)
        for r in rows[: args.limit]:
            print(
                "  {g6} m={m} Gamma={Gamma} margin={margin} overload={overload} "
                "reserve={reserve} deficit={threshold_deficit} len_excess={length_excess} "
                "T=[{Tmin},{Tmax}]".format(**r),
                flush=True,
            )


if __name__ == "__main__":
    main()
