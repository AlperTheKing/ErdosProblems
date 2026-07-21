#!/usr/bin/env python3
"""Exact CP-SAT model for an n=18 SSNC counterexample search.

This file deliberately separates model construction from search.  The
``--calibrate`` command pins many small oriented graphs and checks every model
indicator against a direct set-based definition.  ``--solve`` is explicit so
that importing the module or running it without arguments never starts a
production search.

The success predicate is the literal negation of Seymour's second-neighborhood
conjecture: every vertex v must have |N2+(v)| < |N+(v)|, where N2+(v) contains
only vertices reached in exactly the "new second-neighborhood" sense (a
direct out-neighbor is excluded even if a two-step walk also reaches it).
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from dataclasses import dataclass
from typing import Iterable, Sequence

from ortools.sat.python import cp_model


Adjacency = list[list[int]]


@dataclass(frozen=True)
class ModelArtifacts:
    model: cp_model.CpModel
    arc: dict[tuple[int, int], cp_model.IntVar]
    two_step_term: dict[tuple[int, int, int], cp_model.IntVar]
    reachable_in_two: dict[tuple[int, int], cp_model.IntVar]
    new_second: dict[tuple[int, int], cp_model.IntVar]
    out_degree: list[cp_model.IntVar]


def validate_adjacency(adjacency: Sequence[Sequence[int]]) -> None:
    """Reject anything that is not a square 0/1 oriented adjacency matrix."""
    n = len(adjacency)
    if n < 2:
        raise ValueError("an oriented graph must have at least two vertices")
    if any(len(row) != n for row in adjacency):
        raise ValueError("adjacency matrix is not square")
    for i in range(n):
        for j in range(n):
            if adjacency[i][j] not in (0, 1, False, True):
                raise ValueError(f"adjacency[{i}][{j}] is not binary")
            if i == j and adjacency[i][j]:
                raise ValueError(f"loop at vertex {i}")
    for i in range(n):
        for j in range(i + 1, n):
            if adjacency[i][j] and adjacency[j][i]:
                raise ValueError(f"digon on vertices {i},{j}")


def scalar_definition(adjacency: Sequence[Sequence[int]]) -> dict[str, object]:
    """Evaluate raw two-step reachability and N2+ by direct Python sets."""
    validate_adjacency(adjacency)
    n = len(adjacency)
    out_sets: list[set[int]] = []
    raw_two_sets: list[set[int]] = []
    second_sets: list[set[int]] = []
    ledger: list[dict[str, object]] = []
    for v in range(n):
        out = {w for w in range(n) if adjacency[v][w]}
        raw_two = {
            w
            for w in range(n)
            if w != v
            and any(adjacency[v][u] and adjacency[u][w] for u in range(n))
        }
        second = {w for w in raw_two if w not in out}
        out_sets.append(out)
        raw_two_sets.append(raw_two)
        second_sets.append(second)
        ledger.append(
            {
                "vertex": v,
                "out_degree": len(out),
                "second_out_degree": len(second),
                "out": sorted(out),
                "second": sorted(second),
            }
        )
    return {
        "out_sets": out_sets,
        "raw_two_sets": raw_two_sets,
        "second_sets": second_sets,
        "ledger": ledger,
        "minimum_out_degree": min(map(len, out_sets)),
        "is_counterexample": all(
            len(second_sets[v]) < len(out_sets[v]) for v in range(n)
        ),
    }


def build_model(
    n: int,
    *,
    minimum_out_degree: int,
    require_counterexample: bool,
    target_symmetry: bool,
    fixed_adjacency: Sequence[Sequence[int]] | None = None,
) -> ModelArtifacts:
    """Build an exact model, with iff constraints for all derived Booleans.

    ``reachable_in_two[v,w]`` is equivalent to
    ``OR_u (arc[v,u] AND arc[u,w])``.  ``new_second[v,w]`` is equivalent to
    ``reachable_in_two[v,w] AND NOT arc[v,w]``.  Both implications of each
    equivalence are present; no derived Boolean can be chosen opportunistically
    by the solver to satisfy a cardinality bound.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    if not 0 <= minimum_out_degree <= n - 1:
        raise ValueError("minimum_out_degree must lie in [0,n-1]")
    if fixed_adjacency is not None:
        validate_adjacency(fixed_adjacency)
        if len(fixed_adjacency) != n:
            raise ValueError("fixed adjacency order does not equal n")
    if target_symmetry and (n != 18 or minimum_out_degree != 8):
        raise ValueError("target symmetry is proved safe only for n=18, delta>=8")

    model = cp_model.CpModel()
    arc: dict[tuple[int, int], cp_model.IntVar] = {}
    for v in range(n):
        for w in range(n):
            if v != w:
                arc[v, w] = model.NewBoolVar(f"a_{v}_{w}")

    # Oriented graph: at most one arc for each unordered pair.  Diagonal arcs
    # do not have variables and are therefore identically false.
    for v in range(n):
        for w in range(v + 1, n):
            model.Add(arc[v, w] + arc[w, v] <= 1)

    out_degree: list[cp_model.IntVar] = []
    for v in range(n):
        degree = model.NewIntVar(0, n - 1, f"d_{v}")
        model.Add(degree == sum(arc[v, w] for w in range(n) if w != v))
        model.Add(degree >= minimum_out_degree)
        out_degree.append(degree)

    if target_symmetry:
        # Safe relabeling proof for this target only:
        # K_18 has 153 unordered pairs, so min out-degree >= 8 implies at
        # least 144 arcs and min out-degree cannot be >= 9 (which would need
        # at least 162 arcs).  Hence some vertex has degree exactly 8.  Relabel
        # it as 0, then arbitrarily relabel its eight out-neighbors as 1..8.
        model.Add(out_degree[0] == 8)
        for w in range(1, 9):
            model.Add(arc[0, w] == 1)
        for w in range(9, 18):
            model.Add(arc[0, w] == 0)

    if fixed_adjacency is not None:
        for v in range(n):
            for w in range(n):
                if v != w:
                    model.Add(arc[v, w] == int(bool(fixed_adjacency[v][w])))

    two_step_term: dict[tuple[int, int, int], cp_model.IntVar] = {}
    reachable_in_two: dict[tuple[int, int], cp_model.IntVar] = {}
    new_second: dict[tuple[int, int], cp_model.IntVar] = {}

    for v in range(n):
        for w in range(n):
            if v == w:
                continue
            terms: list[cp_model.IntVar] = []
            for u in range(n):
                if u == v or u == w:
                    continue
                term = model.NewBoolVar(f"p_{v}_{u}_{w}")
                two_step_term[v, u, w] = term
                terms.append(term)
                # term <=> (arc[v,u] AND arc[u,w]).
                model.Add(term <= arc[v, u])
                model.Add(term <= arc[u, w])
                model.Add(term >= arc[v, u] + arc[u, w] - 1)

            reach = model.NewBoolVar(f"q_{v}_{w}")
            reachable_in_two[v, w] = reach
            if terms:
                # reach <=> OR(terms).  The upper bound is the often-missed
                # reverse implication in unsound SSNC encodings.
                for term in terms:
                    model.Add(reach >= term)
                model.Add(reach <= sum(terms))
            else:
                model.Add(reach == 0)

            second = model.NewBoolVar(f"z_{v}_{w}")
            new_second[v, w] = second
            # second <=> (reach AND NOT arc[v,w]).
            model.Add(second <= reach)
            model.Add(second + arc[v, w] <= 1)
            model.Add(second >= reach - arc[v, w])

    if require_counterexample:
        for v in range(n):
            model.Add(
                sum(new_second[v, w] for w in range(n) if w != v)
                <= out_degree[v] - 1
            )

    validation_error = model.Validate()
    if validation_error:
        raise RuntimeError(f"OR-Tools rejected the model: {validation_error}")
    return ModelArtifacts(
        model=model,
        arc=arc,
        two_step_term=two_step_term,
        reachable_in_two=reachable_in_two,
        new_second=new_second,
        out_degree=out_degree,
    )


