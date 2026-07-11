"""Exact PG(2,4) unique-row falsifier gate for global-minimum collision Hall.

The 21 lines of PG(2,4) form a 2-(21,5,1) design.  We search for a two-
coloring with every line split 2/3 and choose one alternating C5 on every
line.  The resulting 21 C5 edge sets are pairwise edge-disjoint.  Therefore,
if their union is triangle-free and the displayed blue graph is connected,
the displayed cut is maximum: every cut leaves at least one monochromatic
edge on each of the 21 edge-disjoint odd cycles.

If each displayed bad edge has its displayed four-edge blue path as its
unique shortest blue geodesic, the complete row database is singleton.  The
sole row tuple is then automatically a global score minimizer.  Since every
ordered pair of distinct points lies on exactly one selected row, there are
no FreeHalf sources, while every diagonal has multiplicity five and creates
eight CollisionHalf demands.  Such an instance exactly falsifies the global-
minimum collision-Hall route (not Erdos #23).
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

from ortools.sat.python import cp_model

from _codex_r19_global_base_census import edge, evaluate_rows, multiplicities
from _h import Bconn, geos


def gf_add(a: int, b: int) -> int:
    return a ^ b


def gf_mul(a: int, b: int) -> int:
    a0, a1 = a & 1, (a >> 1) & 1
    b0, b1 = b & 1, (b >> 1) & 1
    c0 = a0 & b0
    c1 = (a0 & b1) ^ (a1 & b0)
    c2 = a1 & b1
    return (c0 ^ c2) | ((c1 ^ c2) << 1)


def gf_inv(a: int) -> int:
    assert a
    return next(b for b in range(1, 4) if gf_mul(a, b) == 1)


def normalize(vector: tuple[int, int, int]) -> tuple[int, int, int]:
    pivot = next(value for value in vector if value)
    inverse = gf_inv(pivot)
    return tuple(gf_mul(inverse, value) for value in vector)


def dot(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    value = 0
    for x, y in zip(a, b):
        value = gf_add(value, gf_mul(x, y))
    return value


def projective_plane():
    vectors = tuple(product(range(4), repeat=3))
    points = tuple(sorted({normalize(v) for v in vectors if any(v)}))
    forms = tuple(sorted({normalize(v) for v in vectors if any(v)}))
    assert len(points) == len(forms) == 21
    lines = tuple(
        tuple(index for index, point in enumerate(points) if dot(form, point) == 0)
        for form in forms
    )
    assert all(len(line) == 5 for line in lines)
    pair_lines = {
        pair: tuple(i for i, line in enumerate(lines) if set(pair) <= set(line))
        for pair in combinations(range(21), 2)
    }
    assert all(len(indices) == 1 for indices in pair_lines.values())
    assert all(sum(point in line for line in lines) == 5 for point in range(21))
    return points, lines


def solve_coloring(lines, blocked, workers, time_limit):
    model = cp_model.CpModel()
    color = [model.new_bool_var(f"color_{v}") for v in range(21)]
    model.add(color[0] == 0)
    for line in lines:
        total = sum(color[v] for v in line)
        model.add(total >= 2)
        model.add(total <= 3)
    for assignment in blocked:
        model.add(sum(color[v] if assignment[v] else 1 - color[v]
                      for v in range(21)) <= 20)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, solver.status_name(status)
    return tuple(solver.value(bit) for bit in color), solver.status_name(status)


def line_cycle_options(line, coloring):
    anchor = min(line)
    rest = tuple(v for v in line if v != anchor)
    options = {}
    for tail in permutations(rest):
        order = (anchor,) + tail
        edges = frozenset(edge(order[i], order[(i + 1) % 5]) for i in range(5))
        bad = tuple(e for e in edges if coloring[e[0]] == coloring[e[1]])
        if len(bad) != 1:
            continue
        canonical_order = min(order, (order[0],) + tuple(reversed(order[1:])))
        options.setdefault(edges, (canonical_order, bad[0]))
    return tuple(options.values())


def orientation_model(lines, coloring):
    options = tuple(line_cycle_options(line, coloring) for line in lines)
    assert all(options_line for options_line in options)
    model = cp_model.CpModel()
    choose = []
    for line_index, line_options in enumerate(options):
        variables = [model.new_bool_var(f"line_{line_index}_option_{j}")
                     for j in range(len(line_options))]
        model.add_exactly_one(variables)
        choose.append(variables)
    edge_var = {}
    for pair in combinations(range(21), 2):
        line_index = next(i for i, line in enumerate(lines)
                          if pair[0] in line and pair[1] in line)
        containing = [choose[line_index][j]
                      for j, (order, _bad) in enumerate(options[line_index])
                      if edge(pair[0], pair[1]) in {
                          edge(order[k], order[(k + 1) % 5]) for k in range(5)
                      }]
        variable = model.new_bool_var(f"edge_{pair[0]}_{pair[1]}")
        model.add(variable == sum(containing))
        edge_var[pair] = variable
    for triple in combinations(range(21), 3):
        model.add(sum(edge_var[edge(u, v)]
                      for u, v in combinations(triple, 2)) <= 2)
    return model, options, choose


def adjacency_of(edges):
    adjacency = [set() for _ in range(21)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def replay(lines, coloring, selected):
    cycles = []
    row_by_bad = {}
    graph_edges = set()
    bad_edges = set()
    for line_index, option_index in enumerate(selected):
        order, bad = line_cycle_options(lines[line_index], coloring)[option_index]
        cycle_edges = {edge(order[i], order[(i + 1) % 5]) for i in range(5)}
        assert not (graph_edges & cycle_edges)
        graph_edges |= cycle_edges
        bad_edges.add(bad)
        u, v = bad
        bad_position = next(i for i in range(5)
                            if edge(order[i], order[(i + 1) % 5]) == bad)
        path = tuple(order[(bad_position + 1 + j) % 5] for j in range(5))
        if path[0] != u:
            path = tuple(reversed(path))
        assert path[0] == u and path[-1] == v
        row_by_bad[bad] = path
        cycles.append(cycle_edges)
    assert len(graph_edges) == 105
    assert len(bad_edges) == 21
    rows = [row_by_bad[bad] for bad in sorted(bad_edges)]
    blue_edges = graph_edges - bad_edges
    adjacency = adjacency_of(graph_edges)
    triangle_free = not any(
        adjacency[u] & adjacency[v]
        for u, v in graph_edges
    )
    connected_blue = Bconn(21, adjacency, coloring)
    geodesic_counts = []
    complete_rows = []
    for bad, displayed in zip(sorted(bad_edges), rows):
        paths = tuple(tuple(path) for path in geos(
            adjacency, coloring, bad[0], bad[1]
        ))
        geodesic_counts.append(len(paths))
        complete_rows.append(paths)
        assert displayed in paths
    singleton = all(count == 1 for count in geodesic_counts)
    count = multiplicities(21, rows)
    distinct_pair_counts = {count[x][y] for x in range(21)
                            for y in range(21) if x != y}
    diagonal_counts = {count[x][x] for x in range(21)}
    info = {"adj": adjacency, "Bset": blue_edges, "Mset": bad_edges}
    match_status, _, match_detail = evaluate_rows(
        "PG24", 21, info, tuple(rows), "row-reserved"
    )
    return {
        "triangleFree": triangle_free,
        "blueConnected": connected_blue,
        "uniqueShortestRows": singleton,
        "geodesicCountHistogram": {
            str(value): geodesic_counts.count(value)
            for value in sorted(set(geodesic_counts))
        },
        "distinctPairCounts": sorted(distinct_pair_counts),
        "diagonalCounts": sorted(diagonal_counts),
        "matchingStatus": match_status,
        "matchingDetail": match_detail,
        "coloring": list(coloring),
        "selectedOptions": list(selected),
        "rows": [list(row) for row in rows],
        "edges": [list(e) for e in sorted(graph_edges)],
        "blueEdges": [list(e) for e in sorted(blue_edges)],
        "badEdges": [list(e) for e in sorted(bad_edges)],
        "maxCutCertifiedBy21EdgeDisjointC5": True,
    }


def search_orientations(lines, coloring, workers, time_limit, limit):
    model, _options, choose = orientation_model(lines, coloring)
    for _ in range(limit):
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = workers
        solver.parameters.max_time_in_seconds = time_limit
        status = solver.solve(model)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return None, solver.status_name(status)
        selected = tuple(next(j for j, var in enumerate(variables)
                              if solver.value(var))
                         for variables in choose)
        result = replay(lines, coloring, selected)
        if result["triangleFree"] and result["blueConnected"] \
                and result["uniqueShortestRows"]:
            return result, "FOUND"
        model.add(sum(choose[i][selected[i]] for i in range(21)) <= 20)
    return None, "ORIENTATION_LIMIT"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--colorings", type=int, default=64)
    parser.add_argument("--orientations", type=int, default=256)
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--output", type=Path,
                        default=Path("../../../tmp/codex_r22_pg24.json"))
    args = parser.parse_args()
    if not 1 <= args.workers <= 64:
        parser.error("--workers must be in [1,64]")
    _points, lines = projective_plane()
    blocked = []
    attempts = []
    falsifier = None
    final_status = "NO_COLORING"
    for _ in range(args.colorings):
        coloring, color_status = solve_coloring(
            lines, blocked, args.workers, args.time_limit
        )
        if coloring is None:
            final_status = color_status
            break
        blocked.append(coloring)
        result, orientation_status = search_orientations(
            lines, coloring, args.workers, args.time_limit, args.orientations
        )
        attempts.append({
            "coloring": list(coloring),
            "orientationStatus": orientation_status,
        })
        if result is not None:
            falsifier = result
            final_status = "FALSIFIED_GLOBAL_MIN_HALL"
            break
        final_status = orientation_status
    payload = {
        "design": "PG(2,4)",
        "points": 21,
        "blocks": 21,
        "parameters": vars(args) | {"output": str(args.output)},
        "coloringsTested": len(attempts),
        "status": final_status,
        "falsifier": falsifier,
        "attempts": attempts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="ascii")
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 1 if falsifier is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
