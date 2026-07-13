"""Exact global unreserved collision-Hall gate on the N=12 fixture.

The demand is every global collision half. Sources are actual off-diagonal
free ordered-pair halves. Eligibility uses P1, P3, and corrected common-blue;
P4/P5 are omitted, so a PASS is valid for the larger six-relation union while
a FAIL is only diagnostic.
"""

from collections import Counter, defaultdict, deque
from itertools import product
from pathlib import Path
import json
import networkx as nx
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "problems/23/writeup"))

from _h import dec, maxcut_all, gmin


G6 = "K??E@cyjFgWk"


def norm(u, v):
    return (u, v) if u < v else (v, u)


def main():
    n, edges = dec(G6)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    cuts = maxcut_all(n, [sorted(a) for a in adj])
    best = gmin(n, [sorted(a) for a in adj], cuts)
    assert best is not None
    side = best[0]
    blue = {norm(u, v) for u, v in edges if side[u] != side[v]}
    bad = sorted(norm(u, v) for u, v in edges if side[u] == side[v])

    badj = [sorted(w for w in adj[u] if side[w] != side[u]) for u in range(n)]

    def bfs(source):
        distance = [-1] * n
        distance[source] = 0
        queue = deque([source])
        while queue:
            x = queue.popleft()
            for y in badj[x]:
                if distance[y] < 0:
                    distance[y] = distance[x] + 1
                    queue.append(y)
        return distance

    def geodesics(source, target):
        ds, dt = bfs(source), bfs(target)
        distance = ds[target]
        rows = []

        def visit(path):
            x = path[-1]
            if x == target:
                rows.append(tuple(path))
                return
            for y in badj[x]:
                if ds[y] == ds[x] + 1 and dt[y] == distance - ds[y]:
                    visit(path + [y])

        visit([source])
        return distance, rows

    families = []
    for u, v in bad:
        distance, rows = geodesics(u, v)
        assert distance == 4
        families.append(rows)
    assert sorted(map(len, families)) == [5, 6, 8, 10]

    blue_adj = defaultdict(set)
    bad_adj = defaultdict(set)
    for u, v in blue:
        blue_adj[u].add(v)
        blue_adj[v].add(u)
    for u, v in bad:
        bad_adj[u].add(v)
        bad_adj[v].add(u)

    def d_blue_pair(x, y):
        return len(blue_adj[x]) + len(blue_adj[y]) - 2 * (y in blue_adj[x])

    def d_bad_pair(x, y):
        return len(bad_adj[x]) + len(bad_adj[y]) - 2 * (y in bad_adj[x])

    signed_degree = Counter()
    edge_sign = {}
    for edge in blue:
        edge_sign[edge] = 1
        signed_degree[edge[0]] += 1
        signed_degree[edge[1]] += 1
    for edge in bad:
        edge_sign[edge] = -1
        signed_degree[edge[0]] -= 1
        signed_degree[edge[1]] -= 1

    def state(rows):
        pair = Counter()
        for row in rows:
            for x in row:
                for y in row:
                    pair[x, y] += 1

        demand = {
            owner: 2 * sum(max(0, pair[owner, y] - 1) for y in range(n))
            for owner in range(n)
        }
        owners = [owner for owner in range(n) if demand[owner] > 0]
        source_owners = defaultdict(set)

        for owner in owners:
            # P1: same first coordinate.
            for y in range(n):
                if y == owner or pair[owner, y] != 0:
                    continue
                for half in (0, 1):
                    source_owners[(owner, y, half)].add(owner)

            # P3: row companions with nonnegative two-vertex cut slack.
            companions = [x for x in range(n) if x != owner and pair[owner, x] > 0]
            for x in companions:
                for y in companions:
                    if x == y or pair[x, y] != 0:
                        continue
                    edge = norm(x, y)
                    sigma_pair = (
                        signed_degree[x] + signed_degree[y]
                        - 2 * edge_sign.get(edge, 0)
                    )
                    if sigma_pair < 0:
                        continue
                    for half in (0, 1):
                        source_owners[(x, y, half)].add(owner)

            # P2/common-blue: corrected sigma >= 2 terminal.
            neighbours = sorted(blue_adj[owner])
            for i, x in enumerate(neighbours):
                for y in neighbours[i + 1:]:
                    if pair[x, y] != 0:
                        continue
                    if d_bad_pair(x, y) + 2 > d_blue_pair(x, y):
                        continue
                    for a, b in ((x, y), (y, x)):
                        for half in (0, 1):
                            source_owners[(a, b, half)].add(owner)

        worst_gap = 0
        worst = None
        for mask in range(1, 1 << len(owners)):
            shore = {owners[i] for i in range(len(owners)) if mask & (1 << i)}
            shore_demand = sum(demand[owner] for owner in shore)
            shore_reach = sum(bool(eligible & shore) for eligible in source_owners.values())
            gap = shore_demand - shore_reach
            if gap > worst_gap:
                worst_gap = gap
                worst = {
                    "owners": sorted(shore),
                    "demand": shore_demand,
                    "reach": shore_reach,
                }

        collision_units = sum(demand.values()) // 2
        free_offdiag = sum(
            x != y and pair[x, y] == 0 for x in range(n) for y in range(n)
        )
        graph = nx.DiGraph()
        source_node = ("source",)
        sink_node = ("sink",)
        for owner in owners:
            owner_node = ("owner", owner)
            graph.add_edge(source_node, owner_node, capacity=demand[owner])
        for key, eligible_owners in source_owners.items():
            key_node = ("key",) + key
            graph.add_edge(key_node, sink_node, capacity=1)
            for owner in eligible_owners:
                graph.add_edge(("owner", owner), key_node, capacity=1)
        max_flow = int(nx.maximum_flow_value(graph, source_node, sink_node))

        return {
            "collisionUnits": collision_units,
            "demand": sum(demand.values()),
            "freeOffDiagonalBases": free_offdiag,
            "sourceKeys": len(source_owners),
            "maxFlow": max_flow,
            "worstGap": worst_gap,
            "worst": worst,
        }

    total = 0
    failures = []
    passes = []
    states = []
    margin_histogram = Counter()
    minimum_margin = None
    minimum_choice = None
    for choice in product(*[range(len(rows)) for rows in families]):
        rows = tuple(families[i][choice[i]] for i in range(len(families)))
        result = state(rows)
        assert result["maxFlow"] == result["demand"] - result["worstGap"]
        states.append((choice, result))
        total += 1
        margin = -result["worstGap"]
        margin_histogram[margin] += 1
        if minimum_margin is None or margin < minimum_margin:
            minimum_margin = margin
            minimum_choice = choice
        if result["worstGap"] > 0:
            failures.append({"choice": choice, **result})
        else:
            passes.append({"choice": choice, **result})

    minimum_collision_units = min(result["collisionUnits"] for _, result in states)
    minimum_collision_states = [
        (choice, result) for choice, result in states
        if result["collisionUnits"] == minimum_collision_units
    ]
    minimum_collision_failures = [
        {"choice": choice, **result}
        for choice, result in minimum_collision_states if result["worstGap"] > 0
    ]

    output = {
        "graph6": G6,
        "n": n,
        "badEdges": bad,
        "familySizes": [len(rows) for rows in families],
        "tuples": total,
        "failures": failures,
        "passes": len(passes),
        "firstPassingState": passes[0] if passes else None,
        "minimumCollisionUnits": minimum_collision_units,
        "minimumCollisionTupleCount": len(minimum_collision_states),
        "minimumCollisionFailures": minimum_collision_failures,
        "minimumMargin": minimum_margin,
        "minimumChoice": minimum_choice,
        "marginHistogram": dict(sorted(margin_histogram.items())),
        "relation": ["P1", "P3", "corrected-common-blue"],
        "reservation": "none",
        "demandScope": "all-global-collision-halves",
    }
    output_path = Path(__file__).with_name("global_unreserved_n12_result.json")
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="ascii")

    print(
        f"tuples={total} passes={len(passes)} failures={len(failures)} "
        f"minimumMargin={minimum_margin}"
    )
    print(
        f"minimumCollisionUnits={minimum_collision_units} "
        f"minimumCollisionTuples={len(minimum_collision_states)} "
        f"minimumCollisionFailures={len(minimum_collision_failures)}"
    )
    if failures:
        print("smallest failure:", failures[0])
    if passes:
        print("first passing state:", passes[0])
        print("VERDICT=PASS_EXISTS_GLOBAL_UNRESERVED_P1_P3_COMMONBLUE")
        return 0
    print("VERDICT=FAIL_NO_FEASIBLE_TUPLE_IN_SUBRELATION")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
