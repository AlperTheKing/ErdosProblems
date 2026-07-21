#!/usr/bin/env python3
"""Focused calibration tests for the standalone C++ quintic verifier."""

from __future__ import annotations

import json
import math
import random
import subprocess
import unittest
from pathlib import Path


ENGINE_DIR = Path(__file__).resolve().parent
VERIFIER = ENGINE_DIR / "verify_independent.exe"
FIXTURES = ENGINE_DIR / "fixtures"


def run_verifier(*arguments: str) -> tuple[int, dict]:
    completed = subprocess.run(
        [str(VERIFIER), *arguments],
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


def python_oracle(values: tuple[int, int, int, int]) -> dict:
    a, b, c, d = values
    left = a**5 + b**5
    right = c**5 + d**5
    positive = all(value > 0 for value in values)
    equal = left == right
    disjoint = a not in (c, d) and b not in (c, d)
    common_gcd = math.gcd(math.gcd(abs(a), abs(b)), math.gcd(abs(c), abs(d)))
    valid = positive and equal and disjoint
    return {
        "valid": valid,
        "code": "VERIFIED" if valid else "REJECTED",
        "checks": {
            "positive": positive,
            "fifth_power_equal": equal,
            "cross_disjoint": disjoint,
        },
        "primitive": common_gcd == 1,
        "common_gcd": str(common_gcd),
        "left_sum": str(left),
        "right_sum": str(right),
    }


class IndependentVerifierCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not VERIFIER.is_file():
            raise RuntimeError(f"compile the verifier first: {VERIFIER}")

    def assert_matches_oracle(self, values: tuple[int, int, int, int]) -> None:
        code, report = run_verifier(*(str(value) for value in values))
        expected = python_oracle(values)
        self.assertEqual(report, expected)
        self.assertEqual(code, 0 if expected["valid"] else 1)

    def test_embedded_cpp_self_test(self) -> None:
        code, report = run_verifier("--self-test")
        self.assertEqual(code, 0)
        self.assertEqual(
            report, {"valid": True, "code": "SELF_TEST_OK", "checks": 11}
        )

    def test_trivial_positive_equality_is_rejected_for_overlap(self) -> None:
        self.assert_matches_oracle((1, 2, 1, 2))

    def test_signed_disjoint_equality_is_rejected_for_positivity(self) -> None:
        self.assert_matches_oracle((1, -1, 2, -2))

    def test_positive_disjoint_inequality_is_rejected_for_equation(self) -> None:
        self.assert_matches_oracle((1, 2, 3, 4))

    def test_repetition_within_one_representation_is_permitted(self) -> None:
        code, report = run_verifier("2", "2", "3", "4")
        self.assertEqual(code, 1)
        self.assertTrue(report["checks"]["cross_disjoint"])
        self.assertFalse(report["checks"]["fifth_power_equal"])

    def test_large_multiprecision_arithmetic_matches_python(self) -> None:
        x = 123456789012345678901234567890123456789
        y = 987654321098765432109876543210987654321
        self.assert_matches_oracle((x, y, y, x))

    def test_file_input_and_exact_token_count(self) -> None:
        code, report = run_verifier(
            "--file", str(FIXTURES / "rejected_1_2_3_4.txt")
        )
        self.assertEqual(code, 1)
        self.assertEqual(report, python_oracle((1, 2, 3, 4)))

        code, report = run_verifier(
            "--file", str(FIXTURES / "wrong_count.txt")
        )
        self.assertEqual(code, 2)
        self.assertEqual(
            report, {"valid": False, "code": "COUNT", "count": 5}
        )

    def test_malformed_decimal_and_usage_are_machine_readable(self) -> None:
        code, report = run_verifier("1", "2", "3x", "4")
        self.assertEqual(code, 2)
        self.assertEqual(
            report, {"valid": False, "code": "PARSE", "index": 2}
        )

        code, report = run_verifier("1", "2", "3")
        self.assertEqual(code, 2)
        self.assertEqual(report, {"valid": False, "code": "USAGE"})

    def test_deterministic_python_oracle_calibration(self) -> None:
        rng = random.Random(0x5155494E544943)
        cases: list[tuple[int, int, int, int]] = []
        for index in range(64):
            bits = 16 + (index * 11) % 497
            values = [rng.getrandbits(bits) + 1 for _ in range(4)]
            if index % 4 == 0:
                values[2], values[3] = values[0], values[1]
            elif index % 4 == 1:
                values[1] = -values[0]
                values[3] = -values[2]
            elif index % 4 == 2:
                values[1] = values[0]
            else:
                scale = index + 2
                values = [scale * value for value in values]
            cases.append(tuple(values))

        for index, values in enumerate(cases):
            with self.subTest(
                index=index,
                bits=max(abs(value).bit_length() for value in values),
            ):
                self.assert_matches_oracle(values)


if __name__ == "__main__":
    unittest.main(verbosity=2)
