#!/usr/bin/env python3
"""Exact Todd audit for the actual rank-four hive facet-birth wall.

The refined fan is the star subdivision of the coarse fan along cone(a,b)
by c=a+b.  This checker verifies the smooth complete fans, their Chow rings,
all Todd degrees, the canonical pullback corrections, endpoint q=2 GHTE
representatives, and balanced separators for the two negative exceptional
corrections.  It tests canonical GHTE transport only; it is not a GHTE or KTT
counterexample.
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from math import gcd

import sympy as sp


ALL_RAYS = {
    "a": (-1, 1, 0),
    "b": (0, -1, 0),
    "c": (-1, 0, 0),
    "e": (1, 0, 0),
    "u": (0, 0, 1),
    "v": (1, 0, -1),
}
COARSE_RAYS = {name: ALL_RAYS[name] for name in "abeuv"}
REFINED_RAYS = dict(ALL_RAYS)

COARSE_MAXIMAL = ("abu", "abv", "aeu", "aev", "beu", "bev")
REFINED_MAXIMAL = (
    "acu", "acv", "bcu", "bcv", "aeu", "aev", "beu", "bev"
)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def determinant(left, middle, right):
    return dot(left, cross(middle, right))


def primitive(vector):
    divisor = gcd(0, *(abs(int(value)) for value in vector))
    assert divisor > 0
    return tuple(int(value) // divisor for value in vector)


def inverse(matrix):
    size = len(matrix)
    work = [
        [Q(matrix[i][j]) for j in range(size)]
        + [Q(i == j) for j in range(size)]
        for i in range(size)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [x - scale * y
                         for x, y in zip(work[row], work[column])]
    return tuple(tuple(row[size:]) for row in work)


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def transpose(matrix):
    return tuple(tuple(row[column] for row in matrix)
                 for column in range(len(matrix[0])))


def integer_vectors_l1(radius):
    return tuple(
        vector for vector in product(range(-radius, radius + 1), repeat=3)
        if sum(abs(value) for value in vector) <= radius
    )


def quotient_completion(normal):
    """Return an exact unimodular coordinate map with normal first."""
    for radius in range(1, 7):
        vectors = integer_vectors_l1(radius)
        candidates = []
        for first in vectors:
            for second in vectors:
                if determinant(normal, first, second) == 1:
                    candidates.append((
                        sum(abs(x) for x in first)
                        + sum(abs(x) for x in second),
                        first,
                        second,
                    ))
        if candidates:
            _, first, second = min(candidates)
            columns = (normal, first, second)
            rows = tuple(tuple(columns[j][i] for j in range(3))
                         for i in range(3))
            answer = inverse(rows)
            assert all(value.denominator == 1
                       for row in answer for value in row)
            return answer
    raise AssertionError(f"no quotient completion for {normal}")


def quotient_vector(normal, other, completion):
    coordinates = matvec(completion, other)
    return primitive(tuple(int(value) for value in coordinates[1:]))


def two_cones(maximal):
    return tuple(sorted({"".join(sorted(pair))
                         for cone in maximal for pair in combinations(cone, 2)}))


def verify_fan(rays, maximal):
    cells = two_cones(maximal)
    assert len(rays) - len(cells) + len(maximal) == 2
    for cone in maximal:
        assert abs(determinant(*(rays[ray] for ray in cone))) == 1
    for cell in cells:
        containing = [cone for cone in maximal if set(cell) < set(cone)]
        assert len(containing) == 2
        extras = [next(ray for ray in cone if ray not in cell)
                  for cone in containing]
        left, right = (rays[ray] for ray in cell)
        signs = [determinant(left, right, rays[extra]) for extra in extras]
        assert signs[0] * signs[1] < 0
    return cells


def build_q2_balance(rays, cells):
    ray_order = tuple(sorted(rays))
    completions = {ray: quotient_completion(rays[ray]) for ray in ray_order}
    matrix = [[0] * len(cells) for _ in range(2 * len(ray_order))]
    for column, cell in enumerate(cells):
        left, right = cell
        for ray, other in ((left, right), (right, left)):
            quotient = quotient_vector(rays[ray], rays[other], completions[ray])
            block = ray_order.index(ray)
            matrix[2 * block][column] = quotient[0]
            matrix[2 * block + 1][column] = quotient[1]
    return tuple(tuple(row) for row in matrix)


def pair_index(left, right):
    return gcd(0, *(abs(value) for value in cross(left, right)))


def bv_alpha_q2(left, right):
    assert pair_index(left, right) == 1
    aa, bb, ab = dot(left, left), dot(right, right), dot(left, right)
    return Q(1, 4) - Q(ab, 12) * (Q(1, aa) + Q(1, bb))


def solve_linear(rows, rhs):
    columns = len(rows[0])
    work = [[Q(value) for value in row] + [Q(rhs[index])]
            for index, row in enumerate(rows)]
    pivots = []
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, len(work))
                      if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [x - scale * y
                         for x, y in zip(work[row], work[pivot_row])]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    for row in range(pivot_row, len(work)):
        assert any(work[row][column] for column in range(columns)) or not work[row][-1]
    answer = [Q(0)] * columns
    for row, column in enumerate(pivots):
        answer[column] = work[row][-1]
    assert matvec(rows, answer) == tuple(map(Q, rhs))
    return tuple(answer)


def verify_q2_effective(rays, maximal, representative_by_cell):
    cells = verify_fan(rays, maximal)
    balance = build_q2_balance(rays, cells)
    bv = tuple(bv_alpha_q2(rays[cell[0]], rays[cell[1]]) for cell in cells)
    representative = tuple(Q(representative_by_cell.get(cell, 0)) for cell in cells)
    assert min(representative) >= 0
    target = tuple(representative[index] - bv[index]
                   for index in range(len(cells)))
    relation = solve_linear(transpose(balance), target)
    assert tuple(bv[index] + matvec(transpose(balance), relation)[index]
                 for index in range(len(cells))) == representative
    return cells, balance, bv, representative, relation


def todd_components(divisors, variables):
    expression = sp.Integer(1)
    for divisor in divisors:
        expression = sp.expand(
            expression * (1 + divisor / 2 + divisor**2 / 12)
        )
    output = []
    for degree in range(4):
        terms = [term for term in sp.Add.make_args(expression)
                 if sp.Poly(term, *variables).total_degree() == degree]
        output.append(sp.expand(sum(terms, sp.Integer(0))))
    return tuple(output)


def main():
    a, b, c = (ALL_RAYS[name] for name in "abc")
    assert tuple(a[index] + b[index] for index in range(3)) == c
    coarse_cells = verify_fan(COARSE_RAYS, COARSE_MAXIMAL)
    refined_cells = verify_fan(REFINED_RAYS, REFINED_MAXIMAL)
    assert set(refined_cells) - set(coarse_cells) == {"ac", "bc", "cu", "cv"}
    assert set(coarse_cells) - set(refined_cells) == {"ab"}

    x, y, z = sp.symbols("x y z")
    coarse_divisors = (x, x, y, y, x - y)
    refined_divisors = (x, x, z, y, y, x + z - y)
    coarse_raw = todd_components(coarse_divisors, (x, y, z))
    refined_raw = todd_components(refined_divisors, (x, y, z))
    coarse_groebner = sp.groebner(
        [y**2, x**2 * (x - y)], y, x, order="lex", domain=sp.QQ
    )
    refined_groebner = sp.groebner(
        [x**2, y**2, z * (x + z - y)], z, y, x,
        order="lex", domain=sp.QQ,
    )

    def reduce_coarse(expression):
        return sp.expand(coarse_groebner.reduce(sp.expand(expression))[1])

    def reduce_refined(expression):
        return sp.expand(refined_groebner.reduce(sp.expand(expression))[1])

    coarse_todd = tuple(reduce_coarse(component) for component in coarse_raw)
    refined_todd = tuple(reduce_refined(component) for component in refined_raw)
    pulled_todd = tuple(
        reduce_refined(component.subs({x: x + z, y: y}, simultaneous=True))
        for component in coarse_todd
    )
    corrections = tuple(
        reduce_refined(refined_todd[q] - pulled_todd[q]) for q in range(4)
    )
    assert coarse_todd == (
        1,
        3 * x / 2 + y / 2,
        x**2 + 5 * x * y / 6,
        x**3,
    )
    assert refined_todd == (
        1,
        3 * x / 2 + y / 2 + z,
        5 * x * y / 6 + x * z + y * z,
        x * y * z,
    )
    assert corrections == (0, -z / 2, -5 * y * z / 6, 0)

    coarse_q2 = verify_q2_effective(
        COARSE_RAYS, COARSE_MAXIMAL, {"ab": Q(1), "au": Q(5, 6)}
    )
    refined_q2 = verify_q2_effective(
        REFINED_RAYS, REFINED_MAXIMAL,
        {"ac": Q(1), "au": Q(5, 6), "cu": Q(1)},
    )
    refined_cells, refined_balance = refined_q2[0], refined_q2[1]

    # q=1 separator: all ray weights are positive and balanced.
    ray_order = tuple(sorted(REFINED_RAYS))
    q1_balance = tuple(tuple(REFINED_RAYS[ray][coordinate]
                             for ray in ray_order)
                       for coordinate in range(3))
    q1_weight = (Q(1),) * len(ray_order)
    assert matvec(q1_balance, q1_weight) == (Q(0), Q(0), Q(0))
    q1_correction = tuple(Q(-1, 2) if ray == "c" else Q(0)
                          for ray in ray_order)
    assert dot(q1_correction, q1_weight) == Q(-1, 2)

    # q=2 separator in the exact quotient-balance ordering.
    q2_weight_by_cell = {
        "ac": 2, "ae": 1, "au": 1, "av": 1,
        "bc": 2, "be": 1, "bu": 1, "bv": 1,
        "cu": 1, "cv": 1, "eu": 2, "ev": 2,
    }
    q2_weight = tuple(Q(q2_weight_by_cell[cell]) for cell in refined_cells)
    assert min(q2_weight) > 0
    assert matvec(refined_balance, q2_weight) == (Q(0),) * len(refined_balance)
    q2_correction = tuple(Q(-5, 6) if cell == "cu" else Q(0)
                          for cell in refined_cells)
    assert dot(q2_correction, q2_weight) == Q(-5, 6)

    # Effective representatives in every degree show that both endpoint fans
    # themselves satisfy GHTE.  The obstruction concerns the canonical lift.
    effective_endpoint_representatives = {
        "coarse_q0": ("fundamental", Q(1)),
        "coarse_q1": tuple((ray, Q(1, 2)) for ray in sorted(COARSE_RAYS)),
        "coarse_q2": ("ab", Q(1), "au", Q(5, 6)),
        "coarse_q3": ("abu", Q(1)),
        "refined_q0": ("fundamental", Q(1)),
        "refined_q1": tuple((ray, Q(1, 2)) for ray in sorted(REFINED_RAYS)),
        "refined_q2": ("ac", Q(1), "au", Q(5, 6), "cu", Q(1)),
        "refined_q3": ("acu", Q(1)),
    }

    payload = repr((
        ALL_RAYS, COARSE_MAXIMAL, REFINED_MAXIMAL,
        coarse_todd, refined_todd, pulled_todd, corrections,
        coarse_q2, refined_q2, q1_weight, q1_correction,
        q2_weight, q2_correction, effective_endpoint_representatives,
    )).encode("ascii")
    digest = sha256(payload).hexdigest()
    print("PASS")
    print(f"payload_sha256={digest}")
    print("star=c=a+b; refined_to_coarse_is_blowdown")
    print(f"coarse_todd={coarse_todd}")
    print(f"refined_todd={refined_todd}")
    print(f"pulled_coarse_todd={pulled_todd}")
    print("corrections_refined_minus_pullback=(0,-z/2,-5*yz/6,0)")
    print(f"q1_positive_balanced={q1_weight}; pairing=-1/2")
    print(f"q2_cells={refined_cells}")
    print(f"q2_positive_balanced={q2_weight}; pairing=-5/6")
    print("endpoint_GHTE=TRUE_TRUE; canonical_upward_effective_transport=FAIL")
    print("scope=transport obstruction only; not a GHTE or KTT counterexample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