def _new_solver(seconds: float, workers: int, seed: int) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    return solver


def extract_adjacency(
    solver: cp_model.CpSolver, artifacts: ModelArtifacts, n: int
) -> Adjacency:
    adjacency = [[0] * n for _ in range(n)]
    for (v, w), variable in artifacts.arc.items():
        adjacency[v][w] = int(solver.Value(variable))
    return adjacency


def _check_model_indicators(
    solver: cp_model.CpSolver,
    artifacts: ModelArtifacts,
    adjacency: Sequence[Sequence[int]],
) -> None:
    scalar = scalar_definition(adjacency)
    n = len(adjacency)
    for v in range(n):
        if solver.Value(artifacts.out_degree[v]) != len(scalar["out_sets"][v]):
            raise AssertionError(f"out-degree mismatch at vertex {v}")
        for w in range(n):
            if v == w:
                continue
            got_reach = bool(solver.Value(artifacts.reachable_in_two[v, w]))
            want_reach = w in scalar["raw_two_sets"][v]
            if got_reach != want_reach:
                raise AssertionError(
                    f"two-step reification mismatch at ({v},{w}): "
                    f"model={got_reach}, scalar={want_reach}"
                )
            got_second = bool(solver.Value(artifacts.new_second[v, w]))
            want_second = w in scalar["second_sets"][v]
            if got_second != want_second:
                raise AssertionError(
                    f"N2 reification mismatch at ({v},{w}): "
                    f"model={got_second}, scalar={want_second}"
                )


