#!/usr/bin/env python3
"""Exact fixed-exception CP-SAT analysis for Erdos Problem #864."""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import os
import sys
import time
import uuid
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, TextIO

import ortools
from ortools.sat.python import cp_model


MODES = ("existence", "min-multiplicity", "max-unpaired")
MAX_PROCESSES = 64
MAX_PROCESS_POOL_WORKERS = 61 if os.name == "nt" else MAX_PROCESSES
MAX_RANDOM_SEED = 2**31 - 1
FEASIBLE_STATUSES = {cp_model.FEASIBLE, cp_model.OPTIMAL}


@dataclass(frozen=True)
class BranchSpec:
    kind: str
    sigma: int | None = None

    def __post_init__(self) -> None:
        if self.kind == "ordinary":
            if self.sigma is not None:
                raise ValueError("ordinary branch cannot have sigma")
        elif self.kind == "exceptional":
            if self.sigma is None:
                raise ValueError("exceptional branch requires sigma")
        else:
            raise ValueError(f"unknown branch kind: {self.kind}")

    @property
    def branch_id(self) -> str:
        return "ordinary" if self.sigma is None else f"sigma-{self.sigma}"

    def as_json(self) -> dict[str, Any]:
        return {"id": self.branch_id, "kind": self.kind, "sigma": self.sigma}


@dataclass(frozen=True)
class SolveRequest:
    run_id: str
    N: int
    k: int
    mode: str
    branch: BranchSpec
    time_limit_seconds: float
    random_seed: int


