"""Refine unresolved Gamma_11 sign cones by the location of a maximum.

This is a deterministic finite LP diagnostic.  A leaf fixes the eleven signs
selecting min(q_{i,4},q_{i,5}) and a vertex j satisfying x_j>=x_k for all k.
It then tests a degree-2 Handelman identity on that polyhedral cone.
"""
from __future__ import annotations

from itertools import combinations_with_replacement

import numpy as np
from scipy.optimize import linprog

from R10_analytic_handelman import product
from R10_analytic_probe import N
from R10_analytic_signcones import A_CUTS, B_CUTS, SIGN_FORMS, test as sign_test, TARGET


def forms(mask: int, maximum: int):
    generators = []
    for i in range(N):
        unit = np.zeros(N)
        unit[i] = 1
        generators.append(unit)
    for i, form in enumerate(SIGN_FORMS):
        generators.append(form if (mask >> i) & 1 else -form)
    for k in range(N):
        if k == maximum:
            continue
        form = np.zeros(N)
        form[maximum] = 1
        form[k] = -1
        generators.append(form)
    return generators


def leaf_nonzero(generators) -> bool:
    result = linprog(
        np.zeros(N), A_ub=-np.asarray(generators[11:]),
        b_ub=np.zeros(len(generators) - 11), A_eq=np.ones((1, N)),
        b_eq=np.ones(1), bounds=(0, None), method="highs",
    )
    return result.success


def leaf_certificate(mask: int, maximum: int, generators) -> bool:
    selected = tuple(B_CUTS[i] if (mask >> i) & 1 else A_CUTS[i] for i in range(N))
    pairs = combinations_with_replacement(range(len(generators)), 2)
    products = tuple(product(generators[r], generators[s]) for r, s in pairs)
    matrix = np.column_stack(selected + products)
    aeq = np.vstack((matrix, np.r_[np.ones(N), np.zeros(len(products))]))
    beq = np.r_[TARGET, 1.0]
    result = linprog(
        np.zeros(aeq.shape[1]), A_eq=aeq, b_eq=beq, bounds=(0, None), method="highs",
        options={"dual_feasibility_tolerance": 1e-9, "primal_feasibility_tolerance": 1e-9},
    )
    return result.success


def main():
    unresolved_masks = []
    for mask in range(1 << N):
        nonzero, certificate = sign_test(mask)
        if nonzero and not certificate:
            unresolved_masks.append(mask)
    counts = {"empty": 0, "certificate": 0, "unresolved": 0}
    unresolved_leaves = []
    for mask in unresolved_masks:
        for maximum in range(N):
            generators = forms(mask, maximum)
            if not leaf_nonzero(generators):
                counts["empty"] += 1
            elif leaf_certificate(mask, maximum, generators):
                counts["certificate"] += 1
            else:
                counts["unresolved"] += 1
                unresolved_leaves.append((mask, maximum))
    print("base unresolved masks:", len(unresolved_masks))
    print(counts)
    print("unresolved leaves:", " ".join(f"0x{m:03x}:{j}" for m, j in unresolved_leaves))


if __name__ == "__main__":
    main()
