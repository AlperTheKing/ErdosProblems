#!/usr/bin/env python3
"""Regression tests for the exact P20 support-defect profiler."""

from __future__ import annotations

import unittest

from support_defect_profiles import (
    Sample,
    ceil_nth_root,
    normalized_reflected_sample,
    positive_difference_counts,
    product_ratio,
    profile_sample,
    rational_text,
    verify_sample,
)


class SupportDefectTests(unittest.TestCase):
    def test_diagonal_exception_is_counted(self) -> None:
        result = verify_sample(3, (1, 2, 3))
        self.assertEqual(result.exceptional_sum, 4)
        self.assertEqual(result.exceptional_multiplicity, 2)

    def test_known_duplicate_and_missing_weights(self) -> None:
        sample = Sample("guardrail", 6, (1, 2, 5, 6), "test", "P02")
        row = profile_sample(sample)[2]
        self.assertEqual(row["duplicate_weight"], 2)
        self.assertEqual(row["missing_weight"], 1)
        self.assertEqual(row["Z"], 1)
        self.assertEqual(row["M"], 8)
        self.assertEqual(rational_text(*product_ratio(sample, row)), "44/27")

    def test_gap_components_and_truncation(self) -> None:
        sample = Sample("gaps", 10, (1, 3, 10), "test", "unit")
        row = profile_sample(sample)[2]
        self.assertEqual(row["M"], 8)
        self.assertEqual(row["component_count"], 2)
        self.assertEqual(row["gap_truncation_count"], 1)
        self.assertEqual(row["gap_truncation_weight"], 4)

    def test_every_profile_matches_brute_force(self) -> None:
        sample = Sample("brute", 9, (1, 3, 7, 9), "test", "unit")
        differences = positive_difference_counts(sample.A)
        for row in profile_sample(sample):
            H = int(row["H"])
            thickening = {value - shift for value in sample.A for shift in range(H)}
            Z = sum((H - d) * (differences.get(d, 0) - 1) for d in range(1, H))
            self.assertEqual(row["M"], len(thickening))
            self.assertEqual(row["Z"], Z)

    def test_reflected_normalization(self) -> None:
        sample = normalized_reflected_sample(
            (0, 2, 7), 20, prefix="x", kind="test", source="unit"
        )
        self.assertEqual(sample.A, (1, 3, 8, 14, 19, 21))
        self.assertEqual(sample.N, 21)
        self.assertEqual(verify_sample(sample.N, sample.A).exceptional_multiplicity, 3)

    def test_exact_integer_roots(self) -> None:
        self.assertEqual(ceil_nth_root(64, 3), 4)
        self.assertEqual(ceil_nth_root(65, 3), 5)
        self.assertEqual(ceil_nth_root(10**18, 4), 31623)

    def test_multiple_repeated_sums_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-admissible"):
            verify_sample(4, (1, 2, 3, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
