#!/usr/bin/env python3
"""Independent exact experiments for the V6 full symmetric family.

This intentionally starts from the projected unit-column model.  It does not
reuse the proposed bivariate closed form.  All arithmetic is integral/rational.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import comb
from math import factorial


def c1_direct(a: int, k: int, n: int) -> int:
    """One specified row violates: sum x_j >= a*n+1."""
    cutoff = (k - a) * n - 1
    if cutoff < 0:
        return 0
    # Reverse x_j: u_j=n-x_j, with multiplicity u_j+1 for the other rows.
    dp = [0] * (cutoff + 1)
    dp[0] = 1
    for _ in range(k):
        nxt = [0] * (cutoff + 1)
        for old, multiplicity in enumerate(dp):
            if not multiplicity:
                continue
            for u in range(min(n, cutoff - old) + 1):
                nxt[old + u] += multiplicity * (u + 1)
        dp = nxt
    return sum(dp)


def single_violation_direct(cap: int, k: int, n: int) -> int:
    """One specified row exceeds cap*n, for an arbitrary positive cap."""
    cutoff = (k - cap) * n - 1
    if cutoff < 0:
        return 0
    dp = [0] * (cutoff + 1)
    dp[0] = 1
    for _ in range(k):
        nxt = [0] * (cutoff + 1)
        for old, multiplicity in enumerate(dp):
            if not multiplicity:
                continue
            for u in range(min(n, cutoff - old) + 1):
                nxt[old + u] += multiplicity * (u + 1)
        dp = nxt
    return sum(dp)


def pair_violation_direct(r1: int, r2: int, k: int, n: int) -> int:
    """Rows one and two exceed r1*n and r2*n, respectively."""
    cutoff_u = (k - r1) * n - 1
    cutoff_v = (k - r2) * n - 1
    if cutoff_u < 0 or cutoff_v < 0:
        return 0
    kernel = [
        (u, v)
        for u in range(n + 1)
        for v in range(n + 1)
        if u + v >= n
    ]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        nxt: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (old_u, old_v), multiplicity in states.items():
            for u, v in kernel:
                new_u, new_v = old_u + u, old_v + v
                if new_u <= cutoff_u and new_v <= cutoff_v:
                    nxt[(new_u, new_v)] += multiplicity
        states = dict(nxt)
    return sum(states.values())


def F(k: int, cap: int) -> Fraction:
    """Closed linear correction for one cap."""
    if cap >= k:
        return Fraction(0)
    return sum(
        (Fraction(t, cap + t) for t in range(1, k - cap + 1)),
        Fraction(0),
    ) / 2


def asymmetric_formula(rows: tuple[int, int, int], k: int) -> Fraction:
    return (
        Fraction(3 * k, 2)
        - sum((F(k, r) for r in rows), Fraction(0))
        - sum(
            (
                F(k, rows[i] + rows[j])
                for i, j in ((0, 1), (0, 2), (1, 2))
            ),
            Fraction(0),
        )
    )


def asymmetric_ehrhart_direct(
    rows: tuple[int, int, int], k: int, n: int
) -> int:
    assert sum(rows) > k
    caps = tuple(r * n for r in rows)
    kernel = [
        (x, y)
        for x in range(n + 1)
        for y in range(n - x + 1)
    ]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        nxt: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (old_x, old_y), multiplicity in states.items():
            for x, y in kernel:
                new_x, new_y = old_x + x, old_y + y
                if new_x <= caps[0] and new_y <= caps[1]:
                    nxt[(new_x, new_y)] += multiplicity
        states = dict(nxt)
    return sum(
        multiplicity
        for (x, y), multiplicity in states.items()
        if k * n - x - y <= caps[2]
    )


def c2_direct(a: int, k: int, n: int) -> int:
    """Two specified rows violate, by a direct reversed two-row DP.

    For a unit-column triple (x,y,z), put u=n-x=y+z and
    v=n-y=x+z.  This is a bijection to 0<=u,v<=n and u+v>=n.
    Both row violations are exactly sum u,sum v <= (k-a)n-1.
    """
    cutoff = (k - a) * n - 1
    if cutoff < 0:
        return 0
    kernel = [
        (u, v)
        for u in range(n + 1)
        for v in range(n + 1)
        if u + v >= n
    ]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        nxt: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (old_u, old_v), multiplicity in states.items():
            for u, v in kernel:
                new_u, new_v = old_u + u, old_v + v
                if new_u <= cutoff and new_v <= cutoff:
                    nxt[(new_u, new_v)] += multiplicity
        states = dict(nxt)
    return sum(states.values())


def low_third_direct(a: int, k: int, n: int) -> int:
    """D_b: a specified row total is at most (k-2a)n-2."""
    cutoff = (k - 2 * a) * n - 2
    if cutoff < 0:
        return 0
    dp = [0] * (cutoff + 1)
    dp[0] = 1
    for _ in range(k):
        nxt = [0] * (cutoff + 1)
        for old, multiplicity in enumerate(dp):
            if not multiplicity:
                continue
            for z in range(min(n, cutoff - old) + 1):
                # For fixed z, (x,y) has n-z+1 choices.
                nxt[old + z] += multiplicity * (n - z + 1)
        dp = nxt
    return sum(dp)


def low_third_first_capped_direct(a: int, k: int, n: int) -> int:
    """E: Z <= (k-2a)n-2 and X <= an."""
    zcap = (k - 2 * a) * n - 2
    xcap = a * n
    if zcap < 0:
        return 0
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    kernel = [
        (x, z)
        for x in range(n + 1)
        for z in range(n - x + 1)
    ]
    for _ in range(k):
        nxt: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (old_x, old_z), multiplicity in states.items():
            for x, z in kernel:
                new_x, new_z = old_x + x, old_z + z
                if new_x <= xcap and new_z <= zcap:
                    nxt[(new_x, new_z)] += multiplicity
        states = dict(nxt)
    return sum(states.values())


def ehrhart_ie(a: int, k: int, n: int) -> int:
    unrestricted = comb(n + 2, 2) ** k
    return unrestricted - 3 * c1_direct(a, k, n) + 3 * c2_direct(a, k, n)


def ehrhart_direct(a: int, k: int, n: int) -> int:
    """Raw projected-table DP, used only at small n."""
    cap = a * n
    kernel = [
        (x, y)
        for x in range(n + 1)
        for y in range(n - x + 1)
    ]
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(k):
        nxt: defaultdict[tuple[int, int], int] = defaultdict(int)
        for (old_x, old_y), multiplicity in states.items():
            for x, y in kernel:
                new_x, new_y = old_x + x, old_y + y
                if new_x <= cap and new_y <= cap:
                    nxt[(new_x, new_y)] += multiplicity
        states = dict(nxt)
    return sum(
        multiplicity
        for (x, y), multiplicity in states.items()
        if k * n - x - y <= cap
    )


def first_differences(values: list[int]) -> list[int]:
    ans: list[int] = []
    row = values[:]
    while row:
        ans.append(row[0])
        row = [row[i + 1] - row[i] for i in range(len(row) - 1)]
    return ans


def linear_from_newton(firsts: list[int]) -> Fraction:
    return sum(
        (Fraction((-1) ** (j - 1), j) * firsts[j]
         for j in range(1, len(firsts))),
        Fraction(0),
    )


def newton_eval(firsts: list[int], n: int) -> int:
    return sum(delta * comb(n, j) for j, delta in enumerate(firsts))


def numerator_term_count(a: int, k: int, i: int, j: int, n: int) -> int:
    """One (A,B,C)-multinomial term in the rational H_n expansion."""
    b = k - 2 * a
    r = k - a
    p_degree = (b - j) * n - 2 - 2 * j
    t_degree = (r - i - j) * n - 1 - i - j
    if p_degree < 0 or t_degree < 0:
        return 0
    alpha = i + j + 1       # (1-p)^(-alpha)
    gamma = k + 1 - i       # (1-pt)^(-gamma)
    delta = k - j           # (1-t)^(-delta)
    coefficient = 0
    for q in range(min(p_degree, t_degree) + 1):
        coefficient += (
            comb(gamma + q - 1, q)
            * comb(alpha + p_degree - q - 1, p_degree - q)
            * comb(delta + t_degree - q - 1, t_degree - q)
        )
    multinomial = factorial(k) // (
        factorial(i) * factorial(j) * factorial(k - i - j)
    )
    return (-1) ** i * multinomial * coefficient


def linear_from_shifted_values(values: list[int], start: int) -> Fraction:
    """Derivative at zero of degree <=d polynomial sampled at start..start+d."""
    d = len(values) - 1
    xs = [start + m for m in range(d + 1)]
    answer = Fraction(0)
    for m, x_m in enumerate(xs):
        basis_at_zero = Fraction(1)
        logarithmic_derivative = Fraction(0)
        for j, x_j in enumerate(xs):
            if j == m:
                continue
            basis_at_zero *= Fraction(-x_j, x_m - x_j)
            logarithmic_derivative -= Fraction(1, x_j)
        answer += values[m] * basis_at_zero * logarithmic_derivative
    return answer


def numerator_term_linear(a: int, k: int, i: int, j: int) -> Fraction:
    degree = 2 * k
    start = 2 * k + 10
    values = [
        numerator_term_count(a, k, i, j, n)
        for n in range(start, start + degree + 1)
    ]
    return linear_from_shifted_values(values, start)


def generalized_comb(top: int, bottom: int) -> int:
    if top >= 0:
        return comb(top, bottom) if top >= bottom else 0
    return (-1) ** bottom * comb(bottom - top - 1, bottom)


def affine_binomial_value_derivative(
    slope: int, intercept: int, bottom: int
) -> tuple[Fraction, Fraction]:
    """Value and n-derivative of binom(slope*n+intercept,bottom) at 0."""
    value = Fraction(generalized_comb(intercept, bottom))
    if 0 <= intercept < bottom:
        derivative = Fraction(
            slope * (-1) ** (bottom - 1 - intercept),
            bottom * comb(bottom - 1, intercept),
        )
    else:
        derivative = value * slope * sum(
            (Fraction(1, intercept - q) for q in range(bottom)),
            Fraction(0),
        )
    return value, derivative


def partial_fraction_term_linear(
    r1: int, r2: int, k: int, i: int, j: int
) -> tuple[Fraction, Fraction]:
    """A-pole and B-pole derivatives for one rational numerator term.

    This formula is used only in the chamber P<T, which contains the ray for
    i<r1.  It keeps generalized-binomial conventions explicit.
    """
    assert i < r1
    b = k - r1 - r2
    alpha = i + j + 1
    gamma = k + 1 - i
    delta = k - j
    p_slope, p_intercept = b - j, -2 - 2 * j
    t_slope, t_intercept = k - r2 - i - j, -1 - i - j

    a_derivative = Fraction(0)
    for m in range(alpha):
        constant = (-1) ** m * comb(gamma + m - 1, m)
        v1, d1 = affine_binomial_value_derivative(
            p_slope, p_intercept + alpha - m - 1, alpha - m - 1
        )
        v2, d2 = affine_binomial_value_derivative(
            t_slope,
            t_intercept + gamma + delta - 1,
            gamma + delta + m - 1,
        )
        a_derivative += constant * (d1 * v2 + v1 * d2)

    b_derivative = Fraction(0)
    for m in range(gamma):
        constant = (-1) ** alpha * comb(alpha + m - 1, m)
        v1, d1 = affine_binomial_value_derivative(
            p_slope,
            p_intercept + gamma - m - 1,
            gamma - m - 1,
        )
        v2, d2 = affine_binomial_value_derivative(
            t_slope - p_slope,
            t_intercept - p_intercept + delta + m - 1,
            delta + alpha + m - 1,
        )
        b_derivative += constant * (d1 * v2 + v1 * d2)
    multinomial = factorial(k) // (
        factorial(i) * factorial(j) * factorial(k - i - j)
    )
    sign = (-1) ** i
    return sign * multinomial * a_derivative, sign * multinomial * b_derivative


def swapped_partial_fraction_term_linear(
    r1: int, r2: int, k: int, i: int, j: int
) -> tuple[Fraction, Fraction]:
    """Pole derivatives in the opposite chamber T<P."""
    assert i >= r1
    b = k - r1 - r2
    alpha = i + j + 1
    gamma = k + 1 - i
    delta = k - j
    p_slope, p_intercept = b - j, -2 - 2 * j
    t_slope, t_intercept = k - r2 - i - j, -1 - i - j

    a_derivative = Fraction(0)
    for m in range(delta):
        constant = (-1) ** m * comb(gamma + m - 1, m)
        v1, d1 = affine_binomial_value_derivative(
            t_slope, t_intercept + delta - m - 1, delta - m - 1
        )
        v2, d2 = affine_binomial_value_derivative(
            p_slope,
            p_intercept + gamma + alpha - 1,
            gamma + alpha + m - 1,
        )
        a_derivative += constant * (d1 * v2 + v1 * d2)

    b_derivative = Fraction(0)
    for m in range(gamma):
        constant = (-1) ** delta * comb(delta + m - 1, m)
        v1, d1 = affine_binomial_value_derivative(
            t_slope,
            t_intercept + gamma - m - 1,
            gamma - m - 1,
        )
        v2, d2 = affine_binomial_value_derivative(
            p_slope - t_slope,
            p_intercept - t_intercept + alpha + m - 1,
            alpha + delta + m - 1,
        )
        b_derivative += constant * (d1 * v2 + v1 * d2)
    multinomial = factorial(k) // (
        factorial(i) * factorial(j) * factorial(k - i - j)
    )
    sign = (-1) ** i
    return sign * multinomial * a_derivative, sign * multinomial * b_derivative


def audit_case(a: int, k: int) -> None:
    assert 2 * a < k < 3 * a
    degree = 2 * k
    values = [ehrhart_ie(a, k, n) for n in range(degree + 3)]
    for n in range(0, min(4, degree + 1)):
        assert ehrhart_direct(a, k, n) == values[n]
    firsts = first_differences(values[: degree + 1])
    assert firsts[-1] != 0
    assert newton_eval(firsts, degree + 1) == values[degree + 1]
    assert newton_eval(firsts, degree + 2) == values[degree + 2]
    c1_values = [c1_direct(a, k, n) for n in range(degree + 1)]
    c2_values = [c2_direct(a, k, n) for n in range(degree + 1)]
    low_values = [low_third_direct(a, k, n) for n in range(degree + 1)]
    mixed_values = [
        low_third_first_capped_direct(a, k, n)
        for n in range(degree + 1)
    ]
    assert all(c2 == low - 2 * mixed for c2, low, mixed in zip(
        c2_values, low_values, mixed_values
    ))
    c1_linear = linear_from_newton(first_differences(c1_values))
    c2_linear = linear_from_newton(first_differences(c2_values))
    low_linear = linear_from_newton(first_differences(low_values))
    mixed_linear = linear_from_newton(first_differences(mixed_values))
    linear = linear_from_newton(firsts)
    assert linear == Fraction(3 * k, 2) - 3 * c1_linear + 3 * c2_linear
    print(
        f"a={a} k={k} degree={degree} "
        f"C1_linear={c1_linear} C2_linear={c2_linear} "
        f"D_linear={low_linear} E_linear={mixed_linear} A={linear} "
        f"heldout=({degree+1},{degree+2})"
    )


def audit_pair(r1: int, r2: int, k: int) -> None:
    assert r1 + r2 < k
    degree = 2 * k
    values = [
        pair_violation_direct(r1, r2, k, n)
        for n in range(degree + 3)
    ]
    firsts = first_differences(values[: degree + 1])
    assert newton_eval(firsts, degree + 1) == values[degree + 1]
    assert newton_eval(firsts, degree + 2) == values[degree + 2]
    linear = linear_from_newton(firsts)
    assert linear == -F(k, r1 + r2)
    print(
        f"pair=({r1},{r2};k={k}) linear={linear} "
        f"heldout=({degree+1},{degree+2})"
    )


def audit_asymmetric(rows: tuple[int, int, int], k: int) -> None:
    assert min(rows) > 0 and sum(rows) > k
    degree = 2 * k
    values = [
        asymmetric_ehrhart_direct(rows, k, n)
        for n in range(degree + 3)
    ]
    firsts = first_differences(values[: degree + 1])
    assert firsts[-1] != 0
    assert newton_eval(firsts, degree + 1) == values[degree + 1]
    assert newton_eval(firsts, degree + 2) == values[degree + 2]
    linear = linear_from_newton(firsts)
    assert linear == asymmetric_formula(rows, k)
    assert linear > 0
    print(
        f"rows={rows} k={k} A={linear} "
        f"heldout=({degree+1},{degree+2})"
    )


def audit_partial_fraction_grid() -> None:
    checked = 0
    for a, k in ((2, 5), (3, 8), (4, 11)):
        b = k - 2 * a
        for i in range(k + 1):
            for j in range(k - i + 1):
                # These are precisely the numerator terms whose residual
                # exponents are eventually nonnegative.
                if j >= b or i + j >= k - a:
                    continue
                eventual = numerator_term_linear(a, k, i, j)
                if i < a:
                    pole_one, pole_two = partial_fraction_term_linear(
                        a, a, k, i, j
                    )
                else:
                    pole_one, pole_two = swapped_partial_fraction_term_linear(
                        a, a, k, i, j
                    )
                assert pole_one + pole_two == eventual
                expected = (
                    -Fraction(b - j, 2 * (k - j))
                    if i == 0
                    else Fraction(0)
                )
                assert eventual == expected
                checked += 1
    print(f"partial_fraction_grid=PASS terms={checked}")


def main() -> None:
    for case in ((2, 5), (3, 7), (3, 8)):
        audit_case(*case)
    for case in ((1, 2, 5), (1, 3, 7), (2, 2, 7), (1, 1, 5)):
        audit_pair(*case)
    for rows, k in (
        ((2, 3, 3), 7),
        ((1, 4, 4), 7),
        ((2, 2, 4), 7),
        ((1, 3, 5), 8),
        ((2, 4, 5), 9),
    ):
        audit_asymmetric(rows, k)
    audit_partial_fraction_grid()
    print("PASS")


if __name__ == "__main__":
    main()
