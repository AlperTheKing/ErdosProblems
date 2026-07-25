#!/usr/bin/env python3
"""Exact Chow-ring GHTE gate for one smooth full-dimensional side-five hive.

This finite gate is not a proof of general GHTE or KTT.  It reconstructs one
complete normal fan over Q, proves that the fan is smooth in Z^6, eliminates
the six linear fan relations, builds every graded Chow group from the
Stanley--Reisner ideal, expands the Todd product, and solves the invariant-cycle
effectivity problem over exact rationals.  A failed degree emits an exact
separating functional.
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
import sys

import cdd.gmp as cg
from sympy import Matrix, Rational

sys.path.insert(0, "problems_external/ktt_lr_negativity/engine")
import hive_poly  # noqa: E402


TRIPLE = (
    (16, 13, 10, 4, 1),
    (13, 9, 4, 1),
    (27, 22, 13, 5, 4),
)
DIMENSION = 6
TODD_FACTOR = {
    0: Q(1), 1: Q(1, 2), 2: Q(1, 12), 3: Q(0),
    4: Q(-1, 720), 5: Q(0), 6: Q(1, 30240),
}


def gcd_many(values):
    from math import gcd

    answer = 0
    for value in values:
        answer = gcd(answer, abs(int(value)))
    return answer


def primitive(vector):
    divisor = gcd_many(vector)
    assert divisor > 0
    return tuple(int(value) // divisor for value in vector)


def determinant(columns):
    return int(Matrix.hstack(*(Matrix(column) for column in columns)).det())


def reconstruct_fan():
    A, b, ambient, _, ok = hive_poly.build(*TRIPLE)
    assert ok and ambient == DIMENSION
    matrix = cg.matrix_from_array(
        [[Q(b[row])] + [Q(-value) for value in A[row]]
         for row in range(len(A))],
        rep_type=cg.RepType.INEQUALITY,
    )
    cg.matrix_canonicalize(matrix)
    assert not matrix.lin_set
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    assert generators.array and all(row[0] == 1 for row in generators.array)
    vertices = tuple(tuple(Q(value) for value in row[1:])
                     for row in generators.array)

    facets = []
    for inequality in matrix.array:
        normal = primitive(tuple(-Q(value) for value in inequality[1:]))
        support = Q(inequality[0])
        sources = []
        for source, (raw_normal, raw_support) in enumerate(zip(A, b)):
            divisor = gcd_many(raw_normal)
            if (primitive(raw_normal) == normal
                    and Q(raw_support, divisor) == support):
                sources.append(source)
        assert len(sources) == 1
        facets.append((normal, sources[0], tuple(Q(value) for value in inequality)))
    facets.sort(key=lambda item: (item[0], item[1]))
    rays = tuple(item[0] for item in facets)
    assert len(rays) == len(set(rays))

    maximal = []
    for vertex in vertices:
        tight = tuple(index for index, (_, _, inequality) in enumerate(facets)
                      if inequality[0] + sum(
                          inequality[j + 1] * vertex[j]
                          for j in range(DIMENSION)) == 0)
        assert len(tight) == DIMENSION
        assert abs(determinant(tuple(rays[index] for index in tight))) == 1
        maximal.append(tuple(sorted(tight)))
    maximal = tuple(sorted(set(maximal)))
    assert len(maximal) == len(vertices)
    assert set().union(*(set(cone) for cone in maximal)) == set(range(len(rays)))
    return rays, maximal, vertices


def fan_cones(maximal, degree):
    if degree == 0:
        return ((),)
    return tuple(sorted({face for cone in maximal
                         for face in combinations(cone, degree)}))


def divisor_forms(rays):
    """Express all invariant divisors in two free Picard generators."""
    matrix = Matrix([[ray[j] for ray in rays] for j in range(DIMENSION)])
    reduced, pivots = matrix.rref()
    free = tuple(index for index in range(len(rays)) if index not in pivots)
    assert len(free) == len(rays) - DIMENSION == 2
    forms = [(Q(0), Q(0)) for _ in rays]
    forms[free[0]] = (Q(1), Q(0))
    forms[free[1]] = (Q(0), Q(1))
    for row, pivot in enumerate(pivots):
        forms[pivot] = tuple(
            -Q(int(reduced[row, column].p), int(reduced[row, column].q))
            for column in free
        )
    for coordinate in range(DIMENSION):
        assert all(sum(Q(rays[index][coordinate]) * forms[index][j]
                       for index in range(len(rays))) == 0 for j in range(2))
    return free, tuple(forms)


# A homogeneous binary form of degree d is a tuple of length d+1.  Entry k is
# the coefficient of X^(d-k)Y^k.
def multiply(left, right):
    answer = [Q(0)] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            answer[i + j] += x * y
    return tuple(answer)


def power(form, exponent):
    answer = (Q(1),)
    for _ in range(exponent):
        answer = multiply(answer, form)
    return answer


def cone_form(cone, forms):
    answer = (Q(1),)
    for ray in cone:
        answer = multiply(answer, forms[ray])
    return answer


def todd_components(forms):
    graded = [(Q(1),)] + [tuple(Q(0) for _ in range(q + 1))
                          for q in range(1, DIMENSION + 1)]
    for form in forms:
        factor = [tuple(TODD_FACTOR[q] * value for value in power(form, q))
                  for q in range(DIMENSION + 1)]
        updated = [tuple(Q(0) for _ in range(q + 1))
                   for q in range(DIMENSION + 1)]
        for old_degree in range(DIMENSION + 1):
            for add_degree in range(DIMENSION - old_degree + 1):
                term = multiply(graded[old_degree], factor[add_degree])
                total = old_degree + add_degree
                updated[total] = tuple(updated[total][i] + term[i]
                                       for i in range(total + 1))
        graded = updated
    return tuple(graded)


def is_face(subset, maximal_sets):
    test = frozenset(subset)
    return any(test <= cone for cone in maximal_sets)


def chow_relations(maximal, forms, degree):
    """Degree-q image of the Stanley--Reisner ideal after linear elimination."""
    if degree == 0:
        return tuple()
    maximal_sets = tuple(frozenset(cone) for cone in maximal)
    rows = []
    for size in range(2, degree + 1):
        for subset in combinations(range(len(forms)), size):
            if is_face(subset, maximal_sets):
                continue
            base = cone_form(subset, forms)
            for y_power in range(degree - size + 1):
                monomial = tuple(
                    Q(1) if index == y_power else Q(0)
                    for index in range(degree - size + 1)
                )
                row = multiply(base, monomial)
                if any(row):
                    rows.append(row)
    if not rows:
        return tuple()
    matrix = Matrix([[Rational(value.numerator, value.denominator)
                      for value in row] for row in rows])
    return tuple(tuple(Q(int(value.p), int(value.q)) for value in row)
                 for row in matrix.rowspace())


def annihilator(relations, width):
    if relations:
        matrix = Matrix([[Rational(value.numerator, value.denominator)
                          for value in row] for row in relations])
    else:
        matrix = Matrix.zeros(0, width)
    return tuple(tuple(Q(int(value.p), int(value.q)) for value in column)
                 for column in matrix.nullspace())


def dot(left, right):
    return sum((x * y for x, y in zip(left, right)), Q(0))


def exact_polyhedron_point(inequalities, equalities, variable_count):
    rows = [tuple(row) for row in inequalities] + [tuple(row) for row in equalities]
    matrix = cg.matrix_from_array(rows, rep_type=cg.RepType.INEQUALITY)
    matrix.lin_set = set(range(len(inequalities), len(rows)))
    cg.matrix_canonicalize(matrix)
    polyhedron = cg.polyhedron_from_matrix(matrix)
    generators = cg.copy_generators(polyhedron)
    points = [row for row in generators.array if row[0] == 1]
    if not points:
        return None
    point = tuple(Q(value) for value in points[0][1:])
    assert len(point) == variable_count
    return point


def solve_effectivity(generator_forms, target, quotient_dual):
    projected_target = tuple(dot(vector, target) for vector in quotient_dual)
    columns = tuple(tuple(dot(vector, generator) for vector in quotient_dual)
                    for generator in generator_forms)
    inequalities = []
    for index in range(len(columns)):
        row = [Q(0)] * (len(columns) + 1)
        row[index + 1] = Q(1)
        inequalities.append(tuple(row))
    equalities = [tuple([-projected_target[j]]
                        + [column[j] for column in columns])
                  for j in range(len(quotient_dual))]
    representative = exact_polyhedron_point(
        inequalities, equalities, len(columns))
    if representative is not None:
        assert min(representative) >= 0
        for j, rhs in enumerate(projected_target):
            assert sum(columns[i][j] * representative[i]
                       for i in range(len(columns))) == rhs
        return representative, None, None

    # Farkas separator on the quotient.  Its values on orbit classes form a
    # nonnegative Minkowski-weight functional; its Todd pairing is <= -1.
    dual_inequalities = [tuple([Q(0)] + list(column)) for column in columns]
    dual_inequalities.append(tuple(
        [Q(-1)] + [-value for value in projected_target]))
    separator = exact_polyhedron_point(
        dual_inequalities, (), len(quotient_dual))
    assert separator is not None
    cone_weights = tuple(dot(separator, column) for column in columns)
    todd_pairing = dot(separator, projected_target)
    assert min(cone_weights) >= 0 and todd_pairing <= -1
    return None, separator, (cone_weights, todd_pairing)


def serialize(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, tuple):
        return [serialize(item) for item in value]
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize(item) for key, item in value.items()}
    return value


def main():
    rays, maximal, vertices = reconstruct_fan()
    free, forms = divisor_forms(rays)
    todd = todd_components(forms)
    records = []
    chow_dimensions = []
    for degree in range(DIMENSION + 1):
        cones = fan_cones(maximal, degree)
        generators = tuple(cone_form(cone, forms) for cone in cones)
        relations = chow_relations(maximal, forms, degree)
        quotient_dual = annihilator(relations, degree + 1)
        representative, separator, witness = solve_effectivity(
            generators, todd[degree], quotient_dual)
        status = "EFFECTIVE" if representative is not None else "NON_EFFECTIVE"
        chow_dimensions.append(len(quotient_dual))
        records.append({
            "q": degree,
            "cones": cones,
            "relations": relations,
            "chow_dimension": len(quotient_dual),
            "status": status,
            "representative": representative,
            "separator": separator,
            "witness": witness,
        })
        print(f"q={degree} cones={len(cones)} Aq={len(quotient_dual)} "
              f"status={status}", flush=True)
        if witness is not None:
            print(f"cone_weights={witness[0]}", flush=True)
            print(f"todd_pairing={witness[1]}", flush=True)
            break

    assert chow_dimensions == chow_dimensions[::-1]
    payload = {
        "schema": "r5-full-dimensional-smooth-ghte-chow-v2",
        "triple": TRIPLE,
        "dimension": DIMENSION,
        "rays": rays,
        "maximal_cones": maximal,
        "vertices": vertices,
        "free_divisor_indices": free,
        "divisor_forms": forms,
        "todd_components": todd,
        "records": records,
    }
    encoded = json.dumps(serialize(payload), sort_keys=True,
                         separators=(",", ":")).encode("ascii")
    print("PASS", flush=True)
    print(f"payload_sha256={sha256(encoded).hexdigest()}", flush=True)
    print(f"rays={len(rays)} maximal_cones={len(maximal)}", flush=True)
    print(f"chow_dimensions={tuple(chow_dimensions)}", flush=True)
    print("scope=one actual smooth full-dimensional r5 hive fan only", flush=True)
    return 0 if all(record["status"] == "EFFECTIVE" for record in records) else 10


if __name__ == "__main__":
    raise SystemExit(main())
