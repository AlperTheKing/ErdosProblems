#!/usr/bin/env python3
"""Independent exact codimension-four BV census for rank-five hive normals.

This program implements the defining local Euler--Maclaurin recursion directly;
it does not import or call ``bv_unimodular_alpha.py``.

For a unimodular cone C with lattice-basis rays v_1,...,v_d and ray Gram
matrix H, write s_i=<xi,v_i>.  The defining identity is

    S(C) = sum_{F face of C} mu(t(C,F)) I(F).

For the face spanned by I, normalized lattice integration gives

    I(F_I)(t xi) = (-1)^|I| t^(-|I|) / prod_{i in I} s_i,

and the transverse ray Gram matrix and coordinates are the Schur complements

    H' = H_JJ - H_JI H_II^(-1) H_IJ,
    s' = s_J  - H_JI H_II^(-1) s_I.

The code expands 1/(1-exp(t*s_i)) exactly with Bernoulli numbers and solves
the displayed identity recursively.  Its constant term is alpha^BV(C).

For a saturated independent normal tuple n_i, the inward feasible rays are
the negative basis dual to n_i, hence their Gram matrix is inverse(Gram(n_i)).
All verdict arithmetic is fractions/integers.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from math import comb, factorial, gcd


RANK = 5
EXPECTED_NORMAL_SHA256 = (
    "4bd294a1e92a805f261b93fd66f9be4997ca4320b7995d01a29e772ef2d7a855"
)


def primitive(row):
    divisor = 0
    for entry in row:
        divisor = gcd(divisor, abs(entry))
    assert divisor
    return tuple(entry // divisor for entry in row)


def rank5_hive_normals():
    interior = [
        (x, y)
        for x in range(1, RANK)
        for y in range(1, RANK)
        if x + y <= RANK - 1
    ]
    coordinate = {point: i for i, point in enumerate(interior)}
    rows = []

    def add(plus, minus):
        row = [0] * len(interior)
        for point in plus:
            if point in coordinate:
                row[coordinate[point]] -= 1
        for point in minus:
            if point in coordinate:
                row[coordinate[point]] += 1
        if any(row):
            rows.append(primitive(row))

    for x in range(RANK + 1):
        for y in range(RANK + 1):
            if x + y <= RANK - 2:
                add([(x + 1, y), (x, y + 1)], [(x, y), (x + 1, y + 1)])
            if y >= 1 and x + y <= RANK - 1:
                add([(x, y), (x + 1, y)], [(x, y + 1), (x + 1, y - 1)])
            if x >= 1 and x + y <= RANK - 1:
                add([(x, y), (x, y + 1)], [(x + 1, y), (x - 1, y + 1)])

    assert len(rows) == 30
    normals = sorted(set(rows))
    assert len(normals) == 27
    payload = "\n".join(",".join(map(str, normal)) for normal in normals)
    assert sha256(payload.encode("ascii")).hexdigest() == EXPECTED_NORMAL_SHA256
    return normals, interior


def transpose(matrix):
    return tuple(zip(*matrix))


def matmul(left, right):
    right_t = transpose(right)
    return tuple(
        tuple(sum(a * b for a, b in zip(row, col)) for col in right_t)
        for row in left
    )


def matvec(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


def inverse(matrix):
    size = len(matrix)
    work = [
        [Fraction(matrix[i][j]) for j in range(size)]
        + [Fraction(i == j) for j in range(size)]
        for i in range(size)
    ]
    for col in range(size):
        pivot = next(row for row in range(col, size) if work[row][col])
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [entry / scale for entry in work[col]]
        for row in range(size):
            if row == col:
                continue
            scale = work[row][col]
            if scale:
                work[row] = [
                    a - scale * b for a, b in zip(work[row], work[col])
                ]
    return tuple(tuple(row[size:]) for row in work)


def submatrix(matrix, rows, cols):
    return tuple(tuple(matrix[i][j] for j in cols) for i in rows)


def vector_sub(left, right):
    return tuple(a - b for a, b in zip(left, right))


def matrix_sub(left, right):
    return tuple(
        tuple(a - b for a, b in zip(row_l, row_r))
        for row_l, row_r in zip(left, right)
    )


def bernoulli_numbers(last):
    """Return B_0,...,B_last with B_1=-1/2."""
    values = [Fraction(1)]
    for n in range(1, last + 1):
        values.append(
            -sum(Fraction(comb(n + 1, k)) * values[k] for k in range(n))
            / Fraction(n + 1)
        )
    return values


def add_series(left, right, scale=Fraction(1)):
    answer = dict(left)
    for degree, coefficient in right.items():
        answer[degree] = answer.get(degree, Fraction(0)) + scale * coefficient
        if not answer[degree]:
            del answer[degree]
    return answer


def product_series(left, right, maximum):
    answer = {}
    for degree_l, coefficient_l in left.items():
        for degree_r, coefficient_r in right.items():
            degree = degree_l + degree_r
            if degree <= maximum:
                answer[degree] = (
                    answer.get(degree, Fraction(0))
                    + coefficient_l * coefficient_r
                )
    return {degree: coefficient for degree, coefficient in answer.items() if coefficient}


def exponential_sum_series(coordinates, maximum):
    """Laurent series of prod_i 1/(1-exp(t*s_i)) through t^maximum."""
    dimension = len(coordinates)
    bernoulli = bernoulli_numbers(maximum + dimension + 1)
    answer = {0: Fraction(1)}
    for processed, coordinate in enumerate(coordinates, start=1):
        assert coordinate
        factor = {}
        # Exponent is n-1 in -B_n*(t*s)^(n-1)/n!.
        for n, number in enumerate(bernoulli):
            exponent = n - 1
            factor[exponent] = -number * coordinate ** exponent / factorial(n)
        # Remaining factors can lower degree once each.
        partial_maximum = maximum + (dimension - processed)
        answer = product_series(answer, factor, partial_maximum)
    return {degree: value for degree, value in answer.items() if degree <= maximum}


def transverse_data(gram, coordinates, face):
    dimension = len(gram)
    face = tuple(face)
    rest = tuple(i for i in range(dimension) if i not in face)
    if not rest:
        return (), ()
    gram_ii_inverse = inverse(submatrix(gram, face, face))
    gram_ji = submatrix(gram, rest, face)
    gram_ij = submatrix(gram, face, rest)
    correction_matrix = matmul(matmul(gram_ji, gram_ii_inverse), gram_ij)
    quotient_gram = matrix_sub(submatrix(gram, rest, rest), correction_matrix)
    correction_vector = matvec(
        matmul(gram_ji, gram_ii_inverse), tuple(coordinates[i] for i in face)
    )
    quotient_coordinates = vector_sub(
        tuple(coordinates[i] for i in rest), correction_vector
    )
    return quotient_gram, quotient_coordinates


def canonical_fraction_matrix(matrix):
    return tuple(tuple(Fraction(entry) for entry in row) for row in matrix)


@lru_cache(maxsize=None)
def mu_series_cached(gram, coordinates, maximum):
    dimension = len(gram)
    if dimension == 0:
        return ((0, Fraction(1)),)
    answer = exponential_sum_series(coordinates, maximum)
    indices = tuple(range(dimension))
    for face_size in range(1, dimension + 1):
        for face in combinations(indices, face_size):
            quotient_gram, quotient_coordinates = transverse_data(
                gram, coordinates, face
            )
            quotient = dict(
                mu_series_cached(
                    canonical_fraction_matrix(quotient_gram),
                    tuple(Fraction(x) for x in quotient_coordinates),
                    maximum + face_size,
                )
            )
            integral_scale = Fraction((-1) ** face_size)
            for i in face:
                integral_scale /= coordinates[i]
            face_term = {
                degree - face_size: integral_scale * coefficient
                for degree, coefficient in quotient.items()
                if degree - face_size <= maximum
            }
            answer = add_series(answer, face_term, scale=Fraction(-1))

    # The defining theorem says mu is regular at zero; cancellation is also a
    # strong implementation check on every cone and every generic direction.
    negative = {degree: value for degree, value in answer.items() if degree < 0}
    assert not negative, negative
    return tuple(sorted(
        (degree, value) for degree, value in answer.items()
        if 0 <= degree <= maximum and value
    ))


def mu_alpha(gram, coordinates):
    series = dict(mu_series_cached(
        canonical_fraction_matrix(gram),
        tuple(Fraction(x) for x in coordinates),
        0,
    ))
    return series.get(0, Fraction(0))


def determinant_bareiss(matrix):
    work = [list(map(int, row)) for row in matrix]
    size = len(work)
    sign = 1
    previous = 1
    for k in range(size - 1):
        if work[k][k] == 0:
            pivot = next((i for i in range(k + 1, size) if work[i][k]), None)
            if pivot is None:
                return 0
            work[k], work[pivot] = work[pivot], work[k]
            sign *= -1
        pivot = work[k][k]
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                work[i][j] = (
                    work[i][j] * pivot - work[i][k] * work[k][j]
                ) // previous
        previous = pivot
    return sign * work[-1][-1]


def saturation_index(rows):
    divisor = 0
    for columns in combinations(range(len(rows[0])), len(rows)):
        minor = tuple(tuple(row[column] for column in columns) for row in rows)
        divisor = gcd(divisor, abs(determinant_bareiss(minor)))
    return divisor


def normal_gram(rows):
    return tuple(
        tuple(sum(x * y for x, y in zip(left, right)) for right in rows)
        for left in rows
    )


def self_test():
    # Orthants have alpha=2^-d.  Two nonsymmetric tests recover the published
    # dimension-2 and dimension-3 closed formulas from the defining recursion.
    for dimension in range(1, 5):
        identity = tuple(
            tuple(Fraction(i == j) for j in range(dimension))
            for i in range(dimension)
        )
        assert mu_alpha(identity, tuple(2 ** i for i in range(dimension))) == Fraction(1, 2 ** dimension)

    gram2 = ((Fraction(2), Fraction(1)), (Fraction(1), Fraction(3)))
    closed2 = Fraction(1, 4) + Fraction(1, 12) * (
        gram2[0][1] / gram2[0][0] + gram2[0][1] / gram2[1][1]
    )
    assert mu_alpha(gram2, (1, 7)) == closed2

    gram3 = (
        (Fraction(3), Fraction(1), Fraction(-1)),
        (Fraction(1), Fraction(4), Fraction(1)),
        (Fraction(-1), Fraction(1), Fraction(5)),
    )
    closed3 = Fraction(1, 8)
    for i, j in combinations(range(3), 2):
        closed3 += Fraction(1, 24) * gram3[i][j] * (
            Fraction(1, gram3[i][i]) + Fraction(1, gram3[j][j])
        )
    assert mu_alpha(gram3, (1, 11, 121)) == closed3


def main():
    self_test()
    normals, interior = rank5_hive_normals()
    counts = Counter()
    records = []
    directions = ((1, 17, 289, 4913), (1, 23, 529, 12167))
    for ids in combinations(range(len(normals)), 4):
        rows = tuple(normals[i] for i in ids)
        index = saturation_index(rows)
        if not index:
            counts["dependent"] += 1
            continue
        if index != 1:
            counts[f"index_{index}"] += 1
            continue
        counts["saturated"] += 1
        ray_gram = inverse(normal_gram(rows))
        values = tuple(mu_alpha(ray_gram, direction) for direction in directions)
        assert values[0] == values[1], (ids, values)
        alpha = values[0]
        counts["negative"] += alpha < 0
        counts["zero"] += alpha == 0
        records.append((alpha, ids, rows, normal_gram(rows), ray_gram))

    records.sort(key=lambda record: (record[0], record[1]))
    print("PASS")
    print(f"interior={interior}")
    print(f"normal_sha256={EXPECTED_NORMAL_SHA256}")
    print(f"counts={dict(counts)}")
    print(f"minimum={records[0][0]}")
    print("lowest_records=")
    for alpha, ids, rows, gram, ray_gram in records[:20]:
        print(f"  alpha={alpha} ids={ids}")
        print(f"    rows={rows}")
        print(f"    normal_gram={gram}")
        print(f"    ray_gram={ray_gram}")


if __name__ == "__main__":
    main()
