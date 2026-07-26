"""Search for a max-coordinate Handelman proof of the Gamma_11 arc bound.

On the cone C_0 = {x >= 0, x_0 >= x_i for i=1,...,10}, search for

  (sum x)^2/25 - sum_A lambda_A q_A(x)
      = sum_{r<=s} mu_{r,s} g_r(x) g_s(x),

where lambda is a probability distribution over the 22 length-4/5 arc cuts,
mu >= 0, and the generators are x_0,...,x_10 and x_0-x_i (i>0).
Such an identity is a direct proof on C_0; rotations cover the simplex.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from R10_analytic_probe import N, EDGES


MONOMIALS = tuple((i, j) for i in range(N) for j in range(i, N))
MONO_INDEX = {monomial: k for k, monomial in enumerate(MONOMIALS)}


def product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.zeros(len(MONOMIALS))
    for i in range(N):
        out[MONO_INDEX[i, i]] = a[i] * b[i]
        for j in range(i + 1, N):
            out[MONO_INDEX[i, j]] = a[i] * b[j] + a[j] * b[i]
    return out


def cut_polynomial(start: int, length: int) -> np.ndarray:
    inside = {(start + j) % N for j in range(length)}
    out = np.zeros(len(MONOMIALS))
    for u, v in EDGES:
        if (u in inside) == (v in inside):
            out[MONO_INDEX[u, v]] = 1.0
    return out


def build_lp():
    cut_labels = tuple((start, length) for length in (4, 5) for start in range(N))
    cuts = tuple(cut_polynomial(*label) for label in cut_labels)
    generators = []
    generator_labels = []
    for i in range(N):
        a = np.zeros(N)
        a[i] = 1
        generators.append(a)
        generator_labels.append(f"x{i}")
    for i in range(1, N):
        a = np.zeros(N)
        a[0] = 1
        a[i] = -1
        generators.append(a)
        generator_labels.append(f"x0-x{i}")
    pairs = tuple(combinations_with_replacement(range(len(generators)), 2))
    products = tuple(product(generators[r], generators[s]) for r, s in pairs)
    target = product(np.ones(N), np.ones(N)) / 25
    # Columns are lambda_A and mu_rs.  Identity is cuts*lambda + products*mu = target.
    matrix = np.column_stack(cuts + products)
    aeq = np.vstack((matrix, np.r_[np.ones(len(cuts)), np.zeros(len(products))]))
    beq = np.r_[target, 1.0]
    return cut_labels, generator_labels, pairs, aeq, beq


def main() -> None:
    cut_labels, generator_labels, pairs, aeq, beq = build_lp()
    result = linprog(
        np.zeros(aeq.shape[1]),
        A_eq=aeq,
        b_eq=beq,
        bounds=(0, None),
        method="highs",
        options={"dual_feasibility_tolerance": 1e-9, "primal_feasibility_tolerance": 1e-9},
    )
    print("status:", result.message)
    if not result.success:
        if result.eqlin is not None and result.eqlin.residual is not None:
            print("max equality residual:", np.max(np.abs(result.eqlin.residual)))
        return
    residual = np.max(np.abs(aeq @ result.x - beq))
    print("floating residual:", residual)
    nl = len(cut_labels)
    print("live cuts:")
    for label, value in zip(cut_labels, result.x[:nl]):
        if value > 1e-9:
            print(" ", label, value, Fraction(float(value)).limit_denominator(10**6))
    print("live generator products:")
    for (r, s), value in zip(pairs, result.x[nl:]):
        if value > 1e-9:
            print(
                " ",
                generator_labels[r],
                generator_labels[s],
                value,
                Fraction(float(value)).limit_denominator(10**6),
            )


if __name__ == "__main__":
    main()
