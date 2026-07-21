"""Degree-five-column, degree-four-row AJT F_5, n=8 CEGIS engine.

V5 retains V3's batches of 32 exact uncovered projective vectors and V2's
full-kernel learning. It imposes the proved necessary conditions that every
column has at least five and every row at least four nonzero entries.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model

from cegis_cpsat import (
    N,
    SearchResult,
    _emit,
    _positive_float,
    _seed_value,
    _worker_count,
    _write_certificate,
)
from cegis_cpsat_v2 import (
    CegisModelV2,
    projective_kernel_vectors_mod5,
    seed_exact_cuts,
)
from cegis_cpsat_v3 import UNCOVERED_BATCH, scalar_check_matrix_batched


class CegisModelV5(CegisModelV2):
    """V2 structural model plus exact column-five and row-four bounds."""

    def __init__(self, *, base_structural_pruning: bool = True) -> None:
        super().__init__(base_structural_pruning=base_structural_pruning)
        self._add_degree_bounds()

    def _add_degree_bounds(self) -> None:
        by_row: list[list[cp_model.IntVar]] = [[] for _ in range(N)]
        for column in range(N):
            nonzero: list[cp_model.IntVar] = []
            for row in range(N):
                indicator = self.model.new_bool_var(f"v5_nz_{row}_{column}")
                self.model.add(self.entries[row][column] != 0).only_enforce_if(
                    indicator
                )
                self.model.add(self.entries[row][column] == 0).only_enforce_if(
                    indicator.Not()
                )
                nonzero.append(indicator)
                by_row[row].append(indicator)
            self.model.add(sum(nonzero) >= 5)
        for indicators in by_row:
            self.model.add(sum(indicators) >= 4)


def run_search_v5(
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
    cegis = CegisModelV5()
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
                "candidate_checked_v5",
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
    result = run_search_v5(
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
