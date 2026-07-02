"""Inactive-slack inequality closure for SIB-S7 y=1,u=1 terminal supports.

This exact pruning artifact extends the forced-zero slack closure by using
inactive slack inequalities.  After shifting currently unfixed variables by
their lower bounds, every slack must be nonnegative.  If an inactive slack has
all coefficients nonpositive and zero constant, then every linear negative term
must vanish; if the constant is negative, the support is contradictory.

Only deterministic linear forcing is used here.  Nonlinear monomial branching is
left to a later gate.
"""

from __future__ import annotations

from collections import Counter

import sympy as sp

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_far_support_linear_filter as lin
import _codex_sib_s7_y1_terminal_rank_profile as rankprof
import _codex_sib_s7_y1_u1_implied_slack_closure as implied


def inactive_ineq_forces(support: frozenset[str]) -> tuple[str, frozenset[str]]:
    fixed_labels = frozenset(label for label in support if label in lin.LOWER_LABEL_TO_VAR)
    forced: set[str] = set()
    for label in lin.SLACK_LABELS:
        if label in support:
            continue
        poly, remaining = lin.shifted_poly(lin.EQUATION_EXPR[label], fixed_labels)
        if poly is None:
            value = sp.Rational(lin.EQUATION_EXPR[label].subs({lin.LOWER_LABEL_TO_VAR[x]: 1 for x in fixed_labels}))
            if value < 0:
                return "contradiction", frozenset()
            continue
        if poly.is_zero:
            continue
        coeffs = [sp.Rational(coeff) for coeff in poly.coeffs()]
        const = sp.Rational(poly.coeff_monomial(1))
        if not lin.all_nonpositive(coeffs):
            continue
        if const < 0:
            return "contradiction", frozenset()
        if const != 0 or poly.total_degree() > 1:
            continue
        for monom, coeff in poly.terms():
            if coeff == 0 or sum(monom) != 1:
                continue
            idx = monom.index(1)
            forced.add(lin.VAR_TO_LOWER_LABEL[remaining[idx]])
    return "ok", frozenset(forced)


def close_support(branch: str, cap: str, support_tuple: tuple[str, ...]) -> tuple[str, frozenset[str]]:
    support = frozenset(support_tuple)
    while True:
        status, closure = implied.close_support(branch, cap, tuple(sorted(support)))
        if status == "contradiction":
            return "contradiction", closure
        ineq_status, forced = inactive_ineq_forces(closure)
        if ineq_status == "contradiction":
            return "contradiction", closure
        next_support = closure | forced
        if next_support == support:
            return "alive", closure
        support = next_support


def main() -> None:
    states = sorted(rankprof.collect_unique_still("u1", None))
    assert len(states) == 20152

    status_counts: Counter[str] = Counter()
    by_cap: Counter[tuple[str, str]] = Counter()
    growth: Counter[int] = Counter()
    forced_freq: Counter[str] = Counter()
    examples: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {}
    still_unique: set[tuple[str, str, tuple[str, ...]]] = set()

    for branch, cap, support_tuple in states:
        start = frozenset(support_tuple)
        status, closure = close_support(branch, cap, support_tuple)
        if status == "contradiction":
            cls = "contradiction"
        elif lin.observed_closure_class(branch, cap, closure) == "closes_to_observed_basis":
            cls = "closes_to_observed_basis"
        else:
            cls = "still_unobserved"
            still_unique.add((branch, cap, tuple(sorted(closure))))

        for label in closure - start:
            forced_freq[label] += 1
        growth[len(closure - start)] += 1
        status_counts[cls] += 1
        by_cap[(cap, cls)] += 1
        examples.setdefault(cls, (cap, support_tuple, tuple(sorted(closure))))

    print("U1-INACTIVE-INEQ " + " ".join(f"{key}={status_counts[key]}" for key in sorted(status_counts)))
    print(f"U1-INACTIVE-INEQ-STILL-UNIQUE={len(still_unique)}")
    print("U1-INACTIVE-INEQ-GROWTH " + " ".join(f"{key}:{growth[key]}" for key in sorted(growth)))
    print("U1-INACTIVE-INEQ-FORCED " + " ".join(f"{label}:{forced_freq[label]}" for label in sorted(forced_freq)))
    for cap in census.CAPS:
        pieces = []
        for cls in ("contradiction", "closes_to_observed_basis", "still_unobserved"):
            pieces.append(f"{cls}={by_cap[(cap, cls)]}")
        print(f"U1-INACTIVE-INEQ-CAP cap={cap} " + " ".join(pieces))
    for cls, (cap, support, closure) in sorted(examples.items()):
        print(f"U1-INACTIVE-INEQ-EXAMPLE {cls} cap={cap} support={','.join(support)} closure={','.join(closure)}")
    print("PASS u1 terminal supports closed under deterministic inactive-slack inequalities")


if __name__ == "__main__":
    main()
