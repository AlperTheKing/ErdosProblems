"""Inactive-slack monomial branching for SIB-S7 y=1,u=1 terminal supports.

This exact pruning artifact extends the deterministic inactive-inequality pass.
If an inactive slack, shifted by currently forced lower-bound labels, has all
coefficients nonpositive and zero constant, then slack >= 0 forces every
nonzero monomial to vanish.  For each such monomial, at least one variable in
that monomial is at its lower bound; we branch over those lower-bound labels.

This is a u1-scoped targeting gate, not a global S7 closure proof.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache

import sympy as sp

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_far_support_linear_filter as lin
import _codex_sib_s7_y1_terminal_rank_profile as rankprof
import _codex_sib_s7_y1_u1_inactive_ineq_closure as inactive


MAX_TERMINALS_PER_START = 512


def inactive_ineq_clauses(support: frozenset[str]) -> tuple[frozenset[str], ...]:
    fixed_labels = frozenset(label for label in support if label in lin.LOWER_LABEL_TO_VAR)
    clauses: set[frozenset[str]] = set()
    for label in lin.SLACK_LABELS:
        if label in support:
            continue
        poly, remaining = lin.shifted_poly(lin.EQUATION_EXPR[label], fixed_labels)
        if poly is None or poly.is_zero:
            continue
        coeffs = [sp.Rational(coeff) for coeff in poly.coeffs()]
        const = sp.Rational(poly.coeff_monomial(1))
        if const != 0 or not lin.all_nonpositive(coeffs):
            continue
        for monom, coeff in poly.terms():
            if coeff == 0 or sum(monom) == 0:
                continue
            labels = frozenset(lin.VAR_TO_LOWER_LABEL[remaining[idx]] for idx, exp in enumerate(monom) if exp > 0)
            missing = labels - support
            if missing:
                clauses.add(missing)
    return tuple(sorted(clauses, key=lambda item: (len(item), sorted(item))))


def choose_clause(support: frozenset[str]) -> frozenset[str] | None:
    clauses = inactive_ineq_clauses(support)
    if not clauses:
        return None
    return clauses[0]


@lru_cache(maxsize=None)
def terminal_states(branch: str, cap: str, support_tuple: tuple[str, ...]) -> tuple[tuple[str, tuple[str, ...]], ...]:
    status, closure = inactive.close_support(branch, cap, support_tuple)
    if status == "contradiction":
        return (("contradiction", tuple(sorted(closure))),)
    if lin.observed_closure_class(branch, cap, closure) == "closes_to_observed_basis":
        return (("closes_to_observed_basis", tuple(sorted(closure))),)

    clause = choose_clause(closure)
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
    starts = sorted(rankprof.collect_unique_still("u1", None))
    assert len(starts) == 20152

    start_status: Counter[str] = Counter()
    terminal_counts: Counter[str] = Counter()
    by_cap: Counter[tuple[str, str]] = Counter()
    max_terminals = 0
    still_unique: set[tuple[str, str, tuple[str, ...]]] = set()
    examples: dict[str, tuple[str, tuple[str, ...]]] = {}

    for branch, cap, support_tuple in starts:
        terminals = terminal_states(branch, cap, support_tuple)
        max_terminals = max(max_terminals, len(terminals))
        statuses = {status for status, _closure in terminals}
        if statuses <= {"contradiction", "closes_to_observed_basis"}:
            start_status["all_branches_closed"] += 1
        elif "branch_explosion" in statuses:
            start_status["branch_explosion"] += 1
        else:
            start_status["has_unobserved_terminal"] += 1

        for status, closure in terminals:
            terminal_counts[status] += 1
            by_cap[(cap, status)] += 1
            examples.setdefault(status, (cap, closure))
            if status == "still_unobserved":
                still_unique.add((branch, cap, closure))

    print("U1-INACTIVE-MONOMIAL-START " + " ".join(f"{key}={start_status[key]}" for key in sorted(start_status)))
    print("U1-INACTIVE-MONOMIAL-TERMINALS " + " ".join(f"{key}={terminal_counts[key]}" for key in sorted(terminal_counts)))
    print(f"U1-INACTIVE-MONOMIAL-UNIQUE-STILL={len(still_unique)} max_terminals_per_start={max_terminals}")
    for cap in census.CAPS:
        pieces = []
        for status in ("contradiction", "closes_to_observed_basis", "still_unobserved", "branch_explosion"):
            pieces.append(f"{status}={by_cap[(cap, status)]}")
        print(f"U1-INACTIVE-MONOMIAL-CAP cap={cap} " + " ".join(pieces))
    for status, (cap, closure) in sorted(examples.items()):
        print(f"U1-INACTIVE-MONOMIAL-EXAMPLE {status} cap={cap} closure={','.join(closure)}")
    print("PASS u1 terminal supports filtered by inactive-slack monomial branching")


if __name__ == "__main__":
    main()
