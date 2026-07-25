#!/usr/bin/env python3
"""Targeted exact search for one rank-four hive 2<->2 fan wall.

This is a definition gate for the GHTE wall-crossing route, not a census.
Every polytope and incidence decision is made by cddlib over GMP rationals.
"""

from collections import defaultdict
from fractions import Fraction
from math import gcd, lcm
import random
import sys

import cdd.gmp as cg
from sympy import Matrix

sys.path.insert(0, "problems_external/ktt_lr_negativity/engine")
import hive_poly  # noqa: E402


def partitions(total, length=4):
    out = []

    def rec(rem, maximum, current):
        if len(current) == length:
            if rem == 0:
                out.append(tuple(current))
            return
        for value in range(min(maximum, rem), -1, -1):
            rec(rem - value, value, current + [value])

    rec(total, total, [])
    return out


def primitive(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(int(value)))
    return tuple(int(value) // divisor for value in vector)


def exact_fan(lam, mu, nu):
    A, b, dimension, _, ok = hive_poly.build(lam, mu, nu)
    if not ok or dimension != 3:
        return None
    matrix = cg.matrix_from_array(
        [[Fraction(b[i])] + [Fraction(-x) for x in A[i]] for i in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    if matrix.lin_set:
        return None
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    vertices = [tuple(Fraction(x) for x in row[1:]) for row in generators.array if row[0] == 1]
    if not vertices or any(row[0] != 1 for row in generators.array):
        return None
    facets = []
    supports = {}
    sources = {}
    for row in matrix.array:
        normal = primitive(tuple(-Fraction(x) for x in row[1:]))
        facets.append(normal)
        supports[normal] = tuple(Fraction(x) for x in row)
        source = []
        for index, (raw_normal, raw_rhs) in enumerate(zip(A, b)):
            divisor = 0
            for value in raw_normal:
                divisor = gcd(divisor, abs(value))
            if primitive(raw_normal) == normal and Fraction(raw_rhs, divisor) == Fraction(row[0]):
                source.append(index)
        sources[normal] = tuple(source)
    if len(set(facets)) != len(facets):
        return None
    cones = []
    for vertex in vertices:
        tight = []
        for normal, row in zip(facets, matrix.array):
            if Fraction(row[0]) + sum(Fraction(row[j + 1]) * vertex[j] for j in range(3)) == 0:
                tight.append(normal)
        if len(tight) != 3:
            return None
        cones.append(tuple(sorted(tight)))
    return {
        "facets": tuple(sorted(facets)),
        "cones": frozenset(cones),
        "vertices": tuple(sorted(vertices)),
        "supports": supports,
        "sources": sources,
    }


def circuit_coefficients(normals):
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
    return integers


def wall_boundary(left, right, changed, left_fan, right_fan):
    normals = tuple(sorted(set().union(*map(set, changed))))
    coefficients = circuit_coefficients(normals)
    if coefficients is None or sorted(sum(value > 0 for value in coefficients)
                                       for _ in [0]) != [2]:
        return None
    def omega(fan):
        return sum(Fraction(c) * Fraction(fan["supports"][normal][0])
                   for c, normal in zip(coefficients, normals))
    omega_left, omega_right = omega(left_fan), omega(right_fan)
    if not omega_left or not omega_right or omega_left * omega_right >= 0:
        return None
    t = -omega_left / (omega_right - omega_left)
    if not 0 < t < 1:
        return None
    boundary = []
    denominator = 1
    for lpart, rpart in zip(left, right):
        part = tuple((1 - t) * x + t * y for x, y in zip(lpart, rpart))
        boundary.append(part)
        for value in part:
            denominator = lcm(denominator, value.denominator)
    scaled = tuple(tuple(int(denominator * value) for value in part) for part in boundary)
    A, b, dimension, _, ok = hive_poly.build(*scaled)
    if not ok or dimension != 3:
        return None
    matrix = cg.matrix_from_array(
        [[Fraction(b[i])] + [Fraction(-x) for x in A[i]] for i in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    if matrix.lin_set:
        return None
    wall_facets = tuple(sorted(primitive(tuple(-Fraction(x) for x in row[1:]))
                                for row in matrix.array))
    if wall_facets != left_fan["facets"]:
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
            + sum(Fraction(inequality[j + 1]) * vertex[j] for j in range(3)) == 0
        ))
        tight_sets.append(tight)
    nonsimple = [tight for tight in tight_sets if len(tight) == 4]
    if len(nonsimple) != 1 or set(nonsimple[0]) != set(normals):
        return None
    if any(len(tight) not in (3, 4) for tight in tight_sets):
        return None
    return {"t": t, "scale": denominator, "boundary": scaled,
            "normals": normals, "coefficients": coefficients,
            "omega_left": omega_left, "omega_right": omega_right,
            "wall_tight_sets": tuple(sorted(tight_sets))}


def main():
    rng = random.Random(20260722)
    by_total = {n: partitions(n) for n in range(0, 41)}
    groups = defaultdict(list)
    tested = 0
    accepted = 0
    for _ in range(50000):
        total = rng.randint(12, 40)
        nu_choices = [p for p in by_total[total] if p[-1] > 0]
        nu = rng.choice(nu_choices)
        split = rng.randint(1, total - 1)
        lam_choices = [p for p in by_total[split]
                       if all(p[i] <= nu[i] for i in range(4))]
        mu_choices = [p for p in by_total[total - split]
                      if all(p[i] <= nu[i] for i in range(4))]
        if not lam_choices or not mu_choices:
            continue
        lam = rng.choice(lam_choices)
        mu = rng.choice(mu_choices)
        fan = exact_fan(lam, mu, nu)
        tested += 1
        if fan is None:
            continue
        accepted += 1
        key = (fan["facets"], tuple(sorted(fan["sources"].items())))
        for old_lam, old_mu, old_nu, old in groups[key]:
            left_only = old["cones"] - fan["cones"]
            right_only = fan["cones"] - old["cones"]
            if len(left_only) != 2 or len(right_only) != 2:
                continue
            changed = tuple(left_only | right_only)
            common = set(changed[0])
            union = set()
            for cone in changed:
                common &= set(cone)
                union |= set(cone)
            if len(common) == 0 and len(union) == 4:
                left = (old_lam, old_mu, old_nu)
                right = (lam, mu, nu)
                wall = wall_boundary(left, right, changed, old, fan)
                if wall is None:
                    continue
                print("PASS")
                print("tested", tested, "accepted", accepted)
                print("left", old_lam, old_mu, old_nu)
                print("right", lam, mu, nu)
                print("facets", fan["facets"])
                print("left_only", sorted(left_only))
                print("right_only", sorted(right_only))
                print("wall", wall)
                return 0
        groups[key].append((lam, mu, nu, fan))
    print("NO_PAIR", tested, accepted, len(groups))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
