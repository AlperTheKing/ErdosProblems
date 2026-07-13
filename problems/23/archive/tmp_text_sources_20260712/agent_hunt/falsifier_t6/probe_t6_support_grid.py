#!/usr/bin/env python3
"""Probe which (left,right) shores admit ANY rooted t=6 support graph
(35 edges, connected, two degree-6 owners, live atom, >= 6 d4-partners
per owner, >= 36 exact-distance-4 pairs).  Support-model feasibility only;
no circuit layer.  Exact CP-SAT; UNKNOWN = time capped, not a verdict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
from rooted_tN_support_cp_sat import (
    build_rooted_support_model,
    graph_from_solution,
    distance_four_atoms,
)


def probe(left: int, right: int, t: int, time_limit: float, workers: int):
    try:
        model, edge = build_rooted_support_model(left, right, t)
    except ValueError as exc:
        return {"status": "GUARD", "detail": str(exc)}
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    name = solver.status_name(status)
    record = {"status": name}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        graph = graph_from_solution(solver, edge, left, right)
        atoms = distance_four_atoms(graph, left, right)
        record["atomsAvailable"] = len(atoms)
        record["ownerVd4"] = sum(
            1 for a in atoms if a["shore"] == "L" and 0 in (a["u"], a["v"])
        )
        record["ownerMd4"] = sum(
            1 for a in atoms if a["shore"] == "L" and 1 in (a["u"], a["v"])
        )
    return record


def main() -> None:
    t = 6
    cells = []
    for left in range(8, 19):
        for right in range(7, 16):
            n = left + right
            if not 17 <= n <= 30:
                continue
            # Mantel-live for 36 bad edges split across shores.
            if (left * left) // 4 + (right * right) // 4 < 36:
                continue
            cells.append((left, right))
    out = {}
    for left, right in cells:
        record = probe(left, right, t, 45.0, 8)
        out[f"{left}+{right}"] = record
        print(f"{left}+{right}: {record}", flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
