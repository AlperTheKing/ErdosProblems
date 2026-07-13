"""Exact post-check around an MILP search for the 24-vertex row system.

The MILP only finds a candidate.  The reported objective and all row-family
facts are recomputed with integers from the selected rows.
"""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tmp/fanout/r35_endpoint_diversity/check_real_endpoint_floor_obstruction.py"


def load_fixture():
    spec = importlib.util.spec_from_file_location("endpoint_fixture", FIXTURE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    m = load_fixture()
    bads = list(m.INTENDED_BAD)
    families = [m.shortest_rows(*bad) for bad in bads]
    pairs = [(x, y) for x in range(m.N) for y in range(x + 1, m.N)]

    # Exact, solver-independent positive-defect certificate for an empty
    # realization relation.  Each of the nine main rows contains 8 and one
    # of only three possible predecessors.  If their multiplicities are
    # n_7,n_12,n_13, then sum(max(n_z-1,0)) >= 9-3 = 6.
    main_families = families[:9]
    assert all(row[3] == 8 for rows in main_families for row in rows)
    assert all(row[2] in {7, 12, 13} for rows in main_families for row in rows)
    exact_pair_excess_lower_bound = 9 - 3
    exact_collision_half_lower_bound = 2 * exact_pair_excess_lower_bound

    choices = [(i, j) for i, rows in enumerate(families) for j in range(len(rows))]
    choice_col = {choice: k for k, choice in enumerate(choices)}
    excess_col = {pair: len(choices) + k for k, pair in enumerate(pairs)}
    nvars = len(choices) + len(pairs)

    # One row per atom, and excess[p] >= number of selected rows containing p - 1.
    A = lil_matrix((len(bads) + len(pairs), nvars), dtype=float)
    lb = np.full(A.shape[0], -np.inf)
    ub = np.full(A.shape[0], np.inf)
    for i, rows in enumerate(families):
        for j in range(len(rows)):
            A[i, choice_col[i, j]] = 1
        lb[i] = ub[i] = 1
    for k, pair in enumerate(pairs):
        row_index = len(bads) + k
        for i, rows in enumerate(families):
            for j, row in enumerate(rows):
                if pair[0] in row and pair[1] in row:
                    A[row_index, choice_col[i, j]] = 1
        A[row_index, excess_col[pair]] = -1
        ub[row_index] = 1

    objective = np.zeros(nvars)
    for pair in pairs:
        objective[excess_col[pair]] = 1
    lower = np.zeros(nvars)
    upper = np.ones(nvars)
    upper[len(choices) :] = len(bads) - 1
    integrality = np.ones(nvars)

    result = milp(
        objective,
        integrality=integrality,
        bounds=Bounds(lower, upper),
        constraints=LinearConstraint(A.tocsr(), lb, ub),
        options={"time_limit": 300, "mip_rel_gap": 0.0},
    )
    assert result.x is not None, result.message
    selected_indices = []
    selected_rows = []
    for i, rows in enumerate(families):
        hits = [j for j in range(len(rows)) if result.x[choice_col[i, j]] > 0.5]
        assert len(hits) == 1
        selected_indices.append(hits[0])
        selected_rows.append(rows[hits[0]])

    counts = Counter(
        tuple(sorted((x, y)))
        for row in selected_rows
        for p, x in enumerate(row)
        for y in row[p + 1 :]
    )
    excess = sum(max(0, count - 1) for count in counts.values())
    collision_halves = 2 * excess
    assert abs(result.fun - excess) < 1e-7

    print(f"solver_status={result.status} success={result.success} message={result.message}")
    print(f"atoms={len(bads)} choices={len(choices)} pair_coordinates={len(pairs)}")
    print(
        "exact_forced_pair_excess_lower_bound="
        f"{exact_pair_excess_lower_bound} "
        f"exact_forced_collision_half_lower_bound={exact_collision_half_lower_bound}"
    )
    print(f"minimum_pair_excess={excess} collision_halves={collision_halves}")
    print(f"selected_indices={selected_indices}")
    for bad, row in zip(bads, selected_rows):
        print(f"{bad}: {row}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
