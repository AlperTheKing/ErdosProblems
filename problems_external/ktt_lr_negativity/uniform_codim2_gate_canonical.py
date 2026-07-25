#!/usr/bin/env python3
"""Canonical fast runner for the exact uniform codimension-two audit.

The proof checks live in ``uniform_codim2_gate_repaired.py``.  This runner
replaces only its dense Smith-index scan by the equivalent sparse scan: hive
rows have support at most four, so a two-by-two minor can be nonzero only on
the union of the two supports.  It also exits as soon as the gcd becomes one.

The pre-existing ``uniform_codim2_gate.py`` is superseded because it treats
rank 3 as if a nonparallel pair had to exist and consequently aborts before
the applicable ranks are checked.
"""

from itertools import combinations
from math import gcd

import uniform_codim2_gate_repaired as audit


def sparse_saturation_index(left, right):
    support = [
        index
        for index, (x, y) in enumerate(zip(left, right))
        if x != 0 or y != 0
    ]
    divisor = 0
    for i, j in combinations(support, 2):
        divisor = gcd(
            divisor,
            abs(left[i] * right[j] - left[j] * right[i]),
        )
        if divisor == 1:
            return 1
    return divisor


def main():
    audit.saturation_index = sparse_saturation_index
    audit.main()


if __name__ == "__main__":
    main()
