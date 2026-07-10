"""Exact local gate for internal off-support edges in ell=5 Hall obstructions.

For a minimal Hall obstruction with m bad atoms, the geodesic support F is a
connected bipartite graph with m-1 edges.  This gate adds one further blue edge
e inside V(F) and asks whether m distinct distance-four bad pairs can still:

* avoid e on every shortest path (so e is genuinely off-support);
* cover every edge of F at least twice;
* form a triangle-free bad-edge graph.

A witness is the exact local configuration needed to refute the candidate
rigidity statement "minimal ell=5 Hall obstructions have no internal
off-support blue edge".  Arithmetic is integer/bit-mask exact.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import deque
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

from _claude_d3_local_obstruction import GENG, parse_g6


NODE_CAP = 20_000_000


def bfs(adj, source):
    dist = [-1] * len(adj)
    dist[source] = 0
    queue = deque([source])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


def bipartition(adj):
    colour = [-1] * len(adj)
    colour[0] = 0
    queue = deque([0])
    while queue:
        x = queue.popleft()
        for y in adj[x]:
            if colour[y] < 0:
                colour[y] = 1 - colour[x]
                queue.append(y)
            elif colour[y] == colour[x]:
                return None
    return colour


def ceil_fraction(x):
    return -((-x.numerator) // x.denominator)


def endpoint_flow_hall_margin(n, offsupport, loads, ambient_n=None):
    """Exact Hall margin for routing unit edge loads to incident vertices.

    The source-edge/endpoint-sink network is feasible iff every vertex set U
    has |E[U]| <= sum_{v in U} max(0, N-T(v)).  This is the finite min-cut
    form, evaluated with Fraction throughout.
    """
    if ambient_n is None:
        ambient_n = n
    caps = [max(Fraction(0), Fraction(ambient_n) - loads[v])
            for v in range(n)]
    best = None
    best_mask = 0
    for mask in range(1 << n):
        induced = sum(1 for u, v in offsupport
                      if ((mask >> u) & 1) and ((mask >> v) & 1))
        capacity = sum(caps[v] for v in range(n) if (mask >> v) & 1)
        margin = capacity - induced
        if best is None or margin < best:
            best = margin
            best_mask = mask
    return best, best_mask, caps


def forced_external_vertices(n, blue_edges, bad_edges):
    """Lower bound forced by max-cut on any extension of the local core.

    For U inside the core, max-cut forces at least
    delta_M^core(U)-delta_B^core(U) external blue boundary edges. One external
    vertex contributes at most |U| of them. Maximize the resulting ceiling.
    """
    best = 0
    best_mask = 0
    best_deficit = 0
    for mask in range(1, (1 << n) - 1):
        size = mask.bit_count()
        blue = sum(((mask >> u) ^ (mask >> v)) & 1 for u, v in blue_edges)
        bad = sum(((mask >> u) ^ (mask >> v)) & 1 for u, v in bad_edges)
        deficit = bad - blue
        if deficit <= 0:
            continue
        bound = (deficit + size - 1) // size
        if bound > best:
            best, best_mask, best_deficit = bound, mask, deficit
    return best, best_mask, best_deficit


def two_clique_external_charge(n, blue_edges, bad_edges):
    """Exact outside-vertex lower bound from max-cut singleton inequalities.

    On each cut side choose either no vertex, one vertex, or the endpoints of
    one bad edge. Triangle-freeness lets an outside vertex have at most one
    blue neighbour in that chosen clique. The two outside cut sides are
    disjoint, so the two clique charges add.
    """
    adj = [[] for _ in range(n)]
    for u, v in blue_edges:
        adj[u].append(v)
        adj[v].append(u)
    colours = bipartition(adj)
    assert colours is not None
    blue_degree = [sum(v in e for e in blue_edges) for v in range(n)]
    bad_degree = [sum(v in e for e in bad_edges) for v in range(n)]
    deficit = [bad_degree[v] - blue_degree[v] for v in range(n)]
    choices = []
    total = 0
    for side in (0, 1):
        best = 0
        choice = ()
        for v in range(n):
            if colours[v] == side and deficit[v] > best:
                best, choice = deficit[v], (v,)
        for u, v in bad_edges:
            if colours[u] == side:
                value = deficit[u] + deficit[v]
                if value > best:
                    best, choice = value, (u, v)
        total += best
        choices.append(choice)
    return total, choices, deficit


def valid_offsupport_set(n, support_edges, bad_edges, offsupport):
    blue_edges = support_edges + list(offsupport)
    blue = [set() for _ in range(n)]
    full = [set() for _ in range(n)]
    for u, v in blue_edges:
        blue[u].add(v)
        blue[v].add(u)
        full[u].add(v)
        full[v].add(u)
    for u, v in bad_edges:
        full[u].add(v)
        full[v].add(u)
    if any(full[u] & full[v] for u in range(n) for v in full[u] if u < v):
        return False
    distances = [bfs(blue, s) for s in range(n)]
    for a, b in bad_edges:
        if distances[a][b] != 4:
            return False
        da, db = distances[a], distances[b]
        for u, v in offsupport:
            if da[u] + 1 + db[v] == 4 or da[v] + 1 + db[u] == 4:
                return False
    return True


def component_path_counterexample(n, support_edges, bad_edges, seed_chord,
                                  max_length=6, loads=None,
                                  require_hall_failure=False):
    """Find an off-support-only path joining a selected bad pair.

    With ``require_hall_failure``, retain only paths whose full off-support
    edge set also defeats fractional endpoint-slack routing.
    """
    adj = [[] for _ in range(n)]
    support_set = {tuple(sorted(e)) for e in support_edges}
    for u, v in support_edges:
        adj[u].append(v)
        adj[v].append(u)
    colours = bipartition(adj)
    assert colours is not None
    candidate = [set() for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if colours[u] != colours[v] and (u, v) not in support_set:
                candidate[u].add(v)
                candidate[v].add(u)

    for a, b in bad_edges:
        path = [a]
        used = {a}

        def extend(x, remaining):
            if remaining == 0:
                if x != b:
                    return None
                path_edges = {tuple(sorted((path[i], path[i + 1])))
                              for i in range(len(path) - 1)}
                offsupport = path_edges | {tuple(sorted(seed_chord))}
                if valid_offsupport_set(n, support_edges, bad_edges, offsupport):
                    hall = None
                    if require_hall_failure:
                        assert loads is not None
                        hall = endpoint_flow_hall_margin(n, offsupport, loads)
                        if hall[0] >= 0:
                            return None
                    result = {"badEdge": (a, b), "path": tuple(path),
                              "offSupport": sorted(offsupport)}
                    if hall is not None:
                        result["endpointFlowHallMargin"] = str(hall[0])
                        result["endpointFlowHallSet"] = [
                            v for v in range(n) if (hall[1] >> v) & 1]
                    return result
                return None
            for y in candidate[x]:
                if y in used:
                    continue
                if remaining == 1 and y != b:
                    continue
                used.add(y)
                path.append(y)
                partial_edges = {tuple(sorted((path[i], path[i + 1])))
                                 for i in range(len(path) - 1)}
                partial_offsupport = partial_edges | {tuple(sorted(seed_chord))}
                result = None
                if valid_offsupport_set(
                        n, support_edges, bad_edges, partial_offsupport):
                    result = extend(y, remaining - 1)
                if result is not None:
                    return result
                path.pop()
                used.remove(y)
            return None

        for length in range(6, max_length + 1, 2):
            result = extend(a, length)
            if result is not None:
                return result
    return None


def find_atoms_with_chord(task):
    g6, mode, component_max_length = task
    n, adj0, edges = parse_g6(g6)
    m = len(edges) + 1
    colours = bipartition(adj0)
    assert colours is not None
    edge_set = {tuple(sorted(e)) for e in edges}
    full = (1 << len(edges)) - 1

    for chord in ((u, v) for u in range(n) for v in range(u + 1, n)
                  if colours[u] != colours[v] and (u, v) not in edge_set):
        adj = [set(xs) for xs in adj0]
        adj[chord[0]].add(chord[1])
        adj[chord[1]].add(chord[0])
        dist = [bfs(adj, s) for s in range(n)]

        pairs = []
        for u in range(n):
            for v in range(u + 1, n):
                if dist[u][v] != 4:
                    continue
                du, dv = dist[u], dist[v]
                chord_used = ((du[chord[0]] + 1 + dv[chord[1]] == 4) or
                              (du[chord[1]] + 1 + dv[chord[0]] == 4))
                if chord_used:
                    continue
                support = 0
                for i, (x, y) in enumerate(edges):
                    if ((du[x] + 1 + dv[y] == 4) or
                            (du[y] + 1 + dv[x] == 4)):
                        support |= 1 << i
                paths = []

                def extend(x, path):
                    if x == v:
                        paths.append(tuple(path))
                        return
                    for y in adj[x]:
                        if du[y] == du[x] + 1 and du[y] + dv[y] == 4:
                            extend(y, path + [y])

                extend(u, [u])
                assert paths
                p0 = Fraction(sum(chord[0] in path for path in paths), len(paths))
                p1 = Fraction(sum(chord[1] in path for path in paths), len(paths))
                pvec = tuple(Fraction(sum(x in path for path in paths), len(paths))
                             for x in range(n))
                pairs.append(((u, v), support, p0, p1, pvec))

        if len(pairs) < m:
            continue
        total = 0
        for _, support, _, _, _ in pairs:
            total |= support
        if total != full:
            continue

        count = len(pairs)
        availability = [[0] * len(edges) for _ in range(count + 1)]
        for i in range(count - 1, -1, -1):
            support = pairs[i][1]
            for k in range(len(edges)):
                availability[i][k] = availability[i + 1][k] + ((support >> k) & 1)

        multiplicity = [0] * len(edges)
        bad_neighbours = [set() for _ in range(n)]
        chosen = []
        nodes = 0

        def dfs(i, need):
            nonlocal nodes
            nodes += 1
            if nodes > NODE_CAP:
                raise RuntimeError(f"node cap on {g6} chord={chord}")
            if need == 0:
                if not all(x >= 2 for x in multiplicity):
                    return None
                if mode == "any":
                    return list(chosen)
                loads = [5 * sum(pairs[k][2 + side] for k in chosen)
                         for side in range(2)]
                all_loads = [5 * sum(pairs[k][4][v] for k in chosen)
                             for v in range(n)]
                margins = [max(Fraction(0), Fraction(n) - load) - Fraction(1, 2)
                           for load in loads]
                if min(margins) >= 0:
                    return None
                if mode == "capacity":
                    return list(chosen)
                if mode == "flow":
                    hall_margin, _, _ = endpoint_flow_hall_margin(
                        n, {tuple(sorted(chord))}, all_loads)
                    return list(chosen) if hall_margin < 0 else None
                chosen_bad = [pairs[k][0] for k in chosen]
                if mode == "dichotomy":
                    component_ce = component_path_counterexample(
                        n, edges, chosen_bad, chord, component_max_length)
                    return list(chosen) if component_ce is not None else None
                if mode == "flowdichotomy":
                    component_ce = component_path_counterexample(
                        n, edges, chosen_bad, chord, component_max_length,
                        all_loads, True)
                    return list(chosen) if component_ce is not None else None
                if mode == "clique":
                    extension_lb, _, _ = two_clique_external_charge(
                        n, edges + [chord], chosen_bad)
                else:
                    extension_lb, _, _ = forced_external_vertices(
                        n, edges + [chord], chosen_bad)
                global_margins = [
                    max(Fraction(0), Fraction(n + extension_lb) - load) - Fraction(1, 2)
                    for load in loads
                ]
                return list(chosen) if min(global_margins) < 0 else None
            if count - i < need:
                return None
            for k in range(len(edges)):
                if multiplicity[k] + availability[i][k] < 2:
                    return None

            (u, v), support, _, _, _ = pairs[i]
            if not (bad_neighbours[u] & bad_neighbours[v]):
                bad_neighbours[u].add(v)
                bad_neighbours[v].add(u)
                for k in range(len(edges)):
                    multiplicity[k] += (support >> k) & 1
                chosen.append(i)
                result = dfs(i + 1, need - 1)
                if result is not None:
                    return result
                chosen.pop()
                for k in range(len(edges)):
                    multiplicity[k] -= (support >> k) & 1
                bad_neighbours[u].remove(v)
                bad_neighbours[v].remove(u)
            return dfs(i + 1, need)

        witness = dfs(0, m)
        if witness is not None:
            chosen_bad = [pairs[i][0] for i in witness]
            extension_lb, extension_mask, extension_deficit = forced_external_vertices(
                n, edges + [chord], chosen_bad)
            clique_lb, clique_choices, vertex_deficits = two_clique_external_charge(
                n, edges + [chord], chosen_bad)
            all_loads = [5 * sum(pairs[i][4][v] for i in witness)
                         for v in range(n)]
            component_ce = component_path_counterexample(
                n, edges, chosen_bad, chord, component_max_length,
                all_loads, mode == "flowdichotomy")
            hall_margin, hall_mask, hall_caps = endpoint_flow_hall_margin(
                n, {tuple(sorted(chord))}, all_loads)
            return {
                "g6": g6,
                "n": n,
                "m": m,
                "support": edges,
                "internalOffSupport": chord,
                "atoms": [pairs[i][0] for i in witness],
                "supports": [pairs[i][1] for i in witness],
                "endpointLoads": [str(5 * sum(pairs[i][2 + side] for i in witness))
                                  for side in range(2)],
                "endpointMargins": [
                    str(max(Fraction(0), Fraction(n) -
                            5 * sum(pairs[i][2 + side] for i in witness)) - Fraction(1, 2))
                    for side in range(2)
                ],
                "endpointFlowHallMargin": str(hall_margin),
                "endpointFlowHallSet": [v for v in range(n)
                                        if (hall_mask >> v) & 1],
                "vertexSlackCaps": [str(x) for x in hall_caps],
                "forcedExternalVertices": extension_lb,
                "forcingSet": [x for x in range(n) if (extension_mask >> x) & 1],
                "forcingDeficit": extension_deficit,
                "forcedGlobalMargins": [
                    str(max(Fraction(0), Fraction(n + extension_lb) -
                            5 * sum(pairs[i][2 + side] for i in witness)) - Fraction(1, 2))
                    for side in range(2)
                ],
                "twoCliqueCharge": clique_lb,
                "twoCliqueChoices": clique_choices,
                "vertexDeficits": vertex_deficits,
                "twoCliqueMargins": [
                    str(max(Fraction(0), Fraction(n + clique_lb) -
                            5 * sum(pairs[i][2 + side] for i in witness)) - Fraction(1, 2))
                    for side in range(2)
                ],
                "componentPathCounterexample": component_ce,
                "nodes": nodes,
            }
    return None


def graph_records(m):
    edge_count = m - 1
    records = []
    for n in range(5, edge_count + 2):
        if edge_count > (n * n) // 4:
            continue
        run = subprocess.run(
            [GENG, "-q", "-c", "-b", str(n), f"{edge_count}:{edge_count}"],
            capture_output=True, text=True, check=True,
        )
        records.extend(x for x in run.stdout.splitlines() if x.strip())
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mlo", type=int, default=9)
    parser.add_argument("--mhi", type=int, default=11)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--mode",
                        choices=("any", "capacity", "flow", "global", "clique",
                                 "dichotomy", "flowdichotomy"),
                        default="any")
    parser.add_argument("--component-max-length", type=int, default=6)
    args = parser.parse_args()

    all_results = []
    for m in range(args.mlo, args.mhi + 1):
        records = graph_records(m)
        witnesses = []
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            tasks = [(record, args.mode, args.component_max_length) for record in records]
            for result in pool.map(find_atoms_with_chord, tasks, chunksize=4):
                if result is not None:
                    witnesses.append(result)
        row = {"m": m, "graphs": len(records), "witnesses": witnesses}
        all_results.append(row)
        print(json.dumps(row, separators=(",", ":")), flush=True)

    print("INTERNAL_OFFSUPPORT_GATE", json.dumps({
        "range": [args.mlo, args.mhi],
        "mode": args.mode,
        "graphs": sum(r["graphs"] for r in all_results),
        "witnesses": sum(len(r["witnesses"]) for r in all_results),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
