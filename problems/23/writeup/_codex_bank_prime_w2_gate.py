#!/usr/bin/env python3
"""Exact bank-prime split-or-root gate on Claude's abstract W2 counterexample.

This is a scope guardrail, not a real-graph counterexample.  It proves that
`ClosedPositiveSplitOrRoot` cannot follow from the bare closure axioms and
legal-neighborhood partition alone.  Any surviving proof must use the real
forced-ell=5 cage/exchange geometry.
"""

from fractions import Fraction
from itertools import chain, combinations, product


A, B = "A", "B"
PA, PB = "pA", "pB"
SA, SB = "sA", "sB"

LEGAL = {(PA, SA), (PB, SB)}
CAP = {SA: Fraction(1), SB: Fraction(1)}
LOAD = {PA: Fraction(3), PB: Fraction(1)}


def powerset(xs):
    return [
        frozenset(c)
        for c in chain.from_iterable(combinations(xs, r) for r in range(len(xs) + 1))
    ]


def closure(shore):
    return frozenset({A, B}) if A in shore else frozenset(shore)


def exposed(shore):
    ports = set()
    if A in shore:
        ports.add(PA)
    if B in shore:
        ports.add(PB)
    return frozenset(ports)


def neighbors(ports):
    return frozenset(
        sink for sink in (SA, SB) if any((port, sink) in LEGAL for port in ports)
    )


def defect(ports):
    return sum((LOAD[p] for p in ports), Fraction(0)) - sum(
        (CAP[s] for s in neighbors(ports)), Fraction(0)
    )


shores = powerset([A, B])
closed_shores = [shore for shore in shores if closure(shore) == shore]
closed_ports = sorted({exposed(shore) for shore in closed_shores}, key=lambda p: (len(p), sorted(p)))

parent = frozenset({PA, PB})
proper_children = [ports for ports in closed_ports if ports < parent]
split_rows = []
for left, right in product(proper_children, repeat=2):
    slack = defect(left) + defect(right) - defect(parent)
    split_rows.append((left, right, slack))

best_left, best_right, best_split_slack = max(split_rows, key=lambda row: row[2])

# The legal-incidence partition has the two singleton root blocks.  The pA
# block is positive but not closed; pB is closed but has zero defect.
root_blocks = [frozenset({PA}), frozenset({PB})]
closed_positive_roots = [
    block for block in root_blocks if block in closed_ports and defect(block) > 0
]

assert defect(parent) == 2
assert closed_positive_roots == []
assert best_split_slack == -2

print(
    {
        "parent": sorted(parent),
        "parent_defect": str(defect(parent)),
        "closed_port_sets": [sorted(p) for p in closed_ports],
        "closed_positive_roots": [sorted(p) for p in closed_positive_roots],
        "best_split": [sorted(best_left), sorted(best_right)],
        "best_split_slack": str(best_split_slack),
        "split_or_root": False,
        "scope": "abstract W2 closure counterexample; not a real forced-ell5 cage",
    }
)
