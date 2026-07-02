"""Rank-shape profile for monomial-hit terminal SIB-S7 y=1 supports.

This is not a proof gate.  It profiles still-unobserved terminal support states
produced by `_codex_sib_s7_y1_far_support_monomial_hit_filter.py` by active
equality-gradient rank at a fixed exact generic point respecting active lower
bounds.  Use `--branch` and `--cap` for chart-scoped profiling.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations

import sympy as sp

import _codex_sib_s7_y1_basis_pruning_census as census
import _codex_sib_s7_y1_far_support_linear_filter as lin
import _codex_sib_s7_y1_far_support_monomial_hit_filter as hit
import _codex_sib_s7_y1_fj_support_inventory as inv


GENERIC_VALUES = {
    inv.a: sp.Integer(2),
    inv.b: sp.Integer(3),
    inv.c: sp.Integer(5),
    inv.d: sp.Integer(7),
    inv.e: sp.Integer(11),
    inv.f: sp.Integer(13),
    inv.x: sp.Integer(17),
    inv.u: sp.Integer(19),
    inv.v: sp.Integer(23),
}
ALL_EQUATIONS = {**{name: expr for name, expr in inv.SLACKS.items()}, "xq": inv.BRANCH_EQ["xq"]}
ALL_EQUATIONS.update({label: var - 1 for label, var in lin.LOWER_LABEL_TO_VAR.items()})
GRADIENTS = {label: tuple(sp.diff(expr, var) for var in inv.VARS) for label, expr in ALL_EQUATIONS.items()}


def active_equation_labels(branch: str, cap: str, support: frozenset[str]) -> tuple[str, ...]:
    labels = set(label for label in support if label in ALL_EQUATIONS)
    labels.add(cap)
    if branch in {"s2", "s3", "xq"}:
        labels.add(branch)
    elif branch == "u1":
        labels.add("u1")
    return tuple(sorted(labels))


def rank_fraction(rows: tuple[tuple[int, ...], ...]) -> int:
    mat = [[Fraction(value) for value in row] for row in rows if any(value != 0 for value in row)]
    rank = 0
    col = 0
    row_count = len(mat)
    col_count = len(inv.VARS)
    while rank < row_count and col < col_count:
        pivot = None
        for idx in range(rank, row_count):
            if mat[idx][col] != 0:
                pivot = idx
                break
        if pivot is None:
            col += 1
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        pv = mat[rank][col]
        mat[rank] = [value / pv for value in mat[rank]]
        for idx in range(row_count):
            if idx == rank or mat[idx][col] == 0:
                continue
            factor = mat[idx][col]
            mat[idx] = [a - factor * b for a, b in zip(mat[idx], mat[rank])]
        rank += 1
        col += 1
    return rank


@lru_cache(maxsize=None)
def rank_for_key(branch: str, cap: str, support_tuple: tuple[str, ...]) -> tuple[int, int, tuple[str, ...]]:
    support = frozenset(support_tuple)
    subs = dict(GENERIC_VALUES)
    for label in support:
        if label in lin.LOWER_LABEL_TO_VAR:
            subs[lin.LOWER_LABEL_TO_VAR[label]] = sp.Integer(1)
    if branch == "u1":
        subs[inv.u] = sp.Integer(1)

    labels = active_equation_labels(branch, cap, support)
    rows = []
    for label in labels:
        row = []
        for grad in GRADIENTS[label]:
            value = sp.Rational(grad.subs(subs))
            assert value.q == 1
            row.append(int(value))
        rows.append(tuple(row))
    return rank_fraction(tuple(rows)), len(labels), labels


def collect_unique_still(branch_filter: str | None, cap_filter: str | None) -> set[tuple[str, str, tuple[str, ...]]]:
    out: set[tuple[str, str, tuple[str, ...]]] = set()
    branches = (branch_filter,) if branch_filter else census.BRANCHES
    caps = (cap_filter,) if cap_filter else census.CAPS
    for branch in branches:
        for cap in caps:
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
                    for status, closure_tuple in hit.terminal_states(branch, cap, tuple(sorted(lin_closure))):
                        if status == "still_unobserved":
                            out.add((branch, cap, closure_tuple))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=census.BRANCHES)
    parser.add_argument("--cap", choices=census.CAPS)
    args = parser.parse_args()

    still = collect_unique_still(args.branch, args.cap)
    if args.branch is None and args.cap is None:
        assert len(still) == 84087

    rank_hist: Counter[int] = Counter()
    eq_count_hist: Counter[int] = Counter()
    by_chart_rank: Counter[tuple[str, str, int]] = Counter()
    examples: dict[int, tuple[str, str, tuple[str, ...], tuple[str, ...]]] = {}

    for branch, cap, support_tuple in sorted(still):
        rank, eq_count, labels = rank_for_key(branch, cap, support_tuple)
        rank_hist[rank] += 1
        eq_count_hist[eq_count] += 1
        by_chart_rank[(branch, cap, rank)] += 1
        examples.setdefault(rank, (branch, cap, support_tuple, labels))

    scope = f"branch={args.branch or 'ALL'} cap={args.cap or 'ALL'} unique={len(still)}"
    print("TERMINAL-RANK-SCOPE " + scope)
    print("TERMINAL-RANK-HIST " + " ".join(f"{rank}:{rank_hist[rank]}" for rank in sorted(rank_hist)))
    print("TERMINAL-EQCOUNT-HIST " + " ".join(f"{count}:{eq_count_hist[count]}" for count in sorted(eq_count_hist)))
    for branch in (args.branch,) if args.branch else census.BRANCHES:
        for cap in (args.cap,) if args.cap else census.CAPS:
            pieces = [f"r{rank}={by_chart_rank[(branch, cap, rank)]}" for rank in sorted(rank_hist)]
            print(f"TERMINAL-RANK-CHART branch={branch} cap={cap} " + " ".join(pieces))
    for rank, (branch, cap, support, labels) in sorted(examples.items()):
        print(f"TERMINAL-RANK-EXAMPLE rank={rank} branch={branch} cap={cap} support={','.join(support)} equations={','.join(labels)}")
    print("PASS y=1 monomial-hit terminal supports profiled by exact generic active-equation rank")


if __name__ == "__main__":
    main()
