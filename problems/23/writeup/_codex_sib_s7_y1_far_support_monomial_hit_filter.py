"""Exact monomial-hit branching filter for y=1 SIB-S7 far supports.

This is still a pruning/targeting artifact rather than a final closure proof.  It
extends `_codex_sib_s7_y1_far_support_linear_filter.py` by using the following
safe disjunctive consequence.

After active lower-bound labels are shifted to nonnegative variables, if an
active equality becomes a polynomial with all coefficients of one sign and zero
constant term, then every nonconstant monomial in that polynomial must vanish.
For each monomial, at least one of its variables is at its lower bound.  The
script branches on these forced lower-bound alternatives, propagates again, and
records the remaining terminal support states.
"""

from __future__ import annotations

from collections import Counter, deque
from functools import lru_cache
from itertools import combinations

import sympy as sp

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_far_support_linear_filter as lin


MAX_TERMINALS_PER_START = 256


def shifted_one_sign_clauses(eq_label: str, support: frozenset[str]) -> tuple[frozenset[str], ...]:
    fixed_labels = frozenset(label for label in support if label in lin.LOWER_LABEL_TO_VAR)
    expr = lin.EQUATION_EXPR[eq_label]
    poly, remaining = lin.shifted_poly(expr, fixed_labels)
    if poly is None or poly.is_zero:
        return ()

    coeffs = [sp.Rational(coeff) for coeff in poly.coeffs()]
    const = sp.Rational(poly.coeff_monomial(1))
    if const != 0:
        return ()
    if not (lin.all_nonnegative(coeffs) or lin.all_nonpositive(coeffs)):
        return ()

    clauses: set[frozenset[str]] = set()
    for monom, coeff in poly.terms():
        if coeff == 0 or sum(monom) == 0:
            continue
        labels = frozenset(lin.VAR_TO_LOWER_LABEL[remaining[idx]] for idx, exp in enumerate(monom) if exp > 0)
        if labels:
            clauses.add(labels)
    return tuple(sorted(clauses, key=lambda item: (len(item), sorted(item))))


def choose_branch_clause(branch: str, cap: str, support: frozenset[str]) -> frozenset[str] | None:
    eq_labels = lin.equation_labels(branch, cap, support)
    best: frozenset[str] | None = None
    for eq_label in eq_labels:
        for clause in shifted_one_sign_clauses(eq_label, support):
            missing = clause - support
            if not missing:
                continue
            if best is None or len(missing) < len(best):
                best = missing
    return best


@lru_cache(maxsize=None)
def terminal_states(branch: str, cap: str, support_tuple: tuple[str, ...]) -> tuple[tuple[str, tuple[str, ...]], ...]:
    start_support = frozenset(support_tuple)
    status, closure = lin.propagate(branch, cap, start_support)
    if status == "contradiction":
        return (("contradiction", tuple(sorted(closure))),)
    if lin.observed_closure_class(branch, cap, closure) == "closes_to_observed_basis":
        return (("closes_to_observed_basis", tuple(sorted(closure))),)

    clause = choose_branch_clause(branch, cap, closure)
    if clause is None:
        return (("still_unobserved", tuple(sorted(closure))),)

    out: set[tuple[str, tuple[str, ...]]] = set()
    for label in sorted(clause):
        child = frozenset(closure | frozenset((label,)))
        for state in terminal_states(branch, cap, tuple(sorted(child))):
            out.add(state)
            if len(out) > MAX_TERMINALS_PER_START:
                return (("branch_explosion", tuple(sorted(closure))),)
    return tuple(sorted(out))


def main() -> None:
    start_total = 0
    start_closed: Counter[str] = Counter()
    terminal_supports: set[tuple[str, str, tuple[str, ...]]] = set()
    terminal_counts: Counter[str] = Counter()
    by_chart: Counter[tuple[str, str, str]] = Counter()
    max_terminals = 0

    for branch in census.BRANCHES:
        for cap in census.CAPS:
            movable = sorted(set(census.LABELS) - census.fixed_labels(branch, cap))
            bases = census.observed_for(branch, cap)
            for r in range(8):
                for combo in combinations(movable, r):
                    support = frozenset(combo)
                    if census.classify(support, bases) != "unobserved_far":
                        continue
                    lin_status, lin_closure = lin.propagate(branch, cap, support)
                    if lin_status == "contradiction":
                        continue
                    if lin.observed_closure_class(branch, cap, lin_closure) == "closes_to_observed_basis":
                        continue

                    start_total += 1
                    terminals = terminal_states(branch, cap, tuple(sorted(lin_closure)))
                    max_terminals = max(max_terminals, len(terminals))
                    statuses = {status for status, _closure in terminals}
                    if statuses <= {"contradiction", "closes_to_observed_basis"}:
                        start_closed["all_branches_closed"] += 1
                    elif "branch_explosion" in statuses:
                        start_closed["branch_explosion"] += 1
                    else:
                        start_closed["has_unobserved_terminal"] += 1

                    for status, closure_tuple in terminals:
                        terminal_counts[status] += 1
                        by_chart[(branch, cap, status)] += 1
                        if status == "still_unobserved":
                            terminal_supports.add((branch, cap, closure_tuple))

    assert start_total == 150652
    print("MONOMIAL-HIT-START " + " ".join(f"{key}={start_closed[key]}" for key in sorted(start_closed)))
    print("MONOMIAL-HIT-TERMINALS " + " ".join(f"{key}={terminal_counts[key]}" for key in sorted(terminal_counts)))
    print(f"MONOMIAL-HIT-UNIQUE-STILL={len(terminal_supports)} max_terminals_per_start={max_terminals}")
    for branch in census.BRANCHES:
        for cap in census.CAPS:
            pieces = []
            for status in ("contradiction", "closes_to_observed_basis", "still_unobserved", "branch_explosion"):
                pieces.append(f"{status}={by_chart[(branch, cap, status)]}")
            print(f"MONOMIAL-HIT-CHART branch={branch} cap={cap} " + " ".join(pieces))
    print("PASS y=1 still-unobserved supports filtered by exact monomial-hit branching")


if __name__ == "__main__":
    main()
