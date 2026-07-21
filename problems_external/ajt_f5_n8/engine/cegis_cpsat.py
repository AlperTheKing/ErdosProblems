"""CP-SAT CEGIS search for an AJT counterexample over F_5 in dimension 8.

The solver is used only to propose matrices.  Every proposal is checked by
plain scalar arithmetic over F_5 before it can be written as a certificate.
Two kinds of necessary constraints are learned from failed proposals:

* an uncovered torus vector x adds ``some row r has r.x = 0``;
* a right-nullvector y adds ``some row r has r.y != 0``.

Consequently, FEASIBLE is never accepted without exhaustive verification, and
UNKNOWN (including a time limit) is always reported as inconclusive.  CP-SAT
does not emit a proof certificate here, so INFEASIBLE is not a finite-closure
claim either.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from ortools.sat.python import cp_model


Q = 5
N = 8
TORUS_SIZE = (Q - 1) ** N
NONZERO = tuple(range(1, Q))

Matrix = tuple[tuple[int, ...], ...]
Vector = tuple[int, ...]


def _dot_mod(row: Sequence[int], vector: Sequence[int]) -> int:
    return sum(a * b for a, b in zip(row, vector, strict=True)) % Q


def _mat_vec_mod(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> Vector:
    return tuple(_dot_mod(row, vector) for row in matrix)


def normalize_projective(vector: Sequence[int]) -> Vector:
    """Return the unique scalar representative whose first nonzero entry is 1."""

    if len(vector) != N:
        raise ValueError(f"expected a vector of length {N}, got {len(vector)}")
    reduced = tuple(int(value) % Q for value in vector)
    try:
        first = next(value for value in reduced if value)
    except StopIteration as exc:
        raise ValueError("the zero vector has no projective normalization") from exc
    inverse = pow(first, -1, Q)
    return tuple((inverse * value) % Q for value in reduced)


def _validated_matrix(matrix: Sequence[Sequence[int]]) -> Matrix:
    if len(matrix) != N:
        raise ValueError(f"expected {N} rows, got {len(matrix)}")
    rows: list[tuple[int, ...]] = []
    for row_number, row in enumerate(matrix):
        if len(row) != N:
            raise ValueError(
                f"row {row_number} has length {len(row)}; expected {N}"
            )
        checked: list[int] = []
        for column_number, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(
                    f"matrix[{row_number}][{column_number}] is not an integer"
                )
            if not 0 <= value < Q:
                raise ValueError(
                    f"matrix[{row_number}][{column_number}]={value} is outside F_5"
                )
            checked.append(value)
        rows.append(tuple(checked))
    return tuple(rows)


def rank_and_nullvector_mod5(matrix: Sequence[Sequence[int]]) -> tuple[int, Vector | None]:
    """Compute exact rank and, when singular, a nonzero right-nullvector."""

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

    rank = len(pivot_columns)
    if rank == N:
        return rank, None

    pivot_set = set(pivot_columns)
    free_column = next(column for column in range(N) if column not in pivot_set)
    nullvector = [0] * N
    nullvector[free_column] = 1
    for row, column in enumerate(pivot_columns):
        nullvector[column] = (-reduced[row][free_column]) % Q

    normalized = normalize_projective(nullvector)
    if any(_mat_vec_mod(checked, normalized)):
        raise AssertionError("internal error: computed vector is not in the right kernel")
    return rank, normalized


@dataclass(frozen=True)
class ScalarCheck:
    rank: int
    nullvector: Vector | None
    uncovered: Vector | None
    torus_vectors_checked: int

    @property
    def is_counterexample(self) -> bool:
        return self.rank == N and self.uncovered is None


def scalar_check_matrix(matrix: Sequence[Sequence[int]]) -> ScalarCheck:
    """Independently check rank and exhaustively scan the 65,536 torus vectors."""

    checked = _validated_matrix(matrix)
    rank, nullvector = rank_and_nullvector_mod5(checked)
    uncovered: Vector | None = None
    vectors_checked = 0

    for vector in itertools.product(NONZERO, repeat=N):
        vectors_checked += 1
        if all(_dot_mod(row, vector) != 0 for row in checked):
            # Zero coordinates of A*x are invariant under nonzero scalar
            # multiplication.  Since vector[0] is nonzero on the torus, this
            # canonical representative has first coordinate 1.
            uncovered = normalize_projective(vector)
            break

    return ScalarCheck(
        rank=rank,
        nullvector=nullvector,
        uncovered=uncovered,
        torus_vectors_checked=vectors_checked,
    )


class CegisModel:
    """Incremental CP-SAT model containing only necessary AJT constraints."""

    def __init__(self, *, structural_pruning: bool = False) -> None:
        self.model = cp_model.CpModel()
        self.entries = [
            [self.model.new_int_var(0, Q - 1, f"a_{row}_{column}") for column in range(N)]
            for row in range(N)
        ]
        self._zero_cache: dict[Vector, tuple[cp_model.IntVar, ...]] = {}
        self.cover_vectors: set[Vector] = set()
        self.rank_vectors: set[Vector] = set()
        self._add_safe_row_symmetry_breaking()
        if structural_pruning:
            self._add_proved_support_constraints()

    def _add_proved_support_constraints(self) -> None:
        """Add necessary support conditions derived from AJT below dimension 8."""

        nonzero: list[list[cp_model.IntVar]] = []
        for row in range(N):
            indicators: list[cp_model.IntVar] = []
            for column in range(N):
                indicator = self.model.new_bool_var(f"nz_{row}_{column}")
                self.model.add(self.entries[row][column] != 0).only_enforce_if(indicator)
                self.model.add(self.entries[row][column] == 0).only_enforce_if(indicator.Not())
                indicators.append(indicator)
            nonzero.append(indicators)
            self.model.add(sum(indicators) >= 2)

        for column in range(N):
            self.model.add(sum(nonzero[row][column] for row in range(N)) >= 4)

        for left in range(N):
            for right in range(left + 1, N):
                neighbors: list[cp_model.IntVar] = []
                for row in range(N):
                    neighbor = self.model.new_bool_var(f"pair_nz_{left}_{right}_{row}")
                    self.model.add_max_equality(
                        neighbor, [nonzero[row][left], nonzero[row][right]]
                    )
                    neighbors.append(neighbor)
                self.model.add(sum(neighbors) >= 5)


    def _add_safe_row_symmetry_breaking(self) -> None:
        """Normalize projective rows and sort them using allowed symmetries."""

        row_codes: list[cp_model.IntVar] = []
        weights = [Q ** (N - 1 - column) for column in range(N)]
        for row in range(N):
            leaders = [
                self.model.new_bool_var(f"lead_{row}_{column}")
                for column in range(N)
            ]
            self.model.add_exactly_one(leaders)
            for column, leader in enumerate(leaders):
                self.model.add(self.entries[row][column] == 1).only_enforce_if(leader)
                for earlier in range(column):
                    self.model.add(self.entries[row][earlier] == 0).only_enforce_if(
                        leader
                    )

            code = self.model.new_int_var(1, Q**N - 1, f"row_code_{row}")
            self.model.add(
                code
                == sum(
                    weights[column] * self.entries[row][column]
                    for column in range(N)
                )
            )
            row_codes.append(code)

        for row in range(N - 1):
            self.model.add(row_codes[row] < row_codes[row + 1])

    def fix_matrix(self, matrix: Sequence[Sequence[int]]) -> None:
        """Fix A to a concrete matrix.  Intended for focused model tests."""

        checked = _validated_matrix(matrix)
        for row in range(N):
            for column in range(N):
                self.model.add(self.entries[row][column] == checked[row][column])

    def _zero_indicators(self, vector: Sequence[int]) -> tuple[cp_model.IntVar, ...]:
        normalized = normalize_projective(vector)
        cached = self._zero_cache.get(normalized)
        if cached is not None:
            return cached

        vector_code = sum(
            normalized[column] * Q ** (N - 1 - column) for column in range(N)
        )
        zero_indicators: list[cp_model.IntVar] = []
        for row in range(N):
            quotient = self.model.new_int_var(0, 25, f"q_{vector_code}_{row}")
            remainder = self.model.new_int_var(0, Q - 1, f"rem_{vector_code}_{row}")
            self.model.add(
                sum(
                    normalized[column] * self.entries[row][column]
                    for column in range(N)
                )
                == Q * quotient + remainder
            )
            is_zero = self.model.new_bool_var(f"zero_{vector_code}_{row}")
            self.model.add(remainder == 0).only_enforce_if(is_zero)
            self.model.add(remainder != 0).only_enforce_if(is_zero.Not())
            zero_indicators.append(is_zero)

        result = tuple(zero_indicators)
        self._zero_cache[normalized] = result
        return result

    def add_cover_cut(self, vector: Sequence[int]) -> bool:
        """Require at least one zero coordinate in A*vector."""

        normalized = normalize_projective(vector)
        if any(value == 0 for value in normalized):
            raise ValueError("a cover cut must come from the nowhere-zero torus")
        if normalized in self.cover_vectors:
            return False
        self.model.add_bool_or(self._zero_indicators(normalized))
        self.cover_vectors.add(normalized)
        return True

    def add_rank_cut(self, vector: Sequence[int]) -> bool:
        """Require A*vector != 0 for a nonzero projective vector."""

        normalized = normalize_projective(vector)
        if normalized in self.rank_vectors:
            return False
        self.model.add_bool_or(
            [indicator.Not() for indicator in self._zero_indicators(normalized)]
        )
        self.rank_vectors.add(normalized)
        return True

    def extract_matrix(self, solver: cp_model.CpSolver) -> Matrix:
        return tuple(
            tuple(solver.value(self.entries[row][column]) for column in range(N))
            for row in range(N)
        )


@dataclass(frozen=True)
class SearchResult:
    status: str
    iterations: int
    cover_cuts: int
    rank_cuts: int
    elapsed_seconds: float
    output: str | None = None
    detail: str | None = None


def _emit(event: str, **fields: object) -> None:
    print(json.dumps({"event": event, **fields}, sort_keys=True), flush=True)


def _format_plain_matrix(matrix: Matrix) -> str:
    """Return the common verifier format: eight ASCII rows of eight residues."""

    if len(matrix) != N or any(len(row) != N for row in matrix):
        raise ValueError("matrix must be 8 by 8")
    return "".join(" ".join(str(value % Q) for value in row) + "\n" for row in matrix)


def _write_certificate(
    output: Path,
    matrix: Matrix,
    check: ScalarCheck,
) -> None:
    if not check.is_counterexample or check.torus_vectors_checked != TORUS_SIZE:
        raise ValueError("refusing to write a matrix that did not pass exhaustive checking")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(_format_plain_matrix(matrix), encoding="ascii")
    os.replace(temporary, output)


def run_search(
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
    cegis = CegisModel(structural_pruning=True)

    # Small deterministic seed set.  These are necessary constraints, not
    # assumptions: a nonsingular matrix has no zero column, and it must cover
    # the all-ones torus point.
    cegis.add_cover_cut((1,) * N)
    for column in range(N):
        unit = tuple(1 if index == column else 0 for index in range(N))
        cegis.add_rank_cut(unit)

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
            _emit(
                "candidate_checked",
                iteration=iterations,
                rank=check.rank,
                torus_vectors_checked=check.torus_vectors_checked,
                uncovered=list(check.uncovered) if check.uncovered else None,
                nullvector=list(check.nullvector) if check.nullvector else None,
            )

            if check.is_counterexample:
                _write_certificate(
                    output,
                    matrix,
                    check,
                )
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
                added = cegis.add_cover_cut(check.uncovered)
                if not added:
                    raise AssertionError(
                        "solver candidate violated an existing normalized cover cut"
                    )
                learned = True
            if check.nullvector is not None:
                added = cegis.add_rank_cut(check.nullvector)
                if not added:
                    raise AssertionError(
                        "solver candidate violated an existing normalized rank cut"
                    )
                learned = True
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

        # UNKNOWN commonly means that the current per-solve budget expired.
        # In all cases it is inconclusive and is never relabelled as UNSAT.
        timed_out = time.monotonic() >= deadline - 1e-6
        return SearchResult(
            status="TIMEOUT_INCONCLUSIVE" if timed_out else "UNKNOWN_INCONCLUSIVE",
            iterations=iterations,
            cover_cuts=len(cegis.cover_vectors),
            rank_cuts=len(cegis.rank_vectors),
            elapsed_seconds=time.monotonic() - start,
            detail=f"CP-SAT status {solver.status_name(status)}; no negative conclusion",
        )


def _positive_float(text: str) -> float:
    value = float(text)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return value


def _seed_value(text: str) -> int:
    value = int(text)
    if not 0 <= value <= 2**31 - 1:
        raise argparse.ArgumentTypeError("must be in [0, 2^31-1]")
    return value


def _worker_count(text: str) -> int:
    value = int(text)
    if not 1 <= value <= 64:
        raise argparse.ArgumentTypeError("must be in [1, 64]")
    return value


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=_positive_float, default=60.0)
    parser.add_argument("--seed", type=_seed_value, default=0)
    parser.add_argument("--workers", type=_worker_count, default=1)
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="write a certificate here only after exhaustive scalar verification",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_search(
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
