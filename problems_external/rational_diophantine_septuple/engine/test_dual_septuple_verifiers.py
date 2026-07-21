#!/usr/bin/env python3
"""Focused tests for the proof-grade dual septuple verification gate."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import unittest
from itertools import combinations
from pathlib import Path

from verify_septuple_independent import (
    EXPECTED_PAIR_COUNT,
    decode_json_document as independent_decode_json_document,
    parse_rational as independent_parse_rational,
    verify_septuple,
)
from verify_tuple import CALIBRATIONS, verify_tuple


ENGINE_DIR = Path(__file__).resolve().parent
PRIMARY = ENGINE_DIR / "verify_tuple.py"
INDEPENDENT = ENGINE_DIR / "verify_septuple_independent.py"


class PrimaryCardinalityContractTests(unittest.TestCase):
    def test_generic_calibration_mode_remains_generic(self) -> None:
        values = CALIBRATIONS["gibbs-sextuple"]["values"]
        generic = verify_tuple(values, "gibbs")
        strict = verify_tuple(values, "gibbs", expect_size=7)

        self.assertTrue(generic["valid"])
        self.assertIsNone(generic["required_size"])
        self.assertTrue(generic["size_ok"])
        self.assertTrue(generic["pair_count_ok"])
        self.assertFalse(strict["valid"])
        self.assertFalse(strict["size_ok"])
        self.assertEqual(strict["pair_count"], 15)
        self.assertEqual(strict["expected_pair_count"], 21)
        self.assertFalse(strict["pair_count_ok"])

    def test_cli_expect_size_seven_rejects_a_six_tuple(self) -> None:
        values = json.dumps(CALIBRATIONS["gibbs-sextuple"]["values"])
        process = subprocess.run(
            [
                sys.executable,
                str(PRIMARY),
                "--json",
                values,
                "--expect-size",
                "7",
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(process.returncode, 1, process.stderr)
        report = json.loads(process.stdout)
        self.assertFalse(report["size_ok"])
        self.assertFalse(report["pair_count_ok"])
        self.assertFalse(report["valid"])

    def test_nonpositive_expected_size_is_malformed(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive integer"):
            verify_tuple(["1"], expect_size=0)


class StandaloneArithmeticTests(unittest.TestCase):
    def test_module_has_no_primary_fraction_or_search_imports(self) -> None:
        tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_modules.add(node.module)
        self.assertNotIn("fractions", imported_modules)
        self.assertFalse(any(module.startswith("verify_tuple") for module in imported_modules))
        self.assertFalse(any("search" in module for module in imported_modules))

    def test_normalization_and_exact_decimal_parsing(self) -> None:
        self.assertEqual(str(independent_parse_rational("-6/-8")), "3/4")
        self.assertEqual(str(independent_parse_rational("1.25e-2")), "1/80")
        self.assertEqual(str(independent_parse_rational("-0.000")), "0")

    def test_malformed_rationals_and_json_are_rejected(self) -> None:
        for malformed in ("1/0", "1/2/3", "not-a-number", "1e"):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ValueError):
                    independent_parse_rational(malformed)
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            independent_decode_json_document('["1/2",]')

        process = subprocess.run(
            [sys.executable, str(INDEPENDENT), "--json", '["1/0"]'],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(process.returncode, 2)
        self.assertIn("denominator must be nonzero", process.stderr)


class DualGateTests(unittest.TestCase):
    def test_wrong_sizes_are_rejected(self) -> None:
        six = list(CALIBRATIONS["gibbs-sextuple"]["values"])
        eight = six + ["1", "3"]
        six_report = verify_septuple(six, "six")
        eight_report = verify_septuple(eight, "eight")

        self.assertFalse(six_report["size_ok"])
        self.assertEqual(six_report["pair_count"], 15)
        self.assertFalse(six_report["pair_count_ok"])
        self.assertFalse(six_report["valid"])
        self.assertFalse(eight_report["size_ok"])
        self.assertEqual(eight_report["pair_count"], 28)
        self.assertFalse(eight_report["pair_count_ok"])
        self.assertFalse(eight_report["valid"])

    def test_zero_is_rejected(self) -> None:
        report = verify_septuple(["0", "1", "3", "8", "2", "4", "5"])
        self.assertFalse(report["nonzero"])
        self.assertEqual(report["zero_entries"], [1])
        self.assertFalse(report["valid"])

    def test_duplicate_is_rejected(self) -> None:
        report = verify_septuple(["1", "1", "3", "8", "2", "4", "5"])
        self.assertFalse(report["distinct"])
        self.assertEqual(
            report["duplicate_entries"], [{"value": "1", "indices": [1, 2]}]
        )
        self.assertFalse(report["valid"])

    def test_known_bad_pair_is_rejected_and_identified(self) -> None:
        values = CALIBRATIONS["dujella-almost-septuple"]["values"]
        report = verify_septuple(values, "dujella")
        failures = [pair for pair in report["pairs"] if not pair["is_square"]]

        self.assertTrue(report["size_ok"])
        self.assertTrue(report["pair_count_ok"])
        self.assertFalse(report["valid"])
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["indices"], [6, 7])
        self.assertEqual(failures[0]["product_plus_one"], "1948081/72900")

    def test_all_twenty_one_unordered_pairs_are_covered_once(self) -> None:
        values = CALIBRATIONS["dujella-almost-septuple"]["values"]
        expected_indices = set(combinations(range(1, 8), 2))
        for report in (
            verify_tuple(values, "primary", expect_size=7),
            verify_septuple(values, "independent"),
        ):
            with self.subTest(implementation=report["name"]):
                observed = {tuple(pair["indices"]) for pair in report["pairs"]}
                self.assertEqual(report["pair_count"], EXPECTED_PAIR_COUNT)
                self.assertEqual(len(observed), EXPECTED_PAIR_COUNT)
                self.assertEqual(observed, expected_indices)
                self.assertTrue(report["pair_count_ok"])

    def test_independent_arithmetic_agrees_on_both_calibrations(self) -> None:
        comparison_keys = (
            "size",
            "required_size",
            "size_ok",
            "values",
            "nonzero",
            "zero_entries",
            "distinct",
            "duplicate_entries",
            "pair_count",
            "expected_pair_count",
            "pair_count_ok",
            "square_pair_count",
            "pair_failure_count",
            "pairs",
            "valid",
        )
        for name, calibration in CALIBRATIONS.items():
            with self.subTest(name=name):
                primary = verify_tuple(
                    calibration["values"], name, expect_size=7
                )
                independent = verify_septuple(calibration["values"], name)
                for key in comparison_keys:
                    self.assertEqual(primary[key], independent[key], key)


if __name__ == "__main__":
    unittest.main()
