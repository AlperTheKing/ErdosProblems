"""Guardrail for the local/global distinction in UNIT-FLAT5-OVERLAP.

The local Flat5 overlap-pair atom has two counted length-5 rows, but it does
not require the whole graph to have m=2 bad edges.  This script glues an extra
C5 component to the N=10 local witness by a blue bridge and checks that the
same local atom survives with global m=3.
"""

from __future__ import annotations

import contextlib
import io
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import dec
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch
    from _codex_slack_cage_prebank_classifier import classify_case, subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, sigma_of


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def fmt(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def main() -> None:
    base_g6 = "I?AAD@wF_"
    base_side = "0000011110"
    n0, base_edges = dec(base_g6)
    assert n0 == 10

    # Add a C5 on vertices 10..14 with cut pattern 0,1,0,1,0.
    # Edges 10-11-12-13-14 are blue and 10-14 is bad.  The bridge 0-11 is
    # blue and is not incident to the local U below.
    extra_edges = [
        norm_edge(10, 11),
        norm_edge(11, 12),
        norm_edge(12, 13),
        norm_edge(13, 14),
        norm_edge(10, 14),
        norm_edge(0, 11),
    ]
    edges = [norm_edge(u, v) for u, v in base_edges] + extra_edges
    n = 15
    side = [int(c) for c in base_side + "01010"]

    data = build_data(n, edges, side)
    if data is None:
        raise SystemExit("FAIL: glued graph did not build connected-B data")
    E, B, M, Mset, cyc = data

    Q = (3, 8, 1, 6, 9)
    U = frozenset((1, 3, 4, 6, 8, 9))
    eta = F(n * n, 25) - len(M)
    tw = subset_tw(n, M, cyc, U)
    lhs = sum(tw[v] for v in Q)
    sig = sigma_of(U, B, Mset)
    pre = lhs - len(U) - sig
    rows = counted_rows(Q, U, M, cyc)

    row_lengths = sorted(len(P) for _g, P, _pset in rows)
    row_denoms = sorted(len(cyc[g]) for g, _P, _pset in rows)
    row_sets = [set(P) for _g, P, _pset in rows]
    union = set().union(*row_sets)
    pair_inter = len(row_sets[0] & row_sets[1]) if len(row_sets) == 2 else None

    _switches, zero, strict, _flat = classify_case(n, E, B, Mset, Q, U, rows)
    flat5_banks = []
    for sig_s, dg, Stuple in zero:
        if sig_s != 0 or dg != 0 or not is_flat5_switch(n, E, B, Mset, Stuple):
            continue
        S = frozenset(Stuple)
        U_after = frozenset(v for v in U if v not in S)
        tw_after = subset_tw(n, M, cyc, U_after)
        pre_after = sum(tw_after[v] for v in Q) - len(U_after) - sigma_of(U_after, B, Mset)
        bank = max(F(0), pre) - max(F(0), pre_after)
        flat5_banks.append((tuple(sorted(S)), pre_after, bank))

    expected = {
        "n": 15,
        "m": 3,
        "eta": F(6),
        "lhs": F(9),
        "sigma": 2,
        "prebank": F(1),
        "counted_rows": 2,
        "row_lengths": [5, 5],
        "row_denoms": [1, 1],
        "union_eq_U": True,
        "pair_inter": 4,
        "has_flat5_bank_1": True,
    }
    observed = {
        "n": n,
        "m": len(M),
        "eta": eta,
        "lhs": lhs,
        "sigma": sig,
        "prebank": pre,
        "counted_rows": len(rows),
        "row_lengths": row_lengths,
        "row_denoms": row_denoms,
        "union_eq_U": union == set(U),
        "pair_inter": pair_inter,
        "has_flat5_bank_1": any(bank == 1 for _S, _after, bank in flat5_banks),
    }

    print("=== UNIT-FLAT5 local/global guardrail ===")
    for key in expected:
        print(f"{key}: {fmt(observed[key])}")
    print("counted:", [(g, P) for g, P, _pset in rows])
    print("flat5_banks:", [(S, fmt(after), fmt(bank)) for S, after, bank in flat5_banks])
    print("strict_zero_slack:", strict)

    failures = [key for key, val in expected.items() if observed[key] != val]
    if failures:
        raise SystemExit(f"FAIL_UNIT_ATOM_GUARDRAIL: {failures}")
    print("VERDICT = PASS_UNIT_ATOM_LOCAL_NOT_GLOBAL_M2")


if __name__ == "__main__":
    main()
