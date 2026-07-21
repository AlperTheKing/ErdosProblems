"""Exact-pruning variant of the AJT F_5, n=8 CP-SAT CEGIS search.

This module does not alter the production v1 engine.  It adds three necessary
families of constraints:

* 64 deterministic projective torus cover cuts at startup;
* the proved bound that at most four rows have support exactly two, together
  with the degree-four endpoint obstruction for such a row;
* every projective direction in a failed candidate's right kernel, rather
  than only one nullvector.

As in v1, CP-SAT proposes matrices but a scalar exhaustive check is the only
path to a written counterexample certificate.  UNKNOWN and timeout are
inconclusive, and CP-SAT infeasibility is not a proof certificate.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Sequence

from ortools.sat.python import cp_model

from cegis_cpsat import (
    N,
    NONZERO,
    Q,
    CegisModel,
    Matrix,
    SearchResult,
    Vector,
    _emit,
    _mat_vec_mod,
    _positive_float,
    _seed_value,
    _validated_matrix,
    _worker_count,
    _write_certificate,
    normalize_projective,
    scalar_check_matrix,
)


INITIAL_COVER_CUTS = 64


def nullspace_basis_mod5(matrix: Sequence[Sequence[int]]) -> tuple[Vector, ...]:
    """Return an exact basis of the right kernel over F_5."""

    checked = _validated_matrix(matrix)
    reduced = [list(row) for row in checked]
    pivot_columns: list[int] = []
    pivot_row = 0

    for column in range(N):
        selected = next(
            (row for row in range(pivot_row, N) if reduced[row][column] % Q),
            None,
        )
        if selected is None:
            continue
        reduced[pivot_row], reduced[selected] = reduced[selected], reduced[pivot_row]
        inverse = pow(reduced[pivot_row][column] % Q, -1, Q)
        reduced[pivot_row] = [(inverse * value) % Q for value in reduced[pivot_row]]
        for row in range(N):
            if row == pivot_row:
                continue
            factor = reduced[row][column] % Q
            if factor:
                reduced[row] = [
                    (left - factor * right) % Q
                    for left, right in zip(
                        reduced[row], reduced[pivot_row], strict=True
                    )
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == N:
            break

    pivot_set = set(pivot_columns)
    free_columns = [column for column in range(N) if column not in pivot_set]
    basis: list[Vector] = []
    for free_column in free_columns:
        vector = [0] * N
        vector[free_column] = 1
        for row, column in enumerate(pivot_columns):
            vector[column] = (-reduced[row][free_column]) % Q
        exact = tuple(vector)
        if any(_mat_vec_mod(checked, exact)):
            raise AssertionError("internal error: nullspace basis vector is not exact")
        basis.append(exact)
    return tuple(basis)


def projective_kernel_vectors_mod5(
    matrix: Sequence[Sequence[int]],
) -> tuple[Vector, ...]:
    """Enumerate each nonzero right-kernel direction exactly once."""

    checked = _validated_matrix(matrix)
    basis = nullspace_basis_mod5(checked)
    if not basis:
        return ()

    directions: set[Vector] = set()
    for coefficients in itertools.product(range(Q), repeat=len(basis)):
        if not any(coefficients):
            continue
        vector = tuple(
            sum(coefficients[index] * basis[index][column] for index in range(len(basis)))
            % Q
            for column in range(N)
        )
        normalized = normalize_projective(vector)
        if any(_mat_vec_mod(checked, normalized)):
            raise AssertionError("internal error: enumerated vector left the kernel")
        directions.add(normalized)

    expected = (Q ** len(basis) - 1) // (Q - 1)
    if len(directions) != expected:
        raise AssertionError(
            f"projective kernel count {len(directions)} != expected {expected}"
        )
    return tuple(sorted(directions))


class CegisModelV2(CegisModel):
    """V1 model plus proved support-degree constraints."""

    def __init__(self, *, base_structural_pruning: bool = True) -> None:
        super().__init__(structural_pruning=base_structural_pruning)
        self._add_support_two_constraints()

    def _add_support_two_constraints(self) -> None:
        nonzero: list[list[cp_model.IntVar]] = []
        support_two: list[cp_model.IntVar] = []

        for row in range(N):
            indicators: list[cp_model.IntVar] = []
            for column in range(N):
                indicator = self.model.new_bool_var(f"v2_nz_{row}_{column}")
                self.model.add(self.entries[row][column] != 0).only_enforce_if(indicator)
                self.model.add(self.entries[row][column] == 0).only_enforce_if(
                    indicator.Not()
                )
                indicators.append(indicator)
            nonzero.append(indicators)

            is_two = self.model.new_bool_var(f"v2_support_two_{row}")
            support = sum(indicators)
            self.model.add(support == 2).only_enforce_if(is_two)
            self.model.add(support != 2).only_enforce_if(is_two.Not())
            support_two.append(is_two)

        # Exact theorem: a counterexample has at most four support-two rows.
        self.model.add(sum(support_two) <= 4)

        column_degrees: list[cp_model.IntVar] = []
        degree_four: list[cp_model.IntVar] = []
        for column in range(N):
            degree = self.model.new_int_var(0, N, f"v2_col_degree_{column}")
            self.model.add(degree == sum(nonzero[row][column] for row in range(N)))
            column_degrees.append(degree)

            is_four = self.model.new_bool_var(f"v2_degree_four_{column}")
            self.model.add(degree == 4).only_enforce_if(is_four)
            self.model.add(degree != 4).only_enforce_if(is_four.Not())
            degree_four.append(is_four)

        # Exact endpoint obstruction: a support-two row cannot meet two
        # degree-four columns.  The five-term inequality excludes precisely
        # that simultaneous truth assignment for each possible endpoint pair.
        for row in range(N):
            for left in range(N):
                for right in range(left + 1, N):
                    self.model.add(
                        support_two[row]
                        + nonzero[row][left]
                        + nonzero[row][right]
                        + degree_four[left]
                        + degree_four[right]
                        <= 4
                    )


def seed_exact_cuts(model: CegisModelV2) -> None:
    """Install deterministic necessary cuts before the first solve."""

    tails = itertools.islice(
        itertools.product(NONZERO, repeat=N - 1), INITIAL_COVER_CUTS
    )
    for tail in tails:
        model.add_cover_cut((1, *tail))
    for column in range(N):
        unit = tuple(1 if index == column else 0 for index in range(N))
        model.add_rank_cut(unit)


def run_search_v2(
    *,
    seconds: float,
    seed: int,
    workers: int,
    output: Path,
) -> SearchResult:
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    if not 0 <= seed <= 2**31 - 1:
        raise ValueError("seed must be in [0, 2^31-1]")
    if not 1 <= workers <= 64:
        raise ValueError("workers must be in [1, 64]")

    start = time.monotonic()
    deadline = start + seconds
    cegis = CegisModelV2()
    seed_exact_cuts(cegis)

    solver = cp_model.CpSolver()
    solver.parameters.random_seed = seed
    solver.parameters.num_search_workers = workers
    iterations = 0

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return SearchResult(
                status="TIMEOUT_INCONCLUSIVE",
                iterations=iterations,
                cover_cuts=len(cegis.cover_vectors),
                rank_cuts=len(cegis.rank_vectors),
                elapsed_seconds=time.monotonic() - start,
                detail="time budget expired; no negative conclusion",
            )

        solver.parameters.max_time_in_seconds = remaining
        status = solver.solve(cegis.model)
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            iterations += 1
            matrix = cegis.extract_matrix(solver)
            check = scalar_check_matrix(matrix)
            kernel = (
                projective_kernel_vectors_mod5(matrix) if check.rank < N else ()
            )
            _emit(
                "candidate_checked_v2",
                iteration=iterations,
                rank=check.rank,
                torus_vectors_checked=check.torus_vectors_checked,
                uncovered=list(check.uncovered) if check.uncovered else None,
                projective_kernel_size=len(kernel),
            )

            if check.is_counterexample:
                _write_certificate(output, matrix, check)
                return SearchResult(
                    status="VERIFIED_COUNTEREXAMPLE",
                    iterations=iterations,
                    cover_cuts=len(cegis.cover_vectors),
                    rank_cuts=len(cegis.rank_vectors),
                    elapsed_seconds=time.monotonic() - start,
                    output=str(output),
                )

            learned = False
            if check.uncovered is not None:
                if not cegis.add_cover_cut(check.uncovered):
                    raise AssertionError(
                        "candidate violated an existing normalized cover cut"
                    )
                learned = True
            for vector in kernel:
                learned = cegis.add_rank_cut(vector) or learned
            if check.rank < N and not kernel:
                raise AssertionError("singular candidate had an empty right kernel")
            if not learned:
                raise AssertionError("failed candidate supplied no exact CEGIS cut")
            continue

        if status == cp_model.INFEASIBLE:
            return SearchResult(
                status="CP_SAT_INFEASIBLE_NO_CERTIFICATE",
                iterations=iterations,
                cover_cuts=len(cegis.cover_vectors),
                rank_cuts=len(cegis.rank_vectors),
                elapsed_seconds=time.monotonic() - start,
                detail="CP-SAT produced no independently checkable closure proof",
            )
        if status == cp_model.MODEL_INVALID:
            return SearchResult(
                status="MODEL_INVALID",
                iterations=iterations,
                cover_cuts=len(cegis.cover_vectors),
                rank_cuts=len(cegis.rank_vectors),
                elapsed_seconds=time.monotonic() - start,
                detail=solver.solution_info(),
            )

        timed_out = time.monotonic() >= deadline - 1e-6
        return SearchResult(
            status="TIMEOUT_INCONCLUSIVE" if timed_out else "UNKNOWN_INCONCLUSIVE",
            iterations=iterations,
            cover_cuts=len(cegis.cover_vectors),
            rank_cuts=len(cegis.rank_vectors),
            elapsed_seconds=time.monotonic() - start,
            detail=f"CP-SAT status {solver.status_name(status)}; no negative conclusion",
        )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=_positive_float, default=60.0)
    parser.add_argument("--seed", type=_seed_value, default=0)
    parser.add_argument("--workers", type=_worker_count, default=1)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_search_v2(
        seconds=args.seconds,
        seed=args.seed,
        workers=args.workers,
        output=args.out,
    )
    print(json.dumps(asdict(result), sort_keys=True), flush=True)
    if result.status == "VERIFIED_COUNTEREXAMPLE":
        return 0
    if result.status in {"TIMEOUT_INCONCLUSIVE", "UNKNOWN_INCONCLUSIVE"}:
        return 2
    if result.status == "CP_SAT_INFEASIBLE_NO_CERTIFICATE":
        return 3
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
