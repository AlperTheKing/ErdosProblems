#!/usr/bin/env python3
"""Zero-trust exact checker for the codimension-two BV weights at hive rank 5.

The checker is deliberately standalone: it reconstructs the rank-5 rhombus
rows rather than importing the earlier hive or normal-atlas programs.  All
arithmetic that affects the verdict is integer or Fraction arithmetic.

What is checked:

* 30 rhombus rows give 27 oriented primitive normals in Z^6;
* among the 342 nonparallel pairs, the saturation-index histogram is
  339 pairs of index 1 and three pairs of index 2;
* the Berline--Vergne constant of every index-1 transverse feasible cone is
  computed from the inverse normal Gram matrix and is at least 1/9;
* every index-2 pair has the claimed symmetric saturated-lattice form, and a
  unimodular subdivision gives 7/18 + 7/18 - 1/2 = 5/18.

This finite checker supports the mathematical proof in
R5_E4_CODIM2_POSITIVITY.md; it is not a replacement for the BV theorem.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import gcd


RANK = 5
EXPECTED_NORMAL_SHA256 = (
    "4bd294a1e92a805f261b93fd66f9be4997ca4320b7995d01a29e772ef2d7a855"
)


def primitive(row):
    divisor = 0
    for entry in row:
        divisor = gcd(divisor, abs(entry))
    assert divisor > 0
    return tuple(entry // divisor for entry in row)


def rank5_hive_normals():
    """Rebuild the nonconstant oriented rows of A in A h <= b."""
    interior = [
        (x, y)
        for x in range(1, RANK)
        for y in range(1, RANK)
        if x + y <= RANK - 1
    ]
    assert interior == [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1)]
    coordinate = {point: i for i, point in enumerate(interior)}
    rows = []

    def add(plus, minus):
        # Rhombus concavity is sum(plus) >= sum(minus).  Moving all interior
        # variables to the left produces this oriented A-row.
        row = [0] * len(interior)
        for point in plus:
            if point in coordinate:
                row[coordinate[point]] -= 1
        for point in minus:
            if point in coordinate:
                row[coordinate[point]] += 1
        assert any(row)
        rows.append(primitive(row))

    for x in range(RANK + 1):
        for y in range(RANK + 1):
            if x + y <= RANK - 2:
                add(
                    [(x + 1, y), (x, y + 1)],
                    [(x, y), (x + 1, y + 1)],
                )
            if y >= 1 and x + y <= RANK - 1:
                add(
                    [(x, y), (x + 1, y)],
                    [(x, y + 1), (x + 1, y - 1)],
                )
            if x >= 1 and x + y <= RANK - 1:
                add(
                    [(x, y), (x, y + 1)],
                    [(x + 1, y), (x - 1, y + 1)],
                )

    assert len(rows) == 30
    assert Counter(Counter(rows).values()) == Counter({1: 24, 2: 3})
    normals = sorted(set(rows))
    assert len(normals) == 27
    payload = "\n".join(",".join(map(str, normal)) for normal in normals)
    assert sha256(payload.encode("ascii")).hexdigest() == EXPECTED_NORMAL_SHA256
    return normals


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def determinant2(left, right):
    return left[0] * right[1] - left[1] * right[0]


def saturation_index(left, right):
    """Index of Z left + Z right in its saturation; zero means rank < 2."""
    divisor = 0
    for i, j in combinations(range(len(left)), 2):
        divisor = gcd(
            divisor,
            abs(left[i] * right[j] - left[j] * right[i]),
        )
    return divisor


def inverse_gram(normal1, normal2):
    """Gram matrix on the quotient lattice dual to the normal lattice."""
    aa = dot(normal1, normal1)
    ab = dot(normal1, normal2)
    bb = dot(normal2, normal2)
    determinant = aa * bb - ab * ab
    assert determinant > 0
    return (
        (Fraction(bb, determinant), Fraction(-ab, determinant)),
        (Fraction(-ab, determinant), Fraction(aa, determinant)),
    )


def metric_dot(vector1, vector2, gram):
    return sum(
        Fraction(vector1[i]) * gram[i][j] * vector2[j]
        for i in range(2)
        for j in range(2)
    )


def bv_unimodular_alpha(ray1, ray2, gram):
    """BV constant for a two-dimensional unimodular feasible cone."""
    assert abs(determinant2(ray1, ray2)) == 1
    g11 = metric_dot(ray1, ray1, gram)
    g12 = metric_dot(ray1, ray2, gram)
    g22 = metric_dot(ray2, ray2, gram)
    assert g11 > 0 and g22 > 0 and g11 * g22 > g12 * g12
    return Fraction(1, 4) + Fraction(1, 12) * (
        g12 / g11 + g12 / g22
    )


def index1_alpha(normal1, normal2):
    """Compute alpha from feasible rays dual to a saturated normal basis."""
    assert saturation_index(normal1, normal2) == 1
    gram = inverse_gram(normal1, normal2)
    value = bv_unimodular_alpha((-1, 0), (0, -1), gram)

    # Independent sign check in normal coordinates.  The cross term changes
    # sign on inversion because both feasible rays point inward.
    aa = dot(normal1, normal1)
    ab = dot(normal1, normal2)
    bb = dot(normal2, normal2)
    normal_formula = Fraction(1, 4) - Fraction(1, 12) * (
        Fraction(ab, aa) + Fraction(ab, bb)
    )
    assert value == normal_formula
    return value


def half_sum(left, right, sign=1):
    values = []
    for x, y in zip(left, right):
        numerator = x + sign * y
        assert numerator % 2 == 0
        values.append(numerator // 2)
    return tuple(values)


def index2_alpha(normal1, normal2):
    """Certify and subdivide one of the three index-two feasible cones."""
    assert saturation_index(normal1, normal2) == 2

    # In the saturated normal lattice, n1=s+t and n2=s-t.
    s = half_sum(normal1, normal2, +1)
    t = half_sum(normal1, normal2, -1)
    assert tuple(s[i] + t[i] for i in range(6)) == normal1
    assert tuple(s[i] - t[i] for i in range(6)) == normal2
    assert saturation_index(s, t) == 1
    assert (dot(s, s), dot(s, t), dot(t, t)) == (1, 0, 2)

    # Coordinates below are in the quotient lattice dual to the basis (s,t).
    # Its Euclidean Gram matrix is inverse(diag(1,2))=diag(1,1/2).
    gram = ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1, 2)))
    extreme1 = (-1, 1)
    middle = (-1, 0)
    extreme2 = (-1, -1)

    # n1=(1,1), n2=(1,-1) in the (s,t)-basis.  Both extreme
    # rays are feasible for n1(x)<=0 and n2(x)<=0.
    for ray in (extreme1, middle, extreme2):
        assert ray[0] + ray[1] <= 0
        assert ray[0] - ray[1] <= 0
    assert abs(determinant2(extreme1, extreme2)) == 2
    assert determinant2(extreme1, middle) == 1
    assert determinant2(middle, extreme2) == 1

    left_alpha = bv_unimodular_alpha(extreme1, middle, gram)
    right_alpha = bv_unimodular_alpha(middle, extreme2, gram)
    ray_alpha = Fraction(1, 2)
    assert left_alpha == right_alpha == Fraction(7, 18)
    value = left_alpha + right_alpha - ray_alpha
    assert value == Fraction(5, 18)

    # A separate global sign check: these three cones are the vertex cones of
    # the lattice triangle conv(0, extreme1, extreme2).  Pick/BV requires their
    # constants to sum to one.
    at_extreme1 = bv_unimodular_alpha((1, -1), (0, -1), gram)
    at_extreme2 = bv_unimodular_alpha((0, 1), (1, 1), gram)
    assert at_extreme1 == at_extreme2 == Fraction(13, 36)
    assert value + at_extreme1 + at_extreme2 == 1
    return value, s, t


def show_fraction(value):
    return str(value.numerator) if value.denominator == 1 else str(value)


def main():
    normals = rank5_hive_normals()
    index_histogram = Counter()
    index1_value_histogram = Counter()
    all_values = []
    opposite_pairs = []
    index2_records = []
    minimizers = []

    for i, j in combinations(range(len(normals)), 2):
        normal1, normal2 = normals[i], normals[j]
        index = saturation_index(normal1, normal2)
        if index == 0:
            opposite_pairs.append((i, j))
            assert normal1 == tuple(-x for x in normal2)
            continue
        index_histogram[index] += 1
        if index == 1:
            value = index1_alpha(normal1, normal2)
            index1_value_histogram[value] += 1
        elif index == 2:
            value, s, t = index2_alpha(normal1, normal2)
            index2_records.append((i, j, normal1, normal2, s, t, value))
        else:
            raise AssertionError(f"unexpected saturation index {index}")
        all_values.append(value)

    assert len(opposite_pairs) == 9
    assert sum(index_histogram.values()) == 342
    assert index_histogram == Counter({1: 339, 2: 3})
    assert min(all_values) == Fraction(1, 9)
    assert all(value > 0 for value in all_values)
    assert index1_value_histogram[Fraction(1, 9)] == 6
    assert all(record[-1] == Fraction(5, 18) for record in index2_records)

    for i, j in combinations(range(len(normals)), 2):
        if saturation_index(normals[i], normals[j]) == 1:
            value = index1_alpha(normals[i], normals[j])
            if value == Fraction(1, 9):
                minimizers.append((i, j))
    assert minimizers == [(0, 2), (3, 4), (5, 9), (11, 15), (16, 17), (20, 21)]

    expected_index2_pairs = {
        (0, 3),
        (5, 20),
        (11, 16),
    }
    assert {(record[0], record[1]) for record in index2_records} == expected_index2_pairs

    print("PASS")
    print(f"normal_sha256={EXPECTED_NORMAL_SHA256}")
    print(f"normals={len(normals)} opposite_pairs={len(opposite_pairs)}")
    print(f"nonparallel_pairs={sum(index_histogram.values())}")
    print(f"saturation_index_histogram={dict(sorted(index_histogram.items()))}")
    print(f"minimum_alpha={show_fraction(min(all_values))} minimizers={minimizers}")
    print("index1_alpha_histogram=")
    for value, count in sorted(index1_value_histogram.items()):
        print(f"  {show_fraction(value)}: {count}")
    print("index2_records=")
    for i, j, normal1, normal2, s, t, value in index2_records:
        print(
            f"  pair=({i},{j}) n1={normal1} n2={normal2} "
            f"s={s} t={t} alpha={show_fraction(value)}"
        )


if __name__ == "__main__":
    main()
