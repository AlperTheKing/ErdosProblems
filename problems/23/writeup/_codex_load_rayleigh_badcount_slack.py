"""Exact gate for load-Rayleigh bad-count slack.

Candidate:

    (sum_v T(v)^2) / Gamma + |M| <= N + N^2/25.

This is weaker than SBC but still implies Erdos #23:

    Gamma/N <= sum T^2 / Gamma
    Gamma >= 25|M|
    => 25|M|/N + |M| <= N + N^2/25
    => |M| <= N^2/25.
"""

from __future__ import annotations

import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F

from _codex_two_lane_p198_counterexample import gamma_and_info, make_graph
from _h import GENG, dec, loads
from _tail_positive_extra_counterexample import adj_from_edges


def lrs_margin(info):
    n = info["n"]
    m = len(info["M"])
    if not m:
        return None
    gamma = info["G"]
    ray = sum(t * t for t in info["T"]) / gamma
    rhs = F(n) + F(n * n, 25) - F(m)
    return rhs - ray, ray, rhs


def graph_probe(g6: str):
    n, edges = dec(g6)
    info = loads(n, edges)
    if info is None or not info["M"]:
        return None
    margin, ray, rhs = lrs_margin(info)
    return {
        "bad": int(margin < 0),
        "min": (margin, g6, info["n"], len(info["M"]), ray, rhs, info["G"]),
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
        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                iterator = ex.map(graph_probe, graphs, chunksize=chunksize)
                for res in iterator:
                    if res is None:
                        continue
                    total += 1
                    bad += res["bad"]
                    if min_row is None or res["min"][0] < min_row[0]:
                        min_row = res["min"]
        else:
            for g6 in graphs:
                res = graph_probe(g6)
                if res is None:
                    continue
                total += 1
                bad += res["bad"]
                if min_row is None or res["min"][0] < min_row[0]:
                    min_row = res["min"]
        print(f"N={nn} total={total} lrs_bad={bad} min={min_row}", flush=True)


def scan_two_lane(max_l: int):
    print("=== two-lane ===", flush=True)
    for length in range(8, max_l + 1, 2):
        n, edges, side = make_graph(length)
        adj = adj_from_edges(n, edges)
        rec = gamma_and_info(n, adj, side)
        bad_edges, ell, loads_t, _mu, cyc, gamma = rec
        info = {
            "n": n,
            "M": bad_edges,
            "ell": ell,
            "cyc": cyc,
            "G": gamma,
            "T": loads_t,
        }
        margin, ray, rhs = lrs_margin(info)
        print(
            f"L={length} N={n} m={len(bad_edges)} margin={margin} ray={ray} rhs={rhs}",
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
