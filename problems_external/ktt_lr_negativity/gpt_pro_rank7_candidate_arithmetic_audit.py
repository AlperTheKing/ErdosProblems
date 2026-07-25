#!/usr/bin/env python3
"""Exact arithmetic audit of the rank-seven candidate reported by GPT Pro.

This checker validates the supplied degree-13 polynomial, its h*-vector, all
interpolation samples emitted by lrcalc-rs commit 17efa931, and the stated
FrontierMath size bounds.  It does not audit the report's aggregate 14,814-run
corpus, for which no record file was supplied.
"""

from fractions import Fraction as Q
from hashlib import sha256
from math import comb


OUTER = (8, 7, 5, 4, 3, 2, 1)
INNER_LEFT = (5, 4, 3, 2, 1)
INNER_RIGHT = (5, 4, 3, 2, 1)
DEGREE = 13
COEFFICIENTS = (
    Q(1),
    Q(208581, 40040),
    Q(22691293, 1663200),
    Q(79992643, 3326400),
    Q(171585559, 5443200),
    Q(12873893, 403200),
    Q(275968153, 10886400),
    Q(5463001, 345600),
    Q(27875983, 3628800),
    Q(6907559, 2419200),
    Q(8540011, 10886400),
    Q(1330493, 8870400),
    Q(2128963, 119750400),
    Q(338929, 345945600),
)
HSTAR = (
    1, 146, 7901, 128152, 765137, 1903918, 2084165,
    1000574, 197101, 13426, 201, 0, 0, 0,
)
LRCALC_SAMPLE_COUNTS = {
    0: 1,
    1: 160,
    -1: 0,
    2: 10050,
    -2: 0,
    3: 254656,
    -3: 0,
    4: 3473010,
    -4: 201,
    5: 30852404,
    -5: 16240,
    6: 200925962,
    -6: 406170,
    7: 1035303314,
}
EXPECTED_HELD_OUT = {8: 4444160280, 9: 16481696710}


def polynomial(n):
    return sum(coefficient * n**degree
               for degree, coefficient in enumerate(COEFFICIENTS))


def from_hstar(n):
    return sum(Q(HSTAR[j]) * comb(n + DEGREE - j, DEGREE)
               for j in range(DEGREE + 1))


def linear_cancellation_ratio():
    harmonic = sum((Q(1, k) for k in range(1, DEGREE + 1)), Q(0))
    terms = [Q(HSTAR[0]) * harmonic]
    terms.extend(Q(((-1) ** (j - 1)) * HSTAR[j],
                   DEGREE * comb(DEGREE - 1, j - 1))
                 for j in range(1, DEGREE + 1))
    positive = sum((term for term in terms if term > 0), Q(0))
    negative = sum((-term for term in terms if term < 0), Q(0))
    return negative / positive


def main():
    assert sum(OUTER) == sum(INNER_LEFT) + sum(INNER_RIGHT) == 30
    assert max(map(len, (OUTER, INNER_LEFT, INNER_RIGHT))) == 7
    assert len(COEFFICIENTS) == DEGREE + 1
    assert len(HSTAR) == DEGREE + 1
    assert all(coefficient > 0 for coefficient in COEFFICIENTS)

    # Equality on 2d+1 integer arguments is an exact redundant polynomial
    # identity check, not floating-point evaluation.
    for n in range(2 * DEGREE + 1):
        assert polynomial(n) == from_hstar(n)
        assert polynomial(n).denominator == 1

    # lrcalc-rs displays positive interior counts at negative sample labels.
    # Ehrhart reciprocity contributes a minus sign because d=13 is odd.
    for n, displayed_count in LRCALC_SAMPLE_COUNTS.items():
        expected = Q(displayed_count) if n >= 0 else Q(-displayed_count)
        assert polynomial(n) == expected
    for n, value in EXPECTED_HELD_OUT.items():
        assert polynomial(n) == value
    assert linear_cancellation_ratio() == Q(64842736, 65468479)

    payload = repr((OUTER, INNER_LEFT, INNER_RIGHT, COEFFICIENTS, HSTAR,
                    tuple(LRCALC_SAMPLE_COUNTS.items()),
                    tuple(EXPECTED_HELD_OUT.items()))).encode("ascii")
    print("PASS")
    print(f"payload_sha256={sha256(payload).hexdigest()}")
    print(f"degree={DEGREE} lr_at_1={polynomial(1)}")
    print(f"hstar={HSTAR}")
    print(f"held_out_expected={EXPECTED_HELD_OUT}")
    print(f"linear_cancellation_ratio={linear_cancellation_ratio()}")
    print("all_monomial_coefficients_strictly_positive=true")
    print("aggregate_14814_corpus_audited=false")


if __name__ == "__main__":
    main()
