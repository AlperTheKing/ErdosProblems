"""Classify positive corrected-row debt cases by row length and multiplicity.

This is a small diagnostic for the proof split:

  * unique long rows should be handled by Banked-UPO / LONG-SURPLUS,
  * multi rows are tested by MULTI_DEBT_STABILITY,
  * length-5 residue, if any, needs PMS-5 or a direct bridge.

All arithmetic is exact Fraction arithmetic.
"""

import argparse
import contextlib
import io
import subprocess
from collections import defaultdict
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
        multi = len(cyc[f]) > 1
        for Q in cyc[f]:
            row_sum = sum((sum((p[g][v] for g in comp), F(0)) for v in Q), F(0))
            debt = row_sum - n
            margin = A - row_sum
            L = len(Q)
            acc["rows"] += 1
            key = (L, "multi" if multi else "unique")
            acc["all_counts"][key] += 1
            if margin < 0:
                acc["corrected_fail"] += 1
                if acc["first_corrected_fail"] is None:
                    acc["first_corrected_fail"] = (name, n, len(M), f, tuple(Q), row_sum, eta, len(cyc[f]))
            if debt > 0:
                acc["positive"] += 1
                acc["positive_counts"][key] += 1
                ratio = None if eta <= 0 else debt / eta
                rec = (debt, ratio, name, n, len(M), f, tuple(Q), row_sum, eta, len(cyc[f]))
                old = acc["max_by_key"].get(key)
                if old is None or (ratio is not None and (old[1] is None or ratio > old[1])) or (
                    ratio == old[1] and debt > old[0]
                ):
                    acc["max_by_key"][key] = rec
                if acc["first_positive"] is None:
                    acc["first_positive"] = rec


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
        "positive": 0,
        "corrected_fail": 0,
        "first_positive": None,
        "first_corrected_fail": None,
        "all_counts": defaultdict(int),
        "positive_counts": defaultdict(int),
        "max_by_key": {},
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

    print("=== row debt split classifier ===")
    print("cuts:", acc["cuts"])
    print("rows:", acc["rows"])
    print("positive_debt_rows:", acc["positive"])
    print("corrected_fail:", acc["corrected_fail"])
    print("positive_counts:")
    for key in sorted(acc["positive_counts"]):
        print(f"  L={key[0]} {key[1]}: {acc['positive_counts'][key]}")
    print("max_by_positive_key:")
    for key in sorted(acc["max_by_key"]):
        print(f"  L={key[0]} {key[1]}: {acc['max_by_key'][key]}")
    print("first_positive:", acc["first_positive"] or "")
    print("first_corrected_fail:", acc["first_corrected_fail"] or "")
    print("VERDICT:", "HOLDS" if acc["corrected_fail"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
