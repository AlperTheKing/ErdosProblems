#!/usr/bin/env python3
"""Independent contract tests for the frozen Q5 candidate table."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import unittest
from pathlib import Path

import q5_manifest as manifest_lib


ENGINE = Path(__file__).resolve().parent
SOURCE = ENGINE / "q5_candidate_table.cpp"
EXECUTABLE = ENGINE / "q5_candidate_table.exe"
TABLE = ENGINE / "q5_candidate_table.json"

EXPECTED_SOURCE_SHA256 = "78928e3074a0c50754990fab6d73c72cddd63b9eb79936902326fed38fab766d"
EXPECTED_EXECUTABLE_SHA256 = "e4b062dd5273e4510c359f55a39565efc9fa8e0b19ad2818a5228ce87a663a6c"
EXPECTED_FILE_SHA256 = "c9cb415199bcb60513c8b41b15c866073f806c9dc7116320471fe7c38e3dac0a"
EXPECTED_PAYLOAD_SHA256 = "f3defaf9d3aa173c800e82d8ab62f24048cafc8d6e8fb16b5ce00106a9791cf8"

REFERENCE_ROWS = {
    48: (1423, 76274, 78585, 69),
    49: (1507, 83469, 85874, 69),
    64: (2519, 240312, 244414, 73),
    128: (10043, 3841277, 3857673, 83),
    256: (39895, 61254641, 61320196, 93),
    384: (89879, 310567671, 310715147, 99),
    512: (159703, 981118966, 981381125, 103),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def floor_sum(n: int, m: int, a: int, b: int) -> int:
    answer = 0
    while True:
        if a >= m:
            answer += (n - 1) * n * (a // m) // 2
            a %= m
        if b >= m:
            answer += n * (b // m)
            b %= m
        y_max = a * n + b
        if y_max < m:
            return answer
        n, b, m, a = y_max // m, y_max % m, a, m


def fast_work(h: int, p: int, q: int) -> int:
    uncapped = min(h, (h * q) // p)
    admissible = floor_sum(uncapped, q, p, p - 1) + (h - uncapped) * h
    return h * h + admissible


class CandidateTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = TABLE.read_bytes()
        cls.table = json.loads(cls.raw.decode("ascii"))
        cls.rows = cls.table["rows"]
        cls.by_h = {row["H"]: row for row in cls.rows}

    def test_frozen_artifact_hashes(self) -> None:
        self.assertEqual(sha256_file(SOURCE), EXPECTED_SOURCE_SHA256)
        self.assertEqual(sha256_file(EXECUTABLE), EXPECTED_EXECUTABLE_SHA256)
        self.assertEqual(sha256_file(TABLE), EXPECTED_FILE_SHA256)
        self.assertEqual(
            manifest_lib.sha256_bytes(manifest_lib.canonical_bytes(self.table)),
            EXPECTED_PAYLOAD_SHA256,
        )
        self.assertEqual(
            self.raw, manifest_lib.canonical_bytes(self.table) + b"\n"
        )

    def test_exact_schema_and_range(self) -> None:
        self.assertEqual(
            set(self.table), {"kind", "rows", "schema_version"}
        )
        self.assertEqual(self.table["schema_version"], 1)
        self.assertEqual(self.table["kind"], "Q5_TORSOR_CANDIDATE_TABLE")
        self.assertEqual([row["H"] for row in self.rows], list(range(48, 513)))
        self.assertEqual(len(self.rows), 465)
        expected_keys = {
            "H",
            "b",
            "balance_pass",
            "max_lane_weight",
            "min_lane_weight",
            "oeis_gate_pass",
            "specialization_count",
        }
        for row in self.rows:
            self.assertEqual(set(row), expected_keys)
            h = row["H"]
            self.assertEqual(row["b"], (5760 * h**10).bit_length())
            self.assertGreater(row["min_lane_weight"], 0)
            self.assertGreaterEqual(
                row["max_lane_weight"], row["min_lane_weight"]
            )
            self.assertEqual(
                row["balance_pass"],
                4 * row["max_lane_weight"] <= 5 * row["min_lane_weight"],
            )
            self.assertEqual(
                row["oeis_gate_pass"],
                manifest_lib.oeis_redundancy_gate(h, h, h)["passes"],
            )
            self.assertTrue(row["balance_pass"])
            self.assertTrue(row["oeis_gate_pass"])

    def test_reference_rows(self) -> None:
        for h, expected in REFERENCE_ROWS.items():
            row = self.by_h[h]
            actual = (
                row["specialization_count"],
                row["min_lane_weight"],
                row["max_lane_weight"],
                row["b"],
            )
            self.assertEqual(actual, expected)

    def test_floor_sum_work_matches_frozen_python_definition(self) -> None:
        for h in range(1, 65):
            for p in range(1, h + 1):
                for q in range(1, h + 1):
                    if math.gcd(p, q) != 1:
                        continue
                    self.assertEqual(
                        fast_work(h, p, q),
                        manifest_lib.estimated_work(
                            p,
                            q,
                            h,
                            h,
                            "canonical_positive_u_positive_y",
                        ),
                    )

    def test_lpt_rows_match_python_at_48_and_64(self) -> None:
        for h in (48, 64):
            lanes = manifest_lib.balanced_assignments(
                h, h, h, h, "canonical_positive_u_positive_y"
            )
            weights = [lane["estimated_weight"] for lane in lanes]
            row = self.by_h[h]
            self.assertEqual(len(list(manifest_lib.reduced_pairs(h, h))),
                             row["specialization_count"])
            self.assertEqual(min(weights), row["min_lane_weight"])
            self.assertEqual(max(weights), row["max_lane_weight"])

    def test_generator_reproduces_exact_bytes_and_refuses_overwrite(self) -> None:
        output = ENGINE / "_q5_candidate_table_test_output.json"
        temporary = ENGINE / "._q5_candidate_table_test_output.json.tmp"
        self.assertFalse(output.exists())
        self.assertFalse(temporary.exists())
        try:
            first = subprocess.run(
                [str(EXECUTABLE), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(output.read_bytes(), self.raw)
            second = subprocess.run(
                [str(EXECUTABLE), "--output", str(output)],
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(second.returncode, 2)
            self.assertIn("refusing to overwrite", second.stderr)
        finally:
            output.unlink(missing_ok=True)
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

