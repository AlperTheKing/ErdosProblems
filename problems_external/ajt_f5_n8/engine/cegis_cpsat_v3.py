"""Batched-cover variant of the exact AJT F_5, n=8 CP-SAT CEGIS search.

V2 learns all projective directions in a singular candidate's kernel, but its
scalar verifier stops at the first uncovered torus point.  V3 collects up to
32 distinct projective uncovered points in the same scalar pass and adds every
corresponding necessary cover cut before re-solving.  A matrix is still
accepted only after the scalar loop exhausts all 65,536 torus vectors.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from ortools.sat.python import cp_model

from cegis_cpsat import (
    N,
    NONZERO,
    TORUS_SIZE,
    Matrix,
    SearchResult,
    Vector,
    _dot_mod,
    _emit,
    _positive_float,
    _seed_value,
    _validated_matrix,
    _worker_count,
    _write_certificate,
    normalize_projective,
    rank_and_nullvector_mod5,
)
from cegis_cpsat_v2 import (
    CegisModelV2,
    projective_kernel_vectors_mod5,
    seed_exact_cuts,
)


UNCOVERED_BATCH = 32


@dataclass(frozen=True)
class BatchedScalarCheck:
    rank: int
    uncovered: tuple[Vector, ...]
    torus_vectors_checked: int

    @property
    def is_counterexample(self) -> bool:
        return (
            self.rank == N
            and not self.uncovered
            and self.torus_vectors_checked == TORUS_SIZE
        )


def scalar_check_matrix_batched(
    matrix: Sequence[Sequence[int]], *, limit: int = UNCOVERED_BATCH
) -> BatchedScalarCheck:
    """Collect up to ``limit`` exact projective coverage violations."""

    if limit <= 0:
        raise ValueError("uncovered batch limit must be positive")
    checked = _validated_matrix(matrix)
    rank, _ = rank_and_nullvector_mod5(checked)
    uncovered: list[Vector] = []
    seen: set[Vector] = set()
    vectors_checked = 0

    for vector in itertools.product(NONZERO, repeat=N):
        vectors_checked += 1
        if all(_dot_mod(row, vector) != 0 for row in checked):
            normalized = normalize_projective(vector)
            if normalized not in seen:
                seen.add(normalized)
                uncovered.append(normalized)
                if len(uncovered) == limit:
                    break

    return BatchedScalarCheck(
        rank=rank,
        uncovered=tuple(uncovered),
        torus_vectors_checked=vectors_checked,
    )


def run_search_v3(
    *,
    seconds: float,
    seed: int,
    workers: int,
    output: Path,
    cover_batch: int = UNCOVERED_BATCH,
) -> SearchResult:
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    if not 0 <= seed <= 2**31 - 1:
        raise ValueError("seed must be in [0, 2^31-1]")
    if not 1 <= workers <= 64:
        raise ValueError("workers must be in [1, 64]")
    if cover_batch <= 0:
        raise ValueError("cover_batch must be positive")

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
            check = scalar_check_matrix_batched(matrix, limit=cover_batch)
            kernel = (
                projective_kernel_vectors_mod5(matrix) if check.rank < N else ()
            )
            _emit(
                "candidate_checked_v3",
                iteration=iterations,
                rank=check.rank,
                torus_vectors_checked=check.torus_vectors_checked,
                uncovered_count=len(check.uncovered),
                first_uncovered=list(check.uncovered[0]) if check.uncovered else None,
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
            for vector in check.uncovered:
                learned = cegis.add_cover_cut(vector) or learned
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
    result = run_search_v3(
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
