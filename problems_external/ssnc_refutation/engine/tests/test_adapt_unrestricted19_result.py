"""Tests for the engine-result to strict-candidate adapter."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import sys

import unittest


ADAPTER = Path(__file__).resolve().parents[1] / "adapt_unrestricted19_result.py"
SPEC = importlib.util.spec_from_file_location("unrestricted_result_adapter", ADAPTER)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

ROWS = [[1], [], []]


class ResultAdapterTests(unittest.TestCase):
    def test_01_legacy_projection_is_exact(self) -> None:
        value = {"n": 3, "out_neighbors": ROWS, "energy": 17, "q": 2}
        self.assertEqual(
            mod.adapt(value, "legacy"),
            {"n": 3, "out_neighbors": ROWS},
        )

    def test_02_oracle_projection_adds_only_schema(self) -> None:
        self.assertEqual(
            mod.adapt({"n": 3, "out_neighbors": ROWS}, "oracle"),
            {
                "schema": "ssnc-oriented-graph-v1",
                "n": 3,
                "out_neighbors": ROWS,
            },
        )

    def test_03_nested_candidate_is_supported(self) -> None:
        value = {
            "status": "BEST_CHECKPOINT",
            "candidate": {"n": 3, "out_neighbors": ROWS},
        }
        self.assertEqual(mod.adapt(value, "legacy")["out_neighbors"], ROWS)

    def test_04_partial_candidate_is_rejected(self) -> None:
        for value in (
            {"n": 3},
            {"out_neighbors": ROWS},
            {"candidate": {"n": 3}},
            {"status": "NO_HIT"},
        ):
            with self.assertRaises(mod.AdapterError):
                mod.adapt(value, "legacy")

    def test_05_bad_graph_structure_is_rejected(self) -> None:
        mutants = (
            {"n": 1, "out_neighbors": [[0]]},
            {"n": 2, "out_neighbors": [[1], [0]]},
            {"n": 3, "out_neighbors": [[1, 1], [], []]},
            {"n": 3, "out_neighbors": [[2, 1], [], []]},
            {"n": 3, "out_neighbors": [[3], [], []]},
        )
        for value in mutants:
            with self.assertRaises(mod.AdapterError):
                mod.adapt(value, "legacy")

    def test_06_parser_rejects_truncated_json(self) -> None:
        with self.assertRaises(json.JSONDecodeError):
            json.loads('{"n":19,"out_neighbors":[')

    def test_07_parser_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(mod.DuplicateKeyError):
            json.loads(
                '{"n":1,"n":1,"out_neighbors":[[]]}',
                object_pairs_hook=mod.reject_duplicate_keys,
            )

    def test_08_input_object_is_not_mutated(self) -> None:
        value = {"n": 3, "out_neighbors": [[1], [], []], "energy": 4}
        before = json.dumps(value, sort_keys=True)
        mod.adapt(value, "oracle")
        self.assertEqual(json.dumps(value, sort_keys=True), before)


if __name__ == "__main__":
    unittest.main()
