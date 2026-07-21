"""Focused tests for the exact checks and learned constraints in cegis_cpsat."""

from __future__ import annotations

import unittest

from ortools.sat.python import cp_model

from cegis_cpsat import (
    CegisModel,
    N,
    _format_plain_matrix,
    _mat_vec_mod,
    normalize_projective,
    rank_and_nullvector_mod5,
    scalar_check_matrix,
)


def canonical_identity() -> tuple[tuple[int, ...], ...]:
    """A row-normalized, strictly row-code-sorted permutation matrix."""

    return tuple(
        tuple(1 if column == N - 1 - row else 0 for column in range(N))
        for row in range(N)
    )


def canonical_rank_seven() -> tuple[tuple[int, ...], ...]:
    rows = [
        tuple(1 if column == pivot else 0 for column in range(N))
        for pivot in range(N - 1, 0, -1)
    ]
    rows.append(tuple(1 if column in (1, 2) else 0 for column in range(N)))
    return tuple(rows)


def solve_fixed(model: CegisModel) -> int:
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 2.0
    return solver.solve(model.model)


class ExactArithmeticTests(unittest.TestCase):
    def test_projective_normalization_is_scale_invariant(self) -> None:
        vector = (0, 2, 4, 1, 3, 0, 2, 1)
        scaled = tuple((3 * value) % 5 for value in vector)
        expected = (0, 1, 2, 3, 4, 0, 1, 3)
        self.assertEqual(normalize_projective(vector), expected)
        self.assertEqual(normalize_projective(scaled), expected)

    def test_scalar_checker_rejects_identity_by_first_torus_vector(self) -> None:
        check = scalar_check_matrix(canonical_identity())
        self.assertEqual(check.rank, N)
        self.assertIsNone(check.nullvector)
        self.assertEqual(check.uncovered, (1,) * N)
        self.assertEqual(check.torus_vectors_checked, 1)
        self.assertFalse(check.is_counterexample)

    def test_plain_matrix_format_matches_both_verifiers(self) -> None:
        rendered = _format_plain_matrix(canonical_identity())
        lines = rendered.splitlines()
        self.assertEqual(len(lines), N)
        self.assertTrue(all(len(line.split()) == N for line in lines))
        self.assertEqual(len([int(token) for token in rendered.split()]), N * N)

    def test_rank_checker_returns_exact_right_nullvector(self) -> None:
        matrix = canonical_rank_seven()
        rank, nullvector = rank_and_nullvector_mod5(matrix)
        self.assertEqual(rank, N - 1)
        self.assertIsNotNone(nullvector)
        assert nullvector is not None
        self.assertNotEqual(nullvector, (0,) * N)
        self.assertEqual(_mat_vec_mod(matrix, nullvector), (0,) * N)


class LearnedCutTests(unittest.TestCase):
    def test_uncovered_vector_cut_eliminates_fixed_identity(self) -> None:
        model = CegisModel()
        model.fix_matrix(canonical_identity())
        self.assertTrue(model.add_cover_cut((1,) * N))
        self.assertEqual(solve_fixed(model), cp_model.INFEASIBLE)

    def test_exact_nullvector_cut_eliminates_singular_matrix(self) -> None:
        matrix = canonical_rank_seven()
        _, nullvector = rank_and_nullvector_mod5(matrix)
        assert nullvector is not None
        model = CegisModel()
        model.fix_matrix(matrix)
        self.assertTrue(model.add_rank_cut(nullvector))
        self.assertEqual(solve_fixed(model), cp_model.INFEASIBLE)

    def test_valid_rank_cut_keeps_fixed_identity(self) -> None:
        model = CegisModel()
        model.fix_matrix(canonical_identity())
        model.add_rank_cut((1,) + (0,) * (N - 1))
        self.assertIn(solve_fixed(model), (cp_model.FEASIBLE, cp_model.OPTIMAL))

    def test_cuts_are_projectively_deduplicated(self) -> None:
        model = CegisModel()
        self.assertTrue(model.add_cover_cut((1,) * N))
        self.assertFalse(model.add_cover_cut((2,) * N))
        unit = (1,) + (0,) * (N - 1)
        scaled_unit = (4,) + (0,) * (N - 1)
        self.assertTrue(model.add_rank_cut(unit))
        self.assertFalse(model.add_rank_cut(scaled_unit))


if __name__ == "__main__":
    unittest.main()
