"""Fast weighted quotient gate for fixed-mask-size C5 layer-set bounds.

For every length-5 row Q and every nonempty mask A subset {0,...,4}, test

    sum_{i in A}(s_i - tau) <= (25/N + c_|A|) eta,

where c_1=c_2=c_3=1/10, c_4=1/2, c_5=2/3.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from itertools import product

from _codex_c5lift_active_size_quotient_fast import (
    EQ,
    SIB,
    automorphisms,
    canon_mask,
    canonical_weight,
    edges_of,
    fmt,
    jsonable,
    loads_for,
    mask_string,
    qcut_value,
    qmaxcut_value,
    side_data,
    sides_to_scan,
)


def bits(mask: int):
    return tuple(i for i in range(5) if (mask >> i) & 1)


def coeff_for_size(k: int) -> F:
    if k <= 3:
        return F(1, 10)
    if k == 4:
        return F(1, 2)
    if k == 5:
        return F(2, 3)
    raise ValueError(k)


def record_case(graph_name, weights, side, f, row, mask, N, m, eta, tau, s, lhs, budget, margin):
    return {
        "graph": graph_name,
        "weights": tuple(weights),
        "side": side,
        "f": f,
        "Q": tuple(row),
        "mask": mask_string(mask),
        "orbit": mask_string(canon_mask(mask)),
        "size": len(bits(mask)),
        "coeff": coeff_for_size(len(bits(mask))),
        "N": N,
        "m": m,
        "eta": eta,
        "tau": tau,
        "s": tuple(s),
        "lhs": lhs,
        "budget": budget,
        "margin": margin,
        "active": tuple(i for i, x in enumerate(s) if x > tau),
    }


def print_case(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in ("margin", "orbit", "mask", "size", "coeff", "graph", "N", "m", "eta", "tau", "lhs", "budget", "active", "s", "f", "Q", "side", "weights"):
        print(f"  {k}: {fmt(rec[k])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], default="sib")
    ap.add_argument("--max-weight", type=int, default=3)
    ap.add_argument("--weight-orbits", action="store_true")
    ap.add_argument("--shard-index", type=int, default=0)
    ap.add_argument("--shard-count", type=int, default=1)
    ap.add_argument("--json-out")
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()
    if args.shard_count < 1:
        raise SystemExit("--shard-count must be positive")
    if not (0 <= args.shard_index < args.shard_count):
        raise SystemExit("--shard-index must be in [0, shard-count)")

    g6 = EQ if args.graph == "eq" else SIB
    graph_name = args.graph
    n, _ = edges_of(g6)
    side_cache = {}
    qmax_cache = {}
    auts = automorphisms(g6) if args.weight_orbits else None

    weights_count = 0
    orbit_skips = 0
    qmax_cuts = 0
    rows_checked = 0
    mask_checks = 0
    fails = 0
    first_fail = None
    worst = None
    min_by_size = {}
    min_by_orbit = {}

    for raw_weight_index, weights0 in enumerate(product(range(1, args.max_weight + 1), repeat=n)):
        if raw_weight_index % args.shard_count != args.shard_index:
            continue
        weights = list(weights0)
        weights_count += 1
        if auts is not None and tuple(weights) != canonical_weight(weights, auts):
            orbit_skips += 1
            continue
        key = tuple(weights)
        if key not in qmax_cache:
            qmax_cache[key] = qmaxcut_value(g6, weights)
        best = qmax_cache[key]
        N = sum(weights)
        for side in sides_to_scan(g6):
            if qcut_value(g6, side, weights) != best:
                continue
            qmax_cuts += 1
            if side not in side_cache:
                side_cache[side] = side_data(g6, side)
            sn, _E, M, paths, rows = side_cache[side]
            m = sum(weights[a] * weights[b] for a, b in M)
            eta = F(N * N, 25) - m
            if eta <= 0:
                continue
            tau = F(5 * m, N)
            loads = loads_for(sn, M, paths, weights)
            for f, row in rows:
                if len(row) != 5:
                    continue
                rows_checked += 1
                s = [loads[v] for v in row]
                for mask in range(1, 32):
                    b = bits(mask)
                    k = len(b)
                    lhs = sum((s[i] - tau for i in b), F(0))
                    budget = (F(25, N) + coeff_for_size(k)) * eta
                    margin = budget - lhs
                    rec = record_case(graph_name, weights, side, f, row, mask, N, m, eta, tau, s, lhs, budget, margin)
                    mask_checks += 1
                    if worst is None or margin < worst["margin"]:
                        worst = rec
                    if k not in min_by_size or margin < min_by_size[k]["margin"]:
                        min_by_size[k] = rec
                    orb = mask_string(canon_mask(mask))
                    if orb not in min_by_orbit or margin < min_by_orbit[orb]["margin"]:
                        min_by_orbit[orb] = rec
                    if margin < 0:
                        fails += 1
                        if first_fail is None:
                            first_fail = rec
                        if args.stop_first:
                            break
                if args.stop_first and first_fail is not None:
                    break
            if args.stop_first and first_fail is not None:
                break
        if args.stop_first and first_fail is not None:
            break

    print("=== fast quotient fixed-mask-size gate ===")
    print("graph:", args.graph)
    print("max_weight:", args.max_weight)
    print("shard:", f"{args.shard_index}/{args.shard_count}")
    print("weight_orbits:", args.weight_orbits)
    print("weights:", weights_count)
    print("orbit_skips:", orbit_skips)
    print("qmax_cuts:", qmax_cuts)
    print("rows_checked:", rows_checked)
    print("mask_checks:", mask_checks)
    print("fails:", fails)
    print_case("worst", worst)
    print("min_by_size:")
    for k in sorted(min_by_size):
        print_case(f"  {k}", min_by_size[k])
    print("min_by_orbit:")
    for orb in sorted(min_by_orbit):
        print_case(f"  {orb}", min_by_orbit[orb])
    print_case("first_fail", first_fail)
    print("VERDICT:", "PASS" if fails == 0 else "FAIL")

    if args.json_out:
        payload = {
            "graph": args.graph,
            "max_weight": args.max_weight,
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "weight_orbits": args.weight_orbits,
            "weights": weights_count,
            "orbit_skips": orbit_skips,
            "qmax_cuts": qmax_cuts,
            "rows_checked": rows_checked,
            "mask_checks": mask_checks,
            "fails": fails,
            "worst": worst,
            "min_by_size": min_by_size,
            "min_by_orbit": min_by_orbit,
            "first_fail": first_fail,
            "verdict": "PASS" if fails == 0 else "FAIL",
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(jsonable(payload), fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
