#!/usr/bin/env python3
"""Exact Berline--Vergne constant for a unimodular simplicial cone.

The input is the Gram matrix of a lattice basis generating the feasible
cone.  The implementation is the defining local Euler--Maclaurin recursion

    S(C) = sum_F mu(T(C,F)) I(F)

specialized to a unimodular simplicial cone and evaluated on a generic
one-parameter covector.  All arithmetic is rational.  This is intended as a
small independent audit tool for codimension four; dimensions two and three
are checked against their published closed formulas in ``self_test``.
"""

from fractions import Fraction
from itertools import combinations
from math import factorial


Q = Fraction

# Bernoulli convention z/(exp(z)-1) = sum B_n z^n/n!, so B_1=-1/2.
BERNOULLI = {
    0: Q(1),
    1: Q(-1, 2),
    2: Q(1, 6),
    3: Q(0),
    4: Q(-1, 30),
    5: Q(0),
    6: Q(1, 42),
    7: Q(0),
    8: Q(-1, 30),
    9: Q(0),
    10: Q(5, 66),
    11: Q(0),
    12: Q(-691, 2730),
}


def inverse(matrix):
    """Gauss--Jordan inverse over Q."""
    n = len(matrix)
    work = [
        [Q(matrix[i][j]) for j in range(n)]
        + [Q(i == j) for j in range(n)]
        for i in range(n)
    ]
    for column in range(n):
        pivot = next(row for row in range(column, n) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                work[row][j] - scale * work[column][j]
                for j in range(2 * n)
            ]
    return tuple(
        tuple(work[i][n + j] for j in range(n)) for i in range(n)
    )


def _transverse(gram, pairings, face):
    """Schur-complement metric and projected pairings transverse to face."""
    face = tuple(face)
    rest = tuple(i for i in range(len(gram)) if i not in face)
    if not rest:
        return (), ()
    block = tuple(tuple(gram[i][j] for j in face) for i in face)
    block_inverse = inverse(block)

    def correction(left, right):
        return sum(
            gram[left][a] * block_inverse[ia][ib] * gram[b][right]
            for ia, a in enumerate(face)
            for ib, b in enumerate(face)
        )

    new_gram = tuple(
        tuple(gram[i][j] - correction(i, j) for j in rest) for i in rest
    )
    new_pairings = tuple(
        pairings[i]
        - sum(
            gram[i][a] * block_inverse[ia][ib] * pairings[b]
            for ia, a in enumerate(face)
            for ib, b in enumerate(face)
        )
        for i in rest
    )
    return new_gram, new_pairings


def _discrete_ray_series(pairing, maximum_exponent):
    # 1/(1-exp(t*x)) = -sum_n B_n (t*x)^(n-1)/n!.
    if not pairing:
        raise ZeroDivisionError("nongeneric covector")
    answer = {}
    for n, bernoulli in BERNOULLI.items():
        exponent = n - 1
        if exponent <= maximum_exponent:
            answer[exponent] = (
                -bernoulli * Q(pairing) ** exponent / Q(factorial(n))
            )
    return answer


def _multiply(left, right, maximum_exponent):
    answer = {}
    for i, a in left.items():
        for j, b in right.items():
            if i + j <= maximum_exponent:
                answer[i + j] = answer.get(i + j, Q(0)) + a * b
    return {exponent: value for exponent, value in answer.items() if value}


def _discrete_cone_series(pairings, order):
    dimension = len(pairings)
    answer = {0: Q(1)}
    for pairing in pairings:
        answer = _multiply(
            answer,
            _discrete_ray_series(pairing, order + dimension),
            order + dimension,
        )
    return {
        exponent: value
        for exponent, value in answer.items()
        if exponent <= order
    }


def _mu_series(gram, pairings, order, cache):
    gram = tuple(tuple(Q(value) for value in row) for row in gram)
    pairings = tuple(Q(value) for value in pairings)
    key = gram, pairings, order
    if key in cache:
        return cache[key]
    dimension = len(gram)
    if dimension == 0:
        return {0: Q(1)}

    answer = _discrete_cone_series(pairings, order)
    for face_dimension in range(1, dimension + 1):
        for face in combinations(range(dimension), face_dimension):
            new_gram, new_pairings = _transverse(gram, pairings, face)
            transverse_mu = _mu_series(
                new_gram,
                new_pairings,
                order + face_dimension,
                cache,
            )
            integral_factor = Q((-1) ** face_dimension)
            for index in face:
                integral_factor /= pairings[index]
            for exponent, value in transverse_mu.items():
                shifted = exponent - face_dimension
                answer[shifted] = (
                    answer.get(shifted, Q(0)) - integral_factor * value
                )

    poles = {
        exponent: value
        for exponent, value in answer.items()
        if exponent < 0 and value
    }
    if poles:
        raise AssertionError(("uncancelled poles", poles))
    result = {exponent: answer.get(exponent, Q(0)) for exponent in range(order + 1)}
    cache[key] = result
    return result


def alpha(gram):
    """Return the BV constant term for a unimodular feasible cone."""
    gram = tuple(tuple(Q(value) for value in row) for row in gram)
    candidates = (
        (1, 7, 43, 257, 1543, 9257),
        (1, 11, 101, 1009, 10007, 100003),
        (2, 17, 137, 1091, 8719, 69763),
    )
    for candidate in candidates:
        try:
            return _mu_series(
                gram,
                candidate[: len(gram)],
                0,
                {},
            )[0]
        except ZeroDivisionError:
            continue
    raise RuntimeError("failed to choose a generic covector")


def alpha2_closed(gram):
    return Q(1, 4) + Q(1, 12) * gram[0][1] * (
        Q(1, gram[0][0]) + Q(1, gram[1][1])
    )


def alpha3_closed(gram):
    answer = Q(1, 8)
    for i, j in combinations(range(3), 2):
        answer += Q(1, 24) * gram[i][j] * (
            Q(1, gram[i][i]) + Q(1, gram[j][j])
        )
    return answer


def self_test():
    test_grams = (
        ((1,),),
        ((1, Q(1, 2)), (Q(1, 2), 1)),
        ((1, Q(-1, 2)), (Q(-1, 2), 1)),
        ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ((2, 1, 0), (1, 3, 1), (0, 1, 2)),
        ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    )
    assert alpha(test_grams[0]) == Q(1, 2)
    for gram in test_grams[1:3]:
        assert alpha(gram) == alpha2_closed(gram)
    for gram in test_grams[3:5]:
        assert alpha(gram) == alpha3_closed(gram)
    assert alpha(test_grams[5]) == Q(1, 16)
    print("PASS bv_unimodular_alpha")


if __name__ == "__main__":
    self_test()
