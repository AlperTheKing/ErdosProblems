#!/usr/bin/env python3
"""Small, compute-audit-approved tests for the PARI quartic calibration."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "pari_quartic_calibration.py"
SPEC = importlib.util.spec_from_file_location("pari_quartic_calibration", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {MODULE_PATH}")
CAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAL)
def require_clean_worker(completed: subprocess.CompletedProcess[str]) -> None:
    if completed.returncode != 0:
        raise RuntimeError(
            f"PARI integration failed rc={completed.returncode}: "
            f"stdout={completed.stdout!r}, stderr={completed.stderr!r}"
        )
    if completed.stderr != "":
        raise RuntimeError(
            f"PARI integration emitted stderr despite rc=0: {completed.stderr!r}"
        )




class ExactCalibrationUnitTests(unittest.TestCase):
    def test_audit_quartic_coefficients(self) -> None:
        self.assertEqual(CAL.quartic_coefficients(1, 3), (32400, 7200, 327760))

    def test_audit_point_and_both_z_branches(self) -> None:
        coefficients = CAL.quartic_coefficients(1, 3)
        w = Fraction(1, 5)
        y_prime = Fraction(2864, 5)
        self.assertEqual(y_prime * y_prime, CAL.quartic_rhs(coefficients, w))
        plus = CAL.evaluate_signed_branch(1, 3, coefficients, w, y_prime, +1)
        minus = CAL.evaluate_signed_branch(1, 3, coefficients, w, -y_prime, -1)
        self.assertEqual(plus["Z"], "-14/75")
        self.assertFalse(plus["gates"]["z_nonnegative"])
        self.assertFalse(minus["gates"]["z_nonnegative"])
        self.assertEqual(plus["status"], "REJECTED")
        self.assertEqual(minus["status"], "REJECTED")

    def test_audit_positive_nonsquare_z_rejection(self) -> None:
        coefficients = CAL.quartic_coefficients(181, 15)
        branch = CAL.evaluate_signed_branch(
            181,
            15,
            coefficients,
            Fraction(86, 15),
            Fraction(84913220),
            +1,
        )
        self.assertEqual(branch["Z"], "68699/3150")
        self.assertTrue(branch["gates"]["z_nonnegative"])
        self.assertFalse(branch["gates"]["z_rational_square"])
        self.assertEqual(branch["status"], "REJECTED")

    def test_trivial_equality_fails_cross_disjointness(self) -> None:
        record = CAL.verify_integer_quadruple((2, 8, 2, 8))
        self.assertTrue(record["positivity"])
        self.assertTrue(record["fifth_power_equality"])
        self.assertFalse(record["cross_disjoint"])
        self.assertFalse(record["accepted"])

    def test_parser_rejects_unexpected_output(self) -> None:
        with self.assertRaises(CAL.CalibrationError):
            CAL.parse_pari_points("[[1,2],malformed]")

    def test_calibration_cap_is_small(self) -> None:
        self.assertEqual(CAL.MAX_CALIBRATION_BOUND, 1_000)
    def test_worker_stderr_fails_closed_even_with_rc_zero(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["synthetic-worker"],
            returncode=0,
            stdout='{"status":"PASS"}',
            stderr="synthetic warning\n",
        )
        with self.assertRaisesRegex(RuntimeError, "emitted stderr"):
            require_clean_worker(completed)



def run_pari_integration(libpari: Path, case: str) -> None:
    if case == "p1_q3":
        p, q = 1, 3
        numerator_bound, denominator_bound = 10, 10
    elif case == "p181_q15":
        p, q = 181, 15
        numerator_bound, denominator_bound = 100, 15
    else:
        raise RuntimeError(f"unsupported integration case: {case}")

    with tempfile.TemporaryDirectory(prefix="q5_pari_calibration_") as temporary:
        output = Path(temporary) / f"{case}.json"
        command = [
            sys.executable,
            str(MODULE_PATH),
            "--libpari",
            str(libpari),
            "--p",
            str(p),
            "--q",
            str(q),
            "--N",
            str(numerator_bound),
            "--D",
            str(denominator_bound),
            "--output",
            str(output),
        ]
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        require_clean_worker(completed)
        record = json.loads(output.read_text(encoding="utf-8"))
        if record["status"] != "PASS" or not record["point_set_agreement"]:
            raise RuntimeError(f"PARI integration did not pass: {record}")
        expected_input = {
            "p": p,
            "q": q,
            "t": str(Fraction(p, q)),
            "numerator_bound_N": numerator_bound,
            "denominator_bound_D": denominator_bound,
        }
        if record["input"] != expected_input:
            raise RuntimeError(
                f"worker input mismatch: expected={expected_input}, got={record['input']}"
            )
        observed = {(point["w"], point["Y_prime"]) for point in record["points"]}
        if case == "p1_q3":
            expected = {("1/5", "2864/5"), ("1/5", "-2864/5")}
            if not expected.issubset(observed):
                raise RuntimeError(f"approved points absent: {expected - observed}")
            branches = [
                branch for branch in record["branches"] if branch["w"] == "1/5"
            ]
            if (
                len(branches) != 2
                or {branch["sign_test"] for branch in branches} != {-1, 1}
            ):
                raise RuntimeError(
                    "the two approved p1/q3 Y-sign branches were not both tested"
                )
            plus = next(branch for branch in branches if branch["sign_test"] == 1)
            if plus["Z"] != "-14/75" or plus["status"] != "REJECTED":
                raise RuntimeError(f"approved Z rejection disagreed: {plus}")
            summary = {
                "integration": "PASS",
                "case": "p=1,q=3,N=10,D=10",
                "pari_point_count": record["pari_point_count"],
                "signed_branch_count": record["signed_branch_count"],
                "Z": plus["Z"],
                "libpari_sha256": record["engine"]["libpari_sha256"],
            }
        else:
            expected = {("86/15", "84913220"), ("86/15", "-84913220")}
            if not expected.issubset(observed):
                raise RuntimeError(f"approved p181 points absent: {expected - observed}")
            branches = [
                branch for branch in record["branches"] if branch["w"] == "86/15"
            ]
            if (
                len(branches) != 2
                or {branch["sign_test"] for branch in branches} != {-1, 1}
            ):
                raise RuntimeError(
                    "the two approved p181 Y-sign branches were not both tested"
                )
            plus = next(branch for branch in branches if branch["sign_test"] == 1)
            if (
                plus["Z"] != "68699/3150"
                or not plus["gates"]["z_nonnegative"]
                or plus["gates"]["z_rational_square"]
                or plus["status"] != "REJECTED"
            ):
                raise RuntimeError(
                    f"approved p181 positive nonsquare rejection disagreed: {plus}"
                )
            if record["torsor_certificate_candidates"]:
                raise RuntimeError("p181 calibration unexpectedly emitted a candidate")
            summary = {
                "integration": "PASS",
                "case": "p=181,q=15,N=100,D=15",
                "pari_point_count": record["pari_point_count"],
                "signed_branch_count": record["signed_branch_count"],
                "Z": plus["Z"],
                "z_rational_square": plus["gates"]["z_rational_square"],
                "libpari_sha256": record["engine"]["libpari_sha256"],
            }
        print(json.dumps(summary, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--libpari", type=Path)
    parser.add_argument(
        "--integration-case",
        choices=("p1_q3", "p181_q15", "all"),
        help="run one or both approved WSL/PARI integration cases",
    )
    args = parser.parse_args()
    if (args.libpari is None) != (args.integration_case is None):
        parser.error("--libpari and --integration-case must be supplied together")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExactCalibrationUnitTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if args.integration_case in ("p1_q3", "all"):
        run_pari_integration(args.libpari, "p1_q3")
    if args.integration_case in ("p181_q15", "all"):
        run_pari_integration(args.libpari, "p181_q15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
