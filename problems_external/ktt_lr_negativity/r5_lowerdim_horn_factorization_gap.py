#!/usr/bin/env python3
"""Exact rank-five example showing why Horn factorisation alone does not
remove every lower-dimensional hive.

The essential Horn triples are generated from their defining condition
    c_{tau(I),tau(J)}^{tau(K)} = 1,
and the small LR coefficients are counted by the same exact hive model.
No precomputed Horn list or floating-point decision is used.
"""

import itertools
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "r5_certificate"))
sys.path.insert(0, os.path.join(HERE, "r5_rational"))

from hive5 import build_hive5, lattice_count  # noqa: E402
from polytope5 import affine_rank, reduce_rhs, vertices  # noqa: E402
from hiveR import build_hive  # noqa: E402


def tau(index_set):
    """Partition attached to I={i_1<...<i_s}: (i_s-s,...,i_1-1)."""
    values = tuple(index_set)
    size = len(values)
    return tuple(values[size - 1 - j] - (size - j) for j in range(size))


def small_lr(alpha, beta, gamma):
    """Exact LR count for the tiny partitions occurring in the Horn test."""
    rank = len(alpha)
    hive = build_hive(alpha, beta, gamma, rank)
    if not hive["ok"]:
        return 0
    dimension = (rank - 1) * (rank - 2) // 2
    if dimension == 0:
        return 1
    return lattice_count(hive["A"], hive["b"], dimension)


def essential_horn_triples(rank):
    universe = tuple(range(1, rank + 1))
    triples = []
    for size in range(1, rank):
        subsets = tuple(itertools.combinations(universe, size))
        for left in subsets:
            alpha = tau(left)
            for right in subsets:
                beta = tau(right)
                for output in subsets:
                    gamma = tau(output)
                    if small_lr(alpha, beta, gamma) == 1:
                        triples.append((left, right, output))
    return tuple(triples)


def partial_sum(partition, indices):
    return sum(partition[index - 1] for index in indices)


def main():
    lam = (4, 3, 3, 1, 0)
    mu = (4, 2, 1, 1, 0)
    nu = (6, 5, 4, 2, 2)

    hive = build_hive5(lam, mu, nu)
    assert hive["ok"]
    verts = vertices(reduce_rhs(hive["b"]))
    dimension = affine_rank(verts)
    coefficient = lattice_count(hive["A"], hive["b"], 6)

    essential = essential_horn_triples(5)
    equalities = []
    minimum_slack = None
    for left, right, output in essential:
        slack = (partial_sum(lam, left) + partial_sum(mu, right)
                 - partial_sum(nu, output))
        assert slack >= 0
        if slack == 0:
            equalities.append((left, right, output))
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)

    print("PASS")
    print(f"lambda={lam}")
    print(f"mu={mu}")
    print(f"nu={nu}")
    print(f"hive_vertices={len(verts)}")
    print(f"hive_dimension={dimension}")
    print(f"lr_coefficient={coefficient}")
    print(f"essential_horn_triples={len(essential)}")
    print(f"saturated_essential_horn_inequalities={len(equalities)}")
    print(f"minimum_essential_horn_slack={minimum_slack}")
    print(f"lambda_chamber_equalities={[i + 1 for i in range(4) if lam[i] == lam[i + 1]]}")
    print(f"mu_chamber_equalities={[i + 1 for i in range(4) if mu[i] == mu[i + 1]]}")
    print(f"nu_chamber_equalities={[i + 1 for i in range(4) if nu[i] == nu[i + 1]]}")

    assert dimension == 3
    assert coefficient == 4
    assert not equalities
    assert minimum_slack is not None and minimum_slack > 0


if __name__ == "__main__":
    main()
