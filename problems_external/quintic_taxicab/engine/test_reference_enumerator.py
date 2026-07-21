#!/usr/bin/env python3
"""Deterministic small-box tests for the Fraction/isqrt reference."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from reference_enumerator import (
    MAX_DECLARED_CASES,
    BoundsError,
    BoxBounds,
    clear_to_primitive_integers,
    discriminant_radicand,
    enumerate_box,
    evaluate_specialization,
    fifth_form,
    rational_square_root,
    reduced_positive_fractions,
    reduced_signed_fractions,
    z_from_y,
)


ENGINE_DIR = Path(__file__).resolve().parent
REFERENCE = ENGINE_DIR / "reference_enumerator.py"


class FractionArithmeticTests(unittest.TestCase):
    def test_rational_square_root(self) -> None:
        self.assertEqual(rational_square_root(Fraction(49, 121)), Fraction(7, 11))
        self.assertEqual(rational_square_root(Fraction(0)), Fraction(0))
        self.assertIsNone(rational_square_root(Fraction(-1, 4)))
        self.assertIsNone(rational_square_root(Fraction(2, 3)))
        self.assertIsNone(rational_square_root(Fraction(4, 3)))

    def test_reduced_fraction_rectangles_have_no_duplicates(self) -> None:
        positive = list(reduced_positive_fractions(2, 2))
        signed = list(reduced_signed_fractions(1, 2))
        self.assertEqual(positive, [Fraction(1), Fraction(2), Fraction(1, 2)])
        self.assertEqual(
            signed,
            [Fraction(-1), Fraction(0), Fraction(1), Fraction(-1, 2), Fraction(1, 2)],
        )
        self.assertEqual(len(positive), len(set(positive)))
        self.assertEqual(len(signed), len(set(signed)))

    def test_registered_form_and_discriminant_are_exact(self) -> None:
        t = Fraction(3, 2)
        u = Fraction(1, 2)
        a, b = (t - u) / 2, (t + u) / 2
        self.assertEqual(fifth_form(t, u), 16 * (a**5 + b**5))
        T = t + 1
        self.assertEqual(
            discriminant_radicand(t, u),
            80 * T**6 + 20 * T * fifth_form(t, u),
        )

    def test_both_y_signs_feed_distinct_z_values(self) -> None:
        t = Fraction(1)
        self.assertEqual(z_from_y(t, Fraction(100)), Fraction(1))
        self.assertEqual(z_from_y(t, Fraction(-100)), Fraction(-9))
        T = t + 1
        self.assertEqual(z_from_y(t, 10 * T**3), Fraction(0))
        self.assertEqual(rational_square_root(Fraction(0)), Fraction(0))

    def test_denominator_clearing_is_primitive(self) -> None:
        values = (Fraction(1, 2), Fraction(3, 2), Fraction(5, 4), Fraction(7, 4))
        self.assertEqual(clear_to_primitive_integers(values), (2, 6, 5, 7))


    def test_small_quartic_point_is_rejected_by_negative_z_for_both_signs(self) -> None:
        record = evaluate_specialization(Fraction(1, 3), Fraction(1, 5))
        self.assertTrue(record["radicand_rational_square"])
        self.assertEqual(record["y_nonnegative"]["text"], "2864/135")
        self.assertEqual(
            [sign["z"]["text"] for sign in record["signs"]],
            ["-14/75", "-758/225"],
        )
        self.assertTrue(all(not sign["z_nonnegative"] for sign in record["signs"]))
        self.assertTrue(all(not sign["passes_torsor_gates"] for sign in record["signs"]))
        self.assertEqual(record["candidates"], [])

    def test_positive_nonsquare_z_is_rejected_exactly(self) -> None:
        record = evaluate_specialization(Fraction(181, 15), Fraction(86, 15))
        self.assertTrue(record["radicand_rational_square"])
        self.assertEqual(record["y_nonnegative"]["text"], "16982644/675")
        positive_sign, negative_sign = record["signs"]
        self.assertEqual(positive_sign["z"]["text"], "68699/3150")
        self.assertTrue(positive_sign["z_nonnegative"])
        self.assertTrue(positive_sign["z_below_T_squared"])
        self.assertFalse(positive_sign["z_rational_square"])
        self.assertFalse(positive_sign["passes_torsor_gates"])
        self.assertEqual(negative_sign["z"]["text"], "-381449/1050")
        self.assertFalse(negative_sign["z_nonnegative"])
        self.assertFalse(negative_sign["passes_torsor_gates"])
        self.assertEqual(record["candidates"], [])

class EnumerationTests(unittest.TestCase):
    def test_tiny_box_is_exhausted_with_expected_counts(self) -> None:
        report = enumerate_box(BoxBounds(1, 1, 1, 1), emit_points=True)
        self.assertEqual(report["status"], "NO_HIT")
        self.assertEqual(report["scope"], "finite_calibration_box_only")
        self.assertEqual(
            report["counts"],
            {
                "reduced_t_values": 1,
                "reduced_u_values": 3,
                "pairs_considered": 3,
                "admissible_specializations": 1,
                "radicand_squares": 0,
                "y_signs_tested": 0,
                "nonnegative_z": 0,
                "z_squares": 0,
                "bounded_z_squares": 0,
                "candidate_records": 0,
                "verified_integer_certificates": 0,
            },
        )
        self.assertEqual(report["quartic_points"], [])
        self.assertEqual(report["certificates"], [])

    def test_invalid_and_oversized_boxes_fail_closed(self) -> None:
        with self.assertRaisesRegex(BoundsError, "P,Q,D"):
            BoxBounds(0, 1, 1, 1).validate()
        too_large = BoxBounds(MAX_DECLARED_CASES + 1, 1, 0, 1)
        with self.assertRaisesRegex(BoundsError, "exceeds"):
            too_large.validate()

    def test_cli_emits_same_tiny_box_report(self) -> None:
        process = subprocess.run(
            [
                sys.executable,
                str(REFERENCE),
                "--p-max",
                "1",
                "--q-max",
                "1",
                "--u-num-max",
                "1",
                "--u-den-max",
                "1",
                "--emit-points",
            ],
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report["counts"]["pairs_considered"], 3)
        self.assertEqual(report["counts"]["admissible_specializations"], 1)
        self.assertEqual(report["status"], "NO_HIT")


if __name__ == "__main__":
    unittest.main(verbosity=2)
