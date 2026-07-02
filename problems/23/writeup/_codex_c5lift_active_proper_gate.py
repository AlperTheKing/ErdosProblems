"""Gate proper-active C5-LIFT debt coefficients.

For an all-length-5 K-component row Q, write

    debt(Q) = row_sum(Q) + inactive_deficit(Q) - N

where inactive_deficit = sum_i max(0, tau - s_i).

The full C5-LIFT-PMS target is debt <= (2/3) eta.  This script tests the
stronger proper-active hypothesis

    active set != {0,1,2,3,4}  ==>  debt <= coeff * eta

on either the exact small census/gmins battery or the weighted quotient seeds.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from collections import Counter
from fractions import Fraction as F
from itertools import product

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_c5lift_weighted_quotient_gate import (
        EQ,
        SIB,
        all_rows,
        c5lift_record,
        qcut_value,
        qmaxcut_value,
        sides_to_scan,
    )
    from _codex_c5rs_inspect import fmt, norm
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def record_worst(worst, rec):
    if worst[0] is None or rec["margin"] < worst[0]["margin"]:
        worst[0] = rec


def check_fraction(rec, coeff):
    if rec["eta"] <= 0:
        return None
    active = tuple(i for i, s in enumerate(rec["s"]) if s > rec["tau"])
    if len(active) == 5:
        return None
    amin = rec.get("active_min", 0)
    amax = rec.get("active_max", 5)
    if len(active) < amin or len(active) > amax:
        return None
    margin = coeff * rec["eta"] - rec["debt"]
    out = {**rec, "active": active, "margin": margin, "coeff": coeff}
    return out


def scan_cut(name, n, edges, side, coeff, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M_raw, ell_raw, _T, _mu, cyc_raw = st
    if not M_raw:
        return

    M = [norm(g) for g in M_raw]
    ell = {norm(g): ell_raw[g] for g in M_raw}
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)

    m = len(M)
    eta = F(n * n, 25) - m
    tau = F(5 * m, n)

    acc["cuts"] += 1
    for f in M:
        comp = comp_of[f]
        if not comp or any(ell[g] != 5 for g in comp):
            continue
        for Q in cyc[f]:
            if len(Q) != 5:
                continue
            svals = tuple(sum((p[g][v] for g in comp), F(0)) for v in Q)
            row_sum = sum(svals, F(0))
            inactive_deficit = sum((max(F(0), tau - s) for s in svals), F(0))
            debt = row_sum + inactive_deficit - F(n)
            rec = {
                "source": "census",
                "name": name,
                "n": n,
                "N": n,
                "m": m,
                "eta": eta,
                "tau": tau,
                "s": svals,
                "row_sum": row_sum,
                "inactive_deficit": inactive_deficit,
                "debt": debt,
                "f": f,
                "Q": tuple(Q),
                "side": "".join(map(str, side)),
                "active_min": acc["active_min"],
                "active_max": acc["active_max"],
            }
            out = check_fraction(rec, coeff)
            if out is None:
                continue
            acc["proper_rows"] += 1
            acc["active_counts"][len(out["active"])] += 1
            record_worst(acc["worst"], out)
            if out["margin"] < 0:
                acc["fails"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = out


def run_census(args, coeff, acc):
    if not args.skip_named:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            _adj, cuts = gmins(n, edges)
            for side_s in cuts[: args.max_cuts] if args.max_cuts else cuts:
                scan_cut(name, n, edges, [int(c) for c in side_s], coeff, acc)

    if not args.skip_census:
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                _adj, cuts = gmins(n, edges)
                for side_s in cuts[: args.max_cuts] if args.max_cuts else cuts:
                    scan_cut(f"cen:{g6}", n, edges, [int(c) for c in side_s], coeff, acc)


def run_quotient(args, coeff, acc):
    g6 = EQ if args.graph == "eq" else SIB
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

    weights_iter = product(range(1, args.max_weight + 1), repeat=10)
    for weights0 in weights_iter:
        weights = list(weights0)
        acc["weights"] += 1
        best = qmax(weights)
        for side in sides_to_scan(g6):
            if qcut_value(g6, side, weights) != best:
                continue
            acc["cuts"] += 1
            for _f, row in rows(side):
                if len(row) != 5:
                    continue
                r = c5lift_record(g6, side, row, weights)
                rec = {
                    "source": f"quotient:{args.graph}",
                    "name": args.graph,
                    "n": 10,
                    "N": r["N"],
                    "m": r["m"],
                    "eta": r["eta"],
                    "tau": r["tau"],
                    "s": tuple(r["s"]),
                    "row_sum": r["row_sum"],
                    "inactive_deficit": r["inactive_deficit"],
                    "debt": r["row_sum"] + r["inactive_deficit"] - r["N"],
                    "f": _f,
                    "Q": tuple(row),
                    "side": side,
                    "weights": tuple(weights),
                    "active_min": acc["active_min"],
                    "active_max": acc["active_max"],
                }
                out = check_fraction(rec, coeff)
                if out is None:
                    continue
                acc["proper_rows"] += 1
                acc["active_counts"][len(out["active"])] += 1
                record_worst(acc["worst"], out)
                if out["margin"] < 0:
                    acc["fails"] += 1
                    if acc["first_fail"] is None:
                        acc["first_fail"] = out
                        return


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in (
        "margin",
        "source",
        "name",
        "N",
        "m",
        "eta",
        "tau",
        "row_sum",
        "inactive_deficit",
        "debt",
        "active",
        "s",
        "f",
        "Q",
        "side",
        "weights",
    ):
        if k in rec:
            print(f"  {k}: {fmt(rec[k])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["census", "quotient"], default="census")
    ap.add_argument("--coeff", default="1/3")
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--graph", choices=["eq", "sib"], default="sib")
    ap.add_argument("--max-weight", type=int, default=2)
    ap.add_argument("--active-min", type=int, default=0)
    ap.add_argument("--active-max", type=int, default=5)
    args = ap.parse_args()
    coeff = F(args.coeff)
    acc = {
        "weights": 0,
        "cuts": 0,
        "proper_rows": 0,
        "fails": 0,
        "first_fail": None,
        "worst": [None],
        "active_counts": Counter(),
        "active_min": args.active_min,
        "active_max": args.active_max,
    }

    if args.mode == "census":
        run_census(args, coeff, acc)
    else:
        run_quotient(args, coeff, acc)

    print("=== proper-active debt coefficient gate ===")
    print("mode:", args.mode)
    print("coeff:", fmt(coeff))
    print("weights:", acc["weights"])
    print("cuts:", acc["cuts"])
    print("proper_rows:", acc["proper_rows"])
    print("active_counts:", dict(sorted(acc["active_counts"].items())))
    print("fails:", acc["fails"])
    print_rec("worst", acc["worst"][0])
    print_rec("first_fail", acc["first_fail"])
    print("VERDICT:", "PASS" if acc["fails"] == 0 else "FAIL")


if __name__ == "__main__":
    main()

