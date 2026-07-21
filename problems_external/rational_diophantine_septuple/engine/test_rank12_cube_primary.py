#!/usr/bin/env python3
"""Unit tests for the primary fixed rank-12 Boolean-cube engine."""

from __future__ import annotations

import unittest
from fractions import Fraction
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rank12_cube_primary as engine


class Rank12CubePrimaryTests(unittest.TestCase):
    def test_model_and_published_points(self) -> None:
        report = engine.model_preflight()
        self.assertEqual(report["published_point_count"], 12)
        self.assertTrue(report["published_points_on_both_models"])
        self.assertEqual(report["p0_image"][0], "0/1")

    def test_general_weierstrass_inverse_and_doubling(self) -> None:
        for point in engine.PUBLISHED_POINTS:
            inverse = engine.CURVE.negate(point)
            self.assertIsNone(engine.CURVE.add(point, inverse))
            doubled = engine.CURVE.double(point)
            self.assertEqual(doubled, engine.CURVE.add(point, point))
            self.assertTrue(engine.CURVE.is_on_curve(doubled))

    def test_referee_subset_hashes(self) -> None:
        doubled = tuple(engine.CURVE.double(point) for point in engine.PUBLISHED_POINTS)
        for expected in engine.REFEREE_SUBSETS.values():
            rows = [
                engine.referee_row(mask, engine.point_for_mask(mask, doubled))
                for mask in expected["indices"]
            ]
            self.assertEqual(
                engine.canonical_json_sha256(rows), expected["rows_sha256"]
            )

    def test_square_criterion(self) -> None:
        examples = (
            (Fraction(3, 5), Fraction(5), True),
            (Fraction(-2), Fraction(1), False),
            (Fraction(1, 2), Fraction(1, 2), False),
            (Fraction(0), Fraction(17, 19), True),
        )
        for left, right, expected in examples:
            self.assertEqual(engine.compatible(left, right), expected)

    def test_k4_enumerator_is_lexicographic_and_complete(self) -> None:
        adjacency = [0] * 5
        for left in range(4):
            for right in range(left + 1, 4):
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
        self.assertEqual(engine.first_k4(adjacency), (0, 1, 2, 3))
        self.assertEqual(engine.all_k4(adjacency), [(0, 1, 2, 3)])

    def test_cross_mask_union(self) -> None:
        masks = engine._cross_engine_masks()
        self.assertEqual(len(masks), 201)
        self.assertEqual(masks, sorted(set(masks)))


if __name__ == "__main__":
    unittest.main()
