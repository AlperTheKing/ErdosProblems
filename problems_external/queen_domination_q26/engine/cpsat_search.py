#!/usr/bin/env python3
"""Unrestricted CP-SAT search for domination on an n by n queen graph.

There is one Boolean variable for every board square.  Apart from the
requested global cardinality constraint, the model contains only the closed
queen-neighborhood domination constraint for each square.  In particular,
this encoder makes no nonattacking, symmetry, parity, or pattern assumption.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from ortools import __version__ as ortools_version
from ortools.sat.python import cp_model


Coordinate = tuple[int, int]


def closed_neighborhood(n: int, row: int, col: int) -> list[Coordinate]:
    """Return every square that attacks (row, col), including itself."""
    squares: list[Coordinate] = []
    for r in range(n):
        for c in range(n):
            if (
                r == row
                or c == col
                or r - c == row - col
                or r + c == row + col
            ):
                squares.append((r, c))
    return squares


def build_model(
    n: int, k: int, cardinality: str
) -> tuple[cp_model.CpModel, list[list[cp_model.IntVar]]]:
    """Build the full-board domination model with no structural restriction."""
    model = cp_model.CpModel()
    queen = [
        [model.new_bool_var(f"q_{r}_{c}") for c in range(n)]
        for r in range(n)
    ]

    all_queens = [queen[r][c] for r in range(n) for c in range(n)]
    if cardinality == "exact":
        model.add(sum(all_queens) == k)
    elif cardinality == "at-most":
        model.add(sum(all_queens) <= k)
    else:  # Guard callers as well as argparse.
        raise ValueError(f"unsupported cardinality: {cardinality}")

    for row in range(n):
        for col in range(n):
            model.add(
                sum(queen[r][c] for r, c in closed_neighborhood(n, row, col))
                >= 1
            )

    return model, queen


def is_dominating(n: int, queens: Sequence[Coordinate]) -> tuple[bool, list[Coordinate]]:
    """Independently check a witness by direct pairwise attack tests."""
    queen_set = set(queens)
    if len(queen_set) != len(queens):
        return False, []
    if any(not (0 <= r < n and 0 <= c < n) for r, c in queen_set):
        return False, []

    uncovered: list[Coordinate] = []
    for row in range(n):
        for col in range(n):
            covered = False
            for qr, qc in queen_set:
                if (
                    qr == row
                    or qc == col
                    or qr - qc == row - col
                    or qr + qc == row + col
                ):
                    covered = True
                    break
            if not covered:
                uncovered.append((row, col))
    return not uncovered, uncovered


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def load_hint(path: Path, n: int) -> list[Coordinate]:
    """Load and validate a JSON witness used only as a nonbinding search hint."""
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
    for index, item in enumerate(raw_coordinates):
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not all(isinstance(value, int) for value in item)
        ):
            raise ValueError(f"invalid coordinate at hint index {index}: {item!r}")
        row, col = item
        if not (0 <= row < n and 0 <= col < n):
            raise ValueError(f"out-of-range hint coordinate: {(row, col)}")
        coordinates.append((row, col))
    if len(set(coordinates)) != len(coordinates):
        raise ValueError("hint contains duplicate coordinates")
    return coordinates



def solve(args: argparse.Namespace) -> dict[str, object]:
    started = utc_now()
    model, queen = build_model(args.n, args.k, args.cardinality)

    hint_coordinates: list[Coordinate] = []
    if args.hint_json:
        hint_coordinates = load_hint(args.hint_json, args.n)
        hint_set = set(hint_coordinates)
        # A hint affects branching only; it does not constrain the feasible set.
        for r in range(args.n):
            for c in range(args.n):
                model.add_hint(queen[r][c], int((r, c) in hint_set))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.timeout
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.log_search_progress = args.log_search_progress

    status_code = solver.solve(model)
    status = solver.status_name(status_code)

    coordinates: list[Coordinate] = []
    verification: dict[str, object] = {
        "checked": False,
        "dominating": None,
        "uncovered": None,
        "cardinality_ok": None,
    }
    if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        coordinates = [
            (r, c)
            for r in range(args.n)
            for c in range(args.n)
            if solver.value(queen[r][c])
        ]
        dominating, uncovered = is_dominating(args.n, coordinates)
        cardinality_ok = (
            len(coordinates) == args.k
            if args.cardinality == "exact"
            else len(coordinates) <= args.k
        )
        verification = {
            "checked": True,
            "dominating": dominating,
            "uncovered": [list(square) for square in uncovered],
            "cardinality_ok": cardinality_ok,
        }
        if not dominating or not cardinality_ok:
            raise RuntimeError(
                "CP-SAT model failed independent witness verification: "
                f"dominating={dominating}, cardinality_ok={cardinality_ok}"
            )

    return {
        "schema": "queen-domination-cpsat-result-v1",
        "started_utc": started,
        "finished_utc": utc_now(),
        "instance": {
            "n": args.n,
            "k": args.k,
            "cardinality": args.cardinality,
            "board_variables": args.n * args.n,
            "domination_constraints": args.n * args.n,
            "structural_restrictions": [],
        },
        "configuration": {
            "timeout_seconds": args.timeout,
            "workers": args.workers,
            "random_seed": args.seed,
            "hint_json": str(args.hint_json) if args.hint_json else None,
            "hint_coordinate_count": len(hint_coordinates),
            "hint_is_nonbinding": True,
        },
        "solver": {
            "name": "OR-Tools CP-SAT",
            "ortools_version": ortools_version,
            "python_version": platform.python_version(),
            "status": status,
            "status_code": int(status_code),
            "wall_time_seconds": solver.wall_time,
            "user_time_seconds": solver.user_time,
            "conflicts": solver.num_conflicts,
            "branches": solver.num_branches,
            "response_stats": solver.response_stats(),
        },
        "solution": {
            "cardinality": (
                len(coordinates)
                if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL)
                else None
            ),
            "coordinates": [list(square) for square in coordinates],
            "local_verification": verification,
        },
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True, help="board side length")
    parser.add_argument("--k", type=int, required=True, help="queen bound")
    parser.add_argument(
        "--cardinality",
        choices=("exact", "at-most"),
        default="at-most",
        help="require exactly k queens or at most k queens",
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="CP-SAT workers (maximum 64)"
    )
    parser.add_argument(
        "--timeout", type=float, default=60.0, help="wall-clock limit in seconds"
    )
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--output", type=Path, help="write result JSON here")
    parser.add_argument("--log-search-progress", action="store_true")
    parser.add_argument(
        "--hint-json",
        type=Path,
        help="optional coordinate fixture used as a nonbinding CP-SAT hint",
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
    result = solve(args)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
