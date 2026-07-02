"""Exact lower-bound propagation filter for y=1 SIB-S7 far supports.

This is an algebraic prefilter, not a full FJ exclusion.  For every support
currently classified as `unobserved_far`, it applies only safe consequences of
the active equalities and variable lower bounds:

* active lower-bound labels set their variables equal to 1;
* a shifted linear equality with nonnegative or nonpositive coefficients either
  contradicts the lower bounds or forces all participating variables to 1;
* a shifted polynomial with all coefficients of one sign and a strict constant
  term contradicts the lower bounds.

The output records how many far supports are killed or deterministically close
to an observed basis after this exact propagation.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import combinations

import sympy as sp

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_fj_support_inventory as inv


LOWER_LABEL_TO_VAR = {
    "a1": inv.a,
    "b1": inv.b,
    "c1": inv.c,
    "d1": inv.d,
    "e1": inv.e,
    "f1": inv.f,
    "x1": inv.x,
    "u1": inv.u,
    "v1": inv.v,
}
VAR_TO_LOWER_LABEL = {var: label for label, var in LOWER_LABEL_TO_VAR.items()}
SHIFT_VARS = {var: sp.Symbol(f"T_{var}") for var in inv.VARS}
EQUATION_EXPR = {
    **{name: inv.SLACKS[name] for name in ("s1", "s2", "s3", "s4", "s5", "s6", "s7")},
    "xq": inv.BRANCH_EQ["xq"],
}
SLACK_LABELS = frozenset(("s1", "s2", "s3", "s4", "s5", "s6", "s7"))


def equation_labels(branch: str, cap: str, support: frozenset[str]) -> tuple[str, ...]:
    labels = {cap}
    if branch in {"s2", "s3", "xq"}:
        labels.add(branch)
    labels.update(label for label in support if label in SLACK_LABELS)
    return tuple(sorted(labels))


def shifted_poly(expr: sp.Expr, fixed_labels: frozenset[str]) -> tuple[sp.Poly | None, tuple[sp.Symbol, ...]]:
    fixed_vars = {LOWER_LABEL_TO_VAR[label] for label in fixed_labels}
    remaining = tuple(var for var in inv.VARS if var not in fixed_vars)
    fixed_subs = {var: 1 for var in fixed_vars}
    shifted_subs = {var: 1 + SHIFT_VARS[var] for var in remaining}
    shifted = sp.expand(expr.subs(fixed_subs).subs(shifted_subs))
    if not remaining:
        return None, ()
    shift_symbols = tuple(SHIFT_VARS[var] for var in remaining)
    return sp.Poly(shifted, *shift_symbols), remaining


def all_nonnegative(coeffs: list[sp.Rational]) -> bool:
    return all(coeff >= 0 for coeff in coeffs)


def all_nonpositive(coeffs: list[sp.Rational]) -> bool:
    return all(coeff <= 0 for coeff in coeffs)


@lru_cache(maxsize=None)
def analyze_equation(eq_label: str, fixed_labels_tuple: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    fixed_labels = frozenset(fixed_labels_tuple)
    expr = EQUATION_EXPR[eq_label]
    poly, remaining = shifted_poly(expr, fixed_labels)
    if poly is None:
        value = sp.factor(expr.subs({LOWER_LABEL_TO_VAR[label]: 1 for label in fixed_labels}))
        if value != 0:
            return "contradiction", ()
        return "ok", ()

    if poly.is_zero:
        return "ok", ()

    coeffs = [sp.Rational(coeff) for coeff in poly.coeffs()]
    const = sp.Rational(poly.coeff_monomial(1))
    nonneg = all_nonnegative(coeffs)
    nonpos = all_nonpositive(coeffs)

    if (nonneg and const > 0) or (nonpos and const < 0):
        return "contradiction", ()

    forced: list[str] = []
    if poly.total_degree() <= 1 and const == 0 and (nonneg or nonpos):
        for monom, coeff in poly.terms():
            if coeff == 0 or sum(monom) != 1:
                continue
            idx = monom.index(1)
            label = VAR_TO_LOWER_LABEL[remaining[idx]]
            if label not in fixed_labels:
                forced.append(label)
    return "ok", tuple(sorted(set(forced)))


def propagate(branch: str, cap: str, support: frozenset[str]) -> tuple[str, frozenset[str]]:
    eq_labels = equation_labels(branch, cap, support)
    fixed_labels = frozenset(label for label in support if label in LOWER_LABEL_TO_VAR)
    if branch == "u1":
        fixed_labels = fixed_labels | frozenset(("u1",))

    changed = True
    while changed:
        changed = False
        for eq_label in eq_labels:
            status, forced = analyze_equation(eq_label, tuple(sorted(fixed_labels)))
            if status == "contradiction":
                return "contradiction", support | fixed_labels
            new_fixed = fixed_labels | frozenset(forced)
            if new_fixed != fixed_labels:
                fixed_labels = new_fixed
                changed = True

    closure = support | fixed_labels
    return "alive", closure


def observed_closure_class(branch: str, cap: str, closure: frozenset[str]) -> str:
    bases = census.observed_for(branch, cap)
    if any(basis <= closure for _name, basis in bases):
        return "closes_to_observed_basis"
    return "still_unobserved"


def main() -> None:
    totals: Counter[str] = Counter()
    by_chart: Counter[tuple[str, str, str]] = Counter()
    closure_growth: Counter[int] = Counter()

    for branch in census.BRANCHES:
        for cap in census.CAPS:
            movable = sorted(set(census.LABELS) - census.fixed_labels(branch, cap))
            bases = census.observed_for(branch, cap)
            for r in range(8):
                for combo in combinations(movable, r):
                    support = frozenset(combo)
                    if census.classify(support, bases) != "unobserved_far":
                        continue
                    status, closure = propagate(branch, cap, support)
                    if status == "contradiction":
                        cls = "contradiction"
                    else:
                        cls = observed_closure_class(branch, cap, closure)
                        closure_growth[len(closure) - len(support)] += 1
                    totals[cls] += 1
                    by_chart[(branch, cap, cls)] += 1

    assert sum(totals.values()) == 182589
    print("LINEAR-FILTER-TOTAL " + " ".join(f"{key}={totals[key]}" for key in sorted(totals)))
    print("LINEAR-FILTER-GROWTH " + " ".join(f"{key}:{closure_growth[key]}" for key in sorted(closure_growth)))
    for branch in census.BRANCHES:
        for cap in census.CAPS:
            pieces = []
            for cls in ("contradiction", "closes_to_observed_basis", "still_unobserved"):
                pieces.append(f"{cls}={by_chart[(branch, cap, cls)]}")
            print(f"LINEAR-FILTER-CHART branch={branch} cap={cap} " + " ".join(pieces))
    print("PASS y=1 unobserved-far supports filtered by exact lower-bound propagation")


if __name__ == "__main__":
    main()
