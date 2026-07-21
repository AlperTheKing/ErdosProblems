#!/usr/bin/env python3
"""Cross-calibration of the brute-force and optimized structural S lanes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any


ENGINE_DIR = Path(__file__).resolve().parent
CPP_SOURCE = ENGINE_DIR / "s_lane_search.cpp"
REFERENCE = ENGINE_DIR / "s_lane_reference.py"


def run_jsonl(command: list[str]) -> list[dict[str, Any]]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=ENGINE_DIR,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed with {completed.returncode}: {command!r}\n"
            f"stdout={completed.stdout}\nstderr={completed.stderr}"
        )
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(completed.stdout.splitlines(), start=1):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"non-JSON output at line {line_number}: {line!r}"
            ) from exc
    return records


def records_of_type(records: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [record for record in records if record.get("type") == kind]


class StructuralLaneCrossCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        suffix = ".exe" if os.name == "nt" else ""
        cls.executable = ENGINE_DIR / f"s_lane_search{suffix}"
        if not cls.executable.is_file():
            raise AssertionError(
                "build s_lane_search before running calibration"
            )

    def run_reference(self, p_min: int, p_max: int) -> list[dict[str, Any]]:
        return run_jsonl(
            [
                sys.executable,
                str(REFERENCE),
                "--p-min",
                str(p_min),
                "--p-max",
                str(p_max),
                "--emit-values",
                "--emit-identities",
            ]
        )

    def run_cpp(self, p_min: int, p_max: int) -> list[dict[str, Any]]:
        return run_jsonl(
            [
                str(self.executable),
                "--p-min",
                str(p_min),
                "--p-max",
                str(p_max),
                "--threads",
                "1",
                "--emit-values",
                "--emit-identities",
            ]
        )

    def test_every_value_and_join_matches_brute_force_at_p64(self) -> None:
        reference = self.run_reference(2, 64)
        optimized = self.run_cpp(2, 64)

        reference_values = {
            record["fraction"]: (
                tuple(record["pair"]),
                record["h"],
                record["u"],
                record["v"],
            )
            for record in records_of_type(reference, "value")
        }
        optimized_values = {
            record["fraction"]: (
                tuple(record["pair"]),
                record["h"],
                record["u"],
                record["v"],
            )
            for record in records_of_type(optimized, "value")
        }
        self.assertEqual(optimized_values, reference_values)
        self.assertEqual(len(reference_values), 847)

        reference_identities = {
            record["key"]: record for record in records_of_type(reference, "identity")
        }
        optimized_identities = {
            record["key"]: record for record in records_of_type(optimized, "identity")
        }
        self.assertEqual(optimized_identities, reference_identities)

        reference_summary = records_of_type(reference, "summary")[0]
        optimized_summary = records_of_type(optimized, "summary")[0]
        for field in (
            "canonical_pair_count",
            "unique_f_count",
            "pair_comparisons",
            "identity_count",
            "candidate_count",
            "status",
        ):
            self.assertEqual(optimized_summary[field], reference_summary[field], field)
        self.assertEqual(reference_summary["pair_comparisons"], 104786)
        self.assertEqual(reference_summary["status"], "EXHAUSTED")

    def test_cpp_lane_key_partition_is_exact_at_p64(self) -> None:
        full = self.run_cpp(2, 64)
        lower = self.run_cpp(2, 32)
        upper = self.run_cpp(33, 64)
        full_keys = {item["key"] for item in records_of_type(full, "identity")}
        partition_keys = {
            item["key"]
            for records in (lower, upper)
            for item in records_of_type(records, "identity")
        }
        self.assertEqual(partition_keys, full_keys)

    def test_p256_reduced_intermediates_do_not_overflow(self) -> None:
        records = run_jsonl(
            [
                str(self.executable),
                "--p-min",
                "2",
                "--p-max",
                "256",
                "--threads",
                "4",
            ]
        )
        summary = records_of_type(records, "summary")[0]
        self.assertEqual(summary["status"], "EXHAUSTED")
        self.assertEqual(summary["canonical_pair_count"], 13332)
        self.assertEqual(summary["unique_f_count"], 13332)
        self.assertEqual(summary["pair_comparisons"], 26392845)
        self.assertEqual(summary["identity_count"], 0)
        self.assertEqual(summary["candidate_count"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
