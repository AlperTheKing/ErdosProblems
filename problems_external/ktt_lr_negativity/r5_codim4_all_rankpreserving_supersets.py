#!/usr/bin/env python3
"""Exhaust all rank-preserving normal supersets above negative-cell closures.

An actual codimension-four face containing one of the 132 negative saturated
four-ray cells may have additional tight rhombi that are not universally
Farkas-forced.  Such a normal must lie in the same four-dimensional span.
For each of the 96 minimal forced rank-four cones, this checker enumerates
every subset of all 27 hive normal directions lying in that span, adjoins it
to the forced cone, discards non-pointed cones, and evaluates the resulting
normal cone by a saturated direct Berline--Vergne subdivision.

This deliberately over-approximates realizability: every actual cone is in the
finite list, while some listed supersets need not arise from partition data.
Thus positivity of the whole list is a rigorous coverage certificate for every
actual rank-preserving extension of a negative saturated cell.
"""

from collections import Counter
from itertools import combinations, product

import r5_codim4_bv_independent as bv
import r5_codim4_negative_realizability_audit as closure
import r5_codim4_full_cone_alpha as geometry
import r5_codim4_normal_subdivision_alpha as normal


def rank(rows):
    return geometry.rank(rows)


def minimal_forced_cones(normals, A, forms, labels, weight):
    by_normal = {ray: [] for ray in normals}
    for row, ray in enumerate(map(tuple, A)):
        by_normal[ray].append(row)
    negative = closure.negative_normal_tuples(normals)
    expanded = [
        (ids, alpha, tuple(rows))
        for ids, alpha in negative
        for rows in product(*(by_normal[normals[i]] for i in ids))
    ]
    records = {}
    rank5 = 0
    for basis_ids, cell_alpha, target_rows in expanded:
        zero, certificates, closure_rank = closure.closure_to_rank_five(
            target_rows, A, forms, labels, weight
        )
        if closure_rank >= 5:
            rank5 += 1
            continue
        active_rows = tuple(sorted(index - 15 for index in zero if index >= 15))
        active_ids = tuple(sorted({normals.index(tuple(A[row])) for row in active_rows}))
        records.setdefault(active_ids, basis_ids)
    assert len(negative) == 132 and len(expanded) == 192
    assert rank5 == 54 and len(records) == 96
    return negative, expanded, records


def all_supersets(base_ids, span_ids):
    optional = tuple(index for index in span_ids if index not in base_ids)
    for size in range(len(optional) + 1):
        for chosen in combinations(optional, size):
            yield tuple(sorted(set(base_ids).union(chosen)))


def is_pointed_full(normal_coordinates):
    try:
        polar = geometry.feasible_extreme_rays(normal_coordinates)
    except AssertionError:
        return False
    return geometry.rank(polar) == 4


def main():
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = closure.make_nonnegative_forms()
    negative, expanded, bases = minimal_forced_cones(normals, A, forms, labels, weight)

    candidates = {}
    span_size_histogram = Counter()
    generated_occurrences = 0
    for base_ids, basis_ids in bases.items():
        span_ids = tuple(
            index for index in range(len(normals))
            if rank([normals[i] for i in basis_ids] + [normals[index]]) == 4
        )
        span_size_histogram[len(span_ids)] += 1
        for active_ids in all_supersets(base_ids, span_ids):
            generated_occurrences += 1
            candidates.setdefault(active_ids, basis_ids)

    values = {}
    nonpointed = 0
    total_cells = 0
    negative_cells = 0
    for active_ids, basis_ids in sorted(candidates.items()):
        coordinates, feasible_lattice_gram = geometry.coordinates_in_basis(
            normals, basis_ids, active_ids
        )
        if not is_pointed_full(coordinates):
            nonpointed += 1
            continue
        result = normal.direct_normal_alpha(coordinates, feasible_lattice_gram)
        values[active_ids] = result["alpha"]
        total_cells += len(result["cell_values"])
        negative_cells += sum(alpha < 0 for _, alpha in result["cell_values"])

    assert values
    minimum = min(values.values())
    minimizers = tuple(ids for ids, value in values.items() if value == minimum)
    print("PASS" if all(value > 0 for value in values.values()) else "NEGATIVE_FULL_CONE")
    print(f"normal_sha256={bv.EXPECTED_NORMAL_SHA256}")
    print(f"negative_saturated_cells={len(negative)}")
    print(f"expanded_original_rows={len(expanded)}")
    print(f"minimal_forced_rank4_cones={len(bases)}")
    print(f"span_size_histogram={dict(sorted(span_size_histogram.items()))}")
    print(f"generated_superset_occurrences={generated_occurrences}")
    print(f"unique_superset_direction_sets={len(candidates)}")
    print(f"nonpointed_direction_sets={nonpointed}")
    print(f"pointed_full_cones={len(values)}")
    print(f"negative_full_cones={sum(value < 0 for value in values.values())}")
    print(f"zero_full_cones={sum(value == 0 for value in values.values())}")
    print(f"minimum_full_cone_alpha={minimum}")
    print(f"minimum_active_id_sets={minimizers}")
    print(f"saturated_subdivision_cells={total_cells}")
    print(f"negative_subdivision_cells={negative_cells}")
    if any(value <= 0 for value in values.values()):
        print("nonpositive_records=")
        for ids, value in values.items():
            if value <= 0:
                print(f"  active_ids={ids} alpha={value} basis={candidates[ids]}")


if __name__ == "__main__":
    main()
