"""Exact Farkas obstruction to the coarse max-coordinate Handelman ansatz.

The ansatz is the one in R10_analytic_handelman.py on
C_0={x>=0, x_0>=x_i}.  This gate uses integer arithmetic only.
"""
from __future__ import annotations

from itertools import combinations_with_replacement
from fractions import Fraction

from R10_analytic_handelman import MONOMIALS, MONO_INDEX
from R10_analytic_probe import EDGES, N


SPECIAL = {
    (1, 6), (1, 8), (2, 6), (2, 9), (3, 7), (3, 10),
    (4, 8), (5, 9), (6, 10),
}


def ell_quadratic(coefficients: list[int]) -> int:
    moments = []
    for i, j in MONOMIALS:
        if (i, j) == (0, 0):
            moments.append(2)
        elif i == 0 and j > 0:
            moments.append(1)
        elif (i, j) in SPECIAL:
            moments.append(1)
        else:
            moments.append(0)
    return sum(a * b for a, b in zip(coefficients, moments))


def product(a: list[int], b: list[int]) -> list[int]:
    out = [0] * len(MONOMIALS)
    for i in range(N):
        out[MONO_INDEX[i, i]] = a[i] * b[i]
        for j in range(i + 1, N):
            out[MONO_INDEX[i, j]] = a[i] * b[j] + a[j] * b[i]
    return out


def cut(start: int, length: int) -> list[int]:
    inside = {(start + j) % N for j in range(length)}
    out = [0] * len(MONOMIALS)
    for u, v in EDGES:
        if (u in inside) == (v in inside):
            out[MONO_INDEX[u, v]] = 1
    return out


def main() -> None:
    generators = []
    labels = []
    for i in range(N):
        form = [0] * N
        form[i] = 1
        generators.append(form)
        labels.append(f"x{i}")
    for i in range(1, N):
        form = [0] * N
        form[0] = 1
        form[i] = -1
        generators.append(form)
        labels.append(f"x0-x{i}")

    # A certificate identity would be
    # L^2/25 = sum lambda_A q_A + sum mu_rs g_r g_s, sum lambda_A=1.
    # The separator evaluates the normalization row with coefficient -3.
    cut_slacks = {}
    for length in (4, 5):
        for start in range(N):
            value = ell_quadratic(cut(start, length)) - 3
            assert value >= 0
            cut_slacks[(start, length)] = value
    product_slacks = {}
    for r, s in combinations_with_replacement(range(len(generators)), 2):
        value = ell_quadratic(product(generators[r], generators[s]))
        assert value >= 0
        product_slacks[(labels[r], labels[s])] = value

    l2 = product([1] * N, [1] * N)
    ell_l2 = ell_quadratic(l2)
    assert ell_l2 == 40
    # ell(L^2/25)-3 = 8/5-3 = -7/5.
    assert Fraction(ell_l2, 25) - 3 == Fraction(-7, 5)
    print("EXACT FARKAS GATE PASSED")
    print("cut slacks ell(q_A)-3:", cut_slacks)
    print("minimum generator-product slack:", min(product_slacks.values()))
    print("separator on target plus normalization:", Fraction(ell_l2, 25) - 3)


if __name__ == "__main__":
    main()
    # Exact cut-pair identity used by the sign-cone decomposition.
    for i in range(N):
        lhs = [a - b for a, b in zip(cut(i, 4), cut(i, 5))]
        unit = [0] * N
        unit[(i + 4) % N] = 1
        sign = [0] * N
        sign[(i - 3) % N] += 1
        sign[(i - 2) % N] += 1
        sign[(i - 1) % N] += 1
        sign[i] -= 1
        assert lhs == product(unit, sign)

