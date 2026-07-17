#!/usr/bin/env python3
"""Exact arithmetic audit for the e(G) >= 43 reduction in Problem 128."""

from fractions import Fraction
from math import comb


def main() -> None:
    # A fixed edge belongs to this fraction of the 10-subsets.
    half_edge_probability = Fraction(comb(18, 8), comb(20, 10))
    assert half_edge_probability == Fraction(9, 38)

    # For a complementary pair (A,B), an edge is internal to one side with
    # probability 9/19.  These are all possible low-edge cases forced by
    # averaging when 39 <= e <= 42.
    expected_cases = {
        39: ((9, 9),),
        40: ((9, 9),),
        41: ((9, 9), (9, 10)),
        42: ((9, 9), (9, 10)),
    }

    reports = []
    for edges, expected in expected_cases.items():
        pair_mean = Fraction(9 * edges, 19)
        pair_ceiling_minus_one = pair_mean.numerator // pair_mean.denominator
        cases = tuple(
            (a, b)
            for a in range(9, pair_ceiling_minus_one + 1)
            for b in range(a, pair_ceiling_minus_one + 1)
            if a + b <= pair_ceiling_minus_one
        )
        assert cases == expected

        for a, b in cases:
            cross = edges - a - b
            excess = cross - 20
            assert excess >= 0

            if (a, b) == (9, 9):
                # The two swap-capacity inequalities imply
                # 24 - 2q <= Q_A2 + Q_B2 <= 2q.  For q <= 5 this is false.
                lower = 24 - 2 * excess
                upper = 2 * excess
                assert lower > upper
                reason = f"symmetric-capacity: {lower}>{upper}"
            elif (a, b) == (9, 10):
                # The degree-2 core on the 9-edge side sends at least 16
                # cross incidences, while all eligible receivers have total
                # capacity at most 3q.
                receiver_capacity = 3 * excess
                assert receiver_capacity < 16
                reason = f"asymmetric-capacity: {receiver_capacity}<16"
            else:
                raise AssertionError("Unexpected low-edge pair")

            reports.append((edges, a, b, cross, excess, reason))

    assert len(reports) == 6
    for row in reports:
        print(
            "e=%d halves=(%d,%d) cross=%d q=%d KILLED %s" % row
        )
    print("PASS: every 39 <= e <= 42 case forced by exact averaging is killed")


if __name__ == "__main__":
    main()
