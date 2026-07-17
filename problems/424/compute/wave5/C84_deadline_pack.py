#!/usr/bin/env python3
"""Exact CP-SAT gate for deadline-respecting forward C65 path packings.

Commodity ``i`` must use a source-to-ground path entirely below the arrival
cutoff of the ``i``-th hard hole.  Unit seed edges and hard-source edges are
globally disjoint; splitless-source and unary edges have unlimited capacity.
Feasible output is independently replayable without OR-Tools.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "C84_global_dual_coarea.py"
SPEC = importlib.util.spec_from_file_location("c84_flow", SOURCE)
if not SPEC or not SPEC.loader:
    raise RuntimeError(f"cannot load {SOURCE}")
C84 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = C84
SPEC.loader.exec_module(C84)


def arcs_for(data, deadline: int) -> list[tuple[str, int, int, int | None]]:
    """Return (kind, from, to, witness), using -1/-2 for source/sink."""

    arcs: list[tuple[str, int, int, int | None]] = []
    for n in sorted(data.splitless):
        if n <= deadline:
            arcs.append(("splitless_source", -1, n, None))
    for n in sorted(data.hard):
        if n <= deadline:
            arcs.append(("hard_source", -1, n, None))
    for n in sorted(data.holes):
        if n > deadline:
            continue
        for target, witness in data.unary.get(n, ()):
            if target <= deadline:
                arcs.append(("unary", n, target, witness))
        child = 2 * n - 1
        if child <= deadline:
            if child in data.generated:
                arcs.append(("seed_to_ground", n, -2, child))
            elif child in data.holes:
                arcs.append(("seed", n, child, None))
    return arcs


def solve(limit: int, workers: int, seconds: float) -> dict:
    data = C84.arithmetic(limit)
    deadlines = sorted(data.hard)
    model = cp_model.CpModel()
    all_arcs: list[list[tuple[str, int, int, int | None]]] = []
    variables: list[list[cp_model.IntVar]] = []
    seed_uses: dict[tuple[int, int], list[cp_model.IntVar]] = {}
    hard_uses: dict[int, list[cp_model.IntVar]] = {}

    for commodity, deadline in enumerate(deadlines):
        arcs = arcs_for(data, deadline)
        all_arcs.append(arcs)
        local = [model.NewBoolVar(f"f_{commodity}_{index}") for index in range(len(arcs))]
        variables.append(local)
        incoming: dict[int, list[cp_model.IntVar]] = {}
        outgoing: dict[int, list[cp_model.IntVar]] = {}
        for index, (kind, u, v, witness) in enumerate(arcs):
            var = local[index]
            outgoing.setdefault(u, []).append(var)
            incoming.setdefault(v, []).append(var)
            if kind in ("seed", "seed_to_ground"):
                child = v if kind == "seed" else int(witness)
                seed_uses.setdefault((u, child), []).append(var)
            elif kind == "hard_source":
                hard_uses.setdefault(v, []).append(var)

        model.Add(sum(outgoing.get(-1, ())) == 1)
        model.Add(sum(incoming.get(-2, ())) == 1)
        for node in sorted(n for n in data.holes if n <= deadline):
            model.Add(sum(incoming.get(node, ())) == sum(outgoing.get(node, ())))

    for uses in seed_uses.values():
        model.Add(sum(uses) <= 1)
    for uses in hard_uses.values():
        model.Add(sum(uses) <= 1)
    model.Minimize(sum(var for local in variables for var in local))

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    status_name = solver.StatusName(status)
    output = {
        "schema_version": 1,
        "limit": limit,
        "hard_count": len(deadlines),
        "status": status_name,
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "wall_time_seconds": solver.WallTime(),
        "paths": [],
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return output

    for commodity, (deadline, arcs, local) in enumerate(zip(deadlines, all_arcs, variables)):
        chosen = [arcs[index] for index, var in enumerate(local) if solver.Value(var)]
        by_from: dict[int, tuple[str, int, int, int | None]] = {}
        for arc in chosen:
            if arc[1] in by_from:
                raise RuntimeError("chosen flow branches; objective should remove cycles")
            by_from[arc[1]] = arc
        path: list[dict] = []
        node = -1
        seen: set[int] = set()
        while node != -2:
            if node in seen or node not in by_from:
                raise RuntimeError("chosen commodity is not a simple path")
            seen.add(node)
            kind, u, v, witness = by_from[node]
            step = {"kind": kind, "from": u, "to": v}
            if witness is not None:
                step["witness"] = witness
            path.append(step)
            node = v
        output["paths"].append(
            {"commodity": commodity, "deadline": deadline, "steps": path}
        )
    verify(output)
    return output


def verify(certificate: dict) -> dict:
    if certificate["status"] not in ("OPTIMAL", "FEASIBLE"):
        return {
            "limit": int(certificate["limit"]),
            "status": certificate["status"],
            "verified_feasible": False,
        }
    limit = int(certificate["limit"])
    data = C84.arithmetic(limit)
    deadlines = sorted(data.hard)
    if len(certificate["paths"]) != len(deadlines):
        raise RuntimeError("path count mismatch")
    used_seed: set[tuple[int, int]] = set()
    used_hard: set[int] = set()
    for expected, record in zip(deadlines, certificate["paths"]):
        deadline = int(record["deadline"])
        if deadline != expected:
            raise RuntimeError("deadline order mismatch")
        current = -1
        for step in record["steps"]:
            kind = step["kind"]
            u, v = int(step["from"]), int(step["to"])
            if u != current:
                raise RuntimeError("noncontiguous path")
            if kind == "splitless_source":
                if u != -1 or v not in data.splitless or v > deadline:
                    raise RuntimeError("invalid splitless source")
            elif kind == "hard_source":
                if u != -1 or v not in data.hard or v > deadline or v in used_hard:
                    raise RuntimeError("invalid hard source")
                used_hard.add(v)
            elif kind == "unary":
                witness = int(step["witness"])
                if (v, witness) not in data.unary.get(u, ()) or v > deadline:
                    raise RuntimeError("invalid unary arc")
                if u + 1 != v * witness or v == witness:
                    raise RuntimeError("invalid unary arithmetic")
            elif kind in ("seed", "seed_to_ground"):
                child = v if kind == "seed" else int(step["witness"])
                if child != 2 * u - 1 or child > deadline:
                    raise RuntimeError("invalid seed arithmetic")
                if (u, child) in used_seed:
                    raise RuntimeError("seed edge reused")
                used_seed.add((u, child))
                if kind == "seed" and v not in data.holes:
                    raise RuntimeError("internal seed target is not a hole")
                if kind == "seed_to_ground" and (v != -2 or child not in data.generated):
                    raise RuntimeError("terminal seed target is not grounded")
            else:
                raise RuntimeError(f"unknown step kind {kind}")
            current = v
        if current != -2:
            raise RuntimeError("path does not reach ground")
    return {
        "limit": limit,
        "hard_count": len(deadlines),
        "used_seed_edges": len(used_seed),
        "used_hard_sources": len(used_hard),
        "verified_feasible": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--solve", type=int)
    mode.add_argument("--verify", type=Path)
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.solve is not None:
        if args.output is None:
            parser.error("--solve requires --output")
        certificate = solve(args.solve, args.workers, args.seconds)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")
        print(verify(certificate))
    else:
        certificate = json.loads(args.verify.read_text(encoding="utf-8"))
        print(verify(certificate))


if __name__ == "__main__":
    main()
