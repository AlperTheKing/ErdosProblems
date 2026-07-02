"""Exact diagnostics for the C5-RS candidate.

C5-RS: for every row Q=(q0..q4) in an all-length-5 positive K-component,

    sum_i max(0, s(q_i) - tau) <= (1 + 25/N) * eta,

where s=Tw_C is the component load, tau=5m/N, eta=N^2/25-m, and m=|M|
is global.  This script does not prove the lemma; it records the exact
row shape relevant to the current proof split:

  * non-overloaded rows, sum_i s(q_i) <= N;
  * overloaded rows, sum_i s(q_i) > N;
  * self-geodesic floor p_f(q_i) >= 1/|cyc[f]|.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    if isinstance(x, (tuple, list)):
        return "[" + ", ".join(fmt(y) for y in x) + "]"
    return str(x)


def record_min(slot, rec):
    if slot[0] is None or rec["margin"] < slot[0]["margin"]:
        slot[0] = rec


def record_max(slot, rec, key):
    if slot[0] is None or rec[key] > slot[0][key]:
        slot[0] = rec

def check_cut(name, n, edges, side, acc):
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
    rhs = (F(1) + F(25, n)) * eta

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
            pos = sum((max(F(0), s - tau) for s in svals), F(0))
            inactive_deficit = sum((max(F(0), tau - s) for s in svals), F(0))
            margin = rhs - pos
            debt = row_sum + inactive_deficit - F(n)
            lift_margin = F(2, 3) * eta - debt
            den = len(cyc[f])
            floor = F(1, den)
            floor_viol = any(p[f][v] < floor for v in Q)
            active = tuple(i for i, s in enumerate(svals) if s > tau)
            rec = {
                "name": name,
                "n": n,
                "m": m,
                "eta": eta,
                "tau": tau,
                "rhs": rhs,
                "f": f,
                "Q": tuple(Q),
                "comp_size": len(comp),
                "cyc_den": den,
                "floor": floor,
                "p_f_on_Q": tuple(p[f][v] for v in Q),
                "s": svals,
                "row_sum": row_sum,
                "pos": pos,
                "inactive_deficit": inactive_deficit,
                "debt": debt,
                "lift_margin": lift_margin,
                "margin": margin,
                "active": active,
                "side": "".join(map(str, side)),
            }

            acc["rows"] += 1
            acc["active_counts"][len(active)] += 1
            if row_sum > n:
                acc["active_over_counts"][len(active)] += 1
            record_max(acc["max_debt_by_active"].setdefault(len(active), [None]), rec, "debt")
            acc["comp_sizes"][len(comp)] += 1
            record_min(acc["min_by_active"].setdefault(len(active), [None]), rec)
            if floor_viol:
                acc["floor_viol"] += 1
                if acc["first_floor_viol"] is None:
                    acc["first_floor_viol"] = rec
            if row_sum > n:
                acc["over_rows"] += 1
                record_min(acc["min_over"], rec)
                record_max(acc["max_over_debt_by_active"].setdefault(len(active), [None]), rec, "debt")
            else:
                acc["nonover_rows"] += 1
                record_min(acc["min_nonover"], rec)
                record_max(acc["max_nonover_debt_by_active"].setdefault(len(active), [None]), rec, "debt")
            record_min(acc["min_all"], rec)
            record_min(acc["min_lift_by_active"].setdefault(len(active), [None]), {**rec, "margin": lift_margin})
            if lift_margin < acc["min_lift_margin"][0]:
                acc["min_lift_margin"] = (lift_margin, rec)
            if lift_margin < 0:
                acc["lift_fails"] += 1
                if acc["first_lift_fail"] is None:
                    acc["first_lift_fail"] = rec
            if margin < 0:
                acc["fails"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = rec


def run_gmins(name, n, edges, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side_s in cuts:
        side = [int(c) for c in side_s]
        check_cut(name, n, edges, side, acc)


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    keys = (
        "margin",
        "name",
        "n",
        "m",
        "eta",
        "tau",
        "rhs",
        "row_sum",
        "pos",
        "inactive_deficit",
        "debt",
        "lift_margin",
        "active",
        "comp_size",
        "cyc_den",
        "floor",
        "p_f_on_Q",
        "s",
        "f",
        "Q",
        "side",
    )
    for k in keys:
        print(f"  {k}: {fmt(rec[k])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    acc = {
        "cuts": 0,
        "rows": 0,
        "over_rows": 0,
        "nonover_rows": 0,
        "fails": 0,
        "lift_fails": 0,
        "floor_viol": 0,
        "first_fail": None,
        "first_lift_fail": None,
        "first_floor_viol": None,
        "active_counts": Counter(),
        "active_over_counts": Counter(),
        "max_debt_by_active": {},
        "max_nonover_debt_by_active": {},
        "max_over_debt_by_active": {},
        "comp_sizes": Counter(),
        "min_all": [None],
        "min_over": [None],
        "min_nonover": [None],
        "min_by_active": {},
        "min_lift_by_active": {},
        "min_lift_margin": (F(10**18), None),
    }

    if not args.skip_named:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            run_gmins(name, n, edges, args.max_cuts, acc)

    if not args.skip_census:
        for nn in range(args.min_n, args.max_n + 1):
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                run_gmins(f"cen:{g6}", n, edges, args.max_cuts, acc)

    print("=== C5-RS exact inspector ===")
    for k in ("cuts", "rows", "over_rows", "nonover_rows", "fails", "lift_fails", "floor_viol"):
        print(f"{k}: {acc[k]}")
    print("active_counts:", dict(sorted(acc["active_counts"].items())))
    print("active_over_counts:", dict(sorted(acc["active_over_counts"].items())))
    print("comp_sizes:", dict(sorted(acc["comp_sizes"].items())))
    for k in sorted(acc["min_by_active"]):
        print_rec(f"min_active_{k}", acc["min_by_active"][k][0])
    for k in sorted(acc["min_lift_by_active"]):
        print_rec(f"min_lift_active_{k}", acc["min_lift_by_active"][k][0])
    for k in sorted(acc["max_debt_by_active"]):
        print_rec(f"max_debt_active_{k}", acc["max_debt_by_active"][k][0])
    for k in sorted(acc["max_nonover_debt_by_active"]):
        print_rec(f"max_nonover_debt_active_{k}", acc["max_nonover_debt_by_active"][k][0])
    for k in sorted(acc["max_over_debt_by_active"]):
        print_rec(f"max_over_debt_active_{k}", acc["max_over_debt_by_active"][k][0])
    print_rec("min_all", acc["min_all"][0])
    print_rec("min_over", acc["min_over"][0])
    print_rec("min_nonover", acc["min_nonover"][0])
    print_rec("first_fail", acc["first_fail"])
    print_rec("first_lift_fail", acc["first_lift_fail"])
    print("min_lift_margin:", fmt(acc["min_lift_margin"][0]))
    print_rec("first_floor_viol", acc["first_floor_viol"])
    print("VERDICT:", "FAIL" if acc["fails"] or acc["floor_viol"] else "PASS")


if __name__ == "__main__":
    main()
