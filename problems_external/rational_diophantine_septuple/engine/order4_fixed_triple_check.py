#!/usr/bin/env python3
"""Exact canonical-point checks for the two published Z/2 x Z/8 examples."""

from fractions import Fraction as Q
from math import isqrt
import json


def sqrt_q(value: Q) -> Q:
    assert value >= 0
    n = isqrt(value.numerator)
    d = isqrt(value.denominator)
    assert n * n == value.numerator and d * d == value.denominator
    return Q(n, d)


def canonical_check(triple: tuple[Q, Q, Q]) -> dict[str, object]:
    a, b, c = triple
    p, q, r = a * b, a * c, b * c
    a2 = p + q + r
    a4 = p * q + p * r + q * r

    def add(P, R):
        if P is None:
            return R
        if R is None:
            return P
        x1, y1 = P
        x2, y2 = R
        if x1 == x2 and y1 == -y2:
            return None
        if P == R:
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
        else:
            slope = (y2 - y1) / (x2 - x1)
        x3 = slope * slope - a2 - x1 - x2
        y3 = -(y1 + slope * (x3 - x1))
        return x3, y3

    pair_roots = (sqrt_q(p + 1), sqrt_q(q + 1), sqrt_q(r + 1))
    S = (Q(1), pair_roots[0] * pair_roots[1] * pair_roots[2])
    two_S = add(S, S)
    four_S = add(two_S, two_S)
    roots = (-p, -q, -r)
    return {
        "canonical_2S_x": str(two_S[0]),
        "canonical_2S_is_nonzero_2torsion": two_S[1] == 0 and two_S[0] in roots,
        "canonical_2S_root_index": roots.index(two_S[0]) if two_S[0] in roots else None,
        "canonical_4S_is_O": four_S is None,
    }


def main() -> None:
    positive_rank_one = (
        Q(37471518967, 1381254420),
        Q(5832225, 571948),
        Q(6251648, 1562505),
    )
    regular_order_four_candidate = (
        Q(1884586446094351, 25415891646864180),
        Q(14442883687791636, 7402559392524605),
        Q(60340495895762708555, 14487505263205637124),
    )
    result = {
        "published_positive_rank_one": canonical_check(positive_rank_one),
        "published_regular_order_four_candidate": canonical_check(
            regular_order_four_candidate
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
