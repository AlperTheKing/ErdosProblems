"""Gate a sufficient split package for corrected ROWWISE-GERSH.

For each row Q of a bad edge f in a positive K-component C, compute

    R_Q = sum_{v in Q} Tw_C(v),      eta = N^2/25 - |M|.

This script checks the stronger branch package:

  1. multi-geodesic f:       R_Q <= N + (2/3) eta
  2. unique f, |Q| == 5:     R_Q <= N
  3. unique f, |Q| > 5:      R_Q <= N + eta/2 - (|Q|^2-25)/50

Together these imply the corrected ROWWISE-GERSH bound R_Q <= N + eta.
All arithmetic is exact Fraction arithmetic.
"""

import argparse
import contextlib
import io
import subprocess
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, GENG, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def branch_bound(n, eta, row_len, is_multi):
    if is_multi:
        return F(n) + F(2, 3) * eta, "multi-2eta3"
    if row_len == 5:
        return F(n), "unique-p5-old"
    return F(n) + eta / 2 - F(row_len * row_len - 25, 50), "unique-long-surplus"


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
    cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)
    eta = F(n * n, 25) - len(M)
    corrected = F(n) + eta

    acc["cuts"] += 1
    for f in M:
        comp = comp_of[f]
        is_multi = len(cyc[f]) > 1
        for Q in cyc[f]:
            row_sum = sum((sum((p[g][v] for g in comp), F(0)) for v in Q), F(0))
            bound, branch = branch_bound(n, eta, len(Q), is_multi)
            margin = bound - row_sum
            acc["rows"] += 1
            acc["branch_counts"][branch] = acc["branch_counts"].get(branch, 0) + 1
            if margin < acc["min_branch_margin"].get(branch, (F(10**18),))[0]:
                acc["min_branch_margin"][branch] = (
                    margin,
                    name,
                    n,
                    len(M),
                    f,
                    tuple(Q),
                    row_sum,
                    eta,
                    len(cyc[f]),
                )
            if margin < 0:
                acc["branch_fail"] += 1
                if acc["first_branch_fail"] is None:
                    acc["first_branch_fail"] = (
                        branch,
                        margin,
                        name,
                        n,
                        len(M),
                        f,
                        tuple(Q),
                        row_sum,
                        eta,
                        len(cyc[f]),
                    )
            corrected_margin = corrected - row_sum
            if corrected_margin < acc["min_corrected_margin"][0]:
                acc["min_corrected_margin"] = (
                    corrected_margin,
                    name,
                    n,
                    len(M),
                    f,
                    tuple(Q),
                    row_sum,
                    eta,
                    len(cyc[f]),
                )
            if corrected_margin < 0:
                acc["corrected_fail"] += 1
                if acc["first_corrected_fail"] is None:
                    acc["first_corrected_fail"] = acc["min_corrected_margin"]


def run_gmins(name, n, edges, max_cuts, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, edges, side, acc)


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-cuts", type=int, default=4)
    ap.add_argument("--two-lane-max", type=int, default=40)
    ap.add_argument("--k-lane-max", type=int, default=20)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-direct", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    acc = {
        "cuts": 0,
        "rows": 0,
        "branch_fail": 0,
        "corrected_fail": 0,
        "first_branch_fail": None,
        "first_corrected_fail": None,
        "branch_counts": {},
        "min_branch_margin": {},
        "min_corrected_margin": (F(10**18),),
    }

    if not args.skip_direct:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, side, _bad = build_two_lane(L)
            check_cut(f"two-lane-L{L}", n, edges, side, acc)
        for L in range(8, args.k_lane_max + 1, 2):
            for k in (3, 4, 5, 6):
                n, edges, side, _bad = build_k_lane(L, k, [])
                check_cut(f"klane-L{L}k{k}", n, edges, side, acc)

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
            out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                run_gmins(f"cen{g6}", n, edges, args.max_cuts, acc)

    print("=== rowwise split gate ===")
    print("cuts:", acc["cuts"])
    print("rows:", acc["rows"])
    print("branch_counts:", acc["branch_counts"])
    print("branch_fail:", acc["branch_fail"])
    print("corrected_fail:", acc["corrected_fail"])
    print("min_branch_margin:")
    for branch in sorted(acc["min_branch_margin"]):
        print(f"  {branch}: {acc['min_branch_margin'][branch]}")
    print("first_branch_fail:", acc["first_branch_fail"] or "")
    print("min_corrected_margin:", acc["min_corrected_margin"])
    print("first_corrected_fail:", acc["first_corrected_fail"] or "")
    print("VERDICT:", "HOLDS" if acc["branch_fail"] == 0 and acc["corrected_fail"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
