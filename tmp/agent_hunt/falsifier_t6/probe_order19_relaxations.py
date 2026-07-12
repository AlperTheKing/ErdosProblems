#!/usr/bin/env python3
"""Which constraint kills t=6 rooted supports at order 19?

For each order-19 cell (l,r) with l>=8, r>=7 relax, one at a time:
  A: drop the >= t^2 total d4-pair requirement
  B: drop the owner >= t d4-partner requirements
  C: drop both
Exact CP-SAT; 60s cap per solve.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
import rooted_tN_support_cp_sat as eng


def build(left_n, right_n, t, drop_total, drop_owner):
    # Rebuild the model but with switchable d4 aggregate constraints.
    model = cp_model.CpModel()
    edge = {
        (u, r): model.new_bool_var(f"e_{u}_{r}")
        for u in range(left_n)
        for r in range(right_n)
    }
    model.add(sum(edge.values()) == t * t - 1)
    for key in [(2, 0), (0, 0), (1, 0), (0, 1), (1, 1), (3, 1)]:
        model.add(edge[key] == 1)
    model.add(sum(edge[0, r] for r in range(right_n)) == t)
    model.add(sum(edge[1, r] for r in range(right_n)) == t)
    for u in range(left_n):
        model.add(sum(edge[u, r] for r in range(right_n)) >= 1)
    for r in range(right_n):
        model.add(sum(edge[u, r] for u in range(left_n)) >= 1)
    node_count = left_n + right_n
    outflow = [[] for _ in range(node_count)]
    inflow = [[] for _ in range(node_count)]
    for u in range(left_n):
        for r in range(right_n):
            rr = left_n + r
            f_lr = model.new_int_var(0, node_count - 1, f"flr_{u}_{r}")
            f_rl = model.new_int_var(0, node_count - 1, f"frl_{u}_{r}")
            model.add(f_lr <= (node_count - 1) * edge[u, r])
            model.add(f_rl <= (node_count - 1) * edge[u, r])
            outflow[u].append(f_lr)
            inflow[rr].append(f_lr)
            outflow[rr].append(f_rl)
            inflow[u].append(f_rl)
    model.add(sum(outflow[0]) - sum(inflow[0]) == node_count - 1)
    for z in range(node_count):
        if z != 0:
            model.add(sum(inflow[z]) - sum(outflow[z]) == 1)

    has2_left = {}
    for u in range(left_n):
        for w in range(u + 1, left_n):
            wit = [
                eng.and2(model, edge[u, r], edge[w, r], f"l2w_{u}_{w}_{r}")
                for r in range(right_n)
            ]
            has2_left[u, w] = model.new_bool_var(f"l2_{u}_{w}")
            model.add_max_equality(has2_left[u, w], wit)
    has2_right = {}
    for r in range(right_n):
        for s in range(r + 1, right_n):
            wit = [
                eng.and2(model, edge[u, r], edge[u, s], f"r2w_{r}_{s}_{u}")
                for u in range(left_n)
            ]
            has2_right[r, s] = model.new_bool_var(f"r2_{r}_{s}")
            model.add_max_equality(has2_right[r, s], wit)

    def l2(u, w):
        return has2_left[min(u, w), max(u, w)]

    def r2(r, s):
        return has2_right[min(r, s), max(r, s)]

    d4_left = {}
    for u in range(left_n):
        for w in range(u + 1, left_n):
            via = [
                eng.and2(model, l2(u, z), l2(z, w), f"l4w_{u}_{w}_{z}")
                for z in range(left_n)
                if z not in {u, w}
            ]
            p4 = model.new_bool_var(f"l4p_{u}_{w}")
            model.add_max_equality(p4, via)
            d4 = model.new_bool_var(f"l4_{u}_{w}")
            model.add(d4 <= p4)
            model.add(d4 + l2(u, w) <= 1)
            model.add(d4 >= p4 - l2(u, w))
            d4_left[u, w] = d4
    d4_right = {}
    for r in range(right_n):
        for s in range(r + 1, right_n):
            via = [
                eng.and2(model, r2(r, z), r2(z, s), f"r4w_{r}_{s}_{z}")
                for z in range(right_n)
                if z not in {r, s}
            ]
            p4 = model.new_bool_var(f"r4p_{r}_{s}")
            model.add_max_equality(p4, via)
            d4 = model.new_bool_var(f"r4_{r}_{s}")
            model.add(d4 <= p4)
            model.add(d4 + r2(r, s) <= 1)
            model.add(d4 >= p4 - r2(r, s))
            d4_right[r, s] = d4

    def ld4(u, w):
        return d4_left[min(u, w), max(u, w)]

    model.add(ld4(2, 3) == 1)
    if not drop_owner:
        model.add(sum(ld4(0, u) for u in range(left_n) if u != 0) >= t)
        model.add(sum(ld4(1, u) for u in range(left_n) if u != 1) >= t)
    if not drop_total:
        model.add(sum(d4_left.values()) + sum(d4_right.values()) >= t * t)

    left_deg = [sum(edge[u, r] for r in range(right_n)) for u in range(left_n)]
    right_deg = [sum(edge[u, r] for u in range(left_n)) for r in range(right_n)]
    for u in range(4, left_n - 1):
        model.add(left_deg[u] >= left_deg[u + 1])
    for r in range(2, right_n - 1):
        model.add(right_deg[r] >= right_deg[r + 1])
    return model


def solve(model):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = 1
    return solver.status_name(solver.solve(model))


def main():
    t = 6
    out = {}
    for l, r in [(10, 9), (11, 8), (12, 7)]:
        cell = {}
        cell["full"] = solve(build(l, r, t, False, False))
        cell["dropTotalPairs"] = solve(build(l, r, t, True, False))
        cell["dropOwnerPartners"] = solve(build(l, r, t, False, True))
        cell["dropBoth"] = solve(build(l, r, t, True, True))
        out[f"{l}+{r}"] = cell
        print(f"{l}+{r}: {cell}", flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
