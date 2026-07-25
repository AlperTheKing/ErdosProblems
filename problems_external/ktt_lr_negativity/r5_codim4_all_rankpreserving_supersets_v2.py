#!/usr/bin/env python3
"""Coset-refined canonical driver for all rank-preserving supersets."""

from collections import Counter

import r5_codim4_bv_independent as bv
import r5_codim4_negative_realizability_audit as closure
import r5_codim4_full_cone_alpha as geometry
import r5_codim4_all_rankpreserving_supersets as coverage
from r5_codim4_normal_subdivision_alpha_v2 import direct_normal_alpha_refined


def main():
    normals, _ = bv.rank5_hive_normals()
    A, tags, forms, labels, weight = closure.make_nonnegative_forms()
    negative, expanded, bases = coverage.minimal_forced_cones(
        normals, A, forms, labels, weight
    )

    candidates = {}
    span_size_histogram = Counter()
    generated_occurrences = 0
    for base_ids, basis_ids in bases.items():
        span_ids = tuple(
            index for index in range(len(normals))
            if geometry.rank([normals[i] for i in basis_ids] + [normals[index]]) == 4
        )
        span_size_histogram[len(span_ids)] += 1
        for active_ids in coverage.all_supersets(base_ids, span_ids):
            generated_occurrences += 1
            candidates.setdefault(active_ids, basis_ids)

    values = {}
    details = {}
    nonpointed = 0
    total_cells = 0
    negative_cells = 0
    coset_ray_count = 0
    for active_ids, basis_ids in sorted(candidates.items()):
        coordinates, feasible_lattice_gram = geometry.coordinates_in_basis(
            normals, basis_ids, active_ids
        )
        if not coverage.is_pointed_full(coordinates):
            nonpointed += 1
            continue
        result = direct_normal_alpha_refined(coordinates, feasible_lattice_gram)
        values[active_ids] = result["alpha"]
        details[active_ids] = result
        total_cells += len(result["cell_values"])
        negative_cells += sum(alpha < 0 for _, alpha in result["cell_values"])
        coset_ray_count += len(result["coset_rays"])

    minimum = min(values.values())
    minimizers = tuple(ids for ids, value in values.items() if value == minimum)
    verdict = "PASS" if all(value > 0 for value in values.values()) else "NEGATIVE_FULL_CONE"
    print(verdict)
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
    print(f"inserted_coset_rays={coset_ray_count}")
    if any(value <= 0 for value in values.values()):
        print("nonpositive_records=")
        for ids, value in values.items():
            if value <= 0:
                print(f"  active_ids={ids} alpha={value} basis={candidates[ids]} detail={details[ids]}")
    else:
        print("minimum_records=")
        for ids in minimizers:
            print(f"  active_ids={ids} alpha={values[ids]} basis={candidates[ids]} detail={details[ids]}")


if __name__ == "__main__":
    main()
