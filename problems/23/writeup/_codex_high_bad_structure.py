"""Inspect the high-bad-count regime in small exact census data.

For Erdős #23 the only relevant counterexample regime is

    |M| > N^2/25.

This script reports exact gamma-min `loads()` configurations near or above the
threshold and summarizes load variance, bad lengths, and row-sum margins.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _h import GENG, dec, loads
from _rowsum_verify import exact_O_rowsums


def graph_probe(g6: str):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None or not info["M"]:
        return None
    m = len(info["M"])
    if 25 * m < n * n:
        return None
    rows, _G, _N = exact_O_rowsums(info)
    T = info["T"]
    ell = info["ell"]
    var = sum((t - F(n)) * (t - F(n)) for t in T)
    return {
        "g6": g6,
        "n": n,
        "m": m,
        "threshold_delta": 25 * m - n * n,
        "Gamma": info["G"],
        "maxrow": max(rows) if rows else F(0),
        "lengths": tuple(sorted(ell[f] for f in info["M"])),
        "Tmin": min(T),
        "Tmax": max(T),
        "var": var,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=61)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    for nn in range(5, args.max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
        rows = []
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=args.chunksize):
                if res is not None:
                    rows.append(res)
        rows.sort(key=lambda r: (r["threshold_delta"], r["Gamma"], r["g6"]), reverse=True)
        print(f"N={nn} high_or_equal={len(rows)}", flush=True)
        for r in rows[: args.limit]:
            print(
                "  {g6} m={m} 25m-N2={threshold_delta} Gamma={Gamma} maxrow={maxrow} "
                "lengths={lengths} Tmin={Tmin} Tmax={Tmax} var={var}".format(**r),
                flush=True,
            )


if __name__ == "__main__":
    main()
