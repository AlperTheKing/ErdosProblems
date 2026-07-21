"""Focused exactness tests for the separate AJT CEGIS v2 engine."""

from __future__ import annotations

import unittest

from ortools.sat.python import cp_model

from cegis_cpsat import N, _mat_vec_mod, normalize_projective
from cegis_cpsat_v2 import (
    CegisModelV2,
    INITIAL_COVER_CUTS,
    projective_kernel_vectors_mod5,
    seed_exact_cuts,
)


def rank_six_matrix() -> tuple[tuple[int, ...], ...]:
    rows = [
        tuple(1 if column == pivot else 0 for column in range(N))
        for pivot in range(2, N)
    ]
    rows.append(tuple(1 if column in (2, 3) else 0 for column in range(N)))
    rows.append(tuple((2 if column == 3 else 1) if column == 2 else 0 for column in range(N)))
    return tuple(rows)


def support_pattern_matrix(support_two_rows: int) -> tuple[tuple[int, ...], ...]:
    if support_two_rows not in (4, 5):
        raise ValueError("test fixture supports only four or five sparse rows")
    rows: list[tuple[int, ...]] = []
    for leading in range(6, 6 - support_two_rows, -1):
        rows.append(
            tuple(1 if column in (leading, 7) else 0 for column in range(N))
        )
    next_leading = 6 - support_two_rows
    while len(rows) < N:
        multiplier = len(rows) - support_two_rows + 1
        rows.append(
            tuple(
                1
                if column in (next_leading, 7)
                else multiplier
                if column == 6
                else 0
                for column in range(N)
            )
        )
        next_leading = max(0, next_leading - 1)
    return tuple(sorted(rows, key=lambda row: sum(v * 5 ** (7 - i) for i, v in enumerate(row))))


def solve_fixed(matrix: tuple[tuple[int, ...], ...]) -> int:
    model = CegisModelV2(base_structural_pruning=False)
    model.fix_matrix(matrix)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 2.0
    return solver.solve(model.model)


class KernelCutTests(unittest.TestCase):
    def test_rank_six_kernel_has_six_projective_directions(self) -> None:
        matrix = rank_six_matrix()
        directions = projective_kernel_vectors_mod5(matrix)
        self.assertEqual(len(directions), 6)
        self.assertEqual(len(set(directions)), 6)
        for vector in directions:
            self.assertEqual(normalize_projective(vector), vector)
            self.assertEqual(_mat_vec_mod(matrix, vector), (0,) * N)


class StructuralPruningTests(unittest.TestCase):
    def test_five_support_two_rows_are_rejected(self) -> None:
        self.assertEqual(solve_fixed(support_pattern_matrix(5)), cp_model.INFEASIBLE)

    def test_four_support_two_rows_are_not_rejected_by_the_cap(self) -> None:
        self.assertIn(
            solve_fixed(support_pattern_matrix(4)),
            (cp_model.FEASIBLE, cp_model.OPTIMAL),
        )

    def test_seed_set_is_projectively_exact_and_deduplicated(self) -> None:
        model = CegisModelV2(base_structural_pruning=False)
        seed_exact_cuts(model)
        self.assertEqual(len(model.cover_vectors), INITIAL_COVER_CUTS)
        self.assertEqual(len(model.rank_vectors), N)
        self.assertTrue(all(vector[0] == 1 for vector in model.cover_vectors))


if __name__ == "__main__":
    unittest.main()
