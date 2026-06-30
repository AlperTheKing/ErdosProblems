"""Scan ROWSUM/SPEC failures against the direct beta-count threshold.

The two-lane family shows ROWSUM/SPEC are false for arbitrary gamma-min
maximum cuts.  This scanner records whether such failures occur in the only
regime where Erdős is not already closed by beta=|M|:

    |M| > N^2 / 25.

This is not a proof, only a regression gate for the repaired target.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from _codex_two_lane_p198_counterexample import make_graph, gamma_and_info, rowsums_for_side
from _gram_spectral import build_O
from _h import dec, GENG, loads
from _tail_positive_extra_counterexample import adj_from_edges


def analyze_info(info):
    n = info["n"]
    m = len(info["M"])
    rows, _G, _N = rowsums_for_side_from_info(info)
    max_row = max(rows) if rows else 0
    O, _lvec, _P = build_O(info)
    rho = float(np.linalg.eigvalsh(O)[-1]) if len(info["M"]) else 0.0
    high_bad = 25 * m > n * n
    return high_bad, m, max_row, rho


def rowsums_for_side_from_info(info):
    from _rowsum_verify import exact_O_rowsums

    return exact_O_rowsums(info)


def info_from_side(n, adj, side):
    rec = gamma_and_info(n, adj, side)
    if rec is None:
        return None
    M, ell, T, mu, cyc, gamma = rec
    return {"n": n, "M": M, "ell": ell, "cyc": cyc, "G": gamma}


def graph_probe(g6):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None or not info["M"]:
        return {
            "total": 0,
            "row_fail": 0,
            "spec_fail": 0,
            "high_row_fail": 0,
            "high_spec_fail": 0,
            "first": None,
        }
    high_bad, m, mr, rho = analyze_info(info)
    row_fail = int(mr > n)
    spec_fail = int(rho > n + 1e-9)
    high_row_fail = int(row_fail and high_bad)
    high_spec_fail = int(spec_fail and high_bad)
    first = None
    if high_row_fail:
        first = ("row", g6, n, m, str(mr), rho)
    elif high_spec_fail:
        first = ("spec", g6, n, m, str(mr), rho)
    return {
        "total": 1,
        "row_fail": row_fail,
        "spec_fail": spec_fail,
        "high_row_fail": high_row_fail,
        "high_spec_fail": high_spec_fail,
        "first": first,
    }


def scan_census(max_n, workers, chunksize):
    print("=== census gamma-min loads() ===")
    for nn in range(5, max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
        total = row_fail = spec_fail = high_row_fail = high_spec_fail = 0
        first = None
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                iterator = ex.map(graph_probe, graphs, chunksize=chunksize)
                for res in iterator:
                    total += res["total"]
                    row_fail += res["row_fail"]
                    spec_fail += res["spec_fail"]
                    high_row_fail += res["high_row_fail"]
                    high_spec_fail += res["high_spec_fail"]
                    first = first or res["first"]
        else:
            for g6 in graphs:
                res = graph_probe(g6)
                total += res["total"]
                row_fail += res["row_fail"]
                spec_fail += res["spec_fail"]
                high_row_fail += res["high_row_fail"]
                high_spec_fail += res["high_spec_fail"]
                first = first or res["first"]
        print(
            f"N={nn} configs={total} row_fail={row_fail} spec_fail={spec_fail} "
            f"high_row_fail={high_row_fail} high_spec_fail={high_spec_fail} first={first}",
            flush=True,
        )


def scan_two_lane(lengths):
    print("=== two-lane family ===")
    for L in lengths:
        n, E, side = make_graph(L)
        adj = adj_from_edges(n, E)
        info = info_from_side(n, adj, side)
        high_bad, m, mr, rho = analyze_info(info)
        print(
            f"L={L} N={n} |M|={m} 25M-N2={25*m-n*n} "
            f"high_bad={high_bad} max_row={mr} rho={rho:.12g}",
            flush=True,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--two-lane-max", type=int, default=30)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    args = ap.parse_args()
    scan_census(args.max_n, args.workers, args.chunksize)
    scan_two_lane([L for L in range(8, args.two_lane_max + 1, 2)])


if __name__ == "__main__":
    main()
