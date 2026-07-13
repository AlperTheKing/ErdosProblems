"""Exact audit of the support-sensitive centered codegree identity."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, chain


def certificate(a_values, x_values):
    a = sorted(set(a_values))
    x = sorted(set(x_values))
    if not x:
        raise ValueError("X must be nonempty")

    m, h = len(a), len(x)
    nu = Counter(b - aa for aa, b in combinations(a, 2))
    rho = Counter(abs(xx - xp) for xx, xp in combinations(x, 2))
    z = sum(mult * (nu.get(d, 0) - 1) for d, mult in rho.items())

    degrees = Counter(aa - xx for aa in a for xx in x)
    support = len(degrees)
    centered = sum(
        (Fraction(degree) - Fraction(m * h, support)) ** 2
        for degree in degrees.values()
    )
    lhs = Fraction(support) * (
        1 + Fraction(m - 1, h) + Fraction(2 * z, h * h)
    ) - m * m
    rhs = Fraction(support, h * h) * centered
    assert lhs == rhs

    return {
        "m": m,
        "h": h,
        "support": support,
        "Z": z,
        "energy": sum(d * d for d in degrees.values()),
        "bound": Fraction(support) * (
            1 + Fraction(m - 1, h) + Fraction(2 * z, h * h)
        ),
        "variance_remainder": rhs,
    }


def powerset(values):
    values = tuple(values)
    return chain.from_iterable(combinations(values, r) for r in range(len(values) + 1))


def exhaustive_audit():
    checked = 0
    universe = range(1, 9)
    test_universe = range(-2, 4)
    for a in powerset(universe):
        for x in powerset(test_universe):
            if x:
                certificate(a, x)
                checked += 1
    return checked


def main():
    a69 = [1, 2, 8, 10, 13, 23, 27, 43, 47, 57, 60, 62, 68, 69]
    result = certificate(a69, range(16))
    assert result == {
        "m": 14,
        "h": 16,
        "support": 84,
        "Z": 120,
        "energy": 704,
        "bound": Fraction(231),
        "variance_remainder": Fraction(35),
    }
    print(f"N69 PASS: {result}")
    print(f"EXHAUSTIVE PASS: {exhaustive_audit()} pairs (A, X)")


if __name__ == "__main__":
    main()
