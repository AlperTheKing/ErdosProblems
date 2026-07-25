#!/usr/bin/env python3
"""Find the first exact rank-four hive wall that is not a unit 2<->2 flip.

This is a bounded falsification gate for the proposed rank-uniform wall
classification.  It compares simple, full-dimensional side-four hives with
the same actual facet rows, accepts only one-circuit fan changes, reconstructs
the integral wall boundary, and checks that the wall has exactly one
four-tight vertex and no other nonsimple vertex.
"""

from collections import defaultdict
from fractions import Fraction
from math import gcd, lcm
import random

import cdd.gmp as cg
from sympy import Matrix

from ghte_find_r4_wall_pair import exact_fan, hive_poly, partitions, primitive


def primitive_relation(normals):
    matrix = Matrix.hstack(*(Matrix(normal) for normal in normals))
    kernel = matrix.nullspace()
    if len(kernel) != 1 or any(value == 0 for value in kernel[0]):
        return None
    vector = kernel[0]
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, int(value.q))
    integers = [int(value * denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    integers = tuple(value // divisor for value in integers)
    if next(value for value in integers if value) < 0:
        integers = tuple(-value for value in integers)
    return integers


def circuit_sides(normals, coefficients):
    positive = frozenset(
        tuple(sorted(set(normals) - {normal}))
        for normal, coefficient in zip(normals, coefficients)
        if coefficient > 0
    )
    negative = frozenset(
        tuple(sorted(set(normals) - {normal}))
        for normal, coefficient in zip(normals, coefficients)
        if coefficient < 0
    )
    return positive, negative


def reconstruct_wall(left_boundary, right_boundary, left_fan, right_fan,
                     normals, coefficients):
    def omega(fan):
        return sum(
            Fraction(coefficient) * Fraction(fan["supports"][normal][0])
            for normal, coefficient in zip(normals, coefficients)
        )

    omega_left = omega(left_fan)
    omega_right = omega(right_fan)
    if not omega_left or not omega_right or omega_left * omega_right >= 0:
        return None
    t = -omega_left / (omega_right - omega_left)
    if not 0 < t < 1:
        return None

    rational_boundary = tuple(
        tuple((1 - t) * left + t * right
              for left, right in zip(left_part, right_part))
        for left_part, right_part in zip(left_boundary, right_boundary)
    )
    scale = 1
    for part in rational_boundary:
        for value in part:
            scale = lcm(scale, value.denominator)
    wall_boundary = tuple(
        tuple(int(scale * value) for value in part)
        for part in rational_boundary
    )

    # Scaling all support numbers does not change the normal fan.
    A, b, dimension, _, ok = hive_poly.build(*wall_boundary)
    if not ok or dimension != 3:
        return None
    matrix = cg.matrix_from_array(
        [[Fraction(b[i])] + [Fraction(-x) for x in A[i]]
         for i in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    if matrix.lin_set:
        return None
    wall_facets = tuple(sorted(
        primitive(tuple(-Fraction(x) for x in row[1:]))
        for row in matrix.array
    ))
    if wall_facets != left_fan["facets"] or wall_facets != right_fan["facets"]:
        return None

    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    tight_sets = []
    for row in generators.array:
        if row[0] != 1:
            return None
        vertex = tuple(Fraction(x) for x in row[1:])
        tight = tuple(sorted(
            primitive(tuple(-Fraction(x) for x in inequality[1:]))
            for inequality in matrix.array
            if Fraction(inequality[0])
            + sum(Fraction(inequality[j + 1]) * vertex[j]
                  for j in range(3)) == 0
        ))
        tight_sets.append(tight)
    nonsimple = [tight for tight in tight_sets if len(tight) == 4]
    if len(nonsimple) != 1 or set(nonsimple[0]) != set(normals):
        return None
    if any(len(tight) not in (3, 4) for tight in tight_sets):
        return None
    return {
        "t": t,
        "scale": scale,
        "boundary": wall_boundary,
        "omega_left": omega_left,
        "omega_right": omega_right,
        "wall_tight_sets": tuple(sorted(tight_sets)),
    }


def main():
    rng = random.Random(2026072204)
    by_total = {total: partitions(total) for total in range(41)}
    groups = defaultdict(list)
    tested = 0
    accepted = 0

    for _ in range(100000):
        total = rng.randint(12, 40)
        nu_choices = [part for part in by_total[total] if part[-1] > 0]
        nu = rng.choice(nu_choices)
        split = rng.randint(1, total - 1)
        lam_choices = [part for part in by_total[split]
                       if all(part[i] <= nu[i] for i in range(4))]
        mu_choices = [part for part in by_total[total - split]
                      if all(part[i] <= nu[i] for i in range(4))]
        if not lam_choices or not mu_choices:
            continue
        boundary = (rng.choice(lam_choices), rng.choice(mu_choices), nu)
        fan = exact_fan(*boundary)
        tested += 1
        if fan is None:
            continue
        accepted += 1
        key = (fan["facets"], tuple(sorted(fan["sources"].items())))

        for old_boundary, old_fan in groups[key]:
            left_only = old_fan["cones"] - fan["cones"]
            right_only = fan["cones"] - old_fan["cones"]
            if not left_only or not right_only:
                continue
            changed = tuple(left_only | right_only)
            normals = tuple(sorted(set().union(*map(set, changed))))
            if len(normals) != 4 or len(left_only) + len(right_only) != 4:
                continue
            coefficients = primitive_relation(normals)
            if coefficients is None:
                continue
            positive, negative = circuit_sides(normals, coefficients)
            if not ((left_only == positive and right_only == negative)
                    or (left_only == negative and right_only == positive)):
                continue
            sign_split = tuple(sorted((len(positive), len(negative))))
            unit = all(abs(value) == 1 for value in coefficients)
            if sign_split == (2, 2) and unit:
                continue

            wall = reconstruct_wall(
                old_boundary, boundary, old_fan, fan, normals, coefficients
            )
            if wall is None:
                continue
            print("PASS")
            print("tested", tested, "accepted", accepted)
            print("left", old_boundary)
            print("right", boundary)
            print("facets", fan["facets"])
            print("left_only", sorted(left_only))
            print("right_only", sorted(right_only))
            print("normals", normals)
            print("coefficients", coefficients)
            print("sign_split", sign_split, "unit", unit)
            print("wall", wall)
            return 0

        groups[key].append((boundary, fan))

    print("NO_COUNTERWALL", tested, accepted, len(groups))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
