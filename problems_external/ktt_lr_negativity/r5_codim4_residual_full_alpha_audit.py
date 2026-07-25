#!/usr/bin/env python3
"""Exact full-cone BV audit for all residual negative r=5 quadruples."""

from collections import Counter
from itertools import product

import r5_codim4_bv_independent as bv
import r5_codim4_negative_realizability_audit as closure
import r5_codim4_full_cone_alpha as cone
from r5_codim4_full_cone_alpha_v2 import pulling_tetrahedra_unimodular


cone.pulling_tetrahedra = pulling_tetrahedra_unimodular


def main():
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = closure.make_nonnegative_forms()
    by_normal = {normal: [] for normal in normals}
    for row, normal in enumerate(map(tuple, A)):
        by_normal[normal].append(row)
    negative = closure.negative_normal_tuples(normals)
    expanded = [
        (ids, alpha, tuple(rows))
        for ids, alpha in negative
        for rows in product(*(by_normal[normals[i]] for i in ids))
    ]

    cache = {}
    occurrences = Counter()
    rank5 = 0
    for ids, cell_alpha, target_rows in expanded:
        zero, certificates, closure_rank = closure.closure_to_rank_five(
            target_rows, A, forms, labels, weight
        )
        if closure_rank >= 5:
            rank5 += 1
            continue
        active_rows = tuple(sorted(index - 15 for index in zero if index >= 15))
        active_ids = tuple(sorted({normals.index(tuple(A[row])) for row in active_rows}))
        occurrences[active_ids] += 1
        if active_ids in cache:
            continue
        coordinates, lattice_gram = cone.coordinates_in_basis(normals, ids, active_ids)
        result = cone.full_cone_alpha(coordinates, lattice_gram)
        cache[active_ids] = {
            "alpha": result["alpha"],
            "basis_ids": ids,
            "active_rows": active_rows,
            "rays": result["rays"],
            "tetrahedra": result["tetrahedra"],
            "internal_terms": result["internal_terms"],
        }

    assert rank5 == 54
    assert len(cache) == 96
    values = [record["alpha"] for record in cache.values()]
    minimum = min(values)
    minimizers = [key for key, record in cache.items() if record["alpha"] == minimum]
    print("PASS")
    print(f"negative_saturated_cells={len(negative)}")
    print(f"expanded_original_rows={len(expanded)}")
    print(f"forced_rank_at_least_5={rank5}")
    print(f"residual_rank4_occurrences={sum(occurrences.values())}")
    print(f"unique_residual_full_cones={len(cache)}")
    print(f"full_cone_negative_count={sum(value < 0 for value in values)}")
    print(f"full_cone_zero_count={sum(value == 0 for value in values)}")
    print(f"minimum_full_cone_alpha={minimum}")
    print(f"minimum_active_id_sets={minimizers}")
    print("minimum_records=")
    for key in minimizers:
        print(f"  active_ids={key} occurrences={occurrences[key]} record={cache[key]}")


if __name__ == "__main__":
    main()
