"""Gate the spectral bad-count slack inequality.

Candidate scalar inequality:

    rho(O) + |M| <= N + N^2/25.          (SBC)

This repairs the false universal SPEC bound by allowing spectral excess when
the bad-edge count is far below the conjectural threshold.  If (SBC) holds,
then Erdős #23 follows:

    rho(O) >= (ell^T O ell)/(ell^T ell)
           = sum_v T(v)^2 / Gamma
           >= Gamma/N
           >= 25|M|/N.

Together with (SBC):

    25m/N <= N + N^2/25 - m
    => m <= N^2/25.

This script is only an exact/float gate for candidate discovery.  It reports
the margin

    N + N^2/25 - |M| - rho(O).
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

import numpy as np

from _codex_two_lane_p198_counterexample import make_graph, gamma_and_info
from _gram_spectral import build_O
from _h import dec, GENG, loads
from _tail_positive_extra_counterexample import adj_from_edges


def spectral_margin(info):
    n = info["n"]
    m = len(info["M"])
    O, _lvec, _P = build_O(info)
    rho = float(np.linalg.eigvalsh(O)[-1]) if m else 0.0
    rhs = float(F(n) + F(n * n, 25) - F(m))
    return rhs - rho, rho, rhs


def load_margin(info):
    n = info["n"]
    m = len(info["M"])
    tmax = max(info["T"]) if "T" in info else None
    if tmax is None:
        return None
    rhs = F(n) + F(n * n, 25) - F(m)
    return rhs - tmax, tmax, rhs


def row_margin(info):
    from _rowsum_verify import exact_O_rowsums

    n = info["n"]
    m = len(info["M"])
    rows, _G, _N = exact_O_rowsums(info)
    maxrow = max(rows) if rows else F(0)
    rhs = F(n) + F(n * n, 25) - F(m)
    return rhs - maxrow, maxrow, rhs


def graph_probe(g6):
    n, E = dec(g6)
    info = loads(n, E)
    if info is None or not info["M"]:
        return {
            "total": 0,
            "spec_bad": 0,
            "row_bad": 0,
            "load_bad": 0,
            "min_spec": None,
            "min_row": None,
            "min_load": None,
            "first": None,
        }
    sm, rho, srhs = spectral_margin(info)
    rm, maxrow, rrhs = row_margin(info)
    lm = load_margin(info)
    return {
        "total": 1,
        "spec_bad": int(sm < -1e-9),
        "row_bad": int(rm < 0),
        "load_bad": int(lm is not None and lm[0] < 0),
        "min_spec": (sm, g6, info["n"], len(info["M"]), rho, srhs),
        "min_row": (rm, g6, info["n"], len(info["M"]), str(maxrow), str(rrhs)),
        "min_load": (lm[0], g6, info["n"], len(info["M"]), str(lm[1]), str(lm[2])) if lm is not None else None,
        "first": ("spec", g6, info["n"], len(info["M"]), rho, srhs) if sm < -1e-9 else (
            ("row", g6, info["n"], len(info["M"]), str(maxrow), str(rrhs)) if rm < 0 else (
                ("load", g6, info["n"], len(info["M"]), str(lm[1]), str(lm[2])) if lm is not None and lm[0] < 0 else None
            )
        ),
    }


def scan_census(max_n, workers, chunksize):
    print("=== census gamma-min loads() ===")
    for nn in range(5, max_n + 1):
        graphs = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout.split()
        total = spec_bad = row_bad = load_bad = 0
        min_spec = None
        min_row = None
        min_load = None
        first = None
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                iterator = ex.map(graph_probe, graphs, chunksize=chunksize)
                for res in iterator:
                    total += res["total"]
                    spec_bad += res["spec_bad"]
                    row_bad += res["row_bad"]
                    load_bad += res["load_bad"]
                    if res["min_spec"] is not None and (min_spec is None or res["min_spec"][0] < min_spec[0]):
                        min_spec = res["min_spec"]
                    if res["min_row"] is not None and (min_row is None or res["min_row"][0] < min_row[0]):
                        min_row = res["min_row"]
                    if res["min_load"] is not None and (min_load is None or res["min_load"][0] < min_load[0]):
                        min_load = res["min_load"]
                    first = first or res["first"]
        else:
            for g6 in graphs:
                res = graph_probe(g6)
                total += res["total"]
                spec_bad += res["spec_bad"]
                row_bad += res["row_bad"]
                load_bad += res["load_bad"]
                if res["min_spec"] is not None and (min_spec is None or res["min_spec"][0] < min_spec[0]):
                    min_spec = res["min_spec"]
                if res["min_row"] is not None and (min_row is None or res["min_row"][0] < min_row[0]):
                    min_row = res["min_row"]
                if res["min_load"] is not None and (min_load is None or res["min_load"][0] < min_load[0]):
                    min_load = res["min_load"]
                first = first or res["first"]
        print(
            f"N={nn} total={total} spec_bad={spec_bad} row_bad={row_bad} load_bad={load_bad} "
            f"min_spec={min_spec} min_row={min_row} min_load={min_load} first={first}",
            flush=True,
        )


def info_from_side(n, adj, side):
    rec = gamma_and_info(n, adj, side)
    if rec is None:
        return None
    M, ell, _T, _mu, cyc, gamma = rec
    return {"n": n, "M": M, "ell": ell, "cyc": cyc, "G": gamma, "T": _T}


def scan_two_lane(max_l):
    print("=== two-lane ===")
    for L in range(8, max_l + 1, 2):
        n, E, side = make_graph(L)
        adj = adj_from_edges(n, E)
        info = info_from_side(n, adj, side)
        sm, rho, srhs = spectral_margin(info)
        rm, maxrow, rrhs = row_margin(info)
        lm, tmax, lrhs = load_margin(info)
        print(
            f"L={L} N={n} m={len(info['M'])} spec_margin={sm:.12g} rho={rho:.12g} rhs={srhs:.12g} "
            f"row_margin={rm} maxrow={maxrow} load_margin={lm} Tmax={tmax}",
            flush=True,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--two-lane-max", type=int, default=30)
    args = ap.parse_args()
    scan_census(args.max_n, args.workers, args.chunksize)
    scan_two_lane(args.two_lane_max)


if __name__ == "__main__":
    main()
