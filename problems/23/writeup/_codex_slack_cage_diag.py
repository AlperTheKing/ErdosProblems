"""Diagnose Slack-CAGE/GERSH on specific graph6 instances.

For each gamma-min connected max cut, prints row profiles s_i=Tw_C(q_i), full
row sum margin A-sum(s_i), and the minimum Slack-CAGE margin over all subsets
for that row.
"""

import argparse
import contextlib
import io
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_dwhall_uniform_probe import components, supports_and_p
    from _codex_rowcap_non5_half_gate import adj_of
    from _h import Bconn, dec
    from _satzmu_conn import struct_for_side
    from _stark1 import gmins


def norm(e):
    u, v = e
    return (u, v) if u < v else (v, u)


def bitset(mask, n):
    return frozenset(i for i in range(n) if (mask >> i) & 1)


def delta(edges, S):
    return sum(1 for u, v in edges if ((u in S) ^ (v in S)))


def subset_tw(n, M, cyc, U):
    tw = [F(0) for _ in range(n)]
    for g in M:
        den = len(cyc[g])
        for P in cyc[g]:
            pset = frozenset(P)
            if pset <= U:
                mass = F(1, den)
                for v in P:
                    tw[v] += mass
    return tw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g6", nargs="+")
    ap.add_argument("--target-s", default=None, help="comma-separated Fractions, e.g. 1,2,4/3,4/3,2")
    args = ap.parse_args()
    target = None
    if args.target_s:
        target = tuple(F(x) for x in args.target_s.split(","))

    for g6 in args.g6:
        n, edges = dec(g6)
        adj = adj_of(n, edges)
        _adj, cuts = gmins(n, edges)
        print(f"GRAPH {g6} N={n} gamma-min-cuts={len(cuts)}")
        for ci, side in enumerate(cuts):
            if not Bconn(n, adj, side):
                continue
            st = struct_for_side(n, adj, side)
            if st is None:
                continue
            M_raw, _ell, _T, _mu, cyc_raw = st
            M = [norm(g) for g in M_raw]
            cyc = {norm(g): [tuple(P) for P in rows] for g, rows in cyc_raw.items()}
            supp, p = supports_and_p(n, M, cyc)
            comp_of = components(M, supp)
            E = {norm(e) for e in edges}
            Mset = set(M)
            B = E - Mset
            eta = F(n * n, 25) - len(M)
            A = F(n) + eta
            print(f"  CUT {ci} side={''.join(map(str, side))} m={len(M)} eta={eta} A={A}")
            rows = []
            for f in M:
                comp = comp_of[f]
                for Q in cyc[f]:
                    svals = tuple(sum((p[g][v] for g in comp), F(0)) for v in Q)
                    row_sum = sum(svals, F(0))
                    if target is not None and svals != target:
                        continue
                    min_margin = None
                    min_data = None
                    min_proper = None
                    min_proper_data = None
                    for mask in range(1 << n):
                        U = bitset(mask, n)
                        tw = subset_tw(n, M, cyc, U)
                        lhs = sum(tw[v] for v in Q)
                        sigma = delta(B, U) - delta(Mset, U)
                        rhs = F(len(U) + sigma) + eta
                        margin = rhs - lhs
                        if min_margin is None or margin < min_margin:
                            min_margin = margin
                            min_data = (U, lhs, rhs, sigma)
                        if U and len(U) < n:
                            if min_proper is None or margin < min_proper:
                                min_proper = margin
                                min_proper_data = (U, lhs, rhs, sigma)
                    rows.append((A-row_sum, f, Q, svals, row_sum, min_margin, min_data, min_proper, min_proper_data))
            rows.sort(key=lambda x: (x[0], x[1], x[2]))
            for rec in rows[:20]:
                full_margin, f, Q, svals, row_sum, min_margin, min_data, min_proper, min_proper_data = rec
                print(f"    f={f} Q={Q} s={svals} sum={row_sum} full_margin={full_margin}")
                U,lhs,rhs,sigma = min_data
                print(f"      min_all margin={min_margin} U={tuple(sorted(U))} lhs={lhs} rhs={rhs} sigma={sigma}")
                if min_proper_data:
                    U,lhs,rhs,sigma = min_proper_data
                    print(f"      min_proper margin={min_proper} U={tuple(sorted(U))} lhs={lhs} rhs={rhs} sigma={sigma}")


if __name__ == "__main__":
    main()