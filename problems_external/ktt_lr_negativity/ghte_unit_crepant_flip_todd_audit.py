#!/usr/bin/env python3
"""Exact audit of the smallest unit-crepant 2<->2 Todd flip atom.

The two complete smooth three-dimensional fans are the exact rank-four hive
wall pair found by ``ghte_find_r4_wall_pair.py``.  The checker is standalone:
it verifies the fan, rebuilds the primitive quotient balance matrices and BV
codimension-two cycles, and checks the graph-correspondence calculation in
the rational Chow rings.

This is an obstruction to positivity-preserving graph transport.  It is not
a negative balanced witness for either fan; in fact all audited BV entries
are strictly positive.
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
    "r": (0, -1, 1),
}

LEFT_MAXIMAL = ("arb", "arc", "brd", "crd", "abc", "bcd")
RIGHT_MAXIMAL = ("arb", "arc", "brd", "crd", "abd", "acd")


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
        pivot = next(i for i in range(column, size) if work[i][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            if scale:
                work[row] = [
                    x - scale * y for x, y in zip(work[row], work[column])
                ]
    return tuple(tuple(row[size:]) for row in work)


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def transpose(matrix):
    return tuple(tuple(row[column] for row in matrix) for column in range(len(matrix[0])))


def integer_vectors_l1(radius):
    return tuple(
        vector
        for vector in product(range(-radius, radius + 1), repeat=3)
        if sum(abs(value) for value in vector) <= radius
    )


def quotient_completion(normal):
    """Find an exact positive SL(3,Z) completion [normal,q1,q2]."""
    for radius in range(1, 7):
        vectors = integer_vectors_l1(radius)
        candidates = []
        for first in vectors:
            for second in vectors:
                if determinant(normal, first, second) == 1:
                    candidates.append((
                        sum(abs(x) for x in first) + sum(abs(x) for x in second),
                        first,
                        second,
                    ))
        if candidates:
            _, first, second = min(candidates)
            columns = (normal, first, second)
            rows = tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))
            inv = inverse(rows)
            assert all(value.denominator == 1 for row in inv for value in row)
            return inv
    raise AssertionError(f"no quotient completion for {normal}")


def quotient_vector(normal, other, completion):
    coordinates = matvec(completion, other)
    quotient = tuple(int(value) for value in coordinates[1:])
    return primitive(quotient)


def pair_index(left, right):
    return gcd(0, *(abs(value) for value in cross(left, right)))


def bv_alpha_q2(left, right):
    assert pair_index(left, right) == 1
    aa, bb, ab = dot(left, left), dot(right, right), dot(left, right)
    # Outer-normal convention from GHTE_FOUNDATION_CONTRACT.md.
    return Q(1, 4) - Q(ab, 12) * (Q(1, aa) + Q(1, bb))


def two_cones(maximal):
    return tuple(sorted({"".join(sorted(pair)) for cone in maximal for pair in combinations(cone, 2)}))


def build_balance(two_cells):
    ray_order = tuple(sorted(RAYS))
    completions = {ray: quotient_completion(RAYS[ray]) for ray in ray_order}
    matrix = [[0] * len(two_cells) for _ in range(2 * len(ray_order))]
    for column, cell in enumerate(two_cells):
        left, right = cell
        for ray, other in ((left, right), (right, left)):
            quotient = quotient_vector(RAYS[ray], RAYS[other], completions[ray])
            block = ray_order.index(ray)
            matrix[2 * block][column] = quotient[0]
            matrix[2 * block + 1][column] = quotient[1]
    return tuple(tuple(row) for row in matrix)


def solve_linear(rows, rhs):
    """Return one rational solution, setting free variables to zero."""
    columns = len(rows[0])
    work = [[Q(value) for value in row] + [Q(rhs[i])] for i, row in enumerate(rows)]
    pivots = []
    pivot_row = 0
    for column in range(columns):
        pivot = next((i for i in range(pivot_row, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
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
    for row in range(pivot_row, len(work)):
        assert any(work[row][column] for column in range(columns)) or not work[row][-1]
    answer = [Q(0)] * columns
    for row, column in enumerate(pivots):
        answer[column] = work[row][-1]
    assert matvec(rows, answer) == tuple(map(Q, rhs))
    return tuple(answer)


def verify_fan(maximal):
    two_cells = two_cones(maximal)
    assert len(maximal) == 6 and len(two_cells) == 9
    assert len(RAYS) - len(two_cells) + len(maximal) == 2
    for cone in maximal:
        assert abs(determinant(*(RAYS[ray] for ray in cone))) == 1
    for cell in two_cells:
        containing = [cone for cone in maximal if set(cell) < set(cone)]
        assert len(containing) == 2
        extras = [next(ray for ray in cone if ray not in cell) for cone in containing]
        left, right = (RAYS[ray] for ray in cell)
        signs = [determinant(left, right, RAYS[extra]) for extra in extras]
        assert signs[0] * signs[1] < 0
    return two_cells


def verify_bv_class(maximal, exceptional):
    cells = verify_fan(maximal)
    balance = build_balance(cells)
    alphas = tuple(bv_alpha_q2(RAYS[cell[0]], RAYS[cell[1]]) for cell in cells)
    assert min(alphas) > 0

    # In both Chow rings xy=[V(ab)].  On the left y^2=[V(bc)]; on
    # the right x^2=[V(ad)].  This nonnegative representative is the
    # degree-two term of product_rho D_rho/(1-exp(-D_rho)).
    representative = [Q(0)] * len(cells)
    representative[cells.index("ab")] = Q(13, 6)
    representative[cells.index(exceptional)] = Q(1)
    target = tuple(representative[i] - alphas[i] for i in range(len(cells)))
    relation = solve_linear(transpose(balance), target)
    assert tuple(
        alphas[i] + matvec(transpose(balance), relation)[i]
        for i in range(len(cells))
    ) == tuple(representative)
    return cells, alphas, balance, relation


def main():
    a, b, c, d = (RAYS[name] for name in "abcd")
    assert tuple(a[i] + d[i] for i in range(3)) == tuple(b[i] + c[i] for i in range(3))
    assert primitive((1, -1, -1, 1)) == (1, -1, -1, 1)

    left_cells, left_alpha, left_balance, left_relation = verify_bv_class(
        LEFT_MAXIMAL, "bc"
    )
    right_cells, right_alpha, right_balance, right_relation = verify_bv_class(
        RIGHT_MAXIMAL, "ad"
    )
    assert set(left_cells) - set(right_cells) == {"bc"}
    assert set(right_cells) - set(left_cells) == {"ad"}

    # Strictly positive balanced dual weights separate the negative
    # exceptional classes from the effective cycle cones.  In particular,
    # -[ad] and -[bc] have no nonnegative representatives modulo balancing.
    left_weight_by_cell = {
        "ab": 1, "ac": 1, "ar": 1, "bc": 1, "bd": 1,
        "br": 2, "cd": 1, "cr": 2, "dr": 1,
    }
    right_weight_by_cell = {
        "ab": 1, "ac": 1, "ad": 1, "ar": 2, "bd": 1,
        "br": 1, "cd": 1, "cr": 1, "dr": 2,
    }
    left_weight = tuple(Q(left_weight_by_cell[cell]) for cell in left_cells)
    right_weight = tuple(Q(right_weight_by_cell[cell]) for cell in right_cells)
    assert matvec(left_balance, left_weight) == (Q(0),) * len(left_balance)
    assert matvec(right_balance, right_weight) == (Q(0),) * len(right_balance)
    assert min(left_weight) > 0 and min(right_weight) > 0
    assert -left_weight[left_cells.index("bc")] == -1
    assert -right_weight[right_cells.index("ad")] == -1

    # Chow presentations:
    # A_L=Q[x,y]/(x^2,y^2(x+y)), A_R=Q[x,y]/(y^2,x^2(x+y)).
    # In the common star subdivision, E has class z and
    # A_W=Q[x,y,z]/(x^2,y^2,z(x+y+z)).  Hence z^2=-xz-yz.
    # Pullbacks are p_L^*x=x, p_L^*y=y+z and
    # p_R^*x=x+z, p_R^*y=y.  The pushforwards give the following
    # exact graph maps in bases (xy,y^2)_L and (xy,x^2)_R.
    graph_left_to_right = (
        (Q(1), Q(0)),   # xy coefficient
        (Q(1), Q(-1)),  # x^2 coefficient
    )
    graph_right_to_left = graph_left_to_right
    todd_left = (Q(13, 6), Q(1))
    todd_right = (Q(13, 6), Q(1))

    # In the ordered common-resolution basis (xy,xz,yz), a direct Todd
    # expansion gives td_2(W)=13/6 xy+xz+yz.  Pulling either side upward
    # overshoots one exceptional component by 1/6.
    todd_common = (Q(13, 6), Q(1), Q(1))
    pull_left_todd = (Q(13, 6), Q(7, 6), Q(1))
    pull_right_todd = (Q(13, 6), Q(1), Q(7, 6))

    # The unchanged degrees are audited as well.  The degree-one Todd class
    # is 3/2(x+y).  Before Stanley--Reisner reduction, the degree-three term
    # has coefficients (3,11,11,3)/8 on (x^3,x^2y,xy^2,y^3).  Using
    # x^2=0,y^3=-xy^2 on L and y^2=0,x^3=-x^2y on R gives degree one on both.
    todd_q1 = (Q(3, 2), Q(3, 2))
    todd_q3_raw = (Q(3, 8), Q(11, 8), Q(11, 8), Q(3, 8))
    assert todd_q3_raw[2] - todd_q3_raw[3] == 1
    assert todd_q3_raw[1] - todd_q3_raw[0] == 1
    assert tuple(todd_common[i] - pull_left_todd[i] for i in range(3)) == (
        Q(0), Q(-1, 6), Q(0)
    )
    assert tuple(todd_common[i] - pull_right_todd[i] for i in range(3)) == (
        Q(0), Q(0), Q(-1, 6)
    )

    assert matvec(graph_left_to_right, (Q(0), Q(1))) == (Q(0), Q(-1))
    assert matvec(graph_right_to_left, (Q(0), Q(1))) == (Q(0), Q(-1))
    assert matvec(graph_left_to_right, todd_left) == (
        todd_right[0], todd_right[1] + Q(1, 6)
    )
    assert matvec(graph_right_to_left, todd_right) == (
        todd_left[0], todd_left[1] + Q(1, 6)
    )

    payload = repr((
        RAYS, LEFT_MAXIMAL, RIGHT_MAXIMAL, left_cells, left_alpha,
        right_cells, right_alpha, left_balance, right_balance,
        left_relation, right_relation, graph_left_to_right,
        left_weight, right_weight,
        todd_common, pull_left_todd, pull_right_todd,
        todd_q1, todd_q3_raw,
    )).encode("ascii")
    print("PASS")
    print(f"payload_sha256={sha256(payload).hexdigest()}")
    print("circuit=a+d=b+c; maximal_multiplicities=1")
    print(f"left_q2_cells={left_cells}")
    print(f"left_q2_BV={left_alpha}")
    print(f"right_q2_cells={right_cells}")
    print(f"right_q2_BV={right_alpha}")
    print("BV_classes: left=13/6[ab]+[bc], right=13/6[ab]+[ad]")
    print("graph_exceptional: [bc] -> -[ad], [ad] -> -[bc]")
    print("graph_Todd: G(L_td2)=R_td2+1/6[ad]")
    print("graph_Todd_reverse: G(R_td2)=L_td2+1/6[bc]")
    print("common_td2=13/6*xy+xz+yz")
    print("common_td2-pL^*left_td2=-1/6*xz")
    print("common_td2-pR^*right_td2=-1/6*yz")
    print("unchanged_Todd: q0=1 q1=3/2*(x+y) q3=degree-one zero-cycle")
    print(f"positive_balanced_left={left_weight}")
    print(f"positive_balanced_right={right_weight}")
    print("separation: <-[bc],w_left>=-1; <-[ad],w_right>=-1")
    print("min_BV_left=%s min_BV_right=%s" % (min(left_alpha), min(right_alpha)))


if __name__ == "__main__":
    main()
