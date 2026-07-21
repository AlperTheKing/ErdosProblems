from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "audit_cycle19_cnf.py"
SPEC = importlib.util.spec_from_file_location("audit_cycle19_cnf", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class Cycle19OracleTests(unittest.TestCase):
    def test_fixed_support_counts(self) -> None:
        self.assertEqual(len(audit.present_edges()), 152)
        missing = {
            (a, b)
            for a in range(audit.N)
            for b in range(a + 1, audit.N)
            if audit.is_cycle_missing_pair(a, b)
        }
        self.assertEqual(len(missing), 19)

    def test_two_independent_oracles_on_random_orientations(self) -> None:
        rng = random.Random(788321)
        for _ in range(64):
            adjacency = audit.orientation_from_bits([rng.randrange(2) for _ in audit.present_edges()])
            matrix = audit.triple_loop_oracle(adjacency)
            out, second, unreachable = audit.set_oracle(adjacency)
            self.assertEqual(tuple(map(frozenset, matrix.out_neighbors)), out)
            self.assertEqual(tuple(map(frozenset, matrix.second_neighbors)), second)
            self.assertEqual(tuple(map(frozenset, matrix.unreachable)), unreachable)

    def test_direct_neighbor_excluded_even_with_two_step_path(self) -> None:
        bits = [0] * len(audit.present_edges())
        adjacency = audit.orientation_from_bits(bits)

        def force(tail: int, head: int) -> None:
            self.assertFalse(audit.is_cycle_missing_pair(tail, head))
            adjacency[tail][head] = 1
            adjacency[head][tail] = 0

        force(0, 2)
        force(0, 4)
        force(4, 2)
        ledger = audit.triple_loop_oracle(adjacency)
        self.assertTrue(ledger.reach2[0][2])
        self.assertNotIn(2, ledger.second_neighbors[0])
        self.assertNotIn(2, ledger.unreachable[0])

    def test_self_is_excluded_from_second_and_unreachable(self) -> None:
        # The semantic exclusion is explicit, independently of reach2[0][0].
        invalid = audit.adjacency_from_arcs([(0, 2), (2, 0)])
        ledger = audit.triple_loop_oracle(invalid)
        self.assertTrue(ledger.reach2[0][0])
        self.assertNotIn(0, ledger.second_neighbors[0])
        self.assertNotIn(0, ledger.unreachable[0])

    def test_known_circulant_near_miss(self) -> None:
        steps = {2, 4, 6, 8, 10, 12, 14, 16}
        arcs = [(v, (v + step) % audit.N) for v in range(audit.N) for step in steps]
        adjacency = audit.adjacency_from_arcs(arcs)
        audit.validate_fixed_support(adjacency)
        ledger = audit.triple_loop_oracle(adjacency)
        self.assertEqual(ledger.out_degrees, (8,) * audit.N)
        self.assertEqual(ledger.second_degrees, (8,) * audit.N)
        self.assertEqual(ledger.unreachable_row_sums, (2,) * audit.N)
        self.assertEqual(ledger.unreachable_column_sums, (2,) * audit.N)
        self.assertFalse(audit.target_predicate(ledger))
        self.assertFalse(audit.strict_ssnc_failure(ledger))

    def test_row_identity_encodes_strict_inequality_at_regular_degree_eight(self) -> None:
        checked_regular = 0
        # Circulant orientations give a deterministic supply of regular examples.
        inverse_pairs = [(step, audit.N - step) for step in range(2, 10)]
        for mask in range(1 << len(inverse_pairs)):
            chosen = {pair[(mask >> index) & 1] for index, pair in enumerate(inverse_pairs)}
            arcs = [(v, (v + step) % audit.N) for v in range(audit.N) for step in chosen]
            adjacency = audit.adjacency_from_arcs(arcs)
            ledger = audit.triple_loop_oracle(adjacency)
            self.assertEqual(ledger.out_degrees, (8,) * audit.N)
            for v in range(audit.N):
                self.assertEqual(ledger.second_degrees[v] + ledger.unreachable_row_sums[v], 10)
                self.assertEqual(ledger.unreachable_row_sums[v] == 3, ledger.second_degrees[v] == 7)
                self.assertEqual(ledger.unreachable_row_sums[v] >= 3, ledger.second_degrees[v] < 8)
            checked_regular += 1
        self.assertEqual(checked_regular, 256)

    def test_reflection_symmetry_is_support_preserving_and_involutive(self) -> None:
        rng = random.Random(20260721)
        for _ in range(128):
            adjacency = audit.orientation_from_bits([rng.randrange(2) for _ in audit.present_edges()])
            reflected = audit.reflect_swap_0_2(adjacency)
            audit.validate_fixed_support(reflected)
            self.assertEqual(audit.reflect_swap_0_2(reflected), adjacency)
            if adjacency[2][0]:
                self.assertTrue(reflected[0][2])
            normalized = audit.normalize_symmetry_0_to_2(adjacency)
            self.assertTrue(normalized[0][2])
            before = audit.triple_loop_oracle(adjacency)
            after = audit.triple_loop_oracle(normalized)
            self.assertEqual(sorted(before.out_degrees), sorted(after.out_degrees))
            self.assertEqual(sorted(before.second_degrees), sorted(after.second_degrees))
            self.assertEqual(sorted(before.unreachable_row_sums), sorted(after.unreachable_row_sums))

    def test_signed_literals_and_zero_rejection(self) -> None:
        assignment = {1: True, 2: False}
        self.assertTrue(audit.lit_truth(1, assignment))
        self.assertFalse(audit.lit_truth(-1, assignment))
        self.assertFalse(audit.lit_truth(2, assignment))
        self.assertTrue(audit.lit_truth(-2, assignment))
        self.assertTrue(audit.clause_truth((-1, -2), assignment))
        with self.assertRaises(audit.AuditError):
            audit.lit_truth(0, assignment)
        with self.assertRaises(audit.AuditError):
            audit.lit_truth(3, assignment)

    def test_strict_dimacs_parser(self) -> None:
        parsed = audit.parse_dimacs_text("c split clause\np cnf 3 2\n1 -2\n3 0\n0\n")
        self.assertEqual(parsed.variables, 3)
        self.assertEqual(parsed.clauses, ((1, -2, 3), ()))
        for bad_text in (
            "1 0\np cnf 1 1\n",
            "p cnf 1 2\n1 0\n",
            "p cnf 1 1\n2 0\n",
            "p cnf 1 1\n1\n",
            "p cnf 1 1\n1 0\np cnf 1 0\n",
        ):
            with self.assertRaises(audit.AuditError):
                audit.parse_dimacs_text(bad_text)
    def test_raw_cycle19_artifact_reconstructs_exactly(self) -> None:
        engine = Path(__file__).resolve().parents[1]
        instance = engine / "instances" / "cycle19-fixed-v1"
        result = audit.audit_raw_artifacts(
            instance / "cycle19.cnf",
            instance / "manifest.json",
            engine / "generate_cycle19_cnf.py",
            definition_samples=2,
            full_random_samples=2,
        )
        self.assertEqual(result["status"], "RAW_ARTIFACT_AUDIT_PASS")
        self.assertEqual(result["counts"]["variables"], 11248)
        self.assertEqual(result["counts"]["clauses"], 31275)
        self.assertEqual(result["counts"]["semantic_definition_clauses"], 19570)
        self.assertEqual(result["counts"]["cardinality_blocks"], 57)
        self.assertEqual(result["counts"]["unit_clauses"], 1)
        self.assertEqual(result["mutation_rejections"], 6)
        self.assertTrue(result["formula_byte_order_reconstruction"])
        self.assertTrue(result["independent_parser_agreement"])
        self.assertFalse(result["unpinned_production_solve"])
        self.assertEqual(result["full_pinned_calibration"]["actual_sat"], 0)


if __name__ == "__main__":
    unittest.main()