def _adjacency_from_pair_states(n: int, states: Iterable[int]) -> Adjacency:
    adjacency = [[0] * n for _ in range(n)]
    for (i, j), state in zip(itertools.combinations(range(n), 2), states):
        if state == 1:
            adjacency[i][j] = 1
        elif state == 2:
            adjacency[j][i] = 1
        elif state != 0:
            raise ValueError("pair state must be 0, 1, or 2")
    return adjacency


def _check_pinned_graph(adjacency: Adjacency) -> None:
    """Compare a pinned model with the scalar definition, including iff test."""
    n = len(adjacency)
    scalar = scalar_definition(adjacency)
    artifacts = build_model(
        n,
        minimum_out_degree=0,
        require_counterexample=False,
        target_symmetry=False,
        fixed_adjacency=adjacency,
    )
    solver = _new_solver(seconds=2.0, workers=1, seed=0)
    status = solver.Solve(artifacts.model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise AssertionError(f"pinned oriented graph was rejected: {solver.StatusName(status)}")
    _check_model_indicators(solver, artifacts, adjacency)

    counter_model = build_model(
        n,
        minimum_out_degree=0,
        require_counterexample=True,
        target_symmetry=False,
        fixed_adjacency=adjacency,
    )
    counter_solver = _new_solver(seconds=2.0, workers=1, seed=0)
    counter_status = counter_solver.Solve(counter_model.model)
    feasible = counter_status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
    if feasible != bool(scalar["is_counterexample"]):
        raise AssertionError(
            "strict-cardinality predicate mismatch: "
            f"model={feasible}, scalar={scalar['is_counterexample']}"
        )


def _cyclic_k18_minus_matching() -> Adjacency:
    """An 8-out-regular target-order calibration graph in canonical form."""
    n = 18
    adjacency = [[0] * n for _ in range(n)]
    for i in range(n):
        for step in range(1, 9):
            adjacency[i][(i + step) % n] = 1
    validate_adjacency(adjacency)
    return adjacency


def calibrate(full: bool) -> dict[str, object]:
    """Run deterministic calibration; never perform an unpinned search."""
    checked = 0

    # Every oriented graph on three vertices: 3 choices per unordered pair.
    for states in itertools.product(range(3), repeat=3):
        _check_pinned_graph(_adjacency_from_pair_states(3, states))
        checked += 1

    # On four vertices, full mode covers all 3^6=729 graphs.  Quick mode uses
    # deterministic random cases plus a directed cycle and a transitive
    # tournament, which deliberately exercise direct-and-two-step overlap.
    if full:
        four_states = itertools.product(range(3), repeat=6)
    else:
        rng = random.Random(20260721)
        samples = [tuple(rng.randrange(3) for _ in range(6)) for _ in range(32)]
        samples.extend(
            [
                (1, 0, 2, 1, 0, 1),
                (1, 1, 1, 1, 1, 1),
            ]
        )
        four_states = iter(samples)
    for states in four_states:
        _check_pinned_graph(_adjacency_from_pair_states(4, states))
        checked += 1

    # Invalid inputs must fail before reaching CP-SAT.
    loop = [[1, 0], [0, 0]]
    digon = [[0, 1], [1, 0]]
    for invalid in (loop, digon):
        try:
            build_model(
                2,
                minimum_out_degree=0,
                require_counterexample=False,
                target_symmetry=False,
                fixed_adjacency=invalid,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid loop/digon input was accepted")

    # Exercise the target-only symmetry constraints on a known canonical
    # 8-out-regular oriented graph.  It is not asserted to be a counterexample.
    target = _cyclic_k18_minus_matching()
    target_model = build_model(
        18,
        minimum_out_degree=8,
        require_counterexample=False,
        target_symmetry=True,
        fixed_adjacency=target,
    )
    target_solver = _new_solver(seconds=5.0, workers=1, seed=0)
    target_status = target_solver.Solve(target_model.model)
    if target_status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise AssertionError(
            f"safe target symmetry rejected canonical graph: "
            f"{target_solver.StatusName(target_status)}"
        )
    _check_model_indicators(target_solver, target_model, target)

    return {
        "status": "CALIBRATION_OK",
        "full": full,
        "pinned_oriented_graphs": checked,
        "invalid_graphs_rejected": 2,
        "target_symmetry_graph_checked": True,
    }


def solve_target(args: argparse.Namespace) -> dict[str, object]:
    """Run an explicitly requested model search and replay any model found."""
    artifacts = build_model(
        args.n,
        minimum_out_degree=args.minimum_out_degree,
        require_counterexample=True,
        target_symmetry=not args.no_target_symmetry,
    )
    solver = _new_solver(args.seconds, args.workers, args.seed)
    solver.parameters.log_search_progress = args.log_search_progress
    status = solver.Solve(artifacts.model)
    status_name = solver.StatusName(status)
    base: dict[str, object] = {
        "solver_status": status_name,
        "wall_time_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "n": args.n,
        "minimum_out_degree_constraint": args.minimum_out_degree,
        "target_symmetry": not args.no_target_symmetry,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        adjacency = extract_adjacency(solver, artifacts, args.n)
        _check_model_indicators(solver, artifacts, adjacency)
        scalar = scalar_definition(adjacency)
        if not scalar["is_counterexample"]:
            raise AssertionError("CP-SAT witness failed scalar counterexample replay")
        if scalar["minimum_out_degree"] < args.minimum_out_degree:
            raise AssertionError("CP-SAT witness failed scalar minimum-degree replay")
        base.update(
            {
                "status": "SAT_CANDIDATE_SCALAR_REPLAY_OK",
                "adjacency_list": [
                    sorted(w for w, value in enumerate(row) if value)
                    for row in adjacency
                ],
                "ledger": scalar["ledger"],
            }
        )
    elif status == cp_model.INFEASIBLE:
        # CP-SAT does not emit a proof artifact here.  Never upgrade this label
        # to a mathematical UNSAT theorem without a separate checked proof.
        base["status"] = "INFEASIBLE_UNCHECKED"
    else:
        base["status"] = "NO_HIT"
    return base


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--calibrate", action="store_true")
    mode.add_argument("--solve", action="store_true")
    parser.add_argument(
        "--full",
        action="store_true",
        help="with --calibrate, exhaust all 729 oriented graphs on four vertices",
    )
    parser.add_argument("--n", type=int, default=18)
    parser.add_argument("--minimum-out-degree", type=int, default=8)
    parser.add_argument("--seconds", type=float, default=60.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260721)
    parser.add_argument("--no-target-symmetry", action="store_true")
    parser.add_argument("--log-search-progress", action="store_true")
    args = parser.parse_args(argv)
    if args.calibrate and args.no_target_symmetry:
        parser.error("--no-target-symmetry is a solve-only option")
    if args.solve and args.full:
        parser.error("--full is a calibration-only option")
    if args.workers < 1 or args.workers > 64:
        parser.error("--workers must lie in [1,64]")
    if args.seconds <= 0:
        parser.error("--seconds must be positive")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = calibrate(args.full) if args.calibrate else solve_target(args)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
