#!/usr/bin/env python3
"""Unrestricted set-cover MILP for domination on an n by n queen graph.

There is one binary variable for every board square.  Every square contributes
one closed-neighborhood covering constraint, and the sole global restriction
is ``sum(x) <= k``.  There are no nonattacking, symmetry, parity, or pattern
assumptions.

The normal CLI runs the solver in a disposable subprocess, so ``--timeout`` is
a hard wall-clock bound even if a native MILP backend fails to return.  The
same timeout is also passed to the backend.  A returned witness is checked by
direct coordinate comparisons that do not use the generated MILP rows.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import platform
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from ortools import __version__ as ortools_version
from ortools.linear_solver import pywraplp


Coordinate = tuple[int, int]

BACKENDS: dict[str, tuple[str, str]] = {
    "scip": ("SCIP", "SCIP"),
    "cbc": ("CBC_MIXED_INTEGER_PROGRAMMING", "CBC"),
    "highs": ("HIGHS_MIXED_INTEGER_PROGRAMMING", "HiGHS"),
}
AUTO_BACKEND_ORDER = ("scip", "cbc", "highs")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def square_index(n: int, row: int, column: int) -> int:
    """Return the zero-based variable index for a board square."""
    return row * n + column


def closed_neighborhood_indices(n: int, row: int, column: int) -> list[int]:
    """Return sorted variable indices that dominate ``(row, column)``."""
    return [
        square_index(n, queen_row, queen_column)
        for queen_row in range(n)
        for queen_column in range(n)
        if (
            queen_row == row
            or queen_column == column
            or queen_row - queen_column == row - column
            or queen_row + queen_column == row + column
        )
    ]


def build_model_document(n: int, k: int) -> dict[str, Any]:
    """Build a JSON-serializable, complete description of the MILP."""
    variables = [
        {
            "index": square_index(n, row, column),
            "name": f"q_{row}_{column}",
            "type": "binary",
            "row": row,
            "column": column,
        }
        for row in range(n)
        for column in range(n)
    ]
    domination_constraints = [
        {
            "name": f"dominate_{row}_{column}",
            "target": [row, column],
            "sense": ">=",
            "rhs": 1,
            "unit_coefficient_variable_indices": closed_neighborhood_indices(
                n, row, column
            ),
        }
        for row in range(n)
        for column in range(n)
    ]
    return {
        "schema": "queen-domination-mip-model-v1",
        "instance": {
            "n": n,
            "k": k,
            "board_variables": n * n,
            "domination_constraints": n * n,
            "cardinality": "at-most",
            "structural_restrictions": [],
        },
        "variables": variables,
        "constraints": {
            "cardinality": {
                "name": "queen_count_at_most_k",
                "sense": "<=",
                "rhs": k,
                "unit_coefficient_variable_indices": list(range(n * n)),
            },
            "domination": domination_constraints,
        },
        "objective": None,
    }


def model_sha256(model_document: dict[str, Any]) -> str:
    canonical = json.dumps(
        model_document, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def resolve_backend(requested: str) -> tuple[str, str, str]:
    """Return (short name, OR-Tools id, display name) for an available backend."""
    candidates = AUTO_BACKEND_ORDER if requested == "auto" else (requested,)
    for short_name in candidates:
        solver_id, display_name = BACKENDS[short_name]
        probe = pywraplp.Solver.CreateSolver(solver_id)
        if probe is not None:
            return short_name, solver_id, display_name
    raise RuntimeError(
        f"no requested MILP backend is available (requested={requested!r})"
    )


def build_solver(
    model_document: dict[str, Any],
    backend_id: str,
    timeout_seconds: float,
    workers: int,
    enable_output: bool,
) -> tuple[pywraplp.Solver, list[pywraplp.Variable], bool]:
    """Translate the explicit JSON model directly into OR-Tools pywraplp."""
    solver = pywraplp.Solver.CreateSolver(backend_id)
    if solver is None:
        raise RuntimeError(f"OR-Tools could not create backend {backend_id!r}")
    solver.SetTimeLimit(int(timeout_seconds * 1000))
    threads_accepted = bool(solver.SetNumThreads(workers))
    if enable_output:
        solver.EnableOutput()

    variables = [solver.BoolVar(variable["name"]) for variable in model_document["variables"]]
    cardinality = model_document["constraints"]["cardinality"]
    solver.Add(
        solver.Sum(
            variables[index]
            for index in cardinality["unit_coefficient_variable_indices"]
        )
        <= cardinality["rhs"],
        cardinality["name"],
    )
    for constraint in model_document["constraints"]["domination"]:
        solver.Add(
            solver.Sum(
                variables[index]
                for index in constraint["unit_coefficient_variable_indices"]
            )
            >= constraint["rhs"],
            constraint["name"],
        )
    return solver, variables, threads_accepted


def verify_witness(
    n: int, k: int, coordinates: Sequence[Sequence[int]]
) -> dict[str, Any]:
    """Check a witness directly, independently of the model neighborhoods."""
    errors: list[str] = []
    points: list[Coordinate] = []
    for index, coordinate in enumerate(coordinates):
        if (
            not isinstance(coordinate, (list, tuple))
            or len(coordinate) != 2
            or any(isinstance(value, bool) or not isinstance(value, int) for value in coordinate)
        ):
            errors.append(f"coordinate {index} is not an integer pair")
            continue
        points.append((coordinate[0], coordinate[1]))

    if len(points) != len(coordinates):
        errors.append("one or more coordinates could not be parsed")
    if len(points) > k:
        errors.append(f"witness has {len(points)} queens, exceeding k={k}")
    if len(set(points)) != len(points):
        errors.append("witness contains duplicate coordinates")
    if any(not (0 <= row < n and 0 <= column < n) for row, column in points):
        errors.append("witness contains an out-of-range coordinate")

    uncovered: list[list[int]] = []
    if not errors:
        for row in range(n):
            for column in range(n):
                if not any(
                    queen_row == row
                    or queen_column == column
                    or abs(queen_row - row) == abs(queen_column - column)
                    for queen_row, queen_column in points
                ):
                    uncovered.append([row, column])
        if uncovered:
            errors.append(f"{len(uncovered)} board squares are undominated")

    return {
        "checked": True,
        "valid": not errors,
        "queen_count": len(points),
        "dominated_count": n * n - len(uncovered),
        "uncovered": uncovered,
        "errors": errors,
        "method": "direct pairwise row/column/absolute-diagonal comparisons",
    }



def load_hint(path: Path, n: int, k: int) -> list[Coordinate]:
    """Load coordinate values used only as a nonbinding branching hint."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload_n = payload.get("n")
        if payload_n is not None and payload_n != n:
            raise ValueError(f"hint board size is {payload_n}, expected {n}")
        raw_coordinates = payload.get("coordinates")
    else:
        raw_coordinates = payload
    if not isinstance(raw_coordinates, list):
        raise ValueError("hint JSON must be a coordinate list or contain coordinates")
    coordinates: list[Coordinate] = []
    for index, coordinate in enumerate(raw_coordinates):
        if (
            not isinstance(coordinate, list)
            or len(coordinate) != 2
            or any(
                isinstance(value, bool) or not isinstance(value, int)
                for value in coordinate
            )
        ):
            raise ValueError(f"invalid coordinate at hint index {index}: {coordinate!r}")
        row, column = coordinate
        if not (0 <= row < n and 0 <= column < n):
            raise ValueError(f"out-of-range hint coordinate: {(row, column)}")
        coordinates.append((row, column))
    if len(coordinates) > k:
        raise ValueError(f"hint has {len(coordinates)} queens, exceeding k={k}")
    if len(set(coordinates)) != len(coordinates):
        raise ValueError("hint contains duplicate coordinates")
    return coordinates

