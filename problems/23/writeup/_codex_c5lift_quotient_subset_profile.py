"""Weighted quotient subset-orbit margins for C5-RS / C5-LIFT.

Imports the quotient seed machinery from _codex_c5lift_weighted_quotient_gate.py
and records min margins by D5 orbit of row-position subsets.
"""

from __future__ import annotations

import argparse
import random
from fractions import Fraction as F
from itertools import product

from _codex_c5lift_weighted_quotient_gate import (
    EQ,
    SIB,
    all_rows,
    c5lift_record,
    edges_of,
    qcut_value,
    qmaxcut_value,
    sides_to_scan,
)


def bits(mask):
    return tuple(i for i in range(5) if (mask >> i) & 1)


def rot(mask, k):
    out = 0
    for i in range(5):
        if (mask >> i) & 1:
            out |= 1 << ((i + k) % 5)
    return out


def refl(mask):
    out = 0
    for i in range(5):
        if (mask >> i) & 1:
            out |= 1 << ((-i) % 5)
    return out


def canon(mask):
    vals = []
    for k in range(5):
        vals.append(rot(mask, k))
        vals.append(rot(refl(mask), k))
    return min(vals)


def mask_s(mask):
    return "".join("1" if (mask >> i) & 1 else "0" for i in range(5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", choices=["eq", "sib"], default="sib")
    ap.add_argument("--mode", choices=["exhaustive", "random"], default="exhaustive")
    ap.add_argument("--max-weight", type=int, default=2)
    ap.add_argument("--samples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=230701)
    ap.add_argument("--require-qmax", action="store_true")
    ap.add_argument("--only-length5", action="store_true")
    ap.add_argument("--positive-eta", action="store_true")
    args = ap.parse_args()

    g6 = EQ if args.graph == "eq" else SIB
    n, _E = edges_of(g6)
    qmax_cache = {}
    rows_cache = {}

    def qmax(weights0):
        key = tuple(weights0)
        if key not in qmax_cache:
            qmax_cache[key] = qmaxcut_value(g6, list(weights0))
        return qmax_cache[key]

    def rows(side):
        if side not in rows_cache:
            rows_cache[side] = all_rows(g6, side)
        return rows_cache[side]

    if args.mode == "exhaustive":
        weights_iter = product(range(1, args.max_weight + 1), repeat=n)
    else:
        rng = random.Random(args.seed)
        weights_iter = (
            tuple(rng.randint(1, args.max_weight) for _ in range(n))
            for _ in range(args.samples)
        )

    min_c5 = {}
    min_lift = {}
    checked_weights = 0
    checked_rows = 0
    subset_checks = 0
    first_c5_fail = None
    first_lift_fail = None

    for weights0 in weights_iter:
        weights = list(weights0)
        checked_weights += 1
        best = qmax(weights) if args.require_qmax else None
        for side in sides_to_scan(g6):
            if args.require_qmax and qcut_value(g6, side, weights) != best:
                continue
            for _f, row in rows(side):
                if args.only_length5 and len(row) != 5:
                    continue
                rec = c5lift_record(g6, side, row, weights)
                if args.positive_eta and rec["eta"] <= 0:
                    continue
                checked_rows += 1
                tau = rec["tau"]
                eta = rec["eta"]
                c5_budget = (F(1) + F(25, rec["N"])) * eta
                lift_budget = (F(2, 3) + F(25, rec["N"])) * eta
                for mask in range(1, 32):
                    orb = canon(mask)
                    lhs = sum((rec["s"][i] - tau for i in bits(mask)), F(0))
                    c5_margin = c5_budget - lhs
                    lift_margin = lift_budget - lhs
                    out = (c5_margin, lift_margin, weights, side, row, rec, mask)
                    subset_checks += 1
                    if orb not in min_c5 or c5_margin < min_c5[orb][0]:
                        min_c5[orb] = out
                    if orb not in min_lift or lift_margin < min_lift[orb][1]:
                        min_lift[orb] = out
                    if c5_margin < 0 and first_c5_fail is None:
                        first_c5_fail = out
                    if lift_margin < 0 and first_lift_fail is None:
                        first_lift_fail = out
                if first_c5_fail or first_lift_fail:
                    break
            if first_c5_fail or first_lift_fail:
                break
        if first_c5_fail or first_lift_fail:
            break

    print("graph", args.graph, g6)
    print("checked_weights", checked_weights)
    print("checked_rows", checked_rows)
    print("subset_checks", subset_checks)
    print("first_c5_fail", first_c5_fail)
    print("first_lift_fail", first_lift_fail)
    print("min_c5_by_orbit")
    for orb in sorted(min_c5):
        val = min_c5[orb]
        print(mask_s(orb), val[0], "mask", mask_s(val[6]), "N", val[5]["N"], "m", val[5]["m"], "eta", val[5]["eta"], "s", val[5]["s"], "row", val[4], "side", val[3], "weights", val[2])
    print("min_lift_by_orbit")
    for orb in sorted(min_lift):
        val = min_lift[orb]
        print(mask_s(orb), val[1], "mask", mask_s(val[6]), "N", val[5]["N"], "m", val[5]["m"], "eta", val[5]["eta"], "s", val[5]["s"], "row", val[4], "side", val[3], "weights", val[2])


if __name__ == "__main__":
    main()
