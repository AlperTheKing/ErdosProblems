#!/usr/bin/env python3
"""Exact obstruction to a generic positivity-preserving box-spline proof.

The computation is over Q and uses only the standard library.  It checks a
nonnegative polynomial in the type-A4 Dahmen--Micchelli space on which the
Todd operator has negative homogeneous coefficients.
"""

from fractions import Fraction
from itertools import combinations
from math import factorial


N_VERTICES = 5
ROOTS = tuple(combinations(range(N_VERTICES), 2))

# The covector L has vertex potentials (1,0,1,1,0).  Thus
# L(e_i-e_j) is in {0,+1,-1} for every positive A4 root.
POTENTIAL = (1, 0, 1, 1, 0)
ROOT_VALUES = tuple(POTENTIAL[i] - POTENTIAL[j] for i, j in ROOTS)


def cut_edges(subset):
    subset = frozenset(subset)
    return tuple(
        (i, j)
        for i, j in ROOTS
        if (i in subset) != (j in subset)
    )


def multiply_truncated(left, right, degree):
    out = [Fraction(0) for _ in range(degree + 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= degree:
                out[i + j] += a * b
    return out


def todd_series_on_line(degree=4):
    """Return prod_alpha Todd(z L(alpha)) through z**degree."""
    series = [Fraction(1)]
    for value in ROOT_VALUES:
        # x/(1-exp(-x)) = 1+x/2+x^2/12-x^4/720+O(x^5).
        factor = [
            Fraction(1),
            Fraction(value, 2),
            Fraction(value * value, 12),
            Fraction(0),
            Fraction(-(value**4), 720),
        ]
        series = multiply_truncated(series, factor, degree)
    return tuple(series)


def main():
    assert ROOT_VALUES == (1, 0, 0, 1, -1, -1, 0, 0, 1, 1)

    # For A4, cocircuits of the graphic configuration are nontrivial cuts of
    # K5.  A cut has size 4 or 6.  On p=L^4, cuts of size >4 annihilate by
    # degree.  Every size-4 cut is a vertex star and contains an edge on which
    # L is zero.  Hence every cocircuit differential operator annihilates p,
    # proving p is in D(Phi+).
    checked_cuts = 0
    for size in range(1, N_VERTICES):
        for subset in combinations(range(N_VERTICES), size):
            # Count a cut only once, choosing the representative containing 0.
            if 0 not in subset:
                continue
            cut = cut_edges(subset)
            assert len(cut) in (4, 6)
            if len(cut) == 4:
                product = 1
                for i, j in cut:
                    product *= POTENTIAL[i] - POTENTIAL[j]
                assert product == 0
            checked_cuts += 1
    assert checked_cuts == 15

    series = todd_series_on_line()
    assert series == (
        Fraction(1),
        Fraction(1),
        Fraction(1, 4),
        Fraction(-1, 12),
        Fraction(-1, 20),
    )

    # Acting on p=L^4 and evaluating at L(x)=N multiplies the order-k symbol
    # coefficient by 4!/(4-k)!.
    output = tuple(
        series[k] * Fraction(factorial(4), factorial(4 - k))
        for k in range(5)
    )
    assert output == (
        Fraction(1),
        Fraction(4),
        Fraction(3),
        Fraction(-2),
        Fraction(-6, 5),
    )

    print("PASS")
    print("A4_positive_roots=10")
    print(f"cocircuit_cuts_checked={checked_cuts}")
    print("p=L^4 is globally nonnegative and belongs to D(Phi+)")
    print("Todd(D)p at L(x)=N: N^4 + 4*N^3 + 3*N^2 - 2*N - 6/5")


if __name__ == "__main__":
    main()
