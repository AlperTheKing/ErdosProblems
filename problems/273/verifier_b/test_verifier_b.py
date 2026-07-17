#!/usr/bin/env python3
"""Adversarial mutation tests for the independent reduced-fiber verifier."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from verifier_b import CertificateError, check_distinct, verify_certificate


BASE = Path(__file__).resolve().parent


def certificate() -> dict:
    return json.loads((BASE / "baseline_half_cover_certificate.json").read_text(encoding="utf-8"))


class VerifierBTests(unittest.TestCase):
    def test_valid_certificate_passes(self) -> None:
        lines = verify_certificate(certificate())
        self.assertEqual(lines[-1], "RESULT PASS")

    def test_changed_transition_mask_is_rejected(self) -> None:
        bad = certificate()
        bad["odd_fiber_chain"][4]["transition"]["removed_mask"] = (
            "0x000800020000000020000800020000800000000800021"
        )
        with self.assertRaisesRegex(CertificateError, "removed mask is incorrect"):
            verify_certificate(bad)

    def test_wrong_lift_is_rejected(self) -> None:
        bad = certificate()
        bad["odd_fiber_chain"][6]["lifted_class"]["residue"] = 25
        with self.assertRaisesRegex(CertificateError, "incorrect odd lift"):
            verify_certificate(bad)

    def test_truncated_chain_is_rejected(self) -> None:
        bad = certificate()
        bad["odd_fiber_chain"].pop()
        with self.assertRaisesRegex(CertificateError, "final residual has 1 points"):
            verify_certificate(bad)

    def test_false_prime_remainder_is_rejected(self) -> None:
        bad = certificate()
        bad["prime_trial_certificates"][-1]["remainders"][-1] = 0
        with self.assertRaisesRegex(CertificateError, "incorrect exact remainder vector"):
            verify_certificate(bad)

    def test_missing_prime_certificate_is_rejected(self) -> None:
        bad = certificate()
        bad["prime_trial_certificates"].pop()
        with self.assertRaisesRegex(CertificateError, "wrong length"):
            verify_certificate(bad)

    def test_duplicate_modulus_checker_is_exact(self) -> None:
        with self.assertRaisesRegex(CertificateError, "duplicate values \[4\]"):
            check_distinct([2, 4, 6, 4], "test moduli")

    def test_noncanonical_mask_is_rejected(self) -> None:
        bad = certificate()
        bad["odd_fiber_chain"][0]["transition"]["after_mask"] = "0X" + "a" * 45
        with self.assertRaisesRegex(CertificateError, "noncanonical hex"):
            verify_certificate(bad)


if __name__ == "__main__":
    unittest.main()