STATUS_NAMES = {
    pywraplp.Solver.OPTIMAL: "OPTIMAL",
    pywraplp.Solver.FEASIBLE: "FEASIBLE",
    pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
    pywraplp.Solver.UNBOUNDED: "UNBOUNDED",
    pywraplp.Solver.ABNORMAL: "ABNORMAL",
    pywraplp.Solver.MODEL_INVALID: "MODEL_INVALID",
    pywraplp.Solver.NOT_SOLVED: "NOT_SOLVED",
}


def _safe_stat(callable_value: Any) -> int | float | None:
    try:
        value = callable_value()
    except Exception:
        return None
    return value if isinstance(value, (int, float)) else None


def solve_direct(args: argparse.Namespace, model_document: dict[str, Any]) -> dict[str, Any]:
    started_utc = utc_now()
    started = time.perf_counter()
    backend, backend_id, backend_display = resolve_backend(args.backend)
    solver, variables, threads_accepted = build_solver(
        model_document,
        backend_id,
        args.timeout,
        args.workers,
        args.solver_output,
    )
    hint_coordinates = (
        load_hint(args.hint_json, args.n, args.k) if args.hint_json else []
    )
    if args.hint_json:
        hint_set = set(hint_coordinates)
        solver.SetHint(
            variables,
            [
                int((index // args.n, index % args.n) in hint_set)
                for index in range(args.n * args.n)
            ],
        )
    status_code = solver.Solve()
    wall_seconds = time.perf_counter() - started
    status = STATUS_NAMES.get(status_code, f"UNKNOWN_STATUS_{status_code}")

    coordinates: list[list[int]] = []
    verification: dict[str, Any] = {
        "checked": False,
        "valid": None,
        "queen_count": None,
        "dominated_count": None,
        "uncovered": None,
        "errors": None,
        "method": None,
    }
    if status_code in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        n = args.n
        coordinates = [
            [index // n, index % n]
            for index, variable in enumerate(variables)
            if variable.solution_value() > 0.5
        ]
        verification = verify_witness(args.n, args.k, coordinates)
        if not verification["valid"]:
            raise RuntimeError(
                "MILP backend returned a witness that failed direct verification: "
                + "; ".join(verification["errors"])
            )

    return {
        "schema": "queen-domination-mip-result-v1",
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "model_sha256": model_sha256(model_document),
        "instance": model_document["instance"],
        "configuration": {
            "backend_requested": args.backend,
            "backend_resolved": backend,
            "timeout_seconds": args.timeout,
            "timeout_enforcement": "backend limit inside hard subprocess wrapper",
            "workers_requested": args.workers,
            "backend_accepted_thread_setting": threads_accepted,
            "solver_output": args.solver_output,
            "hint_json": str(args.hint_json) if args.hint_json else None,
            "hint_coordinate_count": len(hint_coordinates),
            "hint_is_nonbinding": True,
        },
        "solver": {
            "backend": backend_display,
            "backend_id": backend_id,
            "version": solver.SolverVersion(),
            "ortools_version": ortools_version,
            "python_version": platform.python_version(),
            "status": status,
            "status_code": status_code,
            "wall_seconds": wall_seconds,
            "backend_wall_time_milliseconds": _safe_stat(solver.wall_time),
            "iterations": _safe_stat(solver.iterations),
            "branch_and_bound_nodes": _safe_stat(solver.nodes),
        },
        "solution": {
            "cardinality": len(coordinates) if verification["checked"] else None,
            "coordinates": coordinates,
            "independent_direct_check": verification,
        },
    }


@contextmanager
def temporary_result_path() -> Iterator[Path]:
    """Yield a unique result path in the pre-existing writable result tree."""
    result_root = Path(__file__).resolve().parent / "results"
    result_root.mkdir(parents=True, exist_ok=True)
    path = result_root / f".mip_child_{uuid.uuid4().hex}.json"
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)



def solve_with_hard_timeout(
    args: argparse.Namespace, model_document: dict[str, Any]
) -> dict[str, Any]:
    """Solve in a killable subprocess with a strict whole-process deadline."""
    backend, backend_id, backend_display = resolve_backend(args.backend)
    started_utc = utc_now()
    started = time.perf_counter()
    with temporary_result_path() as child_result:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--n",
            str(args.n),
            "--k",
            str(args.k),
            "--backend",
            backend,
            "--workers",
            str(args.workers),
            "--timeout",
            str(args.timeout),
            "--result-json",
            str(child_result),
            "--_solve-direct",
        ]
        if args.solver_output:
            command.append("--solver-output")
        if args.hint_json:
            command.extend(["--hint-json", str(args.hint_json.resolve())])
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "schema": "queen-domination-mip-result-v1",
                "started_utc": started_utc,
                "finished_utc": utc_now(),
                "model_sha256": model_sha256(model_document),
                "instance": model_document["instance"],
                "configuration": {
                    "backend_requested": args.backend,
                    "backend_resolved": backend,
                    "timeout_seconds": args.timeout,
                    "timeout_enforcement": "solver subprocess terminated at hard wall deadline",
                    "workers_requested": args.workers,
                    "backend_accepted_thread_setting": None,
                    "solver_output": args.solver_output,
                    "hint_json": str(args.hint_json) if args.hint_json else None,
                    "hint_coordinate_count": None,
                    "hint_is_nonbinding": True,
                },
                "solver": {
                    "backend": backend_display,
                    "backend_id": backend_id,
                    "version": None,
                    "ortools_version": ortools_version,
                    "python_version": platform.python_version(),
                    "status": "UNKNOWN",
                    "status_code": None,
                    "wall_seconds": time.perf_counter() - started,
                    "backend_wall_time_milliseconds": None,
                    "iterations": None,
                    "branch_and_bound_nodes": None,
                },
                "solution": {
                    "cardinality": None,
                    "coordinates": [],
                    "independent_direct_check": {
                        "checked": False,
                        "valid": None,
                        "queen_count": None,
                        "dominated_count": None,
                        "uncovered": None,
                        "errors": None,
                        "method": None,
                    },
                },
            }
        if completed.returncode != 0:
            raise RuntimeError(
                f"MILP subprocess exited {completed.returncode}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        if not child_result.exists():
            raise RuntimeError("MILP subprocess did not write its result JSON")
        return json.loads(child_result.read_text(encoding="utf-8"))


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=26, help="board side length")
    parser.add_argument("--k", type=int, default=13, help="maximum queen count")
    parser.add_argument(
        "--backend",
        choices=("auto", "scip", "cbc", "highs"),
        default="auto",
        help="MILP backend; auto tries SCIP, then CBC, then HiGHS",
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="backend thread limit (maximum 64)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="hard whole-process wall-clock limit in seconds",
    )
    parser.add_argument("--model-json", type=Path, help="write the explicit model JSON")
    parser.add_argument("--result-json", type=Path, help="write the result JSON")
    parser.add_argument("--solver-output", action="store_true")
    parser.add_argument("--_solve-direct", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--hint-json",
        type=Path,
        help="optional coordinate fixture used only as a nonbinding complete hint",
    )
    args = parser.parse_args(argv)
    if args.n <= 0:
        parser.error("--n must be positive")
    if args.k < 0 or args.k > args.n * args.n:
        parser.error("--k must satisfy 0 <= k <= n^2")
    if args.workers < 1 or args.workers > 64:
        parser.error("--workers must satisfy 1 <= workers <= 64")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    return args


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    model_document = build_model_document(args.n, args.k)
    if args.model_json is not None:
        args.model_json.parent.mkdir(parents=True, exist_ok=True)
        args.model_json.write_text(
            json.dumps(model_document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    result = (
        solve_direct(args, model_document)
        if args._solve_direct
        else solve_with_hard_timeout(args, model_document)
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.result_json is not None:
        args.result_json.parent.mkdir(parents=True, exist_ok=True)
        args.result_json.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 2 if result["solver"]["status"] in {"UNKNOWN", "NOT_SOLVED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
