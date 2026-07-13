#!/usr/bin/env python3
"""Forcing landscape of a zero-vector fixture: for every support edge e,
is there a profile-consistent row selection leaving e latent (unused)?

Profile constraints (owner o, active x0) as in the engine's scope stage:
  one row per chosen atom; r(owner) = t; star edges (o,y) selected for
  y != x0; (o,x0) NOT selected; every pair {x0,y} covered by a selected row;
  x0 occurs in some selected row.
No capture requirement -- this isolates SELECTION-FORCING from capture.
Output: per-edge status LATENT_OK / FORCED (INFEASIBLE).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx
from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
from verify_tN_hit import all_atoms, norm


def solve_profile_with_latent(graph, atoms, chosen, owner, active, t, latent_edge, workers=8, time_limit=120.0):
    model = cp_model.CpModel()
    row_selected = {}
    for i in chosen:
        variables = [
            model.new_bool_var(f"r_{i}_{j}") for j in range(len(atoms[i]["rows"]))
        ]
        model.add(sum(variables) == 1)
        row_selected[i] = variables

    def row_terms(predicate):
        return [
            row_selected[i][j]
            for i in chosen
            for j, row in enumerate(atoms[i]["rows"])
            if predicate(tuple(row))
        ]

    def uses_edge(row, e):
        return e in {norm(row[k], row[k + 1]) for k in range(4)}

    neighbours = sorted(graph[owner])
    model.add(sum(row_terms(lambda row: owner in row)) == t)
    # star edges selected / active edge latent
    for y in neighbours:
        e = norm(owner, y)
        uses = row_terms(lambda row, ee=e: uses_edge(row, ee))
        if y == active:
            model.add(sum(uses) == 0)
        else:
            model.add(sum(uses) >= 1)
            model.add(
                sum(row_terms(lambda row, yy=y: active in row and yy in row)) >= 1
            )
    model.add(sum(row_terms(lambda row: active in row)) >= 1)
    # the probed edge stays latent
    lat = row_terms(lambda row, ee=latent_edge: uses_edge(row, ee))
    model.add(sum(lat) == 0)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    return solver.status_name(status)


def main():
    src = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    t = src["t"]
    left_n, right_n = src["left"], src["right"]
    hit = src["hits"][int(sys.argv[2]) if len(sys.argv) > 3 else 0]
    graph = nx.from_graph6_bytes(hit["graph6"].encode("ascii"))
    atoms = all_atoms(graph, left_n, right_n)
    atom_index = {(a["shore"], a["u"], a["v"]): i for i, a in enumerate(atoms)}
    chosen = [atom_index[(r["shore"], r["u"], r["v"])] for r in hit["selectedAtoms"]]
    owner_key = sorted(hit["selectionMeta"]["localClassifiers"])[0]
    owner = int(owner_key)
    active = hit["selectionMeta"]["localClassifiers"][owner_key]["activeNeighbour"]

    support_edges = sorted(norm(*e) for e in graph.edges())
    out = {"owner": owner, "active": active, "edges": {}}
    for e in support_edges:
        status = solve_profile_with_latent(
            graph, atoms, chosen, owner, active, t, e
        )
        verdict = "LATENT_OK" if status in ("OPTIMAL", "FEASIBLE") else (
            "FORCED" if status == "INFEASIBLE" else status
        )
        out["edges"]["%d-%d" % e] = verdict
        print(e, verdict, flush=True)
    forced = [e for e, v in out["edges"].items() if v == "FORCED"]
    latent_ok = [e for e, v in out["edges"].items() if v == "LATENT_OK"]
    out["forcedCount"] = len(forced)
    out["latentOkCount"] = len(latent_ok)
    out["latentOkEdges"] = latent_ok
    print("FORCED:", len(forced), "LATENT_OK:", len(latent_ok))
    print("latent-possible edges:", latent_ok)
    Path(sys.argv[-1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
