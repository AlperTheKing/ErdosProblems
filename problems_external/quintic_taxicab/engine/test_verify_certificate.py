#!/usr/bin/env python3
"""Unit and CLI tests for the standalone exact certificate verifier."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from verify_certificate import InputError, normalize_quadruple, verify_quadruple


ENGINE_DIR = Path(__file__).resolve().parent
VERIFIER = ENGINE_DIR / "verify_certificate.py"


def run_verifier(*arguments: str, stdin: str | None = None) -> tuple[int, dict]:
    process = subprocess.run(
        [sys.executable, str(VERIFIER), *arguments],
        input=stdin,
        capture_output=True,
        check=False,
        text=True,
    )
    try:
        report = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"verifier emitted non-JSON stdout={process.stdout!r}; "
            f"stderr={process.stderr!r}"
        ) from exc
    return process.returncode, report


class ExactArithmeticTests(unittest.TestCase):
    def test_equal_trivial_representations_fail_only_disjointness(self) -> None:
        report = verify_quadruple(1, 2, 2, 1)
        self.assertFalse(report["valid"])
        self.assertTrue(report["checks"]["positive_integers"])
        self.assertTrue(report["checks"]["fifth_power_equality"])
        self.assertFalse(report["checks"]["cross_disjoint"])
        self.assertEqual(report["cross_collisions"], [1, 2])
        self.assertEqual(report["difference"], 0)

    def test_disjoint_unequal_representations_fail_only_equality(self) -> None:
        report = verify_quadruple(1, 2, 3, 4)
        self.assertFalse(report["valid"])
        self.assertTrue(report["checks"]["positive_integers"])
        self.assertFalse(report["checks"]["fifth_power_equality"])
        self.assertTrue(report["checks"]["cross_disjoint"])
        self.assertEqual(report["difference"], 33 - 1267)

    def test_repetition_inside_one_representation_is_not_a_disjointness_failure(self) -> None:
        report = verify_quadruple(1, 1, 2, 3)
        self.assertTrue(report["checks"]["cross_disjoint"])
        self.assertFalse(report["checks"]["fifth_power_equality"])

    def test_nonpositive_entries_are_reported(self) -> None:
        report = verify_quadruple(0, 2, 3, 4)
        self.assertFalse(report["checks"]["positive_integers"])
        self.assertTrue(report["checks"]["cross_disjoint"])

    def test_arbitrary_precision_fifth_powers_are_exact(self) -> None:
        n = 10**100 + 123
        report = verify_quadruple(n, n + 1, n + 2, n + 3)
        expected = n**5 + (n + 1) ** 5 - (n + 2) ** 5 - (n + 3) ** 5
        self.assertEqual(report["difference"], expected)
        self.assertEqual(report["left_terms"], [n**5, (n + 1) ** 5])


class InputTests(unittest.TestCase):
    def test_supported_json_shapes(self) -> None:
        self.assertEqual(normalize_quadruple([1, 2, 3, 4]), (1, 2, 3, 4))
        self.assertEqual(
            normalize_quadruple({"integer_quadruple": [1, 2, 3, 4]}),
            (1, 2, 3, 4),
        )
        self.assertEqual(
            normalize_quadruple({"a": 1, "b": 2, "c": 3, "d": 4}),
            (1, 2, 3, 4),
        )

    def test_boolean_and_extra_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(InputError, "JSON integers"):
            normalize_quadruple([1, 2, 3, True])
        with self.assertRaisesRegex(InputError, "exactly"):
            normalize_quadruple({"quadruple": [1, 2, 3, 4], "note": "x"})

    def test_cli_invalid_candidate_exit_one_and_json_report(self) -> None:
        code, report = run_verifier("--quadruple", "1", "2", "2", "1")
        self.assertEqual(code, 1)
        self.assertFalse(report["valid"])
        self.assertTrue(report["checks"]["fifth_power_equality"])

    def test_cli_stdin_and_malformed_input(self) -> None:
        code, report = run_verifier("--input", "-", stdin="[1,2,3,4]")
        self.assertEqual(code, 1)
        self.assertEqual(report["certificate"], {"a": 1, "b": 2, "c": 3, "d": 4})

        code, report = run_verifier("--json", "[1,2,3]")
        self.assertEqual(code, 2)
        self.assertFalse(report["valid"])
        self.assertIn("exactly four", report["input_error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
