from __future__ import annotations

import json
import random
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any


ENGINE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
VERIFIER = ENGINE_DIR / "verify_scalar.py"
sys.path.insert(0, str(ENGINE_DIR))

import verify_scalar  # noqa: E402


def _reference_ledger(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Independent matrix/triple-loop calculation used only by the tests."""

    n = data["n"]
    adjacency = [[False] * n for _ in range(n)]
    for source, row in enumerate(data["out_neighbors"]):
        for target in row:
            adjacency[source][target] = True

    result: list[dict[str, Any]] = []
    for source in range(n):
        n1 = [target for target in range(n) if adjacency[source][target]]
        n2_new: list[int] = []
        for target in range(n):
            if target == source or adjacency[source][target]:
                continue
            if any(
                adjacency[source][middle] and adjacency[middle][target]
                for middle in range(n)
            ):
                n2_new.append(target)
        result.append(
            {
                "d1": len(n1),
                "d2": len(n2_new),
                "n1": n1,
                "n2_new": n2_new,
                "strict_d2_lt_d1": len(n2_new) < len(n1),
                "vertex": source,
            }
        )
    return result


class ScalarVerifierTests(unittest.TestCase):
    maxDiff = None

    def _load_fixture(self, name: str) -> str:
        return (FIXTURE_DIR / name).read_text(encoding="utf-8")

    def _run_fixture(self, name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VERIFIER), str(FIXTURE_DIR / name)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_directed_cycle_calibration(self) -> None:
        code, ledger = verify_scalar.verify_certificate_text(
            self._load_fixture("directed_cycle_4.json")
        )
        self.assertEqual(code, verify_scalar.EXIT_VALID_GRAPH_NOT_COUNTEREXAMPLE)
        self.assertEqual(ledger["status"], "VALID_GRAPH_NOT_COUNTEREXAMPLE")
        self.assertEqual(ledger["failing_vertices"], [0, 1, 2, 3])
        for row in ledger["per_vertex"]:
            self.assertEqual((row["d1"], row["d2"]), (1, 1))
            self.assertFalse(row["strict_d2_lt_d1"])

    def test_tournament_calibration(self) -> None:
        raw = self._load_fixture("cyclic_tournament_5.json")
        data = verify_scalar.parse_certificate_json(raw)
        code, ledger = verify_scalar.verify_certificate_data(data)
        self.assertEqual(code, verify_scalar.EXIT_VALID_GRAPH_NOT_COUNTEREXAMPLE)
        self.assertEqual(ledger["per_vertex"], _reference_ledger(data))
        self.assertEqual(ledger["failing_vertices"], [0, 1, 2, 3, 4])

    def test_loop_is_rejected(self) -> None:
        completed = self._run_fixture("invalid_loop.json")
        self.assertEqual(completed.returncode, verify_scalar.EXIT_INVALID_CERTIFICATE)
        ledger = json.loads(completed.stdout)
        self.assertEqual(ledger["status"], "INVALID_CERTIFICATE")
        self.assertIn("loop at vertex 0", ledger["errors"])

    def test_digon_is_rejected(self) -> None:
        completed = self._run_fixture("invalid_digon.json")
        self.assertEqual(completed.returncode, verify_scalar.EXIT_INVALID_CERTIFICATE)
        ledger = json.loads(completed.stdout)
        self.assertEqual(ledger["errors"], ["digon between vertices 0 and 1"])

    def test_malformed_json_is_rejected_with_json_ledger(self) -> None:
        completed = self._run_fixture("malformed_json.json")
        self.assertEqual(completed.returncode, verify_scalar.EXIT_INVALID_CERTIFICATE)
        ledger = json.loads(completed.stdout)
        self.assertEqual(ledger["status"], "INVALID_CERTIFICATE")
        self.assertEqual(ledger["n"], None)
        self.assertTrue(ledger["errors"][0].startswith("invalid JSON:"))

    def test_duplicate_top_level_key_is_rejected(self) -> None:
        completed = self._run_fixture("duplicate_top_level_key.json")
        self.assertEqual(completed.returncode, verify_scalar.EXIT_INVALID_CERTIFICATE)
        ledger = json.loads(completed.stdout)
        self.assertEqual(
            ledger["errors"], ["invalid JSON: duplicate object key 'n'"]
        )

    def test_exact_schema_and_positive_n_are_required(self) -> None:
        cases = [
            ({"n": 1, "out_neighbors": [[]], "extra": 0}, "unexpected top-level keys"),
            ({"n": 1}, "missing top-level keys"),
            ({"n": True, "out_neighbors": [[]]}, "n must be a JSON integer"),
            ({"n": 0, "out_neighbors": []}, "n must be at least 1"),
            ({"n": 2, "out_neighbors": [[]]}, "exactly n=2 rows"),
            ({"n": 1, "out_neighbors": {}}, "out_neighbors must be a JSON array"),
        ]
        for data, expected_fragment in cases:
            with self.subTest(data=data):
                code, ledger = verify_scalar.verify_certificate_data(data)
                self.assertEqual(code, verify_scalar.EXIT_INVALID_CERTIFICATE)
                self.assertTrue(
                    any(expected_fragment in error for error in ledger["errors"]),
                    ledger,
                )

    def test_rows_require_strictly_increasing_unique_integer_vertices(self) -> None:
        cases = [
            ({"n": 3, "out_neighbors": [[2, 1], [], []]}, "strictly increasing"),
            ({"n": 3, "out_neighbors": [[1, 1], [], []]}, "duplicate neighbor 1"),
            ({"n": 3, "out_neighbors": [[True], [], []]}, "must be a JSON integer"),
            ({"n": 3, "out_neighbors": [[1.0], [], []]}, "must be a JSON integer"),
            ({"n": 3, "out_neighbors": [["1"], [], []]}, "must be a JSON integer"),
            ({"n": 3, "out_neighbors": [[3], [], []]}, "outside 0..2"),
            ({"n": 3, "out_neighbors": [[-1], [], []]}, "outside 0..2"),
            ({"n": 3, "out_neighbors": [0, [], []]}, "must be a JSON array"),
        ]
        for data, expected_fragment in cases:
            with self.subTest(data=data):
                code, ledger = verify_scalar.verify_certificate_data(data)
                self.assertEqual(code, verify_scalar.EXIT_INVALID_CERTIFICATE)
                self.assertTrue(
                    any(expected_fragment in error for error in ledger["errors"]),
                    ledger,
                )

    def test_new_second_neighborhood_excludes_source_and_direct_neighbors(self) -> None:
        # 0 -> 1 -> 2 and 0 -> 2.  Vertex 2 is two-step reachable from 0 but
        # is direct, so it must not appear in N2_new(0).
        data = {"n": 3, "out_neighbors": [[1, 2], [2], []]}
        code, ledger = verify_scalar.verify_certificate_data(data)
        self.assertEqual(code, verify_scalar.EXIT_VALID_GRAPH_NOT_COUNTEREXAMPLE)
        self.assertEqual(ledger["per_vertex"][0]["n1"], [1, 2])
        self.assertEqual(ledger["per_vertex"][0]["n2_new"], [])
        self.assertEqual(ledger["per_vertex"][0]["d2"], 0)

    def test_random_oriented_graphs_match_independent_matrix_reference(self) -> None:
        rng = random.Random(0x5E7C0D)
        checked = 0
        for n in range(1, 13):
            for _ in range(40):
                rows = [[] for _ in range(n)]
                for first in range(n):
                    for second in range(first + 1, n):
                        choice = rng.randrange(3)
                        if choice == 1:
                            rows[first].append(second)
                        elif choice == 2:
                            rows[second].append(first)
                for row in rows:
                    row.sort()
                data = {"n": n, "out_neighbors": rows}
                code, ledger = verify_scalar.verify_certificate_data(data)
                self.assertIn(
                    code,
                    (
                        verify_scalar.EXIT_VERIFIED_COUNTEREXAMPLE,
                        verify_scalar.EXIT_VALID_GRAPH_NOT_COUNTEREXAMPLE,
                    ),
                )
                reference = _reference_ledger(data)
                self.assertEqual(ledger["per_vertex"], reference)
                self.assertEqual(
                    ledger["failing_vertices"],
                    [row["vertex"] for row in reference if not row["strict_d2_lt_d1"]],
                )
                checked += 1
        self.assertEqual(checked, 480)

    def test_cli_output_is_byte_deterministic(self) -> None:
        first = self._run_fixture("directed_cycle_4.json")
        second = self._run_fixture("directed_cycle_4.json")
        self.assertEqual(first.returncode, second.returncode)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, "")
        self.assertEqual(second.stderr, "")


if __name__ == "__main__":
    unittest.main()
