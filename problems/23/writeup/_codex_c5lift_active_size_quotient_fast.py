"""Fast weighted quotient active-size C5-LIFT debt scan.

This is a diagnostic companion to _codex_c5lift_active_proper_gate.py.  It is
restricted to quotient seeds, qmax cuts, length-5 rows, and positive eta.  For
each fixed side/weight it computes quotient vertex loads once, then evaluates
all rows from those loads.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from fractions import Fraction as F
from itertools import product

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_c5lift_weighted_quotient_gate import (
        EQ,
        SIB,
        b_edges,
        m_edges,
        edges_of,
        path_weight,
        qcut_value,
        qmaxcut_value,
        shortest_paths,
        sides_to_scan,
    )
    from _codex_c5rs_inspect import fmt


def side_data(g6, side):
    n, E = edges_of(g6)
    B = b_edges(E, tuple(int(c) for c in side))
    M = sorted(m_edges(E, tuple(int(c) for c in side)))
    paths = {e: shortest_paths(n, B, e[0], e[1]) for e in M}
    rows = [(e, P) for e in M for P in paths[e]]
    return n, E, M, paths, rows


def automorphisms(g6):
    n, E = edges_of(g6)
    E = {tuple(sorted(e)) for e in E}
    deg = [sum(1 for e in E if i in e) for i in range(n)]
    order = sorted(range(n), key=lambda i: (deg[i], i))
    candidates = {
        i: [j for j in range(n) if deg[j] == deg[i]]
        for i in range(n)
    }
    perm = [None] * n
    used = [False] * n
    out = []

    def rec(k):
        if k == n:
            out.append(tuple(perm))
            return
        i = order[k]
        for j in candidates[i]:
            if used[j]:
                continue
            ok = True
            for a in range(n):
                if perm[a] is None:
                    continue
                if ((min(i, a), max(i, a)) in E) != ((min(j, perm[a]), max(j, perm[a])) in E):
                    ok = False
                    break
            if not ok:
                continue
            perm[i] = j
            used[j] = True
            rec(k + 1)
            used[j] = False
            perm[i] = None

    rec(0)
    return out


def permute_weights(weights, perm):
    out = [None] * len(weights)
    for old, new in enumerate(perm):
        out[new] = weights[old]
    return tuple(out)


def canonical_weight(weights, auts):
    return min(permute_weights(weights, perm) for perm in auts)


def rot_mask(mask, k):
    out = 0
    for i in range(5):
        if (mask >> i) & 1:
            out |= 1 << ((i + k) % 5)
    return out


def refl_mask(mask):
    out = 0
    for i in range(5):
        if (mask >> i) & 1:
            out |= 1 << ((-i) % 5)
    return out


def canon_mask(mask):
    vals = []
    for k in range(5):
        vals.append(rot_mask(mask, k))
        vals.append(rot_mask(refl_mask(mask), k))
    return min(vals)


def mask_string(mask):
    return "".join("1" if (mask >> i) & 1 else "0" for i in range(5))


def loads_for(n, M, paths, weights):
    loads = [F(0) for _ in range(n)]
    for a, b in M:
        ps = paths[(a, b)]
        if not ps:
            raise RuntimeError((a, b, "no paths"))
        Z = sum(path_weight(p, weights) for p in ps)
        edge_mult = weights[a] * weights[b]
        loads[a] += weights[b]
        loads[b] += weights[a]
        for p in ps:
            wp = path_weight(p, weights)
            for v in p[1:-1]:
                loads[v] += F(edge_mult * wp, Z * weights[v])
    return loads


def record_case(args, graph_name, weights, side, f, row, N, m, eta, tau, s, row_sum, d, debt, active, margin):
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
        "row_sum": row_sum,
        "inactive_deficit": d,
        "debt": debt,
        "active": tuple(active),
        "margin": margin,
    }


def print_case(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in ("margin", "debt_over_eta", "graph", "N", "m", "eta", "tau", "row_sum", "inactive_deficit", "debt", "active", "s", "f", "Q", "side", "weights"):
        if k not in rec:
            continue
        print(f"  {k}: {fmt(rec[k])}")


def jsonable(x):
    if isinstance(x, F):
        return fmt(x)
    if isinstance(x, tuple):
        return [jsonable(v) for v in x]
    if isinstance(x, list):
        return [jsonable(v) for v in x]
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], default="sib")
    ap.add_argument("--max-weight", type=int, default=3)
    ap.add_argument("--coeff", default="1/10")
    ap.add_argument("--active-min", type=int, default=0)
    ap.add_argument("--active-max", type=int, default=3)
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

    coeff = F(args.coeff)
    g6 = EQ if args.graph == "eq" else SIB
    graph_name = args.graph
    n, _E = edges_of(g6)
    side_cache = {}
    qmax_cache = {}
    auts = automorphisms(g6) if args.weight_orbits else None

    weights_count = 0
    orbit_skips = 0
    cuts = 0
    rows_checked = 0
    active_counts = {}
    active_mask_counts = {}
    worst_by_active_mask = {}
    max_ratio_by_active_mask = {}
    fails = 0
    first_fail = None
    worst = None

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
            cuts += 1
            if side not in side_cache:
                side_cache[side] = side_data(g6, side)
            sn, _E2, M, paths, rows = side_cache[side]
            m = sum(weights[a] * weights[b] for a, b in M)
            eta = F(N * N, 25) - m
            if eta <= 0:
                continue
            tau = F(5 * m, N)
            loads = loads_for(sn, M, paths, weights)
            for f, row in rows:
                if len(row) != 5:
                    continue
                s = [loads[v] for v in row]
                active = [i for i, x in enumerate(s) if x > tau]
                if len(active) < args.active_min or len(active) > args.active_max:
                    continue
                active_mask = 0
                for i in active:
                    active_mask |= 1 << i
                active_orbit = mask_string(canon_mask(active_mask))
                active_counts[len(active)] = active_counts.get(len(active), 0) + 1
                active_mask_counts[active_orbit] = active_mask_counts.get(active_orbit, 0) + 1
                rows_checked += 1
                row_sum = sum(s, F(0))
                d = sum(max(F(0), tau - x) for x in s)
                debt = row_sum + d - N
                margin = coeff * eta - debt
                ratio = debt / eta
                rec = record_case(args, graph_name, weights, side, f, row, N, m, eta, tau, s, row_sum, d, debt, active, margin)
                rec["debt_over_eta"] = ratio
                if worst is None or margin < worst["margin"]:
                    worst = rec
                if active_orbit not in worst_by_active_mask or margin < worst_by_active_mask[active_orbit]["margin"]:
                    worst_by_active_mask[active_orbit] = rec
                if active_orbit not in max_ratio_by_active_mask or ratio > max_ratio_by_active_mask[active_orbit]["debt_over_eta"]:
                    max_ratio_by_active_mask[active_orbit] = rec
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

    print("=== fast quotient active-size gate ===")
    print("graph:", args.graph)
    print("coeff:", fmt(coeff))
    print("active_min:", args.active_min)
    print("active_max:", args.active_max)
    print("shard:", f"{args.shard_index}/{args.shard_count}")
    print("weights:", weights_count)
    print("orbit_skips:", orbit_skips)
    print("automorphisms:", len(auts) if auts is not None else 1)
    print("qmax_cuts:", cuts)
    print("rows_checked:", rows_checked)
    print("active_counts:", dict(sorted(active_counts.items())))
    print("active_mask_counts:", dict(sorted(active_mask_counts.items())))
    print("fails:", fails)
    print_case("worst", worst)
    print_case("first_fail", first_fail)
    print("worst_by_active_mask:")
    for active_orbit in sorted(worst_by_active_mask):
        print_case(f"  {active_orbit}", worst_by_active_mask[active_orbit])
    print("max_ratio_by_active_mask:")
    for active_orbit in sorted(max_ratio_by_active_mask):
        print_case(f"  {active_orbit}", max_ratio_by_active_mask[active_orbit])
    print("VERDICT:", "PASS" if fails == 0 else "FAIL")
    if args.json_out:
        payload = {
            "graph": args.graph,
            "coeff": coeff,
            "active_min": args.active_min,
            "active_max": args.active_max,
            "shard_index": args.shard_index,
            "shard_count": args.shard_count,
            "weights": weights_count,
            "orbit_skips": orbit_skips,
            "automorphisms": len(auts) if auts is not None else 1,
            "qmax_cuts": cuts,
            "rows_checked": rows_checked,
            "active_counts": dict(sorted(active_counts.items())),
            "active_mask_counts": dict(sorted(active_mask_counts.items())),
            "worst_by_active_mask": worst_by_active_mask,
            "max_ratio_by_active_mask": max_ratio_by_active_mask,
            "fails": fails,
            "worst": worst,
            "first_fail": first_fail,
            "verdict": "PASS" if fails == 0 else "FAIL",
        }
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(jsonable(payload), fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
