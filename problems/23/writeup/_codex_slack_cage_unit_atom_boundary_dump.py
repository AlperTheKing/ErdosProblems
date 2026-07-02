"""Dump exact boundary data for the UNIT-FLAT5 bank atom.

This is a proof-discovery diagnostic.  It prints the local row-union atom,
the boundary of U, and the zero-slack Flat5 peels that consume one unit of
prebank.  The two built-in cases are:

* the N=10 census atom I?AAD@wF_;
* the same local atom glued to an extra C5 component, showing that the atom is
  local and does not require global m=2.
"""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch
    from _codex_slack_cage_prebank_classifier import classify_case, subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, delta, flip_blue, sigma_of


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def edge_list(edges):
    return "[" + ", ".join(str(tuple(e)) for e in sorted(edges)) + "]"


def build_base_case():
    g6 = "I?AAD@wF_"
    side = "0000011110"
    n, edges = dec(g6)
    return {
        "name": "base-N10-I?AAD@wF_",
        "n": n,
        "edges": [norm_edge(u, v) for u, v in edges],
        "side": [int(c) for c in side],
        "Q": (3, 8, 1, 6, 9),
        "U": frozenset((1, 3, 4, 6, 8, 9)),
    }


def build_glued_case():
    base = build_base_case()
    extra_edges = [
        norm_edge(10, 11),
        norm_edge(11, 12),
        norm_edge(12, 13),
        norm_edge(13, 14),
        norm_edge(10, 14),
        norm_edge(0, 11),
    ]
    return {
        "name": "glued-N15-local-Flat5-plus-C5",
        "n": 15,
        "edges": base["edges"] + extra_edges,
        "side": base["side"] + [0, 1, 0, 1, 0],
        "Q": base["Q"],
        "U": base["U"],
    }


def build_intended_fan_case():
    # Same shape as _codex_slack_cage_flat5_fan_stress.py at t=2.
    # This intended cut is a guardrail: it has the local UNIT-FLAT5 atom but
    # is not a true gmins cut.
    edges = [
        norm_edge(2, 3),
        norm_edge(3, 4),
        norm_edge(4, 5),
        norm_edge(0, 2),
        norm_edge(0, 5),
        norm_edge(1, 2),
        norm_edge(1, 5),
        norm_edge(6, 2),
        norm_edge(7, 5),
    ]
    return {
        "name": "intended-fan-t2-not-gmins",
        "n": 8,
        "edges": sorted(set(edges)),
        "side": [0, 0, 1, 0, 1, 0, 0, 1],
        "Q": (0, 2, 3, 4, 5),
        "U": frozenset((0, 1, 2, 3, 4, 5)),
    }


def dump_case(case):
    n = case["n"]
    data = build_data(n, case["edges"], case["side"])
    if data is None:
        raise SystemExit(f"could not build case {case['name']}")
    E, B, M, Mset, cyc = data
    Q = tuple(case["Q"])
    U = frozenset(case["U"])
    eta = F(n * n, 25) - len(M)
    tw = subset_tw(n, M, cyc, U)
    lhs = sum(tw[v] for v in Q)
    sig = sigma_of(U, B, Mset)
    pre = lhs - len(U) - sig
    rows = counted_rows(Q, U, M, cyc)
    row_sets = [frozenset(P) for _g, P, _pset in rows]
    common = set.intersection(*(set(s) for s in row_sets)) if row_sets else set()
    union = set().union(*(set(s) for s in row_sets)) if row_sets else set()
    switches, zero, strict, _flat = classify_case(n, E, B, Mset, Q, U, rows)

    print(f"=== {case['name']} ===")
    print("n:", n)
    print("side:", "".join(str(c) for c in case["side"]))
    print("m:", len(M))
    print("eta:", fmt(eta))
    print("M:", edge_list(Mset))
    print("Q:", Q)
    print("U:", tuple(sorted(U)))
    print("lhs:", fmt(lhs))
    print("sigma(U):", sig)
    print("pre:", fmt(pre))
    print("delta_B(U):", edge_list(delta(B, U)))
    print("delta_M(U):", edge_list(delta(Mset, U)))
    print("counted_rows:")
    for g, P, _pset in rows:
        print("  g=", g, "den=", len(cyc[g]), "P=", P)
    print("row_intersection:", tuple(sorted(common)))
    print("row_union:", tuple(sorted(union)))
    print("zero_switches:", len(zero))
    print("strict_switches:", len(strict))
    for sig_s, dg, Stuple in zero:
        S = frozenset(Stuple)
        flat5 = is_flat5_switch(n, E, B, Mset, Stuple)
        U_after = frozenset(v for v in U if v not in S)
        tw_after = subset_tw(n, M, cyc, U_after)
        pre_after = sum(tw_after[v] for v in Q) - len(U_after) - sigma_of(U_after, B, Mset)
        bank = max(F(0), pre) - max(F(0), pre_after)
        BS = flip_blue(E, B, S)
        MS = E - BS
        print("  S:", tuple(sorted(S)))
        print("    sigma(S):", sig_s, "DeltaGamma:", dg, "flat5:", flat5)
        print("    delta_B(S):", edge_list(delta(B, S)))
        print("    delta_M(S):", edge_list(delta(Mset, S)))
        print("    new_bad_cross:", edge_list(delta(B, S)))
        print("    pre_after:", fmt(pre_after), "bank:", fmt(bank))
        print("    M_after:", edge_list(MS))
    print()


def main():
    for case in (build_base_case(), build_glued_case(), build_intended_fan_case()):
        dump_case(case)


if __name__ == "__main__":
    main()
