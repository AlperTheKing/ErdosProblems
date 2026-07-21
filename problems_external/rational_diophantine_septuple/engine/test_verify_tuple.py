#!/usr/bin/env python3
"""Calibration and unit tests for the independent exact tuple verifier."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

from verify_tuple import (
    CALIBRATIONS,
    calibration_report,
    decode_json_document,
    rational,
    rational_square_root,
    verify_tuple,
)


ENGINE_DIR = Path(__file__).resolve().parent
VERIFIER = ENGINE_DIR / "verify_tuple.py"


class RationalSquareTests(unittest.TestCase):
    def test_exact_square_root(self) -> None:
        self.assertEqual(rational_square_root(Fraction(49, 121)), (Fraction(7, 11), None))
        self.assertEqual(rational_square_root(Fraction(0)), (Fraction(0), None))

    def test_exact_failure_reasons(self) -> None:
        self.assertEqual(rational_square_root(Fraction(-1, 4)), (None, "negative"))
        self.assertEqual(
            rational_square_root(Fraction(2, 3)),
            (None, "numerator_not_square+denominator_not_square"),
        )

    def test_binary_float_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "floating-point"):
            rational(0.5)


class PublishedCalibrationTests(unittest.TestCase):
    def test_gibbs_sextuple_has_all_fifteen_square_pairs(self) -> None:
        report = calibration_report("gibbs")
        self.assertTrue(report["calibration_ok"])
        self.assertTrue(report["valid"])
        self.assertEqual(report["pair_count"], 15)
        self.assertEqual(report["pair_failure_count"], 0)
        self.assertTrue(all(pair["root"] is not None for pair in report["pairs"]))

    def test_dujella_almost_septuple_has_exactly_one_failure(self) -> None:
        report = calibration_report("dujella")
        failures = [pair for pair in report["pairs"] if not pair["is_square"]]
        self.assertTrue(report["calibration_ok"])
        self.assertFalse(report["valid"])
        self.assertEqual(failures[0]["indices"], [6, 7])
        self.assertEqual(failures[0]["values"], ["38269/6480", "196/45"])
        self.assertEqual(failures[0]["product_plus_one"], "1948081/72900")
        self.assertEqual(failures[0]["failure"], "numerator_not_square")
        self.assertEqual(report["pair_count"], 21)
        self.assertEqual(len(failures), 1)
        self.assertEqual(report["square_pair_count"], 20)

    def test_calibration_values_are_nonzero_and_distinct(self) -> None:
        for name, calibration in CALIBRATIONS.items():
            with self.subTest(name=name):
                report = verify_tuple(calibration["values"], name)
                self.assertTrue(report["nonzero"])
                self.assertTrue(report["distinct"])


class InputAndDiagnosticTests(unittest.TestCase):
    def test_json_array_and_object(self) -> None:
        name, values = decode_json_document('["1", "3", 8.0]')
        self.assertEqual(name, "candidate")
        self.assertEqual([rational(value) for value in values], [Fraction(1), Fraction(3), Fraction(8)])

        name, values = decode_json_document('{"name":"tiny","tuple":["1/3",3]}')
        self.assertEqual(name, "tiny")
        self.assertEqual([rational(value) for value in values], [Fraction(1, 3), Fraction(3)])

    def test_zero_duplicate_and_pair_failure_are_all_reported(self) -> None:
        report = verify_tuple(["0", "0", "2"], "bad")
        self.assertFalse(report["nonzero"])
        self.assertEqual(report["zero_entries"], [1, 2])
        self.assertFalse(report["distinct"])
        self.assertEqual(report["duplicate_entries"], [{"value": "0", "indices": [1, 2]}])
        self.assertEqual(report["pair_count"], 3)
        self.assertFalse(report["valid"])

    def test_cli_json_report_contains_every_pair(self) -> None:
        process = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--json",
                '["1","3","8"]',
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report["pair_count"], 3)
        self.assertEqual([pair["root"] for pair in report["pairs"]], ["2", "3", "5"])


if __name__ == "__main__":
    unittest.main()
