"""Focused tests for batched exact cover learning in CEGIS v3."""

from __future__ import annotations

import unittest

from ortools.sat.python import cp_model

from cegis_cpsat import N, normalize_projective
from cegis_cpsat_v2 import CegisModelV2
from cegis_cpsat_v3 import UNCOVERED_BATCH, scalar_check_matrix_batched


def canonical_identity() -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(1 if column == N - 1 - row else 0 for column in range(N))
        for row in range(N)
    )


class BatchedScalarTests(unittest.TestCase):
    def test_identity_returns_full_distinct_batch(self) -> None:
        check = scalar_check_matrix_batched(canonical_identity())
        self.assertEqual(check.rank, N)
        self.assertEqual(len(check.uncovered), UNCOVERED_BATCH)
        self.assertEqual(len(set(check.uncovered)), UNCOVERED_BATCH)
        self.assertEqual(check.torus_vectors_checked, UNCOVERED_BATCH)
        self.assertTrue(all(normalize_projective(x) == x for x in check.uncovered))
        self.assertFalse(check.is_counterexample)

    def test_requested_batch_size_is_respected(self) -> None:
        check = scalar_check_matrix_batched(canonical_identity(), limit=7)
        self.assertEqual(len(check.uncovered), 7)
        self.assertEqual(check.torus_vectors_checked, 7)

    def test_nonpositive_batch_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            scalar_check_matrix_batched(canonical_identity(), limit=0)

    def test_every_batched_witness_is_an_exact_cover_cut(self) -> None:
        matrix = canonical_identity()
        check = scalar_check_matrix_batched(matrix, limit=8)
        model = CegisModelV2(base_structural_pruning=False)
        model.fix_matrix(matrix)
        for vector in check.uncovered:
            self.assertTrue(model.add_cover_cut(vector))
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        solver.parameters.max_time_in_seconds = 2.0
        self.assertEqual(solver.solve(model.model), cp_model.INFEASIBLE)


if __name__ == "__main__":
    unittest.main()