def ambient_pairs_for_sum(N: int, sigma: int) -> list[tuple[int, int]]:
    """Return all a <= b in [1,N] with a+b=sigma."""
    lower = max(1, sigma - N)
    upper = min(N, sigma // 2)
    return [(a, sigma - a) for a in range(lower, upper + 1)]


def all_branches(N: int) -> list[BranchSpec]:
    """Partition admissible sets into Sidon and possible fixed exceptions."""
    branches = [BranchSpec("ordinary")]
    branches.extend(
        BranchSpec("exceptional", sigma)
        for sigma in range(2, 2 * N + 1)
        if len(ambient_pairs_for_sum(N, sigma)) >= 2
    )
    return branches


def unordered_sum_representations(
    values: list[int] | tuple[int, ...],
) -> dict[int, list[tuple[int, int]]]:
    """Compute literal unordered representations, including diagonals."""
    ordered = sorted(values)
    representations: dict[int, list[tuple[int, int]]] = {}
    for index, left in enumerate(ordered):
        for right in ordered[index:]:
            representations.setdefault(left + right, []).append((left, right))
    return dict(sorted(representations.items()))


def analyze_candidate(N: int, k: int, values: list[int]) -> dict[str, Any]:
    """Recompute every statistic used to accept a solver candidate."""
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise ValueError("candidate elements must be integers")
    ordered = sorted(values)
    if len(ordered) != k:
        raise ValueError(f"candidate has size {len(ordered)}, expected {k}")
    if len(set(ordered)) != len(ordered):
        raise ValueError("candidate has duplicate elements")
    if any(value < 1 or value > N for value in ordered):
        raise ValueError("candidate has an element outside [1,N]")
    if not ordered or ordered[0] != 1:
        raise ValueError("candidate does not satisfy min(A)=1")

    representations = unordered_sum_representations(ordered)
    repeated = [
        (sum_value, pairs)
        for sum_value, pairs in representations.items()
        if len(pairs) >= 2
    ]
    if len(repeated) == 1:
        exceptional_sum = repeated[0][0]
        exceptional_pairs = repeated[0][1]
    else:
        exceptional_sum = None
        exceptional_pairs = []

    paired_elements = sorted({value for pair in exceptional_pairs for value in pair})
    paired_element_set = set(paired_elements)
    unpaired_elements = [value for value in ordered if value not in paired_element_set]
    exceptional_multiplicity = len(exceptional_pairs)
    diagonal_at_exception = next(
        (left for left, right in exceptional_pairs if left == right),
        None,
    )

    return {
        "A": ordered,
        "size": len(ordered),
        "admissible": len(repeated) <= 1,
        "exceptional_sum": exceptional_sum,
        "exceptional_multiplicity": exceptional_multiplicity,
        "repeated_sums": [
            {
                "sum": sum_value,
                "multiplicity": len(pairs),
                "representations": [list(pair) for pair in pairs],
            }
            for sum_value, pairs in repeated
        ],
        "paired_elements": paired_elements,
        "paired_element_count": len(paired_elements),
        "unpaired_elements": unpaired_elements,
        "unpaired_element_count": len(unpaired_elements),
        "exception_diagonal_element": diagonal_at_exception,
        "distinct_sum_count": len(representations),
        "total_unordered_pair_count": k * (k + 1) // 2,
    }


def objective_value_from_analysis(mode: str, analysis: dict[str, Any]) -> int | None:
    if mode == "existence":
        return None
    if mode == "min-multiplicity":
        return int(analysis["exceptional_multiplicity"])
    if mode == "max-unpaired":
        return int(analysis["unpaired_element_count"])
    raise ValueError(f"unknown mode: {mode}")


def self_check_candidate(
    N: int,
    k: int,
    branch: BranchSpec,
    mode: str,
    values: list[int],
    claimed_objective: int | None,
) -> dict[str, Any]:
    """Independently check domain, branch membership, and objective value."""
    analysis = analyze_candidate(N, k, values)
    repeated = analysis["repeated_sums"]

    if branch.kind == "ordinary":
        if repeated:
            raise ValueError("ordinary branch candidate has a repeated sum")
    else:
        if len(repeated) != 1:
            raise ValueError("exceptional branch candidate does not have one repeated sum")
        if repeated[0]["sum"] != branch.sigma:
            raise ValueError(
                f"candidate repeats sum {repeated[0]['sum']}, expected {branch.sigma}"
            )
        if repeated[0]["multiplicity"] < 2:
            raise ValueError("exceptional sum has multiplicity below two")

        diagonal = 1 if analysis["exception_diagonal_element"] is not None else 0
        expected_unpaired = k - 2 * analysis["exceptional_multiplicity"] + diagonal
        if analysis["unpaired_element_count"] != expected_unpaired:
            raise ValueError("exceptional-pair element count is inconsistent")

    actual_objective = objective_value_from_analysis(mode, analysis)
    if actual_objective != claimed_objective:
        raise ValueError(
            f"objective mismatch: solver={claimed_objective}, recomputed={actual_objective}"
        )
    analysis["candidate_self_checked"] = True
    return analysis


def _sum_expression(terms: list[cp_model.IntVar]) -> cp_model.LinearExpr:
    return cp_model.LinearExpr.sum(terms)


def build_model(
    N: int,
    k: int,
    branch: BranchSpec,
    mode: str,
) -> tuple[cp_model.CpModel, list[cp_model.IntVar | None], cp_model.IntVar | None]:
    """Build one exact Sidon or fixed-exception model."""
    model = cp_model.CpModel()
    x: list[cp_model.IntVar | None] = [None]
    x.extend(model.NewBoolVar(f"x_{value}") for value in range(1, N + 1))
    selected = [x[value] for value in range(1, N + 1)]
    model.Add(x[1] == 1)
    model.Add(_sum_expression(selected) == k)

    by_sum: dict[int, list[cp_model.IntVar]] = {
        sum_value: [] for sum_value in range(2, 2 * N + 1)
    }
    for left in range(1, N + 1):
        for right in range(left, N + 1):
            if left == right:
                pair_selected = x[left]
            else:
                pair_selected = model.NewBoolVar(f"pair_{left}_{right}")
                model.Add(pair_selected <= x[left])
                model.Add(pair_selected <= x[right])
                model.Add(pair_selected >= x[left] + x[right] - 1)
            by_sum[left + right].append(pair_selected)

    exceptional_count: cp_model.LinearExpr | None = None
    for sum_value, terms in by_sum.items():
        representation_count = _sum_expression(terms)
        if branch.kind == "exceptional" and sum_value == branch.sigma:
            model.Add(representation_count >= 2)
            exceptional_count = representation_count
        else:
            model.Add(representation_count <= 1)

    if branch.kind == "exceptional" and exceptional_count is None:
        raise AssertionError("fixed exceptional sum is outside the modeled sum domain")

    objective_var: cp_model.IntVar | None = None
    if mode == "min-multiplicity":
        upper = 0 if branch.kind == "ordinary" else len(by_sum[branch.sigma])
        objective_var = model.NewIntVar(0, upper, "exceptional_multiplicity")
        if branch.kind == "ordinary":
            model.Add(objective_var == 0)
        else:
            model.Add(objective_var == exceptional_count)
        model.Minimize(objective_var)
    elif mode == "max-unpaired":
        objective_var = model.NewIntVar(0, k, "unpaired_element_count")
        if branch.kind == "ordinary":
            model.Add(objective_var == k)
        else:
            diagonal = x[branch.sigma // 2] if branch.sigma % 2 == 0 else 0
            model.Add(objective_var == k - 2 * exceptional_count + diagonal)
        model.Maximize(objective_var)
    elif mode != "existence":
        raise ValueError(f"unknown mode: {mode}")

    validation_error = model.Validate()
    if validation_error:
        raise ValueError(f"invalid CP-SAT model: {validation_error}")
    return model, x, objective_var


def universal_objective_bound(k: int, mode: str, branch: BranchSpec) -> int | None:
    """Return a solver-independent lower/upper bound for one branch."""
    if mode == "existence":
        return None
    if mode == "min-multiplicity":
        return 0 if branch.kind == "ordinary" else 2
    if mode == "max-unpaired":
        if branch.kind == "ordinary":
            return k
        minimum_paired = 3 if branch.sigma % 2 == 0 else 4
        return max(0, k - minimum_paired)
    raise ValueError(f"unknown mode: {mode}")


def _branch_seed(base_seed: int, branch: BranchSpec) -> int:
    offset = 0 if branch.sigma is None else 1_000_003 * branch.sigma + 864
    return (base_seed + offset) % (MAX_RANDOM_SEED + 1)


def _base_branch_record(request: SolveRequest) -> dict[str, Any]:
    return {
        "record_type": "branch",
        "run_id": request.run_id,
        "N": request.N,
        "k": request.k,
        "mode": request.mode,
        "branch": request.branch.as_json(),
        "solver_threads": 1,
        "time_limit_seconds": request.time_limit_seconds,
        "random_seed": _branch_seed(request.random_seed, request.branch),
    }


def _error_branch_record(request: SolveRequest, error: BaseException) -> dict[str, Any]:
    record = _base_branch_record(request)
    record.update(
        {
            "status": "ERROR",
            "proof_complete": False,
            "error_type": type(error).__name__,
            "error": str(error),
            "objective_bound": universal_objective_bound(
                request.k, request.mode, request.branch
            ),
            "objective_bound_source": "combinatorial fallback",
        }
    )
    return record


def solve_branch(request: SolveRequest) -> dict[str, Any]:
    """Solve one branch in one process with exactly one CP-SAT search worker."""
    started = time.perf_counter()
    try:
        model, x, objective_var = build_model(
            request.N, request.k, request.branch, request.mode
        )
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = _branch_seed(request.random_seed, request.branch)
        solver.parameters.log_search_progress = False
        if request.time_limit_seconds > 0:
            solver.parameters.max_time_in_seconds = request.time_limit_seconds

        status_code = solver.Solve(model)
        status = solver.StatusName(status_code).upper()
        elapsed = time.perf_counter() - started
        response = solver.ResponseProto()
        record = _base_branch_record(request)
        record.update(
            {
                "status": status,
                "proof_complete": (
                    status_code in (cp_model.INFEASIBLE, cp_model.OPTIMAL)
                    or (
                        request.mode == "existence"
                        and status_code == cp_model.FEASIBLE
                    )
                ),
                "wall_seconds": elapsed,
                "conflicts": solver.NumConflicts(),
                "search_branches": solver.NumBranches(),
                "deterministic_time": response.deterministic_time,
            }
        )

        if request.mode != "existence":
            # Acceptance uses only exact integer quantities. In particular,
            # BestObjectiveBound() is deliberately not consulted: OR-Tools
            # exposes it as a float even for this integral model.
            record["objective_bound"] = universal_objective_bound(
                request.k, request.mode, request.branch
            )
            record["objective_bound_source"] = "combinatorial fallback"

        if status_code in FEASIBLE_STATUSES:
            values = [
                value
                for value in range(1, request.N + 1)
                if solver.Value(x[value])
            ]
            claimed_objective = (
                None if objective_var is None else int(solver.Value(objective_var))
            )
            analysis = self_check_candidate(
                request.N,
                request.k,
                request.branch,
                request.mode,
                values,
                claimed_objective,
            )
            record.update(analysis)
            record["objective_value"] = claimed_objective
            if status_code == cp_model.OPTIMAL and request.mode != "existence":
                record["objective_bound"] = claimed_objective
                record["objective_bound_source"] = "CP-SAT integer optimum"

        return record
    except BaseException as error:
        record = _error_branch_record(request, error)
        record["wall_seconds"] = time.perf_counter() - started
        return record


def _branch_sort_key(record: dict[str, Any]) -> tuple[int, int]:
    sigma = record["branch"]["sigma"]
    return (0, 0) if sigma is None else (1, int(sigma))


def _winner(records: list[dict[str, Any]], mode: str) -> dict[str, Any] | None:
    candidates = [record for record in records if record.get("candidate_self_checked")]
    if not candidates:
        return None
    if mode == "existence":
        return min(candidates, key=lambda record: (_branch_sort_key(record), record["A"]))
    if mode == "min-multiplicity":
        return min(
            candidates,
            key=lambda record: (
                record["objective_value"],
                _branch_sort_key(record),
                record["A"],
            ),
        )
    return min(
        candidates,
        key=lambda record: (
            -record["objective_value"],
            _branch_sort_key(record),
            record["A"],
        ),
    )


def aggregate_results(
    run_id: str,
    N: int,
    k: int,
    mode: str,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Combine all branches without promoting unresolved work to a proof."""
    status_counts = Counter(record["status"] for record in records)
    errors = [
        record["branch"]["id"]
        for record in records
        if record["status"] in {"ERROR", "MODEL_INVALID"}
    ]
    if mode == "existence":
        unresolved = [
            record["branch"]["id"]
            for record in records
            if record["status"] not in {"OPTIMAL", "FEASIBLE", "INFEASIBLE"}
        ]
    else:
        unresolved = [
            record["branch"]["id"]
            for record in records
            if record["status"] not in {"OPTIMAL", "INFEASIBLE"}
        ]

    winner = _winner(records, mode)
    all_infeasible = bool(records) and all(
        record["status"] == "INFEASIBLE" for record in records
    )
    aggregate: dict[str, Any] = {
        "record_type": "aggregate",
        "run_id": run_id,
        "N": N,
        "k": k,
        "mode": mode,
        "branch_count": len(records),
        "branch_status_counts": dict(sorted(status_counts.items())),
        "unresolved_branches": unresolved,
        "error_branches": errors,
        "feasible_candidate": winner is not None,
        "infeasibility_proved": all_infeasible,
        "all_branches_resolved": not unresolved,
    }

    if mode == "existence":
        if winner is not None:
            aggregate["status"] = "FEASIBLE"
            aggregate["existence_proved"] = True
        elif all_infeasible:
            aggregate["status"] = "INFEASIBLE"
            aggregate["existence_proved"] = False
        else:
            aggregate["status"] = "ERROR" if errors else "UNKNOWN"
            aggregate["existence_proved"] = False
    else:
        active_records = [
            record for record in records if record["status"] != "INFEASIBLE"
        ]
        bounds = [
            record["objective_bound"]
            for record in active_records
            if record.get("objective_bound") is not None
        ]
        if mode == "min-multiplicity":
            global_bound = min(bounds) if bounds else None
            bound_kind = "lower"
        else:
            global_bound = max(bounds) if bounds else None
            bound_kind = "upper"
        aggregate["objective_name"] = (
            "exceptional_multiplicity"
            if mode == "min-multiplicity"
            else "unpaired_element_count"
        )
        aggregate["objective_sense"] = (
            "minimize" if mode == "min-multiplicity" else "maximize"
        )
        aggregate["global_objective_bound"] = global_bound
        aggregate["global_objective_bound_kind"] = bound_kind

        if winner is None:
            if all_infeasible:
                aggregate["status"] = "INFEASIBLE"
            else:
                aggregate["status"] = "ERROR" if errors else "UNKNOWN"
            aggregate["optimality_proved"] = False
        else:
            best_value = int(winner["objective_value"])
            aggregate["objective_value"] = best_value
            optimality_proved = global_bound == best_value
            aggregate["optimality_proved"] = optimality_proved
            if optimality_proved:
                aggregate["status"] = "OPTIMAL"
            else:
                aggregate["status"] = "ERROR" if errors else "UNKNOWN"

    if winner is not None:
        claimed_objective = winner.get("objective_value")
        winning_branch = BranchSpec(
            winner["branch"]["kind"], winner["branch"]["sigma"]
        )
        checked = self_check_candidate(
            N,
            k,
            winning_branch,
            mode,
            list(winner["A"]),
            claimed_objective,
        )
        aggregate["winning_branch"] = winning_branch.as_json()
        aggregate.update(checked)
        if mode != "existence":
            aggregate["objective_value"] = claimed_objective

    aggregate["proof_complete"] = aggregate["status"] in {
        "FEASIBLE",
        "INFEASIBLE",
        "OPTIMAL",
    }
    return aggregate


class JsonlSink:
    def __init__(self, output: Path | None, append: bool) -> None:
        self._stream: TextIO | None = None
        if output is not None:
            self._stream = output.open("a" if append else "w", encoding="utf-8")

    def emit(self, record: dict[str, Any]) -> None:
        line = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        print(line, flush=True)
        if self._stream is not None:
            self._stream.write(line + "\n")
            self._stream.flush()

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()


def run_parallel(args: argparse.Namespace) -> dict[str, Any]:
    branches = all_branches(args.N)
    process_workers = min(args.workers, len(branches), MAX_PROCESS_POOL_WORKERS)
    run_id = uuid.uuid4().hex
    requests = [
        SolveRequest(
            run_id=run_id,
            N=args.N,
            k=args.k,
            mode=args.mode,
            branch=branch,
            time_limit_seconds=args.time_limit,
            random_seed=args.seed,
        )
        for branch in branches
    ]
    sink = JsonlSink(args.output, args.append)
    started = time.perf_counter()
    try:
        sink.emit(
            {
                "record_type": "run_start",
                "run_id": run_id,
                "N": args.N,
                "k": args.k,
                "mode": args.mode,
                "branch_count": len(branches),
                "exception_sigmas": [
                    branch.sigma for branch in branches if branch.sigma is not None
                ],
                "requested_process_workers": args.workers,
                "process_workers": process_workers,
                "solver_threads_per_process": 1,
                "time_limit_seconds_per_branch": args.time_limit,
                "random_seed": args.seed,
                "ortools_version": ortools.__version__,
                "python_version": sys.version.split()[0],
            }
        )

        records: list[dict[str, Any]] = []
        context = multiprocessing.get_context("spawn")
        with ProcessPoolExecutor(
            max_workers=process_workers,
            mp_context=context,
        ) as executor:
            futures = {
                executor.submit(solve_branch, request): request for request in requests
            }
            for future in as_completed(futures):
                request = futures[future]
                try:
                    record = future.result()
                except BaseException as error:
                    record = _error_branch_record(request, error)
                records.append(record)
                sink.emit(record)

        aggregate = aggregate_results(run_id, args.N, args.k, args.mode, records)
        aggregate["total_wall_seconds"] = time.perf_counter() - started
        sink.emit(aggregate)
        return aggregate
    finally:
        sink.close()


def _brute_branch_candidates(
    N: int,
    k: int,
    branch: BranchSpec,
) -> list[dict[str, Any]]:
    candidates = []
    for values_tuple in combinations(range(1, N + 1), k):
        if values_tuple[0] != 1:
            continue
        analysis = analyze_candidate(N, k, list(values_tuple))
        repeated = analysis["repeated_sums"]
        if branch.kind == "ordinary":
            matches = not repeated
        else:
            matches = len(repeated) == 1 and repeated[0]["sum"] == branch.sigma
        if matches:
            candidates.append(analysis)
    return candidates


def _check_translation_exhaustively() -> int:
    checked = 0
    for N in range(1, 7):
        for size in range(1, N + 1):
            for values_tuple in combinations(range(1, N + 1), size):
                minimum = values_tuple[0]
                translated = tuple(value - minimum + 1 for value in values_tuple)
                original = unordered_sum_representations(values_tuple)
                shifted = unordered_sum_representations(translated)
                shift = 2 * minimum - 2
                expected = {
                    sum_value - shift: len(pairs)
                    for sum_value, pairs in original.items()
                }
                actual = {
                    sum_value: len(pairs) for sum_value, pairs in shifted.items()
                }
                if actual != expected:
                    raise AssertionError("translation failed to preserve multiplicities")
                if translated[0] != 1 or translated[-1] > N:
                    raise AssertionError("translation left the normalized domain")
                checked += 1
    return checked


def run_self_test() -> dict[str, Any]:
    """Compare every N=12 branch and objective with literal subset search."""
    started = time.perf_counter()
    translation_cases = _check_translation_exhaustively()
    if all_branches(1) != [BranchSpec("ordinary")]:
        raise AssertionError("N=1 branch enumeration is wrong")

    diagonal = self_check_candidate(
        3,
        3,
        BranchSpec("exceptional", 4),
        "max-unpaired",
        [1, 2, 3],
        0,
    )
    if diagonal["exceptional_multiplicity"] != 2:
        raise AssertionError("diagonal representation was not counted")

    N = 12
    branch_cases = 0
    aggregate_cases = 0
    for k in range(1, N + 1):
        branches = all_branches(N)
        brute_by_branch = {
            branch.branch_id: _brute_branch_candidates(N, k, branch)
            for branch in branches
        }
        for mode in MODES:
            records = []
            for branch in branches:
                request = SolveRequest(
                    run_id="self-test",
                    N=N,
                    k=k,
                    mode=mode,
                    branch=branch,
                    time_limit_seconds=0.0,
                    random_seed=864,
                )
                record = solve_branch(request)
                records.append(record)
                brute = brute_by_branch[branch.branch_id]
                if not brute:
                    if record["status"] != "INFEASIBLE":
                        raise AssertionError(
                            f"{mode} {branch.branch_id}: expected INFEASIBLE, "
                            f"got {record['status']}"
                        )
                else:
                    if not record.get("candidate_self_checked"):
                        raise AssertionError(
                            f"{mode} {branch.branch_id}: missing checked candidate"
                        )
                    if mode != "existence":
                        brute_values = [
                            objective_value_from_analysis(mode, candidate)
                            for candidate in brute
                        ]
                        expected = (
                            min(brute_values)
                            if mode == "min-multiplicity"
                            else max(brute_values)
                        )
                        if record["status"] != "OPTIMAL":
                            raise AssertionError(
                                f"{mode} {branch.branch_id}: expected OPTIMAL, "
                                f"got {record['status']}"
                            )
                        if record["objective_value"] != expected:
                            raise AssertionError(
                                f"{mode} {branch.branch_id}: objective mismatch"
                            )
                branch_cases += 1

            aggregate = aggregate_results("self-test", N, k, mode, records)
            all_brute = [
                candidate
                for candidates in brute_by_branch.values()
                for candidate in candidates
            ]
            if not all_brute:
                if aggregate["status"] != "INFEASIBLE":
                    raise AssertionError(f"{mode} k={k}: expected aggregate INFEASIBLE")
            elif mode == "existence":
                if aggregate["status"] != "FEASIBLE":
                    raise AssertionError(f"existence k={k}: expected FEASIBLE")
            else:
                expected_values = [
                    objective_value_from_analysis(mode, candidate)
                    for candidate in all_brute
                ]
                expected = (
                    min(expected_values)
                    if mode == "min-multiplicity"
                    else max(expected_values)
                )
                if aggregate["status"] != "OPTIMAL":
                    raise AssertionError(f"{mode} k={k}: expected OPTIMAL")
                if aggregate["objective_value"] != expected:
                    raise AssertionError(f"{mode} k={k}: aggregate objective mismatch")
            aggregate_cases += 1

    exceptional_request = SolveRequest(
        run_id="self-test-unknown",
        N=3,
        k=3,
        mode="min-multiplicity",
        branch=BranchSpec("exceptional", 4),
        time_limit_seconds=0.0,
        random_seed=864,
    )
    exceptional_record = solve_branch(exceptional_request)
    unresolved_ordinary = {
        "record_type": "branch",
        "run_id": "self-test-unknown",
        "N": 3,
        "k": 3,
        "mode": "min-multiplicity",
        "branch": BranchSpec("ordinary").as_json(),
        "status": "UNKNOWN",
        "proof_complete": False,
        "objective_bound": 0,
    }
    unknown_aggregate = aggregate_results(
        "self-test-unknown",
        3,
        3,
        "min-multiplicity",
        [unresolved_ordinary, exceptional_record],
    )
    if unknown_aggregate["status"] != "UNKNOWN":
        raise AssertionError("unresolved ordinary branch was not aggregated as UNKNOWN")
    resolved_ordinary = dict(unresolved_ordinary, status="INFEASIBLE")
    closed_aggregate = aggregate_results(
        "self-test-unknown",
        3,
        3,
        "min-multiplicity",
        [resolved_ordinary, exceptional_record],
    )
    if closed_aggregate["status"] != "OPTIMAL":
        raise AssertionError("matching global lower bound did not certify OPTIMAL")

    return {
        "record_type": "self_test",
        "status": "PASS",
        "translation_cases": translation_cases,
        "branch_cases": branch_cases,
        "aggregate_cases": aggregate_cases,
        "unknown_aggregate_cases": 2,
        "N": N,
        "ortools_version": ortools.__version__,
        "wall_seconds": time.perf_counter() - started,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Solve exact size-k Problem 864 models by ordinary/fixed-exception "
            "CP-SAT branches. Stdout is JSONL."
        )
    )
    parser.add_argument("--N", "--n", dest="N", type=int)
    parser.add_argument("--k", type=int)
    parser.add_argument("--mode", choices=MODES, default="existence")
    parser.add_argument(
        "--workers",
        type=int,
        default=min(MAX_PROCESSES, os.cpu_count() or 1),
        help="parallel branch processes, each with one CP-SAT search worker",
    )
    parser.add_argument(
        "--time-limit",
        type=float,
        default=0.0,
        help="seconds per branch; 0 means no time limit",
    )
    parser.add_argument("--seed", type=int, default=864)
    parser.add_argument("--output", type=Path, help="also write JSONL to this path")
    parser.add_argument(
        "--append",
        action="store_true",
        help="append to --output instead of replacing it",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return args
    if args.N is None or args.k is None:
        parser.error("--N and --k are required unless --self-test is used")
    if args.N < 1:
        parser.error("--N must be positive")
    if not 1 <= args.k <= args.N:
        parser.error("--k must lie in [1,N]")
    if not 1 <= args.workers <= MAX_PROCESSES:
        parser.error(f"--workers must lie in [1,{MAX_PROCESSES}]")
    if not math.isfinite(args.time_limit) or args.time_limit < 0:
        parser.error("--time-limit must be finite and nonnegative")
    if not 0 <= args.seed <= MAX_RANDOM_SEED:
        parser.error(f"--seed must lie in [0,{MAX_RANDOM_SEED}]")
    if args.append and args.output is None:
        parser.error("--append requires --output")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        print(
            json.dumps(
                run_self_test(),
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        )
        return 0

    aggregate = run_parallel(args)
    if aggregate["status"] in {"FEASIBLE", "INFEASIBLE", "OPTIMAL"}:
        return 0
    if aggregate["status"] == "UNKNOWN":
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
