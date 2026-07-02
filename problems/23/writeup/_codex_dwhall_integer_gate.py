"""Exact integer-width gate for DW-Hall.

DW-Hall asks for positive widths w_i with sum w_i<=N, w_i w_{i+1}>=m,
and sum max(0, s_i-m/w_i)<=D.  The proposed geometric proof interprets w_i
as sizes of disjoint row shadows, hence integer widths are a natural stronger
certificate.  This script searches integer w_i exactly.
"""

import argparse
from fractions import Fraction as F

from _codex_dwhall_uniform_probe import (
    Cn,
    GENG,
    Bconn,
    adj_of,
    blowup,
    bridge,
    build_two_lane,
    check_cut as _unused_check_cut,
    components,
    cycle_blowup_side,
    dec,
    gmins,
    mycielski,
    norm,
    struct_for_side,
    supports_and_p,
)


def eps_for(w, svals, m):
    total = F(0)
    for wi, si in zip(w, svals):
        base = F(m, wi)
        if si > base:
            total += si - base
    return total


def find_integer_widths(svals, n, m):
    L = len(svals)
    D = F(n * n, 25) - m
    if L > n:
        return None

    # Try low total width first; this mirrors disjoint shadows and usually finds
    # sparse certificates quickly.  Positive integer widths, total <= n.
    w = [0] * L

    def dfs(pos, remaining):
        if pos == L:
            if remaining < 0:
                return None
            if w[-1] * w[0] < m:
                return None
            e = eps_for(w, svals, m)
            if e <= D:
                return tuple(w), e
            return None

        left_slots = L - pos - 1
        max_w = remaining - left_slots
        if max_w < 1:
            return None

        # Lower bound from previous product constraint.
        lo = 1
        if pos > 0:
            lo = max(lo, (m + w[pos - 1] - 1) // w[pos - 1])
        if pos == L - 1 and w[0] > 0:
            lo = max(lo, (m + w[0] - 1) // w[0])
        if lo > max_w:
            return None

        # Small widths reduce eps, but can force future widths.  Try increasing.
        for val in range(lo, max_w + 1):
            w[pos] = val
            res = dfs(pos + 1, remaining - val)
            if res is not None:
                return res
        w[pos] = 0
        return None

    return dfs(0, n)


def check_cut(name, n, edges, side, acc, stop_first=False):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return True
    st = struct_for_side(n, adj, side)
    if st is None:
        return True
    M_raw, _ell, _T, _mu, cyc_raw = st
    if not M_raw:
        return True
    M = [norm(g) for g in M_raw]
    cyc = {norm(g): [tuple(row) for row in rows] for g, rows in cyc_raw.items()}
    supp, p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)
    m = len(M)
    acc["cuts"] += 1

    for f in M:
        comp = comp_of[f]
        for Q in cyc[f]:
            svals = [sum((p[g][v] for g in comp), F(0)) for v in Q]
            acc["rows"] += 1
            cert = find_integer_widths(svals, n, m)
            if cert is None:
                acc["fail"] += 1
                rec = {
                    "name": name,
                    "n": n,
                    "m": m,
                    "f": f,
                    "Q": tuple(Q),
                    "svals": tuple(svals),
                    "D": F(n * n, 25) - m,
                }
                if acc["first_fail"] is None:
                    acc["first_fail"] = rec
                if stop_first:
                    return False
            else:
                w, eps = cert
                acc["ok"] += 1
                if acc["first_cert"] is None:
                    acc["first_cert"] = (name, n, m, tuple(Q), w, eps)
    return True


def run_gmins(name, n, edges, max_cuts, acc, stop_first=False):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        if not check_cut(name, n, edges, side, acc, stop_first):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--max-cuts", type=int, default=4)
    ap.add_argument("--two-lane-max", type=int, default=20)
    ap.add_argument("--blowup-t", type=int, default=3)
    ap.add_argument("--blowup-nmax", type=int, default=26)
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--skip-two-lane", action="store_true")
    ap.add_argument("--skip-blowups", action="store_true")
    ap.add_argument("--skip-named", action="store_true")
    ap.add_argument("--stop-first", action="store_true")
    args = ap.parse_args()

    acc = {"cuts": 0, "rows": 0, "ok": 0, "fail": 0, "first_fail": None, "first_cert": None}

    if not args.skip_two_lane:
        for L in range(8, args.two_lane_max + 1, 2):
            n, edges, side, _bad = build_two_lane(L)
            if not check_cut(f"two-lane-L{L}", n, edges, side, acc, args.stop_first):
                break

    if not args.skip_blowups and not (args.stop_first and acc["first_fail"]):
        for c in (5, 7, 9):
            for t in range(1, args.blowup_t + 1):
                n, edges = blowup([t] * c)
                if n <= args.blowup_nmax:
                    if not check_cut(f"direct-C{c}[{t}]", n, edges, cycle_blowup_side([t] * c), acc, args.stop_first):
                        break
            if args.stop_first and acc["first_fail"]:
                break

    if not args.skip_named and not (args.stop_first and acc["first_fail"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for name, (n, edges) in named:
            if not run_gmins(name, n, edges, args.max_cuts, acc, args.stop_first):
                break

    if not args.skip_census and not (args.stop_first and acc["first_fail"]):
        for nn in range(args.min_n, args.max_n + 1):
            for g6 in __import__('subprocess').run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                if not run_gmins(f"cen{g6}", n, edges, args.max_cuts, acc, args.stop_first):
                    break
            if args.stop_first and acc["first_fail"]:
                break

    print("=== DW-Hall integer-width gate ===")
    for k in ("cuts", "rows", "ok", "fail"):
        print(f"{k}: {acc[k]}")
    print("first_cert:", acc["first_cert"] or "")
    print("first_fail:", acc["first_fail"] or "")
    print("VERDICT:", "HOLDS" if acc["fail"] == 0 else "FAILS")


if __name__ == "__main__":
    main()