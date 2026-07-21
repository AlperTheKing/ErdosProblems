"""Tests for the independent unrestricted order-19 set-search prototype."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import random
import sys
import unittest


ENGINE = Path(__file__).resolve().parents[1] / "search_unrestricted19_set.py"
SPEC = importlib.util.spec_from_file_location("unrestricted19_set", ENGINE)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class Unrestricted19SetSearchTests(unittest.TestCase):
    def test_01_pair_state_count_and_roundtrip(self) -> None:
        graph = mod.cyclic_tournament()
        raw = graph.to_out_neighbors()
        replay = mod.PairStateGraph.from_out_neighbors(
            raw, minimum_outdegree=mod.MIN_OUTDEGREE
        )
        self.assertEqual(len(mod.pair_list(19)), 171)
        self.assertEqual(replay.states, graph.states)

    def test_02_cyclic_tournament_has_no_missing_pairs(self) -> None:
        graph = mod.cyclic_tournament()
        self.assertEqual(graph.missing_count, 0)
        self.assertEqual(graph.outdegrees(), [9] * 19)
        graph.validate(mod.MIN_OUTDEGREE)

    def test_03_initial_q_and_degree_profiles(self) -> None:
        cases = ((0, "regular"), (3, "skew"), (7, "mixed"), (12, "regular"),
                 (16, "skew"), (19, "mixed"))
        for offset, (q, profile) in enumerate(cases):
            graph = mod.make_initial_graph(q=q, seed=7700 + offset, profile=profile)
            self.assertEqual(graph.missing_count, q)
            self.assertGreaterEqual(min(graph.outdegrees()), 8)
            self.assertEqual(sum(graph.outdegrees()), 171 - q)

    def test_04_profile_families_are_not_degree_identical(self) -> None:
        profiles = {
            tuple(mod.make_initial_graph(q=5, seed=811, profile=profile).outdegrees())
            for profile in mod.PROFILES
        }
        self.assertGreaterEqual(len(profiles), 2)

    def test_05_parser_rejects_loop_digon_and_unsorted_row(self) -> None:
        with self.assertRaisesRegex(mod.GraphInvariantError, "loop"):
            mod.PairStateGraph.from_out_neighbors(((0,),))
        with self.assertRaisesRegex(mod.GraphInvariantError, "digon"):
            mod.PairStateGraph.from_out_neighbors(((1,), (0,)))
        with self.assertRaisesRegex(mod.GraphInvariantError, "sorted and unique"):
            mod.PairStateGraph.from_out_neighbors(((2, 1), (), ()))

    def test_06_exhaustive_small_oracles_agree(self) -> None:
        self.assertEqual(mod.exhaustive_small_oracle_calibration(4), 729)

    def test_07_literal_strictness_is_not_nonstrict(self) -> None:
        # The directed 3-cycle has d+=1 and new second degree=1 in every row.
        graph = mod.PairStateGraph.from_out_neighbors(((1,), (2,), (0,)))
        rows = mod.set_ledger(graph)
        self.assertEqual([(r.out_degree, r.second_degree) for r in rows], [(1, 1)] * 3)
        self.assertFalse(any(row.strict for row in rows))
        self.assertEqual(mod.exact_objective(rows), 3)

    def test_08_per_row_strict_fixture(self) -> None:
        # For the lone arc 0->1, row 0 has d+=1 and no new second neighbour.
        graph = mod.PairStateGraph.from_out_neighbors(((1,), (), ()))
        rows = mod.set_ledger(graph)
        self.assertTrue(rows[0].strict)
        self.assertFalse(rows[1].strict)
        self.assertFalse(rows[2].strict)

    def test_09_objective_zero_set_is_exact(self) -> None:
        strict_row = mod.RowLedger(0, (1,), (), (), 1, 0, True)
        equality_row = mod.RowLedger(1, (2,), (0,), (), 1, 1, False)
        worse_row = mod.RowLedger(2, (), (0, 1), (), 0, 2, False)
        self.assertEqual(mod.exact_objective((strict_row,)), 0)
        self.assertEqual(mod.exact_objective((equality_row,)), 1)
        self.assertEqual(mod.exact_objective((worse_row,)), 5)

    def test_10_mutation_revert_is_exact(self) -> None:
        self.assertEqual(mod.mutation_revert_calibration(seed=9019, steps=1000), 1000)

    def test_11_random_mutations_preserve_the_domain(self) -> None:
        rng = random.Random(4419)
        graph = mod.make_initial_graph(q=9, seed=4419, profile="mixed")
        for _ in range(500):
            mutation = mod.propose_mutation(graph, rng)
            mod.apply_mutation(graph, mutation)
            graph.validate(mod.MIN_OUTDEGREE)
            self.assertLessEqual(graph.missing_count, 19)

    def test_12_delete_insert_and_revert_account_for_q(self) -> None:
        graph = mod.cyclic_tournament()
        index = next(i for i, state in enumerate(graph.states) if state != 0)
        old = graph.states[index]
        delete = mod.Mutation(index, old, 0)
        mod.apply_mutation(graph, delete)
        self.assertEqual(graph.missing_count, 1)
        mod.revert_mutation(graph, delete)
        self.assertEqual(graph.missing_count, 0)

        graph = mod.make_initial_graph(q=19, seed=12, profile="regular")
        index = graph.states.index(0)
        insert = mod.Mutation(index, 0, 1)
        mod.apply_mutation(graph, insert)
        self.assertEqual(graph.missing_count, 18)
        mod.revert_mutation(graph, insert)
        self.assertEqual(graph.missing_count, 19)

    def test_13_walk_is_seed_deterministic(self) -> None:
        kwargs = dict(seed=7719, q=7, profile="mixed", steps=120)
        first = mod.stochastic_walk(**kwargs)
        second = mod.stochastic_walk(**kwargs)
        self.assertEqual(first, second)

    def test_14_no_hit_returns_no_candidate_claim(self) -> None:
        result = mod.stochastic_walk(
            seed=19, q=0, profile="regular", steps=0
        )
        self.assertFalse(result.hit)
        self.assertIsNone(result.out_neighbors)
        self.assertIsNone(result.ledger)
        self.assertGreater(result.best_objective, 0)

    def test_15_raw_replay_boundary_agrees(self) -> None:
        graph = mod.make_initial_graph(q=11, seed=1519, profile="skew")
        raw = graph.to_out_neighbors()
        self.assertEqual(
            mod.set_ledger(graph),
            mod.matrix_oracle(raw, minimum_outdegree=mod.MIN_OUTDEGREE),
        )

    def test_16_calibration_is_explicitly_nonproduction(self) -> None:
        report = mod.calibration_report(walk_steps=5)
        self.assertEqual(report["status"], "CALIBRATION_PASS")
        self.assertFalse(report["production_run"])
        self.assertEqual(report["exhaustive_small_states"], 729)
        self.assertEqual(len(report["initial_profiles"]), 6)


if __name__ == "__main__":
    unittest.main()
