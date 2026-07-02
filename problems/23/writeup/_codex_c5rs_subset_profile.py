"""Subset-profile diagnostics for the C5-RS layer-cake target.

C5-RS is equivalent to the 31 subset inequalities

    sum_{i in A} (s_i - tau) <= (1 + 25/N) eta

for every nonempty A subset {0,...,4}.  This script records the exact
minimum margin by dihedral orbit of A.  It also records the stronger
C5-LIFT budget (25/N + 2/3) eta for comparison.
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


def record_min(slot, rec, key):
    if slot[0] is None or rec[key] < slot[0][key]:
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
    if acc.get("positive_eta") and eta <= 0:
        return
    tau = F(5 * m, n)
    c5_budget = (F(1) + F(25, n)) * eta
    lift_budget = (F(2, 3) + F(25, n)) * eta

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
            acc["rows"] += 1
            if row_sum > n:
                acc["over_rows"] += 1
            for mask in range(1, 32):
                orb = canon(mask)
                lhs = sum((svals[i] - tau for i in bits(mask)), F(0))
                c5_margin = c5_budget - lhs
                lift_margin = lift_budget - lhs
                rec = {
                    "name": name,
                    "n": n,
                    "m": m,
                    "eta": eta,
                    "tau": tau,
                    "f": f,
                    "Q": tuple(Q),
                    "side": "".join(map(str, side)),
                    "mask": mask,
                    "orbit": orb,
                    "mask_s": mask_s(mask),
                    "orbit_s": mask_s(orb),
                    "size": len(bits(mask)),
                    "s": svals,
                    "row_sum": row_sum,
                    "lhs": lhs,
                    "c5_margin": c5_margin,
                    "lift_margin": lift_margin,
                    "active": tuple(i for i, s in enumerate(svals) if s > tau),
                }
                acc["subset_checks"] += 1
                acc["orbit_counts"][orb] += 1
                record_min(acc["min_c5_by_orbit"].setdefault(orb, [None]), rec, "c5_margin")
                record_min(acc["min_lift_by_orbit"].setdefault(orb, [None]), rec, "lift_margin")
                if c5_margin < 0:
                    acc["c5_fails"] += 1
                    if acc["first_c5_fail"] is None:
                        acc["first_c5_fail"] = rec
                if lift_margin < 0:
                    acc["lift_fails"] += 1
                    if acc["first_lift_fail"] is None:
                        acc["first_lift_fail"] = rec


def run_gmins(name, n, edges, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side_s in cuts:
        check_cut(name, n, edges, [int(c) for c in side_s], acc)


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def print_rec(label, rec):
    print(label + ":")
    if rec is None:
        print("  none")
        return
    for k in ("c5_margin", "lift_margin", "orbit_s", "mask_s", "size", "name", "n", "m", "eta", "tau", "lhs", "row_sum", "active", "s", "f", "Q", "side"):
        print(f"  {k}: {fmt(rec[k])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=8)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--positive-eta", action="store_true")
    args = ap.parse_args()

    acc = {
        "positive_eta": args.positive_eta,
        "cuts": 0,
        "rows": 0,
        "over_rows": 0,
        "subset_checks": 0,
        "c5_fails": 0,
        "lift_fails": 0,
        "first_c5_fail": None,
        "first_lift_fail": None,
        "orbit_counts": Counter(),
        "min_c5_by_orbit": {},
        "min_lift_by_orbit": {},
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

    print("=== C5-RS subset profile ===")
    for k in ("cuts", "rows", "over_rows", "subset_checks", "c5_fails", "lift_fails"):
        print(f"{k}: {acc[k]}")
    print("orbits:", {mask_s(k): v for k, v in sorted(acc["orbit_counts"].items())})
    for orb in sorted(acc["min_c5_by_orbit"]):
        print_rec(f"min_c5_orbit_{mask_s(orb)}", acc["min_c5_by_orbit"][orb][0])
    for orb in sorted(acc["min_lift_by_orbit"]):
        print_rec(f"min_lift_orbit_{mask_s(orb)}", acc["min_lift_by_orbit"][orb][0])
    print_rec("first_c5_fail", acc["first_c5_fail"])
    print_rec("first_lift_fail", acc["first_lift_fail"])


if __name__ == "__main__":
    main()


