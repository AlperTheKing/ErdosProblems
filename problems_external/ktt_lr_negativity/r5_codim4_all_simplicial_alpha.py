#!/usr/bin/env python3
"""Exact BV alpha for every simplicial four-ray size-five hive cone.

Unlike the first census, this includes lattice indices 2, 3, and 4.  Each
nonsaturated cone is star-subdivided by primitive lattice rays from a
fundamental parallelepiped until every maximal cell is saturated in the
intrinsic normal lattice.  Berline--Vergne's simple normal-cone valuation then
adds the exact cell constants.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import gcd

import r5_codim4_bv_independent as bv
import r5_codim4_full_cone_alpha as geometry


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    assert divisor
    return tuple(value // divisor for value in vector)


def coordinates_in_cell(vector, cell, rays):
    basis = tuple(rays[i] for i in cell)
    gram = tuple(tuple(dot(a, b) for b in basis) for a in basis)
    inverse = bv.inverse(gram)
    products = tuple(dot(a, vector) for a in basis)
    return tuple(sum(inverse[i][j] * products[j] for j in range(4))
                 for i in range(4))


def star_insert(cells, ray_index, rays):
    vector = rays[ray_index]
    answer = set()
    used = False
    for cell in cells:
        coefficients = coordinates_in_cell(vector, cell, rays)
        if not all(value >= 0 for value in coefficients):
            answer.add(cell)
            continue
        support = tuple(i for i, value in enumerate(coefficients) if value > 0)
        if len(support) == 1 and cell[support[0]] == ray_index:
            answer.add(cell)
            continue
        used = True
        for local in support:
            replacement = tuple(sorted(
                (ray_index,) + tuple(cell[i] for i in range(4) if i != local)
            ))
            if len(set(replacement)) == 4:
                answer.add(replacement)
    assert used
    return tuple(sorted(answer))


def fundamental_ray(cell, rays):
    rows = tuple(rays[i] for i in cell)
    index = bv.saturation_index(rows)
    assert index > 1
    candidates = []
    for numerators in product(range(index), repeat=4):
        if not any(numerators):
            continue
        vector = []
        for coordinate in range(len(rows[0])):
            numerator = sum(rows[i][coordinate] * numerators[i]
                            for i in range(4))
            if numerator % index:
                break
            vector.append(numerator // index)
        else:
            ray = primitive(tuple(vector))
            if ray in rays:
                continue
            support = sum(value > 0 for value in numerators)
            if support >= 2:
                candidates.append((-support, ray))
    assert candidates, (cell, index)
    return min(candidates)[1]


def saturated_cells(rows):
    rays = list(map(tuple, rows))
    cells = ((0, 1, 2, 3),)
    inserted = []
    while True:
        bad = next((cell for cell in cells
                    if bv.saturation_index(tuple(rays[i] for i in cell)) > 1),
                   None)
        if bad is None:
            return tuple(rays), cells, tuple(inserted)
        ray = fundamental_ray(bad, rays)
        ray_index = len(rays)
        rays.append(ray)
        cells = star_insert(cells, ray_index, rays)
        inserted.append(ray_index)


def cone_alpha(rows):
    rays, cells, inserted = saturated_cells(rows)
    values = []
    for cell in cells:
        cell_rows = tuple(rays[i] for i in cell)
        assert bv.saturation_index(cell_rows) == 1
        feasible_gram = bv.inverse(bv.normal_gram(cell_rows))
        values.append((cell, geometry.alpha_generic(feasible_gram)))
    return sum((value for _, value in values), Fraction(0)), rays, cells, values


def main():
    bv.self_test()
    normals, _ = bv.rank5_hive_normals()
    counts = Counter()
    negative = []
    minima = []
    minimum = None
    for ids in combinations(range(len(normals)), 4):
        rows = tuple(normals[i] for i in ids)
        index = bv.saturation_index(rows)
        if not index:
            counts["dependent"] += 1
            continue
        counts[f"index_{index}"] += 1
        alpha, rays, cells, values = cone_alpha(rows)
        counts["negative"] += alpha < 0
        counts["zero"] += alpha == 0
        if alpha < 0:
            negative.append((ids, index, alpha))
        if minimum is None or alpha < minimum:
            minimum = alpha
            minima = [(ids, index, alpha, rays, cells, values)]
        elif alpha == minimum:
            minima.append((ids, index, alpha, rays, cells, values))
    print("PASS")
    print(f"normal_sha256={bv.EXPECTED_NORMAL_SHA256}")
    print(f"counts={dict(counts)}")
    print(f"negative_cones={len(negative)}")
    print(f"negative_index_histogram={dict(Counter(x[1] for x in negative))}")
    print(f"minimum={minimum}")
    print(f"minimum_records={minima}")
    print("negative_records=")
    for record in negative:
        print(f"  ids={record[0]} index={record[1]} alpha={record[2]}")


if __name__ == "__main__":
    main()
