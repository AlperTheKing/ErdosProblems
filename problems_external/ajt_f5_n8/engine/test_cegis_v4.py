"""Focused tests for the exact column-degree pruning in CEGIS v4."""

from __future__ import annotations

import unittest

from ortools.sat.python import cp_model

from cegis_cpsat import N
from cegis_cpsat_v4 import CegisModelV4


def matrix_with_column_zero_count(zero_count: int) -> tuple[tuple[int, ...], ...]:
    """Return sorted normalized dense rows with zeros only in column zero."""

    if zero_count not in (3, 4):
        raise ValueError("test fixture supports three or four zeros")
    rows: list[tuple[int, ...]] = []
    for tail in range(1, zero_count + 1):
        rows.append((0, 1, 1, 1, 1, 1, 1, tail))

    pairs = ((1, 1), (1, 2), (1, 3), (1, 4), (2, 1))
    for penultimate, last in pairs[: N - zero_count]:
        rows.append((1, 1, 1, 1, 1, 1, penultimate, last))

    def code(row: tuple[int, ...]) -> int:
        return sum(value * 5 ** (N - 1 - index) for index, value in enumerate(row))

    return tuple(sorted(rows, key=code))


def solve_fixed(matrix: tuple[tuple[int, ...], ...]) -> int:
    model = CegisModelV4(base_structural_pruning=False)
    model.fix_matrix(matrix)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 2.0
    return solver.solve(model.model)


def matrix_with_sparse_first_row(support: int) -> tuple[tuple[int, ...], ...]:
    if support not in (2, 3):
        raise ValueError("test fixture supports row support two or three")
    sparse = (0,) * (N - support) + (1,) * support
    pairs = ((1, 1), (1, 2), (1, 3), (1, 4), (2, 1), (2, 2), (2, 3))
    rows = [sparse]
    rows.extend((1, 1, 1, 1, 1, 1, penultimate, last) for penultimate, last in pairs)

    def code(row: tuple[int, ...]) -> int:
        return sum(value * 5 ** (N - 1 - index) for index, value in enumerate(row))

    return tuple(sorted(rows, key=code))


class ColumnDegreeTests(unittest.TestCase):
    def test_degree_four_column_is_rejected(self) -> None:
        matrix = matrix_with_column_zero_count(4)
        self.assertEqual(sum(row[0] != 0 for row in matrix), 4)
        self.assertEqual(solve_fixed(matrix), cp_model.INFEASIBLE)

    def test_degree_five_column_is_retained(self) -> None:
        matrix = matrix_with_column_zero_count(3)
        self.assertEqual(sum(row[0] != 0 for row in matrix), 5)
        self.assertIn(solve_fixed(matrix), (cp_model.FEASIBLE, cp_model.OPTIMAL))

    def test_all_column_degrees_are_at_least_five_in_free_model(self) -> None:
        model = CegisModelV4(base_structural_pruning=False)
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        solver.parameters.max_time_in_seconds = 2.0
        self.assertIn(solver.solve(model.model), (cp_model.FEASIBLE, cp_model.OPTIMAL))
        matrix = model.extract_matrix(solver)
        for column in range(N):
            self.assertGreaterEqual(sum(row[column] != 0 for row in matrix), 5)

    def test_support_two_row_is_rejected(self) -> None:
        matrix = matrix_with_sparse_first_row(2)
        self.assertEqual(min(sum(value != 0 for value in row) for row in matrix), 2)
        self.assertEqual(solve_fixed(matrix), cp_model.INFEASIBLE)

    def test_support_three_row_is_retained(self) -> None:
        matrix = matrix_with_sparse_first_row(3)
        self.assertEqual(min(sum(value != 0 for value in row) for row in matrix), 3)
        self.assertIn(solve_fixed(matrix), (cp_model.FEASIBLE, cp_model.OPTIMAL))


if __name__ == "__main__":
    unittest.main()
