"""Parallel weighted quotient gate for the fixed-mask-size C5 split."""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
from fractions import Fraction as F
from itertools import product

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5_masksize_split_gate import bits, canon, coeff_for_size, fmt, mask_s
    from _codex_c5lift_active_size_quotient_fast import (
        automorphisms,
        canonical_weight,
        loads_for,
        qcut_value,
        qmaxcut_value,
        side_data,
        sides_to_scan,
    )
    from _codex_c5lift_weighted_quotient_gate import EQ, SIB, edges_of


def record_case(graph_name, weights, side, f, row, N, m, eta, tau, s, mask, lhs, budget, margin):
    return {
        "graph": graph_name,
        "weights": tuple(weights),
        "side": side,
        "f": f,
        "Q": tuple(row),
        "N": N,
        "m": m,
        "eta": eta,
        "tau": tau,
        "s": tuple(s),
        "mask": mask,
        "mask_s": mask_s(mask),
        "orbit": canon(mask),
        "orbit_s": mask_s(canon(mask)),
        "size": len(bits(mask)),
        "coeff": coeff_for_size(len(bits(mask))),
        "lhs": lhs,
        "budget": budget,
        "margin": margin,
        "active": tuple(i for i, x in enumerate(s) if x > tau),
    }


def better(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return b if b["margin"] < a["margin"] else a


def worker(args):
    graph_name, max_weight, shard_index, shard_count, weight_orbits = args
    g6 = EQ if graph_name == "eq" else SIB
    n, _ = edges_of(g6)
    auts = automorphisms(g6) if weight_orbits else None
    side_cache = {}
    qmax_cache = {}

    out = {
        "weights": 0,
        "orbit_skips": 0,
        "qmax_cuts": 0,
        "rows": 0,
        "checks": 0,
        "fails": 0,
        "min_by_size": {},
        "min_by_orbit": {},
        "first_fail": None,
    }

    for raw_index, weights0 in enumerate(product(range(1, max_weight + 1), repeat=n)):
        if raw_index % shard_count != shard_index:
            continue
        weights = list(weights0)
        out["weights"] += 1
        if auts is not None and tuple(weights) != canonical_weight(weights, auts):
            out["orbit_skips"] += 1
            continue
        key = tuple(weights)
        if key not in qmax_cache:
            qmax_cache[key] = qmaxcut_value(g6, weights)
        best = qmax_cache[key]
        N = sum(weights)
        for side in sides_to_scan(g6):
            if qcut_value(g6, side, weights) != best:
                continue
            out["qmax_cuts"] += 1
            if side not in side_cache:
                side_cache[side] = side_data(g6, side)
            sn, _E, M, paths, rows = side_cache[side]
            m = sum(weights[a] * weights[b] for a, b in M)
            eta = F(N * N, 25) - m
            if eta < 0:
                continue
            tau = F(5 * m, N)
            loads = loads_for(sn, M, paths, weights)
            for f, row in rows:
                if len(row) != 5:
                    continue
                out["rows"] += 1
                s = [loads[v] for v in row]
                for mask in range(1, 32):
                    b = bits(mask)
                    lhs = sum((s[i] - tau for i in b), F(0))
                    budget = (F(25, N) + coeff_for_size(len(b))) * eta
                    margin = budget - lhs
                    rec = record_case(graph_name, weights, side, f, row, N, m, eta, tau, s, mask, lhs, budget, margin)
                    out["checks"] += 1
                    out["min_by_size"][len(b)] = better(out["min_by_size"].get(len(b)), rec)
                    orb = canon(mask)
                    out["min_by_orbit"][orb] = better(out["min_by_orbit"].get(orb), rec)
                    if margin < 0:
                        out["fails"] += 1
                        if out["first_fail"] is None:
                            out["first_fail"] = rec
                        return out
    return out


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in ("margin", "orbit_s", "mask_s", "size", "coeff", "graph", "N", "m", "eta", "tau", "lhs", "budget", "active", "s", "f", "Q", "side", "weights"):
        print(f"  {k}: {fmt(rec[k])}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], required=True)
    ap.add_argument("--max-weight", type=int, default=3)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--shards", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=1)
    ap.add_argument("--weight-orbits", action="store_true")
    args = ap.parse_args()

    total = {
        "weights": 0,
        "orbit_skips": 0,
        "qmax_cuts": 0,
        "rows": 0,
        "checks": 0,
        "fails": 0,
        "min_by_size": {},
        "min_by_orbit": {},
        "first_fail": None,
    }
    tasks = [(args.graph, args.max_weight, i, args.shards, args.weight_orbits) for i in range(args.shards)]
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for out in pool.imap_unordered(worker, tasks, chunksize=args.chunksize):
            done += 1
            for key in ("weights", "orbit_skips", "qmax_cuts", "rows", "checks", "fails"):
                total[key] += out[key]
            for size, rec in out["min_by_size"].items():
                total["min_by_size"][size] = better(total["min_by_size"].get(size), rec)
            for orb, rec in out["min_by_orbit"].items():
                total["min_by_orbit"][orb] = better(total["min_by_orbit"].get(orb), rec)
            if total["first_fail"] is None and out["first_fail"] is not None:
                total["first_fail"] = out["first_fail"]
                pool.terminate()
                break
            print(f"progress shards={done}/{args.shards} checks={total['checks']}", flush=True)

    print("=== parallel quotient fixed-mask-size C5 split gate ===")
    print("graph:", args.graph)
    print("max_weight:", args.max_weight)
    print("workers:", args.workers)
    print("shards:", args.shards)
    print("weight_orbits:", args.weight_orbits)
    for key in ("weights", "orbit_skips", "qmax_cuts", "rows", "checks", "fails"):
        print(f"{key}:", total[key])
    for size in sorted(total["min_by_size"]):
        print_rec(f"min_size_{size}", total["min_by_size"][size])
    for orb in sorted(total["min_by_orbit"]):
        print_rec(f"min_orbit_{mask_s(orb)}", total["min_by_orbit"][orb])
    print_rec("first_fail", total["first_fail"])
    print("VERDICT:", "PASS" if total["fails"] == 0 else "FAIL")
    return 0 if total["fails"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
