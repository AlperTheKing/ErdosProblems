"""Independent exact max-flow check for the only archived R29 Hall payload.

The archive exposes aggregate capacities, not the graph/row incidence payload.
This checker deliberately has no imports from the production helpers.
"""
from collections import deque
import json


OWNERS = ("r", "cL", "cR")
DEMAND = {v: 6651 for v in OWNERS}
SOURCE_POOLS = {"sameFirst": 17325, "rowCompanion": 2600}


def max_flow(vertices, edges, source, sink):
    residual = {u: {} for u in vertices}
    original = {}
    for u, v, capacity in edges:
        assert isinstance(capacity, int) and capacity >= 0
        residual[u][v] = residual[u].get(v, 0) + capacity
        residual[v].setdefault(u, 0)
        original[(u, v)] = original.get((u, v), 0) + capacity
    value = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in sorted(residual[u]):
                if residual[u][v] > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        increment = min(residual[parent[v]][v] for v in _path(parent, sink))
        v = sink
        while parent[v] is not None:
            u = parent[v]
            residual[u][v] -= increment
            residual[v][u] += increment
            v = u
        value += increment
    reachable = {source}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in sorted(residual[u]):
            if residual[u][v] > 0 and v not in reachable:
                reachable.add(v)
                queue.append(v)
    cut_edges = []
    for (u, v), capacity in sorted(original.items()):
        if u in reachable and v not in reachable:
            cut_edges.append({"from": u, "to": v, "capacity": capacity})
    return value, sorted(reachable), cut_edges


def _path(parent, sink):
    v = sink
    while parent[v] is not None:
        yield v
        v = parent[v]


def main():
    source, sink = "SOURCE", "SINK"
    pools = tuple(SOURCE_POOLS)
    vertices = (source,) + OWNERS + pools + (sink,)
    total_demand = sum(DEMAND.values())
    infinity = total_demand + 1
    edges = [(source, v, DEMAND[v]) for v in OWNERS]
    edges += [(v, p, infinity) for v in OWNERS for p in pools]
    edges += [(p, sink, SOURCE_POOLS[p]) for p in pools]
    value, source_side, cut_edges = max_flow(vertices, edges, source, sink)
    cut_capacity = sum(e["capacity"] for e in cut_edges)
    record = {
        "scope": {"owners": list(OWNERS)},
        "archived_aggregate_input": {
            "collision_demand_per_owner": 6650,
            "hit_need_per_owner": 1,
            "total_demand_per_owner": 6651,
            "source_pools": SOURCE_POOLS,
        },
        "exact_totals": {
            "demand": total_demand,
            "flow": value,
            "cut_capacity": cut_capacity,
            "deficiency": total_demand - value,
        },
        "min_cut": {
            "source_side": source_side,
            "sink_side": sorted(set(vertices) - set(source_side)),
            "crossing_edges": cut_edges,
        },
        "assertions": {
            "demand_is_19953": total_demand == 19953,
            "reach_is_19925": value == 19925,
            "gap_is_28": total_demand - value == 28,
            "maxflow_equals_cut": value == cut_capacity,
        },
    }
    assert all(record["assertions"].values())
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
