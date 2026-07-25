#!/usr/bin/env python3
"""Exact Horn-primitivity certificate for the rank-five non-lattice family.

This reuses the defining essential-Horn generator from
``r5_lowerdim_horn_factorization_gap.py``.  It is a single exact certificate,
not a census.
"""

from r5_lowerdim_horn_factorization_gap import (
    essential_horn_triples,
    partial_sum,
)


def main():
    lam = (2, 2, 1, 0, 0)
    mu = (4, 3, 2, 1, 0)
    nu = (5, 4, 3, 2, 1)

    essential = essential_horn_triples(5)
    slacks = tuple(
        partial_sum(lam, left)
        + partial_sum(mu, right)
        - partial_sum(nu, output)
        for left, right, output in essential
    )
    equalities = tuple(slack for slack in slacks if slack == 0)

    assert len(essential) == 142
    assert min(slacks) == 1
    assert not equalities

    print("PASS")
    print(f"lambda={lam}")
    print(f"mu={mu}")
    print(f"nu={nu}")
    print(f"essential_horn_triples={len(essential)}")
    print(f"minimum_essential_horn_slack={min(slacks)}")
    print(f"saturated_essential_horn_inequalities={len(equalities)}")


if __name__ == "__main__":
    main()
