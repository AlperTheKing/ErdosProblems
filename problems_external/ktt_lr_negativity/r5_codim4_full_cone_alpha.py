#!/usr/bin/env python3
"""Exact BV alpha of a rank-four hive normal cone via pulling triangulation.

Input normals are expressed in a saturated four-normal basis.  The polar
feasible cone is enumerated exactly, its three-dimensional cross-section is
pulling-triangulated, and the cone valuation is evaluated as the alternating
sum over internal simplices.  The current implementation deliberately accepts
only unimodular maximal simplices; this condition is checked, never assumed.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd

import r5_codim4_bv_independent as bv


def determinant(matrix):
    # Fraction Bareiss/Gaussian determinant; dimensions are at most four.
    work = [list(map(Fraction, row)) for row in matrix]
    size = len(work)
    answer = Fraction(1)
    sign = 1
    for col in range(size):
        pivot = next((row for row in range(col, size) if work[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign *= -1
        value = work[col][col]
        answer *= value
        for j in range(col, size):
            work[col][j] /= value
        for row in range(col + 1, size):
            value = work[row][col]
            for j in range(col, size):
                work[row][j] -= value * work[col][j]
    return sign * answer


def rank(rows):
    if not rows:
        return 0
    work = [list(map(Fraction, row)) for row in rows]
    row = 0
    for col in range(len(work[0])):
        pivot = next((i for i in range(row, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        value = work[row][col]
        work[row] = [entry / value for entry in work[row]]
        for i in range(len(work)):
            if i == row:
                continue
            value = work[i][col]
            work[i] = [a - value * b for a, b in zip(work[i], work[row])]
        row += 1
    return row


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(int(value)))
    assert divisor
    return tuple(int(value) // divisor for value in vector)


def kernel_ray(three_rows):
    assert len(three_rows) == 3
    vector = []
    for deleted in range(4):
        minor = [
            [row[j] for j in range(4) if j != deleted]
            for row in three_rows
        ]
        vector.append(((-1) ** deleted) * int(determinant(minor)))
    if not any(vector):
        return None
    return primitive(vector)


def feasible_extreme_rays(normal_coordinates):
    rays = set()
    for ids in combinations(range(len(normal_coordinates)), 3):
        rows = [normal_coordinates[i] for i in ids]
        if rank(rows) != 3:
            continue
        ray = kernel_ray(rows)
        for candidate in (ray, tuple(-value for value in ray)):
            if all(dot(normal, candidate) <= 0 for normal in normal_coordinates):
                rays.add(candidate)
                break
    rays = tuple(sorted(rays))
    assert rank(rays) == 4
    return rays


def cone_facets(normal_coordinates, rays):
    facets = set()
    for normal in normal_coordinates:
        vertices = tuple(i for i, ray in enumerate(rays) if dot(normal, ray) == 0)
        if len(vertices) >= 3 and rank([rays[i] for i in vertices]) == 3:
            facets.add(vertices)
    facets = tuple(sorted(facets))
    assert len(facets) >= 4
    return facets


def pulling_tetrahedra(rays, facets):
    apex = 0
    tetrahedra = set()
    for facet in facets:
        if apex in facet:
            continue
        if len(facet) == 3:
            triangles = {tuple(sorted(facet))}
        else:
            polygon_apex = min(facet)
            edges = set()
            facet_set = set(facet)
            for other in facets:
                if other == facet:
                    continue
                common = tuple(sorted(facet_set.intersection(other)))
                if len(common) == 2:
                    edges.add(common)
            triangles = {
                tuple(sorted((polygon_apex,) + edge))
                for edge in edges if polygon_apex not in edge
            }
            assert len(triangles) == len(facet) - 2, (facet, edges, triangles)
        for triangle in triangles:
            tetrahedron = tuple(sorted((apex,) + triangle))
            assert len(tetrahedron) == 4
            assert rank([rays[i] for i in tetrahedron]) == 4
            tetrahedra.add(tetrahedron)
    assert tetrahedra
    return tuple(sorted(tetrahedra))


def metric_gram(ray_ids, rays, lattice_gram):
    return tuple(
        tuple(
            sum(
                rays[i][a] * lattice_gram[a][b] * rays[j][b]
                for a in range(4) for b in range(4)
            )
            for j in ray_ids
        )
        for i in ray_ids
    )


def alpha_generic(gram):
    dimension = len(gram)
    values = []
    for prime in (17, 23, 29, 31, 37, 41):
        try:
            values.append(bv.mu_alpha(gram, tuple(prime ** i for i in range(dimension))))
        except AssertionError as error:
            if error.args:
                raise
            continue
        if len(values) == 2:
            break
    assert len(values) == 2 and values[0] == values[1]
    return values[0]


def full_cone_alpha(normal_coordinates, lattice_gram):
    normal_coordinates = tuple(sorted(set(map(tuple, normal_coordinates))))
    rays = feasible_extreme_rays(normal_coordinates)
    facets = cone_facets(normal_coordinates, rays)
    tetrahedra = pulling_tetrahedra(rays, facets)
    determinant_histogram = {}
    for tetrahedron in tetrahedra:
        matrix = [[rays[j][i] for j in tetrahedron] for i in range(4)]
        index = abs(int(determinant(matrix)))
        determinant_histogram[index] = determinant_histogram.get(index, 0) + 1
    assert set(determinant_histogram) == {1}, determinant_histogram

    simplices = set()
    for tetrahedron in tetrahedra:
        for size in range(1, 5):
            simplices.update(combinations(tetrahedron, size))

    value = Fraction(0)
    internal_terms = []
    for simplex in sorted(simplices, key=lambda item: (len(item), item)):
        interior_point = tuple(sum(rays[i][j] for i in simplex) for j in range(4))
        if not all(dot(normal, interior_point) < 0 for normal in normal_coordinates):
            continue
        gram = metric_gram(simplex, rays, lattice_gram)
        alpha = alpha_generic(gram)
        sign = (-1) ** (4 - len(simplex))
        value += sign * alpha
        internal_terms.append((simplex, sign, alpha))
    return {
        "alpha": value,
        "rays": rays,
        "facets": facets,
        "tetrahedra": tetrahedra,
        "determinant_histogram": determinant_histogram,
        "internal_terms": tuple(internal_terms),
    }


def coordinates_in_basis(normals, basis_ids, active_ids):
    basis = tuple(normals[i] for i in basis_ids)
    gram = bv.normal_gram(basis)
    gram_inverse = bv.inverse(gram)
    coordinates = []
    for index in active_ids:
        products = tuple(dot(basis[i], normals[index]) for i in range(4))
        coordinate = tuple(
            sum(gram_inverse[i][j] * products[j] for j in range(4))
            for i in range(4)
        )
        assert all(value.denominator == 1 for value in coordinate)
        reconstruction = tuple(
            sum(int(coordinate[i]) * basis[i][j] for i in range(4))
            for j in range(6)
        )
        assert reconstruction == normals[index]
        coordinates.append(tuple(map(int, coordinate)))
    return tuple(coordinates), gram_inverse


def main():
    normals, _ = bv.rank5_hive_normals()
    basis_ids = (0, 1, 4, 5)
    active_ids = (0, 1, 2, 3, 4, 5)
    coordinates, lattice_gram = coordinates_in_basis(normals, basis_ids, active_ids)
    result = full_cone_alpha(coordinates, lattice_gram)
    assert result["alpha"] == Fraction(17977, 604800)
    print("PASS")
    print(f"basis_ids={basis_ids} active_ids={active_ids}")
    for key, value in result.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
