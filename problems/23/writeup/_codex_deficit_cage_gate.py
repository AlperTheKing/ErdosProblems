"""Exact gate for GPT-Pro's DEFICIT-CAGE ROW TRANSPORT lemma.

For a fixed row Q, the proposed Hall condition is

    sum_g 1/|cyc[g]| * sum_{P in cyc[g], P subset U} |P cap Q|
      <= (A/N) * |U|,

for every U subset V, where A = N + N^2/25 - |M|.

This is stronger than ROWWISE-GERSH and is intended as a direct Hall
transport certificate.  The script searches for exact Fraction falsifiers.
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


def bit_vertices(mask, n):
    return [i for i in range(n) if (mask >> i) & 1]


def check_cut(name, n, edges, side, max_subsets, acc):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return

    A = F(n) + F(n * n, 25) - len(M)
    cap_unit = A / n

    row_sets = {}
    for g in M:
        row_sets[g] = [(tuple(P), set(P)) for P in cyc[g]]

    subset_limit = 1 << n
    if max_subsets is not None:
        subset_limit = min(subset_limit, max_subsets)

    for f in M:
        for Q in cyc[f]:
            qset = set(Q)
            for mask in range(subset_limit):
                U = set(bit_vertices(mask, n))
                lhs = F(0)
                for g in M:
                    den = len(cyc[g])
                    for _P, pset in row_sets[g]:
                        if pset <= U:
                            lhs += F(len(pset & qset), den)
                rhs = cap_unit * len(U)
                acc["checks"] += 1
                margin = rhs - lhs
                if margin < acc["min"][0]:
                    acc["min"] = (margin, name, n, len(M), f, tuple(Q), tuple(sorted(U)), lhs, rhs)
                if lhs > rhs:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "A": str(A),
                            "cap_unit": str(cap_unit),
                            "f": f,
                            "Q": tuple(Q),
                            "U": tuple(sorted(U)),
                            "lhs": str(lhs),
                            "rhs": str(rhs),
                            "excess": str(lhs - rhs),
                        }
                    return


def run_gmins(name, n, edges, max_cuts, max_subsets, acc):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, edges, side, max_subsets, acc)
        if acc["first"]:
            return


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
    ap.add_argument("--two-lane-max", type=int, default=20)
    ap.add_argument("--blowup-t", type=int, default=3)
    ap.add_argument("--blowup-nmax", type=int, default=20)
    ap.add_argument("--max-cuts", type=int, default=None)
    ap.add_argument("--max-subsets", type=int, default=None)
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    acc = {"checks": 0, "viol": 0, "first": None, "min": (F(10**18),)}

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _bad = build_two_lane(L)
        check_cut(f"two-lane-L{L}", n, edges, side, args.max_subsets, acc)
        if args.stop_first and acc["first"]:
            break

    if not (args.stop_first and acc["first"]):
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                if n <= args.blowup_nmax:
                    check_cut(f"direct-C{c}[{t}]", n, edges, cycle_blowup_side([t] * c), args.max_subsets, acc)
                    if args.stop_first and acc["first"]:
                        break
            if args.stop_first and acc["first"]:
                break

    if not (args.stop_first and acc["first"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for nm, (n, edges) in named:
            run_gmins(nm, n, edges, args.max_cuts, args.max_subsets, acc)
            if args.stop_first and acc["first"]:
                break

    if not (args.stop_first and acc["first"]):
        for nn in range(args.min_n, args.max_n + 1):
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                run_gmins(f"cen{g6}", n, edges, args.max_cuts, args.max_subsets, acc)
                if args.stop_first and acc["first"]:
                    break
            if args.stop_first and acc["first"]:
                break

    print("=== DEFICIT-CAGE Hall gate ===")
    print("checks:", acc["checks"])
    print("violations:", acc["viol"])
    print("min_margin:", acc["min"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "HOLDS" if acc["viol"] == 0 else "FAILS")


if __name__ == "__main__":
    main()
