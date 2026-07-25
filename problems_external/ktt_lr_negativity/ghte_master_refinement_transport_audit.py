#!/usr/bin/env python3
"""Exact audit of the canonical common refinement of the r=4 unit hive flip.

This checker is intentionally standalone.  It reconstructs the left, right,
and coarsest common smooth fans in N=Z^3, builds the primitive quotient-lattice
balance matrix of the common fan, computes its codimension-two BV cycle, and
checks the Todd pullback corrections in the three rational Chow rings.

The result is an obstruction to an inductive *upward* master-refinement
transport.  It is not a counterexample to GHTE: the common fan itself has an
effective Todd representative.
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from math import gcd


RAYS = {
    "a": (-1, 1, 0),
    "b": (0, 0, -1),
    "c": (0, 1, 0),
    "d": (1, 0, -1),
    "e": (0, 1, -1),
    "r": (0, -1, 1),
}

LEFT = ("arb", "arc", "brd", "crd", "abc", "bcd")
RIGHT = ("arb", "arc", "brd", "crd", "abd", "acd")
MASTER = ("arb", "arc", "brd", "crd", "abe", "ace", "bed", "ecd")


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def cross(left, right):
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def det(left, middle, right):
    return dot(left, cross(middle, right))


def primitive(vector):
    divisor = gcd(0, *(abs(int(value)) for value in vector))
    assert divisor
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
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row != column and work[row][column]:
                scale = work[row][column]
                work[row] = [
                    x - scale * y for x, y in zip(work[row], work[column])
                ]
    return tuple(tuple(row[size:]) for row in work)


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def transpose(matrix):
    return tuple(
        tuple(row[column] for row in matrix) for column in range(len(matrix[0]))
    )


def quotient_completion(normal):
    vectors = tuple(
        vector
        for vector in product(range(-3, 4), repeat=3)
        if sum(abs(value) for value in vector) <= 3
    )
    candidates = []
    for first in vectors:
        for second in vectors:
            if det(normal, first, second) == 1:
                candidates.append((
                    sum(map(abs, first)) + sum(map(abs, second)), first, second
                ))
    _, first, second = min(candidates)
    columns = (normal, first, second)
    rows = tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))
    result = inverse(rows)
    assert all(entry.denominator == 1 for row in result for entry in row)
    return result


def quotient_vector(normal, other, completion):
    coordinates = matvec(completion, other)
    return primitive(tuple(int(value) for value in coordinates[1:]))


def two_cones(maximal):
    return tuple(sorted({
        "".join(sorted(pair))
        for cone in maximal
        for pair in combinations(cone, 2)
    }))


def verify_complete_smooth_fan(maximal):
    cells = two_cones(maximal)
    ray_names = sorted({ray for cone in maximal for ray in cone})
    assert len(ray_names) - len(cells) + len(maximal) == 2
    for cone in maximal:
        assert abs(det(*(RAYS[ray] for ray in cone))) == 1
    for cell in cells:
        containing = [cone for cone in maximal if set(cell) < set(cone)]
        assert len(containing) == 2
        extras = [next(ray for ray in cone if ray not in cell) for cone in containing]
        first, second = (RAYS[ray] for ray in cell)
        signs = [det(first, second, RAYS[extra]) for extra in extras]
        assert signs[0] * signs[1] < 0
    return cells


def verify_refinement(master, coarse):
    for cone in master:
        witnesses = []
        basis = tuple(RAYS[ray] for ray in cone)
        basis_inverse = inverse(tuple(tuple(v[i] for v in basis) for i in range(3)))
        for target in coarse:
            target_basis = tuple(RAYS[ray] for ray in target)
            target_inverse = inverse(
                tuple(tuple(v[i] for v in target_basis) for i in range(3))
            )
            if all(
                min(matvec(target_inverse, vector)) >= 0 for vector in basis
            ):
                witnesses.append(target)
        assert witnesses, cone


def build_balance(cells):
    ray_order = tuple(sorted(RAYS))
    completions = {ray: quotient_completion(RAYS[ray]) for ray in ray_order}
    matrix = [[0] * len(cells) for _ in range(2 * len(ray_order))]
    for column, cell in enumerate(cells):
        left, right = cell
        for ray, other in ((left, right), (right, left)):
            quotient = quotient_vector(RAYS[ray], RAYS[other], completions[ray])
            block = ray_order.index(ray)
            matrix[2 * block][column] = quotient[0]
            matrix[2 * block + 1][column] = quotient[1]
    return tuple(tuple(row) for row in matrix)


def bv_alpha(left, right):
    assert gcd(0, *(abs(value) for value in cross(left, right))) == 1
    aa, bb, ab = dot(left, left), dot(right, right), dot(left, right)
    return Q(1, 4) - Q(ab, 12) * (Q(1, aa) + Q(1, bb))


def solve(rows, rhs):
    columns = len(rows[0])
    work = [
        [Q(value) for value in row] + [Q(rhs[i])]
        for i, row in enumerate(rows)
    ]
    pivot_row = 0
    pivots = []
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                scale = work[row][column]
                work[row] = [
                    x - scale * y for x, y in zip(work[row], work[pivot_row])
                ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    for row in work[pivot_row:]:
        assert any(row[column] for column in range(columns)) or not row[-1]
    answer = [Q(0)] * columns
    for row, column in enumerate(pivots):
        answer[column] = work[row][-1]
    assert matvec(rows, answer) == tuple(Q(value) for value in rhs)
    return tuple(answer)


def add(left, right):
    return tuple(x + y for x, y in zip(left, right))


def scale(value, vector):
    return tuple(value * entry for entry in vector)


def multiply_w(left, right):
    """Multiply degree-one classes in A*(W), basis (xy,xz,yz)."""
    x1, y1, z1 = left
    x2, y2, z2 = right
    return (
        x1 * y2 + y1 * x2,
        x1 * z2 + z1 * x2 - z1 * z2,
        y1 * z2 + z1 * y2 - z1 * z2,
    )


def todd2_w():
    divisors = (
        (Q(1), Q(0), Q(0)),  # a=x
        (Q(0), Q(1), Q(0)),  # b=y
        (Q(0), Q(1), Q(0)),  # c=y
        (Q(1), Q(0), Q(0)),  # d=x
        (Q(1), Q(1), Q(1)),  # r=x+y+z
        (Q(0), Q(0), Q(1)),  # e=z
    )
    c1 = tuple(sum(divisor[i] for divisor in divisors) for i in range(3))
    c1_squared = multiply_w(c1, c1)
    sum_squares = (Q(0), Q(0), Q(0))
    for divisor in divisors:
        sum_squares = add(sum_squares, multiply_w(divisor, divisor))
    c2 = scale(Q(1, 2), add(c1_squared, scale(-1, sum_squares)))
    return scale(Q(1, 12), add(c1_squared, c2))


def main():
    assert add(RAYS["a"], RAYS["d"]) == RAYS["e"]
    assert add(RAYS["b"], RAYS["c"]) == RAYS["e"]
    assert RAYS["e"] == scale(-1, RAYS["r"])
    # The kernel of [b c -a -d] is exactly Q(1,1,1,1).  Hence
    # cone(b,c) intersect cone(a,d)=R_+ e, forcing e in every common fan.
    circuit_columns = (
        RAYS["b"], RAYS["c"], scale(-1, RAYS["a"]), scale(-1, RAYS["d"])
    )
    assert tuple(sum(column[i] for column in circuit_columns) for i in range(3)) == (0, 0, 0)
    assert all(
        det(*(circuit_columns[index] for index in indices)) != 0
        for indices in combinations(range(4), 3)
    )

    verify_complete_smooth_fan(LEFT)
    verify_complete_smooth_fan(RIGHT)
    master_cells = verify_complete_smooth_fan(MASTER)
    verify_refinement(MASTER, LEFT)
    verify_refinement(MASTER, RIGHT)
    assert set(master_cells) == {
        "ab", "ac", "ae", "ar", "bd", "be", "br",
        "cd", "ce", "cr", "de", "dr",
    }

    balance = build_balance(master_cells)
    weight_by_cell = {
        "ab": 1, "ac": 1, "ae": 1, "ar": 2,
        "bd": 1, "be": 1, "br": 2, "cd": 1,
        "ce": 1, "cr": 2, "de": 1, "dr": 2,
    }
    weight = tuple(Q(weight_by_cell[cell]) for cell in master_cells)
    assert matvec(balance, weight) == (Q(0),) * len(balance)
    assert min(weight) > 0

    bv = tuple(bv_alpha(RAYS[cell[0]], RAYS[cell[1]]) for cell in master_cells)
    representative = tuple(
        Q(13, 6) if cell == "ab" else
        Q(1) if cell in ("ae", "be") else Q(0)
        for cell in master_cells
    )
    relation = solve(transpose(balance), tuple(
        representative[i] - bv[i] for i in range(len(master_cells))
    ))
    assert tuple(
        bv[i] + matvec(transpose(balance), relation)[i]
        for i in range(len(master_cells))
    ) == representative
    assert todd2_w() == (Q(13, 6), Q(1), Q(1))

    # A_L=Q[x,y]/(x^2,y^2(x+y)), td2(L)=13/6 xy+y^2.
    # p_L^*(xy)=xy+xz and p_L^*(y^2)=yz-xz.
    pull_left = add(
        scale(Q(13, 6), (Q(1), Q(1), Q(0))),
        (Q(0), Q(-1), Q(1)),
    )
    # A_R=Q[x,y]/(y^2,x^2(x+y)), td2(R)=13/6 xy+x^2.
    # p_R^*(xy)=xy+yz and p_R^*(x^2)=xz-yz.
    pull_right = add(
        scale(Q(13, 6), (Q(1), Q(0), Q(1))),
        (Q(0), Q(1), Q(-1)),
    )
    todd_master = todd2_w()
    correction_left = add(todd_master, scale(-1, pull_left))
    correction_right = add(todd_master, scale(-1, pull_right))
    assert pull_left == (Q(13, 6), Q(7, 6), Q(1))
    assert pull_right == (Q(13, 6), Q(1), Q(7, 6))
    assert correction_left == (Q(0), Q(-1, 6), Q(0))
    assert correction_right == (Q(0), Q(0), Q(-1, 6))

    # xz=[V(ae)] and yz=[V(be)].  The positive balanced weight separates
    # both negative corrections from the effective cone modulo balancing.
    assert dot(correction_left, (Q(0), Q(weight_by_cell["ae"]), Q(0))) == Q(-1, 6)
    assert dot(correction_right, (Q(0), Q(0), Q(weight_by_cell["be"]))) == Q(-1, 6)
    correction_left_cycle = tuple(
        Q(-1, 6) if cell == "ae" else Q(0) for cell in master_cells
    )
    correction_right_cycle = tuple(
        Q(-1, 6) if cell == "be" else Q(0) for cell in master_cells
    )
    assert dot(correction_left_cycle, weight) == Q(-1, 6)
    assert dot(correction_right_cycle, weight) == Q(-1, 6)

    payload = repr((
        RAYS, LEFT, RIGHT, MASTER, master_cells, balance, weight, bv,
        representative, relation, todd_master, pull_left, pull_right,
        correction_left, correction_right,
    )).encode("ascii")
    print("PASS")
    print(f"payload_sha256={sha256(payload).hexdigest()}")
    print(f"master_maximal={MASTER}")
    print(f"master_q2_cells={master_cells}")
    print(f"master_q2_BV={bv}")
    print(f"positive_balanced_weight={weight}")
    print("td2_master=13/6[ab]+[ae]+[be]")
    print("td2_master-pL^*td2_left=-1/6[ae]")
    print("td2_master-pR^*td2_right=-1/6[be]")
    print("separation_pairings=-1/6,-1/6")


if __name__ == "__main__":
    main()
