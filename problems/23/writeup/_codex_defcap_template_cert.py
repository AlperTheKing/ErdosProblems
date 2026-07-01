"""Exact certificate for the canonical deficient-cap atom.

This is a small, read-only verifier for the only deficient-cap pattern found in
the N<=10 census.  It does not prove the geometric classification; it pins down
the finite normal form that the classification should reduce to.
"""

from collections import Counter
from fractions import Fraction as F

from _h import Bconn, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset


CANONICAL_G6 = "I?AEBAwF_"


def residuals(n, st):
    M, _ell, T, _mu, cyc = st
    K2 = build_K2(n, M, cyc)
    return [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


def main():
    n, edges = dec(CANONICAL_G6)
    adj = adj_from_edges(n, edges)
    cases = []
    type_counter = Counter()
    min_global_R = None
    min_switch_R = None

    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        R = residuals(n, st)
        minR = min(R)
        min_global_R = minR if min_global_R is None else min(min_global_R, minR)

        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or det["psi"] <= 0:
                continue
            data = two_cap_data(det)
            if data is None:
                continue
            fset, eset, exits_of_f, leaves = data
            bad = deficient_cap_subset(leaves, exits_of_f, fset)
            if bad is None:
                continue

            witnesses = {e: tuple(sorted(set(det["witnesses"][e]))) for e in sorted(eset)}
            lens = tuple(sorted(ell[f] for f in fset))
            wit_sizes = tuple(sorted(len(witnesses[e]) for e in witnesses))
            assert lens == (5, 7), (lens, fset)
            assert wit_sizes == (1, 2), (wit_sizes, witnesses)
            assert det["psi"] == 24, det["psi"]
            assert bad[2] == 0, bad
            assert len(bad[0]) == 1 and len(bad[1]) == 1, bad

            s_vertices = tuple(i for i in range(n) if (mask >> i) & 1)
            rs = tuple(R[v] for v in s_vertices)
            assert min(rs) >= 0, (side, s_vertices, rs)
            min_switch_R = min(rs) if min_switch_R is None else min(min_switch_R, min(rs))
            type_counter[(lens, wit_sizes, det["psi"], bad[2])] += 1
            cases.append((tuple(side), s_vertices, fset, tuple(sorted(eset)), bad))

    assert len(cases) == 16, len(cases)
    assert min_global_R is not None and min_global_R >= 0, min_global_R
    print("canonical:", CANONICAL_G6, "n=", n)
    print("edges:", edges)
    print("deficient_cases:", len(cases))
    print("type_counter:", dict(type_counter))
    print("min_global_R:", min_global_R)
    print("min_switch_R:", min_switch_R)
    print("VERDICT: PASS")


if __name__ == "__main__":
    main()
