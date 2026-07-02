"""Rowset category minima for Slack-CAGE.

Reports min margins for U=empty, U=V, and nonempty proper rowset-generated
subsets on direct stress families.  This is a diagnostic for the proposed
INTERIOR-SLACK-CAGE unit gap.
"""

import argparse
import contextlib
import io
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _codex_slack_cage_gate import build_subsets, cycle_blowup_side
    from _h import Bconn
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane


def fmt(rec):
    if rec is None:
        return ""
    margin, name, n, m, f, Q, U, lhs, rhs, size, slack, eta = rec
    return {
        "margin": str(margin),
        "name": name,
        "n": n,
        "m": m,
        "f": f,
        "Q": Q,
        "U": tuple(sorted(U)),
        "lhs": str(lhs),
        "rhs": str(rhs),
        "size": size,
        "slack": slack,
        "eta": str(eta),
    }


def merge(dst, src):
    for k, rec in src.items():
        if rec is not None and (dst[k] is None or rec[0] < dst[k][0]):
            dst[k] = rec


def check_cut(name, n, edges, side):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, _ell, _T, _mu, cyc = st
    if not M:
        return None

    bad = {tuple(sorted(e)) for e in M}
    blue = set()
    for u, v in edges:
        e = tuple(sorted((u, v)))
        if side[u] != side[v]:
            blue.add(e)

    eta = F(n * n, 25) - len(M)
    row_sets = {g: [(tuple(P), set(P)) for P in cyc[g]] for g in M}
    subsets = build_subsets(n, row_sets, "rowsets", None)

    subset_data = []
    for U in subsets:
        dB = sum(((u in U) ^ (v in U)) for u, v in blue)
        dM = sum(((u in U) ^ (v in U)) for u, v in bad)
        tw = [F(0) for _ in range(n)]
        for g in M:
            den = len(cyc[g])
            for P, pset in row_sets[g]:
                if pset <= U:
                    mass = F(1, den)
                    for v in P:
                        tw[v] += mass
        subset_data.append((U, len(U), dB - dM, tw))

    mins = {"empty": None, "full": None, "proper_nonempty": None}
    for f in M:
        for Q in cyc[f]:
            q = tuple(Q)
            for U, size, slack, tw in subset_data:
                lhs = sum(tw[v] for v in Q)
                rhs = F(size + slack) + eta
                margin = rhs - lhs
                if size == 0:
                    cat = "empty"
                elif size == n:
                    cat = "full"
                else:
                    cat = "proper_nonempty"
                rec = (margin, name, n, len(M), f, q, U, lhs, rhs, size, slack, eta)
                if mins[cat] is None or margin < mins[cat][0]:
                    mins[cat] = rec
    return mins


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--two-lane-max", type=int, default=100)
    ap.add_argument("--blowup-t", type=int, default=3)
    ap.add_argument("--skip-two-lane", action="store_true")
    ap.add_argument("--skip-blowups", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    mins = {"empty": None, "full": None, "proper_nonempty": None}
    cases = 0

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, side, _bad = build_two_lane(L)
            r = check_cut(f"two-lane-L{L}", n, edges, side)
            if r:
                merge(mins, r)
                cases += 1

    if not args.skip_blowups:
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                r = check_cut(f"direct-C{c}[{t}]", n, edges, cycle_blowup_side([t] * c))
                if r:
                    merge(mins, r)
                    cases += 1

    if not args.skip_named:
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", union_disjoint((7, Cn(7)), mycielski(5, Cn(5)))),
        ]
        for nm, (n, edges) in named:
            _adj, cuts = gmins(n, edges)
            for idx, side in enumerate(cuts[:2]):
                r = check_cut(f"{nm}#cut{idx}", n, edges, side)
                if r:
                    merge(mins, r)
                    cases += 1

    print("=== Slack-CAGE rowset category minima ===")
    print("cases:", cases)
    print("min_empty:", fmt(mins["empty"]))
    print("min_full:", fmt(mins["full"]))
    print("min_proper_nonempty:", fmt(mins["proper_nonempty"]))
    print("INTERIOR_UNIT_GAP:", mins["proper_nonempty"] is not None and mins["proper_nonempty"][0] >= 1)


if __name__ == "__main__":
    run()
