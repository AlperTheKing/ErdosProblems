#!/usr/bin/env python3
"""Independent exact replay of the smallest non-2<->2 hive support wall."""

from fractions import Fraction
from math import gcd, lcm
import sys

import cdd.gmp as cg
from sympy import Matrix

sys.path.insert(0, "problems_external/ktt_lr_negativity/engine")
import hive_poly  # noqa: E402


WALL = ((7, 4, 2, 1), (8, 5, 3, 1), (10, 9, 7, 5))
LEFT = ((13, 8, 4, 3), (16, 10, 6, 2), (20, 18, 14, 10))
RIGHT = ((15, 8, 4, 1), (16, 10, 6, 2), (20, 18, 14, 10))
WALL_POINT = (16, 20, 24)

CIRCUIT_ROWS = (1, 3, 7)
A_RAY = (-1, 1, 0)
B_RAY = (0, -1, 0)
C_RAY = (-1, 0, 0)
CIRCUIT = (A_RAY, B_RAY, C_RAY)
COEFFICIENTS = (1, 1, -1)
LINKS = ((0, 0, 1), (1, 0, -1))


def primitive(vector):
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, Fraction(value).denominator)
    integers = [int(Fraction(value) * denominator) for value in vector]
    divisor = gcd(0, *(abs(value) for value in integers))
    assert divisor
    return tuple(value // divisor for value in integers)


def exact_fan(boundary):
    A, b, dimension, _, ok = hive_poly.build(*boundary)
    assert ok and dimension == 3
    matrix = cg.matrix_from_array(
        [[Fraction(b[row])] + [Fraction(-value) for value in A[row]]
         for row in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    assert not matrix.lin_set
    facets = tuple(sorted(primitive(tuple(-value for value in row[1:]))
                          for row in matrix.array))
    assert len(facets) == len(set(facets))
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    assert generators.array and all(row[0] == 1 for row in generators.array)
    vertices = tuple(tuple(Fraction(value) for value in row[1:])
                     for row in generators.array)
    cones = []
    for vertex in vertices:
        tight = tuple(sorted(
            primitive(tuple(-value for value in inequality[1:]))
            for inequality in matrix.array
            if Fraction(inequality[0])
            + sum(Fraction(inequality[index + 1]) * vertex[index]
                  for index in range(3)) == 0
        ))
        assert len(tight) == 3
        cones.append(tight)
    return facets, frozenset(cones), tuple(sorted(vertices))


def omega(boundary):
    A, b, _, _, ok = hive_poly.build(*boundary)
    assert ok
    assert tuple(tuple(A[row]) for row in CIRCUIT_ROWS) == CIRCUIT
    return sum(coefficient * b[row]
               for coefficient, row in zip(COEFFICIENTS, CIRCUIT_ROWS))


def main():
    # Partition and LR-size checks; 2*WALL is the midpoint of LEFT and RIGHT.
    for boundary in (WALL, LEFT, RIGHT):
        for part in boundary:
            assert all(part[index] >= part[index + 1]
                       for index in range(len(part) - 1))
            assert part[-1] >= 0
        assert sum(boundary[0]) + sum(boundary[1]) == sum(boundary[2])
    assert tuple(tuple(LEFT[p][i] + RIGHT[p][i] for i in range(4))
                 for p in range(3)) == tuple(tuple(4 * value for value in part)
                                              for part in WALL)

    A, b, dimension, _, ok = hive_poly.build(*WALL)
    assert ok and dimension == 3
    assert tuple(tuple(A[row]) for row in CIRCUIT_ROWS) == CIRCUIT

    # Exact primitive dependence a+b-c=0 and no proper dependent subset.
    circuit_matrix = Matrix.hstack(*(Matrix(ray) for ray in CIRCUIT))
    assert circuit_matrix.rank() == 2
    kernel = circuit_matrix.nullspace()
    assert len(kernel) == 1
    kernel_vector = tuple(int(value) for value in kernel[0])
    if kernel_vector[0] < 0:
        kernel_vector = tuple(-value for value in kernel_vector)
    assert kernel_vector == COEFFICIENTS
    assert gcd(0, *(abs(value) for value in COEFFICIENTS)) == 1

    # The restricted support functional is the explicit Horn-type form
    # omega = nu_2-lambda_4-mu_1.
    for boundary in (WALL, LEFT, RIGHT):
        expected = boundary[2][1] - boundary[0][3] - boundary[1][0]
        assert omega(boundary) == expected
    assert (omega(LEFT), omega(WALL), omega(RIGHT)) == (-1, 0, 1)

    # At the wall, precisely the three circuit rows are tight at an interior
    # point of their one-dimensional common face.
    slacks = tuple(
        b[row] - sum(A[row][index] * WALL_POINT[index] for index in range(3))
        for row in range(len(A))
    )
    assert tuple(index for index, slack in enumerate(slacks) if slack == 0) == CIRCUIT_ROWS
    assert min(slack for slack in slacks if slack > 0) == 1
    assert b[1] + b[3] == b[7]

    left_facets, left_cones, left_vertices = exact_fan(LEFT)
    right_facets, right_cones, right_vertices = exact_fan(RIGHT)
    expected_left_facets = (
        A_RAY, B_RAY, (0, 0, 1), (1, 0, -1), (1, 0, 0)
    )
    expected_right_facets = tuple(sorted(expected_left_facets + (C_RAY,)))
    assert left_facets == tuple(sorted(expected_left_facets))
    assert right_facets == expected_right_facets
    assert len(left_vertices) == 6 and len(right_vertices) == 8

    coarse = frozenset(tuple(sorted((A_RAY, B_RAY, link))) for link in LINKS)
    refined = frozenset(
        tuple(sorted((A_RAY, C_RAY, link))) for link in LINKS
    ) | frozenset(
        tuple(sorted((B_RAY, C_RAY, link))) for link in LINKS
    )
    assert left_cones - right_cones == coarse
    assert right_cones - left_cones == refined
    assert len(left_cones & right_cones) == 4

    # Quotient each saturated primitive link.  Both quotient maps are
    # surjective with the link as kernel, and both preserve a+b=c literally.
    quotient_maps = (
        Matrix([[1, 0, 0], [0, 1, 0]]),
        Matrix([[1, 0, 1], [0, 1, 0]]),
    )
    for link, quotient in zip(LINKS, quotient_maps):
        assert tuple(quotient * Matrix(link)) == (0, 0)
        assert gcd(0, *(abs(int(value)) for value in quotient)) == 1
        images = tuple(tuple(quotient * Matrix(ray)) for ray in CIRCUIT)
        assert images == ((-1, 1), (0, -1), (-1, 0))
        assert images[0][0] + images[1][0] == images[2][0]
        assert images[0][1] + images[1][1] == images[2][1]

    print("PASS")
    print("rank 4")
    print("wall", WALL)
    print("left", LEFT, "omega", omega(LEFT))
    print("right", RIGHT, "omega", omega(RIGHT))
    print("circuit", CIRCUIT, COEFFICIENTS)
    print("links", LINKS)
    print("facet_counts", len(left_facets), len(right_facets))
    print("changed_maximal_cones", len(coarse), len(refined))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
