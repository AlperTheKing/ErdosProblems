"""Exhaustive sign-cone test for the Gamma_11 length-4/5 arc bound.

Write a_i=q_{i,4}, b_i=q_{i,5}. Direct expansion gives

  a_i-b_i = x_{i+4}(x_{i-3}+x_{i-2}+x_{i-1}-x_i).

Hence one of a_i,b_i is selected on each of the 2^11 polyhedral sign cones.
For every nonzero cone, this script tests whether a degree-2 Handelman identity
proves that a convex average of the eleven selected cuts is at most L^2/25.
Floating LP results are only diagnostics; no proof is emitted here.
"""
from __future__ import annotations

import argparse
from itertools import combinations_with_replacement

import numpy as np
from scipy.optimize import linprog

from R10_analytic_handelman import cut_polynomial, product
from R10_analytic_probe import N


TARGET = product(np.ones(N), np.ones(N)) / 25
A_CUTS = tuple(cut_polynomial(i, 4) for i in range(N))
B_CUTS = tuple(cut_polynomial(i, 5) for i in range(N))


def sign_form(i: int) -> np.ndarray:
    """p_i-x_i, where p_i=x_{i-3}+x_{i-2}+x_{i-1}."""
    form = np.zeros(N)
    form[(i - 3) % N] += 1
    form[(i - 2) % N] += 1
    form[(i - 1) % N] += 1
    form[i] -= 1
    return form


SIGN_FORMS = tuple(sign_form(i) for i in range(N))


def cone_data(mask: int):
    # bit i = 1 means p_i-x_i >= 0, so b_i <= a_i and b_i is selected.
    generators = []
    for i in range(N):
        unit = np.zeros(N)
        unit[i] = 1
        generators.append(unit)
    for i, form in enumerate(SIGN_FORMS):
        generators.append(form if (mask >> i) & 1 else -form)
    selected = tuple(B_CUTS[i] if (mask >> i) & 1 else A_CUTS[i] for i in range(N))
    pairs = tuple(combinations_with_replacement(range(len(generators)), 2))
    products = tuple(product(generators[r], generators[s]) for r, s in pairs)
    matrix = np.column_stack(selected + products)
    aeq = np.vstack((matrix, np.r_[np.ones(N), np.zeros(len(products))]))
    beq = np.r_[TARGET, 1.0]
    return aeq, beq


def cone_nonzero(mask: int) -> bool:
    aub = []
    for i, form in enumerate(SIGN_FORMS):
        generator = form if (mask >> i) & 1 else -form
        aub.append(-generator)
    result = linprog(
        np.zeros(N),
        A_ub=np.asarray(aub),
        b_ub=np.zeros(N),
        A_eq=np.ones((1, N)),
        b_eq=np.ones(1),
        bounds=(0, None),
        method="highs",
    )
    return result.success


def test(mask: int) -> tuple[bool, bool]:
    nonzero = cone_nonzero(mask)
    if not nonzero:
        return False, True
    aeq, beq = cone_data(mask)
    result = linprog(
        np.zeros(aeq.shape[1]),
        A_eq=aeq,
        b_eq=beq,
        bounds=(0, None),
        method="highs",
        options={"dual_feasibility_tolerance": 1e-9, "primal_feasibility_tolerance": 1e-9},
    )
    return True, result.success


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask", type=lambda value: int(value, 0))
    args = parser.parse_args()
    masks = [args.mask] if args.mask is not None else range(1 << N)
    counts = {"empty": 0, "certificate": 0, "unresolved": 0}
    unresolved = []
    for mask in masks:
        nonzero, certificate = test(mask)
        if not nonzero:
            counts["empty"] += 1
        elif certificate:
            counts["certificate"] += 1
        else:
            counts["unresolved"] += 1
            unresolved.append(mask)
    print(counts)
    print("unresolved masks:", " ".join(f"0x{mask:03x}" for mask in unresolved))


if __name__ == "__main__":
    main()
