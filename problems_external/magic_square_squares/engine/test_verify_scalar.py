#!/usr/bin/env python3
"""Calibration tests for verify_scalar.py."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ENGINE_DIR = Path(__file__).resolve().parent
VERIFIER = ENGINE_DIR / "verify_scalar.py"
FIXTURES = ENGINE_DIR / "fixtures"


def run_verifier(*arguments: str, stdin: str | None = None) -> tuple[int, dict]:
    completed = subprocess.run(
        [sys.executable, str(VERIFIER), *arguments],
        input=stdin,
        capture_output=True,
        check=False,
        text=True,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"verifier did not emit JSON; stdout={completed.stdout!r}, "
            f"stderr={completed.stderr!r}"
        ) from exc
    return completed.returncode, payload


class ScalarVerifierCalibrationTests(unittest.TestCase):
    def test_lo_shu_is_magic_but_rejected_for_squareness(self) -> None:
        code, report = run_verifier(
            "--input", str(FIXTURES / "lo_shu_nonsquare.json")
        )
        self.assertEqual(code, 1)
        self.assertFalse(report["valid"])
        self.assertTrue(report["checks"]["positive"])
        self.assertTrue(report["checks"]["pairwise_distinct"])
        self.assertTrue(report["checks"]["all_eight_sums_equal"])
        self.assertFalse(report["checks"]["perfect_squares"])
        self.assertEqual(report["common_sum"], 15)
        self.assertEqual(report["dominant_line_count"], 8)

    def test_sallows_near_miss_has_exactly_seven_equal_lines(self) -> None:
        code, report = run_verifier(
            "--input", str(FIXTURES / "sallows_7_of_8.json")
        )
        self.assertEqual(code, 1)
        self.assertFalse(report["valid"])
        self.assertTrue(report["checks"]["positive"])
        self.assertTrue(report["checks"]["perfect_squares"])
        self.assertTrue(report["checks"]["pairwise_distinct"])
        self.assertFalse(report["checks"]["all_eight_sums_equal"])
        self.assertEqual(report["dominant_sum"], 21609)
        self.assertEqual(report["dominant_line_count"], 7)
        self.assertEqual(report["line_sums"]["diagonal_main"], 38307)

    def test_repeated_square_matrix_is_rejected_only_for_distinctness(self) -> None:
        code, report = run_verifier(
            "--input", str(FIXTURES / "repeated_square_magic.json")
        )
        self.assertEqual(code, 1)
        self.assertFalse(report["valid"])
        self.assertTrue(report["checks"]["positive"])
        self.assertTrue(report["checks"]["perfect_squares"])
        self.assertFalse(report["checks"]["pairwise_distinct"])
        self.assertTrue(report["checks"]["all_eight_sums_equal"])

    def test_direct_matrix_json_is_accepted_as_input_shape(self) -> None:
        code, report = run_verifier(
            "--matrix", "[[8,1,6],[3,5,7],[4,9,2]]"
        )
        self.assertEqual(code, 1)
        self.assertEqual(report["input_kind"], "matrix")
        self.assertEqual(report["common_sum"], 15)

    def test_msq_d_cli_expands_using_registered_formula(self) -> None:
        code, report = run_verifier("--msq-d", "5", "1", "2")
        self.assertEqual(code, 1)
        self.assertEqual(report["input_kind"], "msq_d")
        self.assertEqual(report["certificate"], {"m": 5, "b": 1, "c": 2, "center": 25})
        self.assertEqual(
            report["matrix"],
            [[24, 28, 23], [24, 25, 26], [27, 22, 26]],
        )
        self.assertTrue(report["checks"]["all_eight_sums_equal"])
        self.assertFalse(report["msq_d_checks"]["all_four_deltas_in_D"])

    def test_direct_msq_d_json_from_stdin_is_detected(self) -> None:
        code, report = run_verifier("--input", "-", stdin="[5,1,2]")
        self.assertEqual(code, 1)
        self.assertEqual(report["input_kind"], "msq_d")
        self.assertEqual(report["certificate"]["center"], 25)

    def test_malformed_input_emits_json_and_exit_two(self) -> None:
        code, report = run_verifier("--matrix", "[[1,2],[3,4]]")
        self.assertEqual(code, 2)
        self.assertFalse(report["valid"])
        self.assertIn("exactly three rows", report["input_error"])

    def test_boolean_is_not_accepted_as_an_integer(self) -> None:
        code, report = run_verifier(
            "--matrix", "[[1,4,9],[16,true,36],[49,64,81]]"
        )
        self.assertEqual(code, 2)
        self.assertFalse(report["valid"])
        self.assertIn("must be a JSON integer", report["input_error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
