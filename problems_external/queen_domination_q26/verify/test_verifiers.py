#!/usr/bin/env python3
"""Regression tests for both independent queen-domination verifiers."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import bitset_verify
import scalar_verify


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
CHECKERS = (scalar_verify, bitset_verify)


def checked(module, fixture: str):
    certificate = module.load_certificate(FIXTURES / fixture)
    return module.verify(
        certificate["n"],
        certificate["coordinates"],
        expected_count=certificate["expected_count"],
        require_independent=certificate["require_independent"],
    )


class PublishedFixtureTests(unittest.TestCase):
    def test_q25_published_fixture(self):
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                result = checked(checker, "q25_ostergard_weakley_13.json")
                self.assertTrue(result["valid"], result)
                self.assertEqual(result["dominated_count"], 625)
                self.assertTrue(result["independent"])

    def test_q26_published_fixture(self):
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                result = checked(checker, "q26_ostergard_weakley_14.json")
                self.assertTrue(result["valid"], result)
                self.assertEqual(result["dominated_count"], 676)
                self.assertTrue(result["independent"])


class CorruptionTests(unittest.TestCase):
    def test_moved_queen_is_rejected(self):
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                result = checked(checker, "q25_corrupt_moved.json")
                self.assertFalse(result["valid"])
                self.assertGreater(len(result["undominated"]), 0)

    def test_duplicate_queen_is_rejected(self):
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                result = checked(checker, "q25_corrupt_duplicate.json")
                self.assertFalse(result["valid"])
                self.assertIn("coordinates are not distinct", result["errors"])

    def test_removed_q26_queen_is_rejected(self):
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                result = checked(checker, "q26_corrupt_removed.json")
                self.assertFalse(result["valid"])
                self.assertIn("expected 14 queens, found 13", result["errors"])

    def test_out_of_range_is_rejected(self):
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                result = checker.verify(5, [(0, 0), (5, 1)])
                self.assertFalse(result["valid"])
                self.assertTrue(any("out-of-range" in error for error in result["errors"]))


class InterfaceTests(unittest.TestCase):
    def test_plain_text_parser(self):
        path = FIXTURES / "q25_ostergard_weakley_13.txt"
        for checker in CHECKERS:
            with self.subTest(checker=checker.__name__):
                certificate = checker.load_certificate(path)
                result = checker.verify(
                    certificate["n"],
                    certificate["coordinates"],
                    expected_count=certificate["expected_count"],
                    require_independent=certificate["require_independent"],
                )
                self.assertTrue(result["valid"], result)

    def test_cli_exit_codes_and_json(self):
        for script in ("scalar_verify.py", "bitset_verify.py"):
            with self.subTest(script=script, kind="valid"):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(HERE / script),
                        str(FIXTURES / "q26_ostergard_weakley_14.json"),
                        "--json-output",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertTrue(json.loads(completed.stdout)["valid"])
            with self.subTest(script=script, kind="invalid"):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(HERE / script),
                        str(FIXTURES / "q25_corrupt_moved.json"),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 1, completed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
