#!/usr/bin/env python3
"""Exact weighted-blowup hunt for NCH T=1 on Mycielskian supports.

For a quotient graph H with a fixed connected gamma-min cut and shortest-row data,
this checks integer vertex weights 1..B.  The terminal is a fixed clone of a
quotient vertex t, so the pruning bound is

    s_H(t) <= sum_v w_v - 1.

For a bad quotient edge ab, there are w_a*w_b bad clone edges.  If t is an
endpoint, a fixed terminal clone contributes w_opposite.  If t is an interior
vertex of a quotient geodesic P, the contribution is

    w_a*w_b * prod_{u in int(P)} w_u / w_t / sum_Q prod_{u in int(Q)} w_u.

All arithmetic is exact Fraction.  A positive gap is a genuine weighted-blowup
falsifier for the checked quotient/cut convention.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from _codex_nch_sanity_gate import named_graphs, gamma_min_structs, side_string, frac_s


def iter_weights(n: int, max_weight: int) -> Iterable[tuple[int, ...]]:
    point = [1] * n

    def rec(i: int):
        if i == n:
            yield tuple(point)
            return
        for value in range(1, max_weight + 1):
            point[i] = value
            yield from rec(i + 1)
        point[i] = 1

    yield from rec(0)


def path_product(path: tuple[int, ...], weights: tuple[int, ...]) -> int:
    prod = 1
    for v in path[1:-1]:
        prod *= weights[v]
    return prod


def terminal_contribs(cyc, n: int, weights: tuple[int, ...]) -> list[Fraction]:
    contrib = [Fraction(0) for _ in range(n)]
    for edge, rows in cyc.items():
        a, b = edge
        prods = [path_product(tuple(path), weights) for path in rows]
        denom = sum(prods)
        if denom <= 0:
            raise ArithmeticError(f"zero denominator for edge {edge}")
        edge_factor = weights[a] * weights[b]

        # Fixed terminal clone at a or b.
        contrib[a] += weights[b]
        contrib[b] += weights[a]

        for path, prod in zip(rows, prods):
            for t in path[1:-1]:
                contrib[t] += Fraction(edge_factor * (prod // weights[t]), denom)
    return contrib


def terminal_values(cyc, n: int, weights: tuple[int, ...], terminals: list[int] | None) -> list[tuple[int, Fraction]]:
    if terminals is None:
        return list(enumerate(terminal_contribs(cyc, n, weights)))
    wanted = set(terminals)
    values = {t: Fraction(0) for t in wanted}
    for edge, rows in cyc.items():
        a, b = edge
        prods = [path_product(tuple(path), weights) for path in rows]
        denom = sum(prods)
        if denom <= 0:
            raise ArithmeticError(f"zero denominator for edge {edge}")
        edge_factor = weights[a] * weights[b]
        if a in wanted:
            values[a] += weights[b]
        if b in wanted:
            values[b] += weights[a]
        interior_hits = wanted - {a, b}
        if not interior_hits:
            continue
        for path, prod in zip(rows, prods):
            pset = set(path[1:-1])
            for t in interior_hits & pset:
                values[t] += Fraction(edge_factor * (prod // weights[t]), denom)
    return [(t, values[t]) for t in sorted(values)]


def scan_cut(name: str, n: int, side: str, gamma: int, cyc, max_weight: int, terminals: list[int] | None):
    checked = 0
    best_gap = None
    best_rec = None
    violations = []
    for weights in iter_weights(n, max_weight):
        checked += 1
        bound = sum(weights) - 1
        for t, value in terminal_values(cyc, n, weights, terminals):
            gap = value - bound
            if best_gap is None or gap > best_gap:
                best_gap = gap
                best_rec = {
                    "terminal": t,
                    "weights": list(weights),
                    "sH": frac_s(value),
                    "bound": str(bound),
                    "gap": frac_s(gap),
                    "gap_num": gap.numerator,
                    "gap_den": gap.denominator,
                }
            if gap > 0 and len(violations) < 5:
                violations.append({
                    "terminal": t,
                    "weights": list(weights),
                    "sH": frac_s(value),
                    "bound": str(bound),
                    "gap": frac_s(gap),
                })
    return {
        "name": name,
        "n": n,
        "side": side,
        "gamma": gamma,
        "max_weight": max_weight,
        "checked_weight_vectors": checked,
        "best": best_rec,
        "violations": violations,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="Grotzsch_MycC5")
    ap.add_argument("--max-myc-cycle", type=int, default=11)
    ap.add_argument("--max-weight", type=int, default=2)
    ap.add_argument("--cut-limit", type=int, default=0, help="0 means all gamma-min connected cuts")
    ap.add_argument("--cut-indices", default="", help="comma-separated gamma-min cut indices to scan")
    ap.add_argument("--terminals", default="", help="comma-separated terminal vertices; empty means all")
    ap.add_argument("--summary", default="tmp/nch_weighted_myc_blowup_hunt_v1.json")
    args = ap.parse_args()

    terminals = None if not args.terminals else [int(x) for x in args.terminals.split(",") if x.strip()]
    cut_indices = None if not args.cut_indices else {int(x) for x in args.cut_indices.split(",") if x.strip()}
    out = {
        "schema": "nch_t1_weighted_myc_blowup_hunt_v1",
        "terminal_convention": "fixed clone; bound=sum(weights)-1",
        "only": args.only,
        "max_weight": args.max_weight,
        "cuts": [],
        "verdict": "PASS",
    }
    for name, n, edges in named_graphs(args.max_myc_cycle):
        if args.only and name != args.only:
            continue
        _best_cut, structs = gamma_min_structs(name, n, edges)
        for idx, (side_int, _side, st, gamma) in enumerate(structs):
            if cut_indices is not None and idx not in cut_indices:
                continue
            if args.cut_limit and idx >= args.cut_limit:
                break
            M, ell, _T, _mu, cyc = st
            rec = scan_cut(name, n, side_string(n, side_int), gamma, cyc, args.max_weight, terminals)
            rec["cut_index"] = idx
            rec["bad_edges"] = len(M)
            rec["ell_values"] = sorted(set(ell.values()))
            print(
                name,
                "cut",
                idx,
                "B",
                args.max_weight,
                "checked",
                rec["checked_weight_vectors"],
                "best_gap",
                rec["best"]["gap"],
                "terminal",
                rec["best"]["terminal"],
                flush=True,
            )
            if rec["violations"]:
                out["verdict"] = "FAIL"
            out["cuts"].append(rec)
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print("VERDICT", out["verdict"], args.summary)
    if out["verdict"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
