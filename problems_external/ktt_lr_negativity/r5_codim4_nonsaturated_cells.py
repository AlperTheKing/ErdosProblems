#!/usr/bin/env python3
"""Exact BV census of every nonsaturated rank-5 normal four-tuple."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product

import r5_codim4_bv_independent as bv
from r5_codim4_normal_subdivision_alpha_v2 import direct_normal_alpha_refined


def saturate_basis(rows):
    """Enlarge Z*rows to span_Q(rows) intersect Z^6, preserving rank four."""
    basis = tuple(map(tuple, rows))
    index = bv.saturation_index(basis)
    assert index
    while index > 1:
        candidates = []
        for residues in product(range(index), repeat=4):
            if not any(residues):
                continue
            numerators = tuple(
                sum(residues[i] * basis[i][j] for i in range(4))
                for j in range(6)
            )
            if not all(value % index == 0 for value in numerators):
                continue
            vector = tuple(value // index for value in numerators)
            if not any(vector):
                continue
            for replaced in range(4):
                trial = list(basis)
                trial[replaced] = vector
                new_index = bv.saturation_index(tuple(trial))
                if 0 < new_index < index:
                    candidates.append((new_index, tuple(trial), vector, residues, replaced))
        assert candidates, (basis, index)
        index, basis, _, _, _ = min(candidates)
    assert bv.saturation_index(basis) == 1
    return basis


def coordinates_in_explicit_basis(basis, active_rows):
    basis_gram = bv.normal_gram(basis)
    basis_gram_inverse = bv.inverse(basis_gram)
    coordinates = []
    for normal in active_rows:
        products = tuple(sum(x * y for x, y in zip(basis[i], normal)) for i in range(4))
        coordinate = tuple(
            sum(basis_gram_inverse[i][j] * products[j] for j in range(4))
            for i in range(4)
        )
        assert all(value.denominator == 1 for value in coordinate)
        reconstruction = tuple(
            sum(int(coordinate[i]) * basis[i][j] for i in range(4))
            for j in range(6)
        )
        assert reconstruction == tuple(normal)
        coordinates.append(tuple(map(int, coordinate)))
    return tuple(coordinates), basis_gram_inverse


def main():
    normals, _ = bv.rank5_hive_normals()
    histogram = Counter()
    records = []
    total_coset_rays = 0
    for ids in combinations(range(len(normals)), 4):
        rows = tuple(normals[i] for i in ids)
        index = bv.saturation_index(rows)
        if index <= 1:
            continue
        basis = saturate_basis(rows)
        coordinates, feasible_lattice_gram = coordinates_in_explicit_basis(basis, rows)
        result = direct_normal_alpha_refined(coordinates, feasible_lattice_gram)
        alpha = result["alpha"]
        histogram[(index, alpha < 0, alpha == 0)] += 1
        total_coset_rays += len(result["coset_rays"])
        records.append((alpha, ids, index, rows, basis, result))
    records.sort(key=lambda record: (record[0], record[1]))
    assert len(records) == 903
    print("PASS")
    print(f"normal_sha256={bv.EXPECTED_NORMAL_SHA256}")
    print(f"nonsaturated_independent_4tuples={len(records)}")
    print(f"index_histogram={dict(Counter(record[2] for record in records))}")
    print(f"negative_count={sum(record[0] < 0 for record in records)}")
    print(f"zero_count={sum(record[0] == 0 for record in records)}")
    print(f"minimum_alpha={records[0][0]}")
    print(f"inserted_coset_rays={total_coset_rays}")
    print("lowest_records=")
    for record in records[:20]:
        alpha, ids, index, rows, basis, result = record
        print(f"  alpha={alpha} ids={ids} index={index} rows={rows} basis={basis}")
        print(f"    coset_rays={result['coset_rays']} cells={result['cells']} values={result['cell_values']}")


if __name__ == "__main__":
    main()
