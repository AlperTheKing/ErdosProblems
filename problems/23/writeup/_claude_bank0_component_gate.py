"""Bank0 census gate (B1 final repair, 2026-07-03).

Bank0: N^2 - 25m >= 0 (eta >= 0) whenever every bad edge of a B-connected
gamma-min max cut has ell = 5 (the pure all-length-5 case; any L > 5 row
already yields eta >= (L^2-25)/25 > 0 via Branch-B Bank-L, so Bank0 = the
missing L=5 member of the Bank-L family).

Checks per gamma-min max cut (exact Fractions):
  GLOBAL : if M nonempty and ALL bad edges have ell = 5  =>  25 m <= N^2.
  LOCAL  : every all-l5 positive K-component C satisfies m_C <= |supp C|^2 / 25
           (the form the C5-hom prefix-product AM-GM proves; checked on ALL
           all-l5 components to probe whether the non-C5-hom branch needs a
           weaker form).
  DISJ   : component supports are pairwise disjoint (definitional via the
           union-find; asserted as an invariant).
Also reported (diagnostic, not a fail): local-bank violations on components
that are NOT all-l5, and mixed cuts (some l5 component + longer rows).
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
    supp, _p = supports_and_p(n, M, cyc)
    comp_of = components(M, supp)

    m = len(M)
    acc["cuts"] += 1

    comps = {}
    for f in M:
        key = tuple(sorted(comp_of[f]))
        comps[key] = key

    seen_supports = []
    all_l5_cut = all(ell[g] == 5 for g in M)

    for key in comps:
        cedges = list(key)
        csupp = set()
        for g in cedges:
            csupp |= supp[g]
        seen_supports.append(csupp)
        m_c = len(cedges)
        all5 = all(ell[g] == 5 for g in cedges)
        acc["comps"] += 1
        local_ok = F(25 * m_c) <= F(len(csupp)) ** 2
        if all5:
            acc["l5_comps"] += 1
            if not local_ok:
                acc["local_fails"] += 1
                if acc["first_local_fail"] is None:
                    acc["first_local_fail"] = (name, side_str(side), m_c, len(csupp))
            margin = F(len(csupp)) ** 2 - 25 * m_c
            if margin < acc["min_local_margin"][0]:
                acc["min_local_margin"] = (margin, name, m_c, len(csupp))
        else:
            if not local_ok:
                acc["non5_local_viol"] += 1
                if acc["first_non5_viol"] is None:
                    acc["first_non5_viol"] = (name, side_str(side), m_c, len(csupp))

    # DISJ invariant
    tot = sum(len(s) for s in seen_supports)
    uni = set().union(*seen_supports) if seen_supports else set()
    if tot != len(uni):
        acc["disj_fails"] += 1
        if acc["first_disj_fail"] is None:
            acc["first_disj_fail"] = (name, side_str(side))

    if all_l5_cut:
        acc["pure_l5_cuts"] += 1
        gmargin = F(n) ** 2 - 25 * m
        if gmargin < acc["min_global_margin"][0]:
            acc["min_global_margin"] = (gmargin, name, n, m)
        if gmargin < 0:
            acc["global_fails"] += 1
            if acc["first_global_fail"] is None:
                acc["first_global_fail"] = (name, side_str(side), n, m)
    elif any(ell[g] == 5 for g in M):
        acc["mixed_cuts"] += 1


def side_str(side):
    return "".join(map(str, side))


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
        "comps": 0,
        "l5_comps": 0,
        "pure_l5_cuts": 0,
        "mixed_cuts": 0,
        "global_fails": 0,
        "local_fails": 0,
        "non5_local_viol": 0,
        "disj_fails": 0,
        "first_global_fail": None,
        "first_local_fail": None,
        "first_non5_viol": None,
        "first_disj_fail": None,
        "min_global_margin": (F(10**18), None, None, None),
        "min_local_margin": (F(10**18), None, None, None),
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
            out = subprocess.run(
                [GENG, "-tc", str(nn)], capture_output=True, text=True, check=True
            ).stdout
            for g6 in out.split():
                n, edges = dec(g6)
                run_gmins(f"cen:{g6}", n, edges, args.max_cuts, acc)

    print("=== Bank0 component gate ===")
    for k in (
        "cuts", "comps", "l5_comps", "pure_l5_cuts", "mixed_cuts",
        "global_fails", "local_fails", "non5_local_viol", "disj_fails",
    ):
        print(f"{k}: {acc[k]}")
    print("min_global_margin (pure-l5 cuts):", acc["min_global_margin"])
    print("min_local_margin (l5 comps):", acc["min_local_margin"])
    for k in ("first_global_fail", "first_local_fail", "first_non5_viol", "first_disj_fail"):
        print(f"{k}: {acc[k]}")
    verdict = "FAIL" if (acc["global_fails"] or acc["local_fails"] or acc["disj_fails"]) else "PASS"
    print("VERDICT:", verdict)


if __name__ == "__main__":
    main()
