"""Focused exact-arithmetic calibration for :mod:`elliptic_core`."""

from fractions import Fraction as F
import unittest

from elliptic_core import (
    CubicCurve,
    extension_point,
    extension_roots,
    rational_sqrt,
)


# The first known rational Diophantine sextuple (Gibbs, 1999), as reproduced
# in the published Diophantine-tuple literature and Dujella's tables.
PUBLISHED_SEXTUPLE = (
    F(11, 192),
    F(35, 192),
    F(155, 27),
    F(512, 27),
    F(1235, 48),
    F(180873, 16),
)


class RationalSquareTests(unittest.TestCase):
    def test_exact_rational_square_root(self) -> None:
        self.assertEqual(rational_sqrt(F(37249, 36864)), F(193, 192))
        self.assertEqual(rational_sqrt(0), F(0))
        self.assertIsNone(rational_sqrt(F(2, 3)))
        self.assertIsNone(rational_sqrt(-1))


class PublishedSextupleCalibration(unittest.TestCase):
    def setUp(self) -> None:
        self.a, self.b, self.c, *self.extensions = PUBLISHED_SEXTUPLE
        self.curve = CubicCurve.from_diophantine_triple(
            self.a, self.b, self.c
        )
        self.points = [
            extension_point(self.a, self.b, self.c, x)
            for x in self.extensions
        ]

    def test_all_fifteen_sextuple_pairs_are_squares(self) -> None:
        for i, left in enumerate(PUBLISHED_SEXTUPLE):
            for right in PUBLISHED_SEXTUPLE[i + 1 :]:
                self.assertIsNotNone(
                    rational_sqrt(left * right + 1),
                    msg=f"failed pair {left}, {right}",
                )

    def test_extension_roots_and_curve_reconstruction(self) -> None:
        expected_roots = (
            (F(13, 9), F(19, 9), F(283, 27)),
            (F(151, 96), F(229, 96), F(439, 36)),
            (F(815, 32), F(1453, 32), F(1019, 4)),
        )
        for x, expected, point in zip(
            self.extensions, expected_roots, self.points, strict=True
        ):
            roots = extension_roots(self.a, self.b, self.c, x)
            self.assertEqual(roots, expected)
            self.assertEqual(point, (x, expected[0] * expected[1] * expected[2]))
            self.assertTrue(self.curve.is_on_curve(point))

    def test_invalid_extension_is_rejected(self) -> None:
        self.assertIsNone(extension_roots(self.a, self.b, self.c, F(1)))
        with self.assertRaises(ValueError):
            extension_point(self.a, self.b, self.c, F(1))

    def test_group_identity_inverse_and_closure(self) -> None:
        for point in self.points:
            self.assertEqual(self.curve.add(None, point), point)
            self.assertEqual(self.curve.add(point, None), point)
            self.assertIsNone(self.curve.add(point, self.curve.neg(point)))
            self.assertTrue(self.curve.is_on_curve(self.curve.add(point, point)))

        for left in self.points:
            for right in self.points:
                sum_lr = self.curve.add(left, right)
                self.assertTrue(self.curve.is_on_curve(sum_lr))
                self.assertEqual(sum_lr, self.curve.add(right, left))

    def test_scalar_law_and_associativity_calibration(self) -> None:
        p, q, r = self.points
        self.assertIsNone(self.curve.scalar_mul(0, p))
        self.assertEqual(self.curve.scalar_mul(1, p), p)
        self.assertEqual(self.curve.scalar_mul(-1, p), self.curve.neg(p))
        self.assertEqual(
            self.curve.scalar_mul(3, p),
            self.curve.add(p, self.curve.add(p, p)),
        )
        self.assertEqual(
            self.curve.add(self.curve.add(p, q), r),
            self.curve.add(p, self.curve.add(q, r)),
        )

    def test_known_induced_point_and_bad_input_guard(self) -> None:
        self.assertTrue(self.curve.is_on_curve((F(0), F(1))))
        with self.assertRaises(ValueError):
            self.curve.add((F(0), F(2)), self.points[0])


if __name__ == "__main__":
    unittest.main()
