"""Exact gate for row-LRS.

For each bad edge f:

    (O ell)_f / ell(f) + |M| <= N + N^2/25.

This implies LRS by averaging with weights ell(f)^2/Gamma.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _codex_two_lane_p198_counterexample import gamma_and_info, make_graph
from _h import GENG, dec, loads
from _schur_spec import pf_exact
from _tail_positive_extra_counterexample import adj_from_edges


def row_lrs_margins(info):
    p_dicts, bad_edges, ell, n = pf_exact(info)
    m = len(bad_edges)
    rhs = F(n) + F(n * n, 25) - F(m)
    rows = []
    for idx, f in enumerate(bad_edges):
        value = F(0)
        for jdx, g in enumerate(bad_edges):
            dot = sum(
                p_dicts[idx].get(v, F(0)) * p_dicts[jdx].get(v, F(0))
                for v in p_dicts[idx]
            )
            value += dot * ell[g]
        avg = value / ell[f]
        rows.append((rhs - avg, avg, rhs, f, ell[f]))
    return rows


def graph_probe(g6: str):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or not info["M"]:
        return None
    rows = row_lrs_margins(info)
    min_row = min(rows, key=lambda r: r[0])
    return {
        "bad": int(min_row[0] < 0),
        "min": (min_row[0], g6, info["n"], len(info["M"])) + min_row[1:],
    }


def scan_census(max_n: int, workers: int, chunksize: int):
    print("=== census gamma-min loads() ===", flush=True)
    for nn in range(5, max_n + 1):
        graphs = subprocess.run(
            [GENG, "-tc", str(nn)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        total = bad = 0
        min_row = None
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for res in ex.map(graph_probe, graphs, chunksize=chunksize):
                if res is None:
                    continue
                total += 1
                bad += res["bad"]
                if min_row is None or res["min"][0] < min_row[0]:
                    min_row = res["min"]
        print(f"N={nn} total={total} row_lrs_bad={bad} min={min_row}", flush=True)


def scan_two_lane(max_l: int):
    print("=== two-lane ===", flush=True)
    for length in range(8, max_l + 1, 2):
        n, edges, side = make_graph(length)
        adj = adj_from_edges(n, edges)
        rec = gamma_and_info(n, adj, side)
        bad_edges, ell, loads_t, _mu, cyc, gamma = rec
        info = {
            "n": n,
            "adj": adj,
            "side": side,
            "M": bad_edges,
            "ell": ell,
            "cyc": cyc,
            "G": gamma,
            "T": loads_t,
        }
        min_row = min(row_lrs_margins(info), key=lambda r: r[0])
        print(
            f"L={length} N={n} m={len(bad_edges)} margin={min_row[0]} "
            f"avg={min_row[1]} rhs={min_row[2]} f={min_row[3]} ell={min_row[4]}",
            flush=True,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=61)
    ap.add_argument("--chunksize", type=int, default=64)
    ap.add_argument("--two-lane-max", type=int, default=30)
    args = ap.parse_args()
    scan_census(args.max_n, args.workers, args.chunksize)
    scan_two_lane(args.two_lane_max)


if __name__ == "__main__":
    main()
