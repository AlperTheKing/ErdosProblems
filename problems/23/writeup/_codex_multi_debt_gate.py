"""Gate a focused multi-row debt-stability candidate.

Candidate:

    if a bad edge has multiple shortest B-geodesics and a row Q has
    row_sum(Q) > N, then 3 * (row_sum(Q) - N) <= 2 * eta,

where eta=N^2/25-|M|.  This is motivated by the first multi-geodesic
old-ceiling obstruction found by _codex_rowwise_debt_profile.py, where the
ratio is exactly 2/3 while corrected ROWWISE-GERSH still has margin 1/3.

The script uses exact Fraction arithmetic and true gamma-min connected
maximum cuts from the existing helpers.
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
    A = F(n) + eta

    acc["cuts"] += 1
    for f in M:
        comp = comp_of[f]
        is_multi = len(cyc[f]) > 1
        for Q in cyc[f]:
            row_sum = sum((sum((p[g][v] for g in comp), F(0)) for v in Q), F(0))
            acc["rows"] += 1
            if is_multi:
                acc["multi_rows"] += 1
                debt = row_sum - n
                if debt > 0:
                    acc["multi_positive_debt"] += 1
                    margin = F(2) * eta - F(3) * debt
                    if margin < acc["min_multi_margin"][0]:
                        acc["min_multi_margin"] = (
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
                        acc["multi_fail"] += 1
                        if acc["first_multi_fail"] is None:
                            acc["first_multi_fail"] = acc["min_multi_margin"]
            corrected_margin = A - row_sum
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
    ap.add_argument("--two-lane-max", type=int, default=60)
    ap.add_argument("--k-lane-max", type=int, default=30)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-direct", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    args = ap.parse_args()

    acc = {
        "cuts": 0,
        "rows": 0,
        "multi_rows": 0,
        "multi_positive_debt": 0,
        "multi_fail": 0,
        "corrected_fail": 0,
        "first_multi_fail": None,
        "first_corrected_fail": None,
        "min_multi_margin": (F(10**18),),
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

    print("=== multi-row debt stability gate ===")
    for key in (
        "cuts",
        "rows",
        "multi_rows",
        "multi_positive_debt",
        "multi_fail",
        "corrected_fail",
    ):
        print(f"{key}: {acc[key]}")
    print("min_multi_margin_2eta_minus_3debt:", acc["min_multi_margin"])
    print("first_multi_fail:", acc["first_multi_fail"] or "")
    print("min_corrected_margin:", acc["min_corrected_margin"])
    print("first_corrected_fail:", acc["first_corrected_fail"] or "")
    print("VERDICT:", "HOLDS" if acc["multi_fail"] == 0 and acc["corrected_fail"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
