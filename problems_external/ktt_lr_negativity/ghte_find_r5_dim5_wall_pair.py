#!/usr/bin/env python3
"""Targeted exact search for one intrinsic-dimension-five hive 2<->2 wall.

The finite input is an existing candidate list; this script is a definition
gate for one wall, not evidence for KTT and not a fixed-rank proof strategy.
All polyhedral decisions use cddlib over GMP rationals.
"""

from collections import defaultdict
from fractions import Fraction
from math import gcd, lcm
import json
import random
import sys

import cdd.gmp as cg
from sympy import Matrix

sys.path.insert(0, "problems_external/ktt_lr_negativity/engine")
import hive_poly  # noqa: E402


def parse(text):
    values = tuple(int(x) for x in text.split(","))
    return values + (0,) * (5 - len(values))


def primitive(vector, canonical=False):
    values = []
    denominator = 1
    for value in vector:
        value = Fraction(value)
        denominator = lcm(denominator, value.denominator)
        values.append(value)
    integers = [int(value * denominator) for value in values]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    answer = tuple(value // divisor for value in integers)
    if canonical:
        first = next(value for value in answer if value)
        if first < 0:
            answer = tuple(-value for value in answer)
    return answer


def extended_gcd(a, b):
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y


def tangent_basis(normal):
    """Columns 1..n-1 of U, where normal*U=(1,0,...,0)."""
    n = len(normal)
    U = [[int(i == j) for j in range(n)] for i in range(n)]
    row = list(normal)
    for j in range(1, n):
        a, b = row[0], row[j]
        if b == 0:
            continue
        g, s, t = extended_gcd(a, b)
        old0 = [U[i][0] for i in range(n)]
        oldj = [U[i][j] for i in range(n)]
        for i in range(n):
            U[i][0] = s * old0[i] + t * oldj[i]
            U[i][j] = (-b // g) * old0[i] + (a // g) * oldj[i]
        row[0], row[j] = g, 0
    assert abs(row[0]) == 1 and all(value == 0 for value in row[1:])
    if row[0] == -1:
        for i in range(n):
            U[i][0] *= -1
    return tuple(tuple(U[i][j] for i in range(n)) for j in range(1, n))


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def exact_fan(boundary, allow_nonsimple=False):
    A, b, ambient, _, ok = hive_poly.build(*boundary)
    if not ok or ambient != 6:
        return None
    matrix = cg.matrix_from_array(
        [[Fraction(b[i])] + [Fraction(-x) for x in A[i]] for i in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    if len(matrix.lin_set) != 1:
        return None
    equality_index = next(iter(matrix.lin_set))
    equality = tuple(Fraction(x) for x in matrix.array[equality_index])
    equality_normal = primitive(equality[1:], canonical=True)
    # Align the equation row with its canonical primitive direction.
    raw_eq_normal = primitive(equality[1:])
    sign = 1 if raw_eq_normal == equality_normal else -1
    eq_rhs = -sign * Fraction(equality[0]) / gcd(0, *[abs(int(x)) for x in equality[1:]])
    basis = tangent_basis(equality_normal)

    inequalities = [tuple(Fraction(x) for x in row)
                    for i, row in enumerate(matrix.array) if i != equality_index]
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    if any(row[0] != 1 for row in generators.array):
        return None
    vertices = [tuple(Fraction(x) for x in row[1:]) for row in generators.array]
    if not vertices:
        return None

    facet_records = []
    for inequality in inequalities:
        ambient_normal = tuple(-Fraction(x) for x in inequality[1:])
        restricted = primitive(tuple(dot(ambient_normal, column) for column in basis))
        on = tuple(i for i, vertex in enumerate(vertices)
                   if Fraction(inequality[0])
                   + dot(inequality[1:], vertex) == 0)
        sources = []
        for raw_index, (raw_normal, raw_rhs) in enumerate(zip(A, b)):
            if all(dot(raw_normal, vertices[i]) == raw_rhs for i in on):
                raw_values = tuple(dot(raw_normal, column) for column in basis)
                if not any(raw_values):
                    continue
                raw_restricted = primitive(raw_values)
                if raw_restricted == restricted:
                    sources.append(raw_index)
        if len(sources) != 1:
            return None
        facet_records.append({"id": (restricted, sources[0]), "on": on,
                              "source": sources[0]})
    ids = [record["id"] for record in facet_records]
    if len(ids) != len(set(ids)):
        return None

    cones = []
    tight_sets = []
    for vertex_index in range(len(vertices)):
        tight = tuple(sorted(record["id"] for record in facet_records
                             if vertex_index in record["on"]))
        tight_sets.append(tight)
        if not allow_nonsimple and len(tight) != 5:
            return None
        if len(tight) == 5:
            cones.append(tight)
    return {
        "boundary": boundary,
        "A": A,
        "b": b,
        "equality_normal": equality_normal,
        "equality_rhs": eq_rhs,
        "basis": basis,
        "facets": tuple(sorted(ids)),
        "cones": frozenset(cones),
        "tight_sets": tuple(sorted(tight_sets)),
        "vertices": tuple(vertices),
    }


def left_kernel_integer(rows):
    kernel = Matrix(rows).T.nullspace()
    if len(kernel) != 1:
        return None
    vector = kernel[0]
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, int(value.q))
    integers = [int(value * denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    return tuple(value // divisor for value in integers)


def wall_gate(left, right, changed):
    changed_ids = tuple(sorted(set().union(*map(set, changed))))
    if len(changed_ids) != 6:
        return None
    source_indices = [item[1] for item in changed_ids]
    rows = [left["equality_normal"]] + [left["A"][i] for i in source_indices]
    relation = left_kernel_integer(rows)
    if relation is None or any(value == 0 for value in relation[1:]):
        return None

    def omega(fan):
        rhs = [fan["equality_rhs"]] + [fan["b"][i] for i in source_indices]
        return dot(relation, rhs)

    omega_left, omega_right = omega(left), omega(right)
    if not omega_left or not omega_right or omega_left * omega_right >= 0:
        return None
    t = -omega_left / (omega_right - omega_left)
    denominator = t.denominator
    boundary = tuple(tuple(int((1 - t) * denominator * x
                               + t * denominator * y)
                           for x, y in zip(left_part, right_part))
                     for left_part, right_part in zip(left["boundary"], right["boundary"]))
    wall = exact_fan(boundary, allow_nonsimple=True)
    if wall is None:
        return None
    if wall["equality_normal"] != left["equality_normal"] or wall["facets"] != left["facets"]:
        return None
    nonsimple = [tight for tight in wall["tight_sets"] if len(tight) == 6]
    if len(nonsimple) != 1 or set(nonsimple[0]) != set(changed_ids):
        return None
    if any(len(tight) not in (5, 6) for tight in wall["tight_sets"]):
        return None
    return {"t": t, "scale": denominator, "boundary": boundary,
            "omega_left": omega_left, "omega_right": omega_right,
            "relation": relation, "changed_ids": changed_ids,
            "wall_tight_sets": wall["tight_sets"]}


def main():
    records = json.load(open(
        "problems_external/ktt_lr_negativity/purged_region/wave4_pop.json",
        encoding="utf-8",
    ))
    candidates = [record for record in records
                  if record.get("d_ambient") == 6 and record.get("dim") == 5
                  and record.get("status") == "NOT_SIMPLEX"]
    groups = defaultdict(list)
    accepted = 0
    tested = 0

    def consider(boundary):
        nonlocal accepted, tested
        tested += 1
        fan = exact_fan(boundary)
        if fan is None:
            return None
        accepted += 1
        key = (fan["equality_normal"], fan["facets"])
        for old in groups[key]:
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
            if len(common) != 2 or len(union) != 6:
                continue
            wall = wall_gate(old, fan, changed)
            if wall is None:
                continue
            return old, fan, left_only, right_only, wall
        groups[key].append(fan)
        return None

    for record in candidates:
        boundary = tuple(parse(record[key]) for key in ("lam", "mu", "nu"))
        result = consider(boundary)
        if result is not None:
            break
    else:
        result = None

    cache = {}

    def bounded_partitions(total, bounds):
        key = total, bounds
        if key in cache:
            return cache[key]
        output = []

        def rec(index, remaining, previous, current):
            if index == len(bounds):
                if remaining == 0:
                    output.append(tuple(current))
                return
            maximum = min(previous, bounds[index], remaining)
            for value in range(maximum, -1, -1):
                rec(index + 1, remaining - value, value, current + [value])

        rec(0, total, 10 ** 9, [])
        cache[key] = tuple(output)
        return cache[key]

    if result is None:
        rng = random.Random(2026072205)
        for _ in range(30000):
            tail = rng.randint(1, 9)
            third = tail + rng.randint(0, 10)
            second = third + rng.randint(0, 10)
            first = second + rng.randint(0, 10)
            nu = (first, second, third, tail, tail)
            total = sum(nu)
            split = rng.randint(1, total - 1)
            lambdas = bounded_partitions(split, nu)
            mus = bounded_partitions(total - split, nu)
            if not lambdas or not mus:
                continue
            boundary = (rng.choice(lambdas), rng.choice(mus), nu)
            result = consider(boundary)
            if result is not None:
                break

    if result is not None:
        old, fan, left_only, right_only, wall = result
        print("PASS")
        print("tested", tested, "accepted_before_pair", accepted)
        print("left", old["boundary"])
        print("right", fan["boundary"])
        print("equality_normal", fan["equality_normal"])
        print("facets", fan["facets"])
        print("left_only", sorted(left_only))
        print("right_only", sorted(right_only))
        print("wall", wall)
        return 0
    print("NO_PAIR", tested, accepted, len(groups))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
