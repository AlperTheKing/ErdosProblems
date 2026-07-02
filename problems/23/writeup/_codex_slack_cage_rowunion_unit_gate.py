"""Row-union stress gate for the UNIT-FLAT5 bank branch.

This avoids all-subset enumeration.  For each tested connected-B cut, it only
checks candidate sets U that are the union of one or two shortest rows and
contain the fixed row Q.  This targets the observed positive-prebank Flat5
atom, while allowing long-row row-union cases that are directly eta-paid:

    two length-5 counted rows, unique geodesics, intersection 4,
    U = row union, prebank = 1, and a Flat5 peel consumes the positive part.

The gate is a falsifier/stress test, not a proof.
"""

from __future__ import annotations

import argparse
import contextlib
import io
from collections import Counter
from fractions import Fraction as F
from itertools import combinations

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _codex_slack_cage_banked_flat_gate import is_flat5_switch
    from _codex_slack_cage_prebank_classifier import classify_case, subset_tw
    from _codex_slack_cage_switch_gate import build_data, counted_rows, sigma_of
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def fmt_frac(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def unit_flat5_signature(n, E, B, M, Mset, cyc, Q, U, rows):
    row_lengths = sorted(len(P) for _g, P, _pset in rows)
    row_denoms = sorted(len(cyc[g]) for g, _P, _pset in rows)
    row_sets = [set(P) for _g, P, _pset in rows]
    union = set().union(*row_sets) if row_sets else set()
    pair_inter = None
    if len(row_sets) == 2:
        pair_inter = len(row_sets[0] & row_sets[1])

    pre_tw = subset_tw(n, M, cyc, U)
    pre = sum(pre_tw[v] for v in Q) - len(U) - sigma_of(U, B, Mset)

    fast_shape = (
        pre == 1
        and len(rows) == 2
        and row_lengths == [5, 5]
        and row_denoms == [1, 1]
        and len(U) == 6
        and union == set(U)
        and pair_inter == 4
    )

    if not fast_shape:
        return {
            "is_unit": False,
            "pre": pre,
            "row_lengths": row_lengths,
            "row_denoms": row_denoms,
            "rows": len(rows),
            "union_eq_U": union == set(U),
            "pair_inter": pair_inter,
            "zero": None,
            "strict": None,
            "flat5_banks": [],
            "fast_shape": False,
        }

    _switches, zero, strict, _flat = classify_case(n, E, B, Mset, Q, U, rows)

    flat5_banks = []
    for sig, dg, Stuple in zero:
        if sig != 0 or dg != 0 or not is_flat5_switch(n, E, B, Mset, Stuple):
            continue
        S = frozenset(Stuple)
        U_after = frozenset(v for v in U if v not in S)
        tw_after = subset_tw(n, M, cyc, U_after)
        pre_after = sum(tw_after[v] for v in Q) - len(U_after) - sigma_of(U_after, B, Mset)
        bank = max(F(0), pre) - max(F(0), pre_after)
        flat5_banks.append((tuple(sorted(S)), pre_after, bank))

    is_unit = (
        pre == 1
        and len(rows) == 2
        and row_lengths == [5, 5]
        and row_denoms == [1, 1]
        and len(U) == 6
        and union == set(U)
        and pair_inter == 4
        and not strict
        and any(bank == 1 and pre_after <= 0 for _S, pre_after, bank in flat5_banks)
    )
    return {
        "is_unit": is_unit,
        "pre": pre,
        "row_lengths": row_lengths,
        "row_denoms": row_denoms,
        "rows": len(rows),
        "union_eq_U": union == set(U),
        "pair_inter": pair_inter,
        "zero": len(zero),
        "strict": len(strict),
        "flat5_banks": flat5_banks,
        "fast_shape": True,
    }


def candidate_unions_for_Q(all_rows, Q, max_rows):
    qset = set(Q)
    touching = []
    for g, P, pset in all_rows:
        if pset & qset:
            touching.append((g, P, pset))
    seen = set()
    qU = frozenset(Q)
    seen.add(qU)
    yield qU
    max_rows = max(1, max_rows)
    for r in range(1, max_rows + 1):
        for combo in combinations(touching, r):
            U = frozenset().union(*(pset for _g, _P, pset in combo))
            if U in seen:
                continue
            seen.add(U)
            yield U


def check_side(name, n, edges, side, max_candidates, max_union_rows, acc, verbose=True):
    data = build_data(n, edges, [int(c) for c in side])
    if data is None:
        return
    E, B, M, Mset, cyc = data
    if not M:
        return
    eta = F(n * n, 25) - len(M)
    all_rows = [(g, tuple(P), frozenset(P)) for g in M for P in cyc[g]]
    seen_cases = set()
    local_candidates = 0
    for f in M:
        for Q in cyc[f]:
            for U in candidate_unions_for_Q(all_rows, Q, max_union_rows):
                if not U or len(U) == n:
                    continue
                key = (tuple(Q), tuple(sorted(U)))
                if key in seen_cases:
                    continue
                seen_cases.add(key)
                if max_candidates is not None and local_candidates >= max_candidates:
                    break
                local_candidates += 1
                acc["candidates"] += 1
                tw = subset_tw(n, M, cyc, U)
                lhs = sum(tw[v] for v in Q)
                sig = sigma_of(U, B, Mset)
                pre = lhs - len(U) - sig
                if pre <= 0:
                    continue
                acc["positive"] += 1
                rows = counted_rows(Q, U, M, cyc)
                sigrec = unit_flat5_signature(n, E, B, M, Mset, cyc, tuple(Q), U, rows)
                margin = eta - pre
                if margin < acc["min_margin"][0]:
                    acc["min_margin"] = (margin, name, n, len(M), tuple(Q), tuple(sorted(U)), pre, eta)
                if margin >= 0:
                    acc["eta_paid"] += 1
                    if sigrec["is_unit"]:
                        acc["unit_eta_paid"] += 1
                    else:
                        acc["nonunit_eta_paid"] += 1
                        if acc["first_nonunit_eta_paid"] is None:
                            acc["first_nonunit_eta_paid"] = {
                                "name": name,
                                "n": n,
                                "m": len(M),
                                "eta": fmt_frac(eta),
                                "Q": tuple(Q),
                                "U": tuple(sorted(U)),
                                "pre": fmt_frac(pre),
                                "margin": fmt_frac(margin),
                                "sig": {
                                    k: (fmt_frac(v) if isinstance(v, F) else v)
                                    for k, v in sigrec.items()
                                    if k != "flat5_banks"
                                },
                            }
                    continue
                acc["fails"] += 1
                if acc["first_fail"] is None:
                    acc["first_fail"] = {
                        "name": name,
                        "n": n,
                        "m": len(M),
                        "eta": fmt_frac(eta),
                        "Q": tuple(Q),
                        "U": tuple(sorted(U)),
                        "lhs": fmt_frac(lhs),
                        "sigma": sig,
                        "pre": fmt_frac(pre),
                        "margin": fmt_frac(margin),
                        "counted": [(g, P) for g, P, _pset in rows],
                        "sig": {
                            k: (fmt_frac(v) if isinstance(v, F) else v)
                            for k, v in sigrec.items()
                            if k != "flat5_banks"
                        },
                        "flat5_banks": [
                            (S, fmt_frac(after), fmt_frac(bank))
                            for S, after, bank in sigrec["flat5_banks"]
                        ],
                    }
                return
            if acc["first_fail"]:
                return
    if verbose:
        print(f"{name}: rowunion_candidates={local_candidates} positive_so_far={acc['positive']} ok", flush=True)


def scan_gmins(name, n, edges, max_cuts, max_candidates, max_union_rows, acc, verbose=True):
    _adj, cuts = gmins(n, edges)
    for idx, side in enumerate(cuts[:max_cuts]):
        check_side(f"{name}#cut{idx}", n, edges, side, max_candidates, max_union_rows, acc, verbose=verbose)
        if acc["first_fail"]:
            return


def glued_guardrail_instance():
    n0, base_edges = __import__("_h").dec("I?AAD@wF_")
    assert n0 == 10
    extra_edges = [
        norm_edge(10, 11),
        norm_edge(11, 12),
        norm_edge(12, 13),
        norm_edge(13, 14),
        norm_edge(10, 14),
        norm_edge(0, 11),
    ]
    return "glued-local-Flat5-C5", 15, [norm_edge(u, v) for u, v in base_edges] + extra_edges, ["000001111001010"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--two-lane-max", type=int, default=24)
    ap.add_argument("--max-cuts", type=int, default=2)
    ap.add_argument("--max-candidates", type=int, default=None)
    ap.add_argument("--max-union-rows", type=int, default=2)
    ap.add_argument("--include-gmins-blowups", action="store_true")
    args = ap.parse_args()

    acc = {
        "candidates": 0,
        "positive": 0,
        "eta_paid": 0,
        "unit_eta_paid": 0,
        "nonunit_eta_paid": 0,
        "fails": 0,
        "first_fail": None,
        "first_nonunit_eta_paid": None,
        "min_margin": (F(10**18),),
    }

    families = [glued_guardrail_instance()]
    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _bad = build_two_lane(L)
        families.append((f"two-lane-L{L}", n, edges, [side]))

    for nm, (n, edges) in [
        ("Grotzsch", mycielski(5, Cn(5))),
        ("M(C7)", mycielski(7, Cn(7))),
        ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
    ]:
        families.append((nm, n, edges, None))

    if args.include_gmins_blowups:
        for parts in ([2, 1, 2, 1, 2], [3, 2, 3, 2, 3]):
            n, edges = blowup(parts)
            families.append((f"gmin-blowup-{parts}", n, edges, None))

    for name, n, edges, sides in families:
        if sides is None:
            scan_gmins(name, n, edges, args.max_cuts, args.max_candidates, args.max_union_rows, acc)
        else:
            for side in sides:
                check_side(name, n, edges, side, args.max_candidates, args.max_union_rows, acc)
                if acc["first_fail"]:
                    break
        if acc["first_fail"]:
            break

    print("=== row-union UNIT-FLAT5 bank gate ===")
    print("candidates:", acc["candidates"])
    print("positive:", acc["positive"])
    print("eta_paid:", acc["eta_paid"])
    print("unit_eta_paid:", acc["unit_eta_paid"])
    print("nonunit_eta_paid:", acc["nonunit_eta_paid"])
    print("fails:", acc["fails"])
    print("min_margin:", acc["min_margin"])
    print("first_nonunit_eta_paid:", acc["first_nonunit_eta_paid"] or "")
    print("first_fail:", acc["first_fail"] or "")
    print("VERDICT:", "PASS_ROWUNION_ETA_OR_UNIT" if acc["fails"] == 0 else "FAIL_ROWUNION_ETA_OR_UNIT")


if __name__ == "__main__":
    main()
