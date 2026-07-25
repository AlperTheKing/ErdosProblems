#!/usr/bin/env python3
"""Exact audit for the O(P_{7,7}) -> homogeneous Kostka/LR proposal.

The arithmetic part is dependency-free.  It reconstructs the h*-polynomial,
the Ehrhart polynomial, its negative linear coefficient, codegree, and the
data used in the two-row contingency-table obstruction.
"""

from fractions import Fraction
from math import comb, factorial


def eulerian(n: int) -> list[int]:
    row = [1]
    for m in range(2, n + 1):
        nxt = [0] * m
        for i, value in enumerate(row):
            nxt[i] += (i + 1) * value
            nxt[i + 1] += (m - i - 1) * value
        row = nxt
    return row


def convolution(a: list[int], b: list[int]) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def poly_mul(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def binomial_polynomial(shift: int, degree: int) -> list[Fraction]:
    """Coefficients of binomial(n+shift, degree), low degree first."""
    out = [Fraction(1)]
    for k in range(degree):
        out = poly_mul(out, [Fraction(shift - k), Fraction(1)])
    return [x / factorial(degree) for x in out]


def ehrhart_coefficients(hstar: list[int], dimension: int) -> list[Fraction]:
    out = [Fraction(0)] * (dimension + 1)
    for j, value in enumerate(hstar):
        term = binomial_polynomial(dimension - j, dimension)
        for k, coefficient in enumerate(term):
            out[k] += value * coefficient
    return out


def evaluate(coefficients: list[Fraction], n: int) -> Fraction:
    return sum(c * n**k for k, c in enumerate(coefficients))


def main() -> None:
    a7 = eulerian(7)
    hstar_short = convolution(a7, a7)
    dimension = 14
    hstar = hstar_short + [0] * (dimension + 1 - len(hstar_short))
    coefficients = ehrhart_coefficients(hstar, dimension)

    assert a7 == [1, 120, 1191, 2416, 1191, 120, 1]
    assert len(hstar_short) - 1 == 12
    assert coefficients[0] == 1
    assert coefficients[1] == Fraction(-3041, 1430)
    assert coefficients[14] == Fraction(1, 3432)
    assert evaluate(coefficients, 1) == 255
    assert evaluate(coefficients, -1) == 0
    assert evaluate(coefficients, -2) == 0
    assert evaluate(coefficients, -3) == 1

    codegree = dimension + 1 - (len(hstar_short) - 1)
    assert codegree == 3

    # O(P_{7,7}) has one vertex for every order ideal of the ordinal sum.
    # Ideals are a proper subset of the lower antichain, or the entire lower
    # antichain together with an arbitrary subset of the upper antichain.
    vertices = (2**7 - 1) + 2**7
    facets = 7 + 7 + 7 * 7
    assert vertices == 255
    assert facets == 63

    # Exact obstruction to the only standard parsimonious Kostka reduction.
    # A full-dimensional 2 x k table fibre has dimension k-1, so degree 14
    # forces k=15 after zero columns are deleted.  Its relative-interior
    # points at dilation 3 are positive bounded compositions.  A product of
    # k interval polynomials has an interior coefficient equal to one only at
    # an endpoint, so (up to row complementation) 3A=k and A=5.  At dilation
    # one, all 0/1 vectors of weight five are feasible because every surviving
    # column margin is at least one.  Hence the base count is at least C(15,5),
    # contradicting the required value 255.
    effective_columns = dimension + 1
    endpoint_row_sum = effective_columns // codegree
    table_base_lower_bound = comb(effective_columns, endpoint_row_sum)
    assert effective_columns == 15
    assert endpoint_row_sum == 5
    assert table_base_lower_bound == 3003
    assert table_base_lower_bound > evaluate(coefficients, 1)

    print("PASS")
    print("dimension=14 hstar_degree=12 codegree=3")
    print("a1=-3041/1430 L(1)=255 L(-1)=L(-2)=0 L(-3)=1")
    print("vertices=255 facets=63")
    print("two_row_kostka_min_base=3003 > 255")


if __name__ == "__main__":
    main()
