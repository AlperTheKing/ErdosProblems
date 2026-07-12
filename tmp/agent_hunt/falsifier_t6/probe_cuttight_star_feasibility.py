#!/usr/bin/env python3
"""Support-stage-only feasibility of CUT-TIGHT DOUBLE-STAR supports:
rooted tN support model + outward(N_B(v) u N_B(m)) >= 2t.  Exact CP-SAT.
Answers: at which (t, l, r) does the outward >= 2t regime exist at all?
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
from rooted_tN_support_cp_sat import build_rooted_support_model
from sweep_t6_cuttight_star import add_cuttight_star_constraint


def probe(left, right, t, time_limit=90.0, workers=8):
    try:
        model, edge = build_rooted_support_model(left, right, t)
    except ValueError as exc:
        return {"status": "GUARD", "detail": str(exc)}
    add_cuttight_star_constraint(model, edge, left, right, t)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 1
    status = solver.solve(model)
    return {"status": solver.status_name(status)}


def main():
    out = {}
    # t=5 archived-fixture territory: orders 18-21.
    for l, r in [(9, 9), (10, 8), (10, 9), (10, 10), (11, 9), (11, 10), (12, 9)]:
        out[f"t5:{l}+{r}"] = probe(l, r, 5)
        print(f"t5:{l}+{r}: {out[f't5:{l}+{r}']}", flush=True)
    # t=6: across the window.
    for l, r in [
        (10, 10), (11, 10), (12, 9), (12, 10), (12, 12), (13, 9),
        (13, 10), (13, 13), (14, 10), (14, 14), (15, 15),
    ]:
        out[f"t6:{l}+{r}"] = probe(l, r, 6)
        print(f"t6:{l}+{r}: {out[f't6:{l}+{r}']}", flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
