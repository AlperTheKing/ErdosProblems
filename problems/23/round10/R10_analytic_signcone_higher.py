"""Higher-degree Handelman diagnostics on the 14 unresolved sign-cone orbits.

For degree d, search for

  L^(d-2) (L^2/25 - sum_i lambda_i r_i)
      = sum_alpha mu_alpha product_{j in alpha} g_j,

where r_i is the smaller length-4/5 arc form on the fixed sign cone,
lambda is a probability vector, and alpha ranges over multisets of d cone
generators. Floating feasibility is diagnostic only.
"""
from __future__ import annotations

import argparse
from itertools import combinations_with_replacement

import numpy as np
from scipy.optimize import linprog

from R10_analytic_handelman import MONOMIALS
from R10_analytic_probe import N
from R10_analytic_signcones import A_CUTS, B_CUTS, SIGN_FORMS


REPRESENTATIVES = (0x1BF, 0x1DF, 0x1EF, 0x1FF, 0x2BF, 0x2DF, 0x2EF,
                   0x2FF, 0x377, 0x37F, 0x3BF, 0x3DF, 0x3FF, 0x7FF)


def multiply(left: dict[tuple[int, ...], float], linear: np.ndarray):
    out: dict[tuple[int, ...], float] = {}
    for exponent, coefficient in left.items():
        for i, value in enumerate(linear):
            if value == 0:
                continue
            target = list(exponent)
            target[i] += 1
            key = tuple(target)
            out[key] = out.get(key, 0.0) + coefficient * value
    return out


def quadratic_dict(vector: np.ndarray):
    out = {}
    for (i, j), coefficient in zip(MONOMIALS, vector):
        if coefficient:
            exponent = [0] * N
            exponent[i] += 1
            exponent[j] += 1
            out[tuple(exponent)] = float(coefficient)
    return out


def lift_quadratic(vector: np.ndarray, degree: int):
    polynomial = quadratic_dict(vector)
    for _ in range(degree - 2):
        polynomial = multiply(polynomial, np.ones(N))
    return polynomial


def exponent_basis(degree: int):
    basis = []
    def rec(index: int, remaining: int, prefix: list[int]):
        if index == N - 1:
            basis.append(tuple(prefix + [remaining]))
            return
        for value in range(remaining + 1):
            rec(index + 1, remaining - value, prefix + [value])
    rec(0, degree, [])
    return tuple(basis)


def as_vector(polynomial, index, size):
    out = np.zeros(size)
    for exponent, coefficient in polynomial.items():
        out[index[exponent]] = coefficient
    return out


def solve(mask: int, degree: int):
    generators = []
    for i in range(N):
        unit = np.zeros(N)
        unit[i] = 1
        generators.append(unit)
    for i, form in enumerate(SIGN_FORMS):
        generators.append(form if (mask >> i) & 1 else -form)
    selected = tuple(B_CUTS[i] if (mask >> i) & 1 else A_CUTS[i] for i in range(N))
    basis = exponent_basis(degree)
    index = {exponent: i for i, exponent in enumerate(basis)}
    target2 = np.zeros(len(MONOMIALS))
    for k, (i, j) in enumerate(MONOMIALS):
        target2[k] = 1 if i == j else 2
    target = as_vector(lift_quadratic(target2, degree), index, len(basis))
    cut_columns = [25 * as_vector(lift_quadratic(cut, degree), index, len(basis)) for cut in selected]
    product_columns = []
    for alpha in combinations_with_replacement(range(len(generators)), degree):
        polynomial = {tuple([0] * N): 1.0}
        for generator in alpha:
            polynomial = multiply(polynomial, generators[generator])
        product_columns.append(as_vector(polynomial, index, len(basis)))
    matrix = np.column_stack(cut_columns + product_columns)
    aeq = np.vstack((matrix, np.r_[np.ones(N), np.zeros(len(product_columns))]))
    beq = np.r_[target, 1.0]
    result = linprog(
        np.zeros(aeq.shape[1]), A_eq=aeq, b_eq=beq, bounds=(0, None), method="highs",
        options={"dual_feasibility_tolerance": 1e-9, "primal_feasibility_tolerance": 1e-9},
    )
    print(f"mask=0x{mask:03x} degree={degree} rows={len(basis)} cols={aeq.shape[1]} "
          f"success={result.success} status={result.message}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--degree", type=int, choices=(3, 4), default=3)
    parser.add_argument("--mask", type=lambda value: int(value, 0))
    args = parser.parse_args()
    for mask in ([args.mask] if args.mask is not None else REPRESENTATIVES):
        solve(mask, args.degree)


if __name__ == "__main__":
    main()
