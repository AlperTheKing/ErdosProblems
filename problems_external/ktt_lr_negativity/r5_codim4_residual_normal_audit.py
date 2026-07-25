#!/usr/bin/env python3
"""Canonical direct-normal BV audit of all 96 residual r=5 cones.

Coverage begins with every saturated simplicial normal 4-tuple whose exact BV
constant is negative.  It expands duplicated rhombus rows, closes vanishing
slacks by exact Farkas identities, discards closures whose normal rank exceeds
four, and evaluates every remaining distinct full forced rank-four cone by a
saturated direct normal-cone subdivision.  A polar-feasible valuation is used
only as an independent equality cross-check.
"""

from collections import Counter
from itertools import product

import r5_codim4_bv_independent as bv
import r5_codim4_negative_realizability_audit as closure
import r5_codim4_full_cone_alpha as polar
from r5_codim4_full_cone_alpha_v2 import pulling_tetrahedra_unimodular
import r5_codim4_normal_subdivision_alpha as normal


polar.pulling_tetrahedra = pulling_tetrahedra_unimodular


def main():
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = closure.make_nonnegative_forms()
    by_normal = {ray: [] for ray in normals}
    for row, ray in enumerate(map(tuple, A)):
        by_normal[ray].append(row)
    negative = closure.negative_normal_tuples(normals)
    expanded = [
        (ids, alpha, tuple(rows))
        for ids, alpha in negative
        for rows in product(*(by_normal[normals[i]] for i in ids))
    ]
    assert len(negative) == 132 and len(expanded) == 192

    cache = {}
    occurrences = Counter()
    forced_rank5 = 0
    for basis_ids, cell_alpha, target_rows in expanded:
        zero, certificates, closure_rank = closure.closure_to_rank_five(
            target_rows, A, forms, labels, weight
        )
        if closure_rank >= 5:
            forced_rank5 += 1
            continue
        active_rows = tuple(sorted(index - 15 for index in zero if index >= 15))
        active_ids = tuple(sorted({normals.index(tuple(A[row])) for row in active_rows}))
        occurrences[active_ids] += 1
        if active_ids in cache:
            continue
        coordinates, feasible_lattice_gram = polar.coordinates_in_basis(
            normals, basis_ids, active_ids
        )
        direct = normal.direct_normal_alpha(coordinates, feasible_lattice_gram)
        independent = polar.full_cone_alpha(coordinates, feasible_lattice_gram)
        assert direct["alpha"] == independent["alpha"], (
            active_ids, direct["alpha"], independent["alpha"]
        )
        cache[active_ids] = {
            "alpha": direct["alpha"],
            "basis_ids": basis_ids,
            "active_rows": active_rows,
            "extreme_indices": direct["extreme_indices"],
            "inserted_indices": direct["inserted_indices"],
            "cells": direct["cells"],
            "cell_values": direct["cell_values"],
        }

    assert forced_rank5 == 54
    assert sum(occurrences.values()) == 138
    assert len(cache) == 96
    values = [record["alpha"] for record in cache.values()]
    assert all(value > 0 for value in values)
    minimum = min(values)
    minimizers = tuple(key for key, record in cache.items() if record["alpha"] == minimum)
    cell_values = [
        alpha for record in cache.values() for _, alpha in record["cell_values"]
    ]
    print("PASS")
    print(f"normal_sha256={bv.EXPECTED_NORMAL_SHA256}")
    print(f"negative_saturated_normal_4tuples={len(negative)}")
    print(f"expanded_original_row_4tuples={len(expanded)}")
    print(f"forced_normal_rank_at_least_5={forced_rank5}")
    print(f"residual_rank4_occurrences={sum(occurrences.values())}")
    print(f"unique_full_forced_rank4_cones={len(cache)}")
    print(f"negative_full_cones={sum(value < 0 for value in values)}")
    print(f"zero_full_cones={sum(value == 0 for value in values)}")
    print(f"minimum_full_cone_alpha={minimum}")
    print(f"minimum_active_id_sets={minimizers}")
    print(f"subdivision_cell_count={len(cell_values)}")
    print(f"negative_subdivision_cells={sum(value < 0 for value in cell_values)}")
    print("minimum_records=")
    for key in minimizers:
        print(f"  active_ids={key} occurrences={occurrences[key]} record={cache[key]}")


if __name__ == "__main__":
    main()
