#!/usr/bin/env python3
"""Small unit tests for the independent rank-12 cube engine."""

from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rank12_cube_independent import (
    AffinePoint,
    GeneralWeierstrass,
    first_k4,
    rational_square_root,
)


class IndependentGroupLawTests(unittest.TestCase):
    def setUp(self) -> None:
        self.curve = GeneralWeierstrass(
            Fraction(0), Fraction(0), Fraction(0), Fraction(-1), Fraction(1)
        )
        self.point = AffinePoint(Fraction(0), Fraction(1))

    def test_point_and_double(self) -> None:
        self.assertTrue(self.curve.contains(self.point))
        doubled = self.curve.add(self.point, self.point)
        self.assertEqual(doubled, AffinePoint(Fraction(1, 4), Fraction(-7, 8)))
        self.assertTrue(self.curve.contains(doubled))

    def test_inverse_and_scalar(self) -> None:
        inverse = self.curve.inverse(self.point)
        self.assertIsNone(self.curve.add(self.point, inverse))
        self.assertEqual(self.curve.multiply(-1, self.point), inverse)
        self.assertEqual(self.curve.multiply(2, self.point), self.curve.add(self.point, self.point))


class ExactPredicateTests(unittest.TestCase):
    def test_rational_square_root(self) -> None:
        self.assertEqual(rational_square_root(Fraction(49, 64)), Fraction(7, 8))
        self.assertIsNone(rational_square_root(Fraction(2, 9)))
        self.assertIsNone(rational_square_root(Fraction(-1, 4)))

    def test_first_k4(self) -> None:
        adjacency = [0] * 5
        for left in range(4):
            for right in range(left + 1, 4):
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
        self.assertEqual(first_k4(adjacency), (0, 1, 2, 3))
        adjacency[0] &= ~(1 << 3)
        adjacency[3] &= ~(1 << 0)
        self.assertIsNone(first_k4(adjacency))


if __name__ == "__main__":
    unittest.main()
