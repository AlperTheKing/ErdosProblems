from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

from pysat.solvers import Solver


ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

import generate_cycle19_cnf as generator  # noqa: E402


FULL_COUNTS = {
    "orientation": 152,
    "path": 4560,
    "reach2": 342,
    "unreachable": 342,
    "semantic": 5396,
    "auxiliary": 5852,
    "variables": 11248,
    "clauses": 31275,
}


class Cycle19CNFTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.full = generator.Cycle19CNF(enforce_unreachable_equalities=True)

    def test_fixed_graph_domain_and_single_edge_variable_semantics(self) -> None:
        self.assertEqual(len(generator.normalized_missing_edges()), 19)
        self.assertEqual(len(self.full.edge_vars), 152)
        self.assertEqual(self.full.arc_lit(0, 2), 1)
        self.assertEqual(self.full.arc_lit(2, 0), -1)
        with self.assertRaises(ValueError):
            self.full.arc_lit(0, 1)
        with self.assertRaises(ValueError):
            self.full.arc_lit(0, 0)

    def test_semantic_and_full_counts_are_frozen(self) -> None:
        self.assertEqual(self.full.counts, FULL_COUNTS)
        self.assertEqual(len(self.full.aux_ranges), 57)
        self.assertEqual(self.full.semantic_top, 5396)
        self.assertEqual(
            set(self.full.variable_names), set(range(1, self.full.pool.top + 1))
        )
        self.assertIn([self.full.arc_lit(0, 2)], self.full.clauses)

    def test_dimacs_header_and_literal_domain(self) -> None:
        dimacs = self.full.dimacs_bytes().decode("ascii").splitlines()
        self.assertEqual(dimacs[0], "p cnf 11248 31275")
        self.assertEqual(len(dimacs) - 1, 31275)
        maximum = 0
        for line in dimacs[1:]:
            literals = [int(token) for token in line.split()]
            self.assertEqual(literals[-1], 0)
            maximum = max(maximum, *(abs(literal) for literal in literals[:-1]))
        self.assertEqual(maximum, 11248)

    def test_manifest_is_hash_complete_and_deterministic(self) -> None:
        dimacs = self.full.dimacs_bytes()
        first_manifest = generator.build_manifest(self.full, dimacs)
        second_manifest = generator.build_manifest(self.full, dimacs)

        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(first_manifest["counts"], FULL_COUNTS)
        self.assertFalse(first_manifest["constraints"]["root_triangle_constraints"])

        cnf_hash = hashlib.sha256(dimacs).hexdigest().upper()
        self.assertEqual(first_manifest["hashes"]["dimacs_sha256"], cnf_hash)

        variable_map = first_manifest["variable_map"]
        canonical_map = json.dumps(
            variable_map, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        map_hash = hashlib.sha256(canonical_map).hexdigest().upper()
        self.assertEqual(first_manifest["hashes"]["variable_map_sha256"], map_hash)
        self.assertEqual(len(variable_map), 11248)
    def test_every_derived_indicator_matches_scalar_circulant(self) -> None:
        result = generator.calibrate("circulant-even")
        self.assertEqual(result["status"], "CALIBRATION_PASS")
        self.assertEqual(result["derived_indicators_checked"], 5244)
        self.assertEqual(result["mismatches"], 0)
        self.assertEqual(result["second_sizes"], [8] * 19)
        self.assertEqual(result["unreachable_rows"], [2] * 19)
        self.assertEqual(result["unreachable_columns"], [2] * 19)

    def test_every_derived_indicator_matches_scalar_triangle_switch(self) -> None:
        result = generator.calibrate("triangle-switch")
        self.assertEqual(result["status"], "CALIBRATION_PASS")
        self.assertEqual(result["derived_indicators_checked"], 5244)
        self.assertEqual(result["mismatches"], 0)
        self.assertNotEqual(result["second_sizes"], [8] * 19)
        self.assertEqual(sum(result["unreachable_rows"]), sum(result["unreachable_columns"]))

    def test_biconditionals_force_every_indicator_under_pin(self) -> None:
        orientation = generator.calibration_orientation("circulant-even")
        builder = generator.Cycle19CNF(
            enforce_unreachable_equalities=False,
            orientation_pin=orientation,
        )
        paths, reach2, unreachable = generator.scalar_indicators(orientation, builder)
        expected = [
            *((var, paths[key]) for key, var in builder.path_vars.items()),
            *((var, reach2[key]) for key, var in builder.reach2_vars.items()),
            *((var, unreachable[key]) for key, var in builder.unreachable_vars.items()),
        ]
        with Solver(name="cadical195", bootstrap_with=builder.clauses) as solver:
            self.assertTrue(solver.solve())
            for var, value in expected:
                opposite = -var if value else var
                self.assertFalse(
                    solver.solve(assumptions=[opposite]),
                    msg=f"indicator {builder.variable_names[var]} is not biconditional",
                )

    def test_full_equalities_reject_pinned_near_miss(self) -> None:
        orientation = generator.calibration_orientation("circulant-even")
        pinned_full = generator.Cycle19CNF(
            enforce_unreachable_equalities=True,
            orientation_pin=orientation,
        )
        with Solver(name="cadical195", bootstrap_with=pinned_full.clauses) as solver:
            self.assertFalse(solver.solve())


if __name__ == "__main__":
    unittest.main()
