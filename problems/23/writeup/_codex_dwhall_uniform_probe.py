"""Exact probe for the uniform-width special case of DW-Hall.

For a row Q of length L, set w_i=sqrt(m).  This is feasible for DW-Hall
when L*sqrt(m) <= N, checked exactly as L^2*m <= N^2.  The excess condition

    sum_i max(0, s_i - sqrt(m)) <= D,   D=N^2/25-m

is checked exactly without floating point: the active set is {i: s_i^2>m},
and the inequality becomes k*sqrt(m) >= sum_active s_i - D.
"""

import argparse
import contextlib
import io
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def supports_and_p(n, M, cyc):
    supp = {}
    p = {}
    for g in M:
        den = len(cyc[g])
        counts = [0] * n
        support = set()
        for row in cyc[g]:
            for v in row:
                counts[v] += 1
                support.add(v)
        supp[g] = support
        p[g] = [F(c, den) for c in counts]
    return supp, p


def components(M, supp):
    parent = {g: g for g in M}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    owner = {}
    for g in M:
        for v in supp[g]:
            if v in owner:
                union(g, owner[v])
            else:
                owner[v] = g
    comps = {}
    for g in M:
        comps.setdefault(find(g), []).append(g)
    comp_of = {}
    for root, gs in comps.items():
        for g in gs:
            comp_of[g] = gs
    return comp_of


def uniform_ok_exact(svals, n, m):
    L = len(svals)
    feasible = (L * L * m <= n * n)
    D = F(n * n, 25) - m
    active = [s for s in svals if s * s > m]
    B = sum(active, F(0)) - D
    if B <= 0:
        return feasible, True, {"active": len(active), "B": B, "D": D}
    # Need k*sqrt(m) >= B, i.e. k^2*m >= B^2.
    k = len(active)
    ok = (k * k * m >= B * B)
    return feasible, ok, {"active": k, "B": B, "D": D, "lhs_sq": F(k * k * m), "rhs_sq": B * B}


def check_cut(name, n, edges, side, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M_raw, _ell, _T, _mu, cyc_raw = st
    if not M_raw:
        return
    M = [norm(g) for g in M_raw]
    cyc = {norm(g): [tuple(row) for row in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)
    m = len(M)

    acc["cuts"] += 1
    for f in M:
        comp = comp_of[f]
        for Q in cyc[f]:
            svals = []
            for v in Q:
                svals.append(sum((p[g][v] for g in comp), F(0)))
            feasible, ok, detail = uniform_ok_exact(svals, n, m)
            acc["rows"] += 1
            if not feasible:
                acc["infeasible"] += 1
                rec = (name, n, m, f, tuple(Q), len(Q), detail)
                if acc["first_infeasible"] is None:
                    acc["first_infeasible"] = rec
                continue
            acc["feasible"] += 1
            if ok:
                acc["ok"] += 1
            else:
                acc["fail"] += 1
                rec = (name, n, m, f, tuple(Q), tuple(svals), detail)
                if acc["first_fail"] is None:
                    acc["first_fail"] = rec


def run_gmins(name, n, edges, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, edges, side, acc)


def cycle_blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=4)
    ap.add_argument("--two-lane-max", type=int, default=30)
    ap.add_argument("--blowup-t", type=int, default=3)
    ap.add_argument("--blowup-nmax", type=int, default=26)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-two-lane", action="store_true")
    ap.add_argument("--skip-blowups", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    acc = {"cuts": 0, "rows": 0, "feasible": 0, "infeasible": 0, "ok": 0, "fail": 0, "first_fail": None, "first_infeasible": None}

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, side, _bad = build_two_lane(L)
            check_cut(f"two-lane-L{L}", n, edges, side, acc)

    if not args.skip_blowups:
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                if n <= args.blowup_nmax:
                    check_cut(f"direct-C{c}[{t}]", n, edges, cycle_blowup_side([t] * c), acc)

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
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                run_gmins(f"cen{g6}", n, edges, args.max_cuts, acc)

    print("=== DW-Hall uniform sqrt(m) probe ===")
    for k in ("cuts", "rows", "feasible", "infeasible", "ok", "fail"):
        print(f"{k}: {acc[k]}")
    print("first_infeasible:", acc["first_infeasible"] or "")
    print("first_fail:", acc["first_fail"] or "")
    if acc["fail"]:
        print("VERDICT: UNIFORM_FAILS")
    elif acc["infeasible"]:
        print("VERDICT: UNIFORM_INFEASIBLE_SOME_ROWS")
    else:
        print("VERDICT: UNIFORM_CERTIFIES_ALL_TESTED")


if __name__ == "__main__":
    main()