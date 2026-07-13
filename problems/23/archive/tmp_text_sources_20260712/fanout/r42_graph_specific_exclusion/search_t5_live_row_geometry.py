#!/usr/bin/env python3
"""Search the graph-only necessary row geometry of a live t=5 transition.

The source tuple has active edge vx and the target tuple has exactly one of
mx,my active.  Every selected row except the live A--B row is unchanged.
Consequently a non-live row used to cover a star pair must avoid both active
edges.  This search asks only whether the complete shortest-row database of a
24-edge rooted support graph contains the required avoiding rows.  A no-hit is
bounded evidence, not a proof.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

from ortools.sat.python import cp_model


HERE = Path(__file__).resolve().parent
GENERATOR = HERE / "rooted_t5_support_cp_sat.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("rooted_t5", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def path_edges(module, row):
    return {module.norm(row[i], row[i + 1]) for i in range(4)}


def avoiding_rows(module, atoms, live_key, pair, forbidden):
    rows = []
    for atom in atoms:
        atom_key = (atom["shore"], atom["u"], atom["v"])
        if atom_key == live_key:
            continue
        for row in atom["rows"]:
            if pair[0] not in row or pair[1] not in row:
                continue
            if path_edges(module, row).isdisjoint(forbidden):
                rows.append(
                    {
                        "atom": [atom["shore"], atom["u"], atom["v"]],
                        "row": list(row),
                    }
                )
    return rows


def live_geometry(module, graph, atoms, left_n):
    v, m = module.V, module.M
    x, y = left_n + module.X, left_n + module.Y
    live_key = ("L", min(module.A, module.B), max(module.A, module.B))
    source_pairs = [
        (x, s) for s in sorted(graph[v]) if s not in {x, y}
    ]

    failures = {}
    for target_active in [x, y]:
        forbidden = {
            module.norm(v, x),
            module.norm(m, target_active),
        }
        target_other_central = y if target_active == x else x
        target_pairs = [
            (target_active, s)
            for s in sorted(graph[m])
            if s not in {target_active, target_other_central}
        ]
        witnesses = {}
        missing = []
        safe_atoms = []
        for atom in atoms:
            atom_key = (atom["shore"], atom["u"], atom["v"])
            if atom_key == live_key:
                continue
            good = [
                list(row)
                for row in atom["rows"]
                if path_edges(module, row).isdisjoint(forbidden)
            ]
            if good:
                safe_atoms.append(
                    {"atom": [atom["shore"], atom["u"], atom["v"]], "rows": good}
                )
        if len(safe_atoms) < 24:
            missing.append(f"safeNonLiveAtoms:{len(safe_atoms)}")
        source_star_rows = []
        target_star_rows = []
        for atom in atoms:
            if v in {atom["u"], atom["v"]}:
                good = [
                    list(row)
                    for row in atom["rows"]
                    if module.norm(v, x) not in path_edges(module, row)
                ]
                if good:
                    source_star_rows.append(
                        {"atom": [atom["shore"], atom["u"], atom["v"]], "rows": good}
                    )
            if m in {atom["u"], atom["v"]}:
                good = [
                    list(row)
                    for row in atom["rows"]
                    if module.norm(m, target_active) not in path_edges(module, row)
                ]
                if good:
                    target_star_rows.append(
                        {"atom": [atom["shore"], atom["u"], atom["v"]], "rows": good}
                    )
        if len(source_star_rows) < 5:
            missing.append(f"sourceStarAtoms:{len(source_star_rows)}")
        if len(target_star_rows) < 5:
            missing.append(f"targetStarAtoms:{len(target_star_rows)}")
        for role, pairs in [("source", source_pairs), ("target", target_pairs)]:
            for pair in pairs:
                rows = avoiding_rows(module, atoms, live_key, pair, forbidden)
                key = f"{role}:{pair[0]}:{pair[1]}"
                if rows:
                    witnesses[key] = rows
                else:
                    missing.append(key)
        if not missing:
            return {
                "targetActive": target_active,
                "forbiddenEdges": [list(edge) for edge in sorted(forbidden)],
                "witnesses": witnesses,
                "safeNonLiveAtoms": safe_atoms,
                "sourceStarRows": source_star_rows,
                "targetStarRows": target_star_rows,
            }, failures
        failures[str(target_active)] = missing
    return None, failures


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", type=int, required=True)
    parser.add_argument("--right", type=int, required=True)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--time", type=float, default=20.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must lie in 1..8")

    module = load_generator()
    model, edge = module.build_rooted_support_model(
        args.left, args.right, False, False
    )
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = args.workers
    solver.parameters.max_time_in_seconds = args.time
    solver.parameters.random_seed = 1

    histogram = Counter()
    payload = {
        "schema": "t5-live-row-geometry-search-v1",
        "left": args.left,
        "right": args.right,
        "limit": args.limit,
        "workers": args.workers,
        "supportsSolved": 0,
        "supportsWithAtLeast25Atoms": 0,
        "missingPairHistogram": {},
        "hit": None,
        "scope": "bounded graph-only necessary-condition search; a no-hit is not proof",
    }

    for _ in range(args.limit):
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            payload["terminalStatus"] = solver.status_name(status)
            break
        payload["supportsSolved"] += 1
        graph = module.graph_from_solution(solver, edge, args.left, args.right)
        atoms = module.distance_four_atoms(graph, args.left, args.right)
        if len(atoms) >= 25:
            payload["supportsWithAtLeast25Atoms"] += 1
            hit, failures = live_geometry(module, graph, atoms, args.left)
            if hit is not None:
                payload["hit"] = {
                    "graph6": module.nx.to_graph6_bytes(
                        graph, header=False
                    ).decode("ascii").strip(),
                    "supportEdges": [list(e) for e in sorted(graph.edges())],
                    "atomCountAvailable": len(atoms),
                    "geometry": hit,
                }
                payload["verdict"] = "HIT_LIVE_AVOIDING_ROW_GEOMETRY"
                break
            for active, missing in failures.items():
                histogram[f"active={active};missing={len(missing)}"] += 1

        differences = [1 - var if solver.value(var) else var for var in edge.values()]
        model.add(sum(differences) >= 1)
    else:
        payload["terminalStatus"] = "LIMIT_REACHED"

    if payload["hit"] is None:
        payload["verdict"] = "NO_HIT_WITHIN_EXPLICIT_LIMIT"
    payload["missingPairHistogram"] = dict(sorted(histogram.items()))
    payload["canonicalSha256"] = canonical_sha(payload)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
