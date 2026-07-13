#!/usr/bin/env python3
"""Exact selected-row check for two simultaneous fully covered t=5 owners."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ortools.sat.python import cp_model


def norm(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def solve_profiles(source: dict, workers: int, time_limit: float):
    hit = source["hit"]
    support_edges = {norm(*edge) for edge in hit["supportEdges"]}
    adjacency = {v: set() for v in range(source["left"] + source["right"])}
    for u, v in support_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    atoms = hit["selectedAtoms"]

    if len(adjacency[0]) != 5 or len(adjacency[1]) != 5:
        raise AssertionError("rooted owners are not degree five")

    def attempt(specification: list[tuple[int, int]]):
        model = cp_model.CpModel()
        choose = []
        for i, atom in enumerate(atoms):
            row_vars = [model.new_bool_var(f"r_{i}_{j}") for j in range(len(atom["rows"]))]
            model.add(sum(row_vars) == 1)
            choose.append(row_vars)

        def rows_with(predicate):
            return [
                choose[i][j]
                for i, atom in enumerate(atoms)
                for j, row in enumerate(atom["rows"])
                if predicate(tuple(row))
            ]

        for owner, active in specification:
            model.add(sum(rows_with(lambda row, o=owner: o in row)) == 5)
            active_edge = norm(owner, active)
            model.add(
                sum(
                    rows_with(
                        lambda row, e=active_edge: e
                        in {norm(row[k], row[k + 1]) for k in range(4)}
                    )
                )
                == 0
            )
            model.add(sum(rows_with(lambda row, x=active: x in row)) >= 1)
            for neighbour in adjacency[owner] - {active}:
                edge = norm(owner, neighbour)
                model.add(
                    sum(
                        rows_with(
                            lambda row, e=edge: e
                            in {norm(row[k], row[k + 1]) for k in range(4)}
                        )
                    )
                    >= 1
                )
                model.add(
                    sum(
                        rows_with(
                            lambda row, x=active, y=neighbour: x in row and y in row
                        )
                    )
                    >= 1
                )

        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = min(workers, 8)
        solver.parameters.max_time_in_seconds = time_limit
        solver.parameters.random_seed = 1
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None
        return {
            "activeNeighbours": {str(owner): active for owner, active in specification},
            "selectedRows": [
                list(atom["rows"][next(j for j, var in enumerate(choose[i]) if solver.value(var))])
                for i, atom in enumerate(atoms)
            ],
            "solverStatus": solver.status_name(status),
        }

    individual = {}
    for owner in [0, 1]:
        individual[str(owner)] = None
        for active in sorted(adjacency[owner]):
            witness = attempt([(owner, active)])
            if witness is not None:
                individual[str(owner)] = witness
                break

    joint = None
    for active_v in sorted(adjacency[0]):
        for active_m in sorted(adjacency[1]):
            joint = attempt([(0, active_v), (1, active_m)])
            if joint is not None:
                break
        if joint is not None:
            break
    return {"individual": individual, "joint": joint}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--time-limit", type=float, default=30.0)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")
    source = json.loads(args.payload.read_text(encoding="utf-8"))
    profiles = solve_profiles(source, args.workers, args.time_limit)
    result = {
        "schema": "t5-two-owner-fully-covered-profile-v1",
        "sourceCanonicalSha256": source["canonicalSha256"],
        "individualProfiles": profiles["individual"],
        "jointWitness": profiles["joint"],
        "verdict": (
            "PASS_TWO_OWNER_FULLY_COVERED_PROFILE"
            if profiles["joint"] is not None
            else "NO_TWO_OWNER_FULLY_COVERED_PROFILE"
        ),
    }
    result["canonicalSha256"] = canonical_sha(result)
    output = args.payload.with_name(args.payload.stem + "_profiles.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
