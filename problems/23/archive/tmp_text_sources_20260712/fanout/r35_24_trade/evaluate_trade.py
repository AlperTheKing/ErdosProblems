"""Exact collision-defect search on the real R35 24-vertex cage.

The source relation is the no-common-blue P1/P3/strict-P4/P5 union used by
CollisionDefectGraphAdapter.  All graph predicates and matching capacities
are integral.  The emitted JSON certificate is replayed independently by
verify_certificate.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path


N = 24
LEFT = (0, 1, 2)
RIGHT = (3, 4, 5)
C_LEFT, OWNER, C_RIGHT = 6, 7, 8
A_LEFT = (9, 10, 11)
Z_LEFT = (12, 13, 14)
MID = (15, 16, 17)
Z_RIGHT = (18, 19, 20)
A_RIGHT = (21, 22, 23)
HERE = Path(__file__).resolve().parent


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def construct():
    edges = set()

    def add(x, y):
        edges.add(edge(x, y))

    def link(xs, ys):
        for x in xs:
            for y in ys:
                add(x, y)

    for x in LEFT:
        add(x, C_LEFT)
    add(C_LEFT, OWNER)
    add(OWNER, C_RIGHT)
    for y in RIGHT:
        add(C_RIGHT, y)
    link(LEFT, RIGHT)
    link(LEFT, A_LEFT)
    link(A_LEFT, Z_LEFT)
    link(Z_LEFT, MID)
    link(MID, Z_RIGHT)
    link(Z_RIGHT, A_RIGHT)
    link(A_RIGHT, RIGHT)
    for x in A_LEFT + MID:
        add(OWNER, x)
    for x in Z_LEFT[:2]:
        add(C_RIGHT, x)
    bads = [edge(x, y) for x in LEFT for y in RIGHT]
    bads += [edge(A_LEFT[i], A_RIGHT[i]) for i in range(3)]
    for x, y in bads[9:]:
        add(x, y)
    displayed = [(x, C_LEFT, OWNER, C_RIGHT, y) for x in LEFT for y in RIGHT]
    displayed += [(A_LEFT[i], Z_LEFT[i], MID[i], Z_RIGHT[i], A_RIGHT[i]) for i in range(3)]
    side0 = set(LEFT + RIGHT + (OWNER,) + Z_LEFT + Z_RIGHT)
    side = [0 if v in side0 else 1 for v in range(N)]
    blue = {e for e in edges if side[e[0]] != side[e[1]]}
    bad = {e for e in edges if side[e[0]] == side[e[1]]}
    assert bad == set(bads)
    return edges, blue, bad, bads, displayed


EDGES, BLUE, BAD, BADS, DISPLAYED_ROWS = construct()


def adjacency(edges):
    out = [set() for _ in range(N)]
    for x, y in edges:
        out[x].add(y)
        out[y].add(x)
    return out


BLUE_ADJ = adjacency(BLUE)


def distances(start):
    dist = [-1] * N
    dist[start] = 0
    queue = deque([start])
    while queue:
        x = queue.popleft()
        for y in BLUE_ADJ[x]:
            if dist[y] < 0:
                dist[y] = dist[x] + 1
                queue.append(y)
    return dist


def shortest_rows(x, y):
    dx = distances(x)
    dy = distances(y)
    assert dx[y] == 4
    layers = [[v for v in range(N) if dx[v] == i and dx[v] + dy[v] == 4] for i in range(5)]
    rows = []
    for a in layers[1]:
        if a not in BLUE_ADJ[x]:
            continue
        for b in layers[2]:
            if b not in BLUE_ADJ[a]:
                continue
            for c in layers[3]:
                if c in BLUE_ADJ[b] and y in BLUE_ADJ[c]:
                    rows.append((x, a, b, c, y))
    return sorted(rows)


ROW_FAMILIES = [shortest_rows(*bad) for bad in BADS]
DISPLAYED = tuple(ROW_FAMILIES[i].index(row) for i, row in enumerate(DISPLAYED_ROWS))
RADICES = tuple(len(rows) for rows in ROW_FAMILIES)


class DSU:
    def __init__(self):
        self.p = list(range(N))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, x, y):
        x, y = self.find(x), self.find(y)
        if x != y:
            self.p[max(x, y)] = min(x, y)


@dataclass
class OutsideSystem:
    comp: list[int]
    vertices: list[tuple[int, ...]]
    boundary: list[tuple[int, ...]]
    loss: list[int]
    cross: Counter

    def union_loss(self, i, j):
        if i == j:
            return self.loss[i]
        return self.loss[i] + self.loss[j] - 2 * self.cross[edge(i, j)]


SIGNED_DEGREE = [0] * N
EDGE_SIGN = {}
for sign, edges in ((1, BLUE), (-1, BAD)):
    for x, y in edges:
        SIGNED_DEGREE[x] += sign
        SIGNED_DEGREE[y] += sign
        EDGE_SIGN[edge(x, y)] = sign


def outside_system(excluded):
    comp = [-1] * N
    vertices, boundary = [], []
    for root in range(N):
        if root in excluded or comp[root] >= 0:
            continue
        cid = len(vertices)
        comp[root] = cid
        vs, bd = [], set()
        queue = deque([root])
        while queue:
            x = queue.popleft()
            vs.append(x)
            for y in BLUE_ADJ[x]:
                if y in excluded:
                    bd.add(y)
                elif comp[y] < 0:
                    comp[y] = cid
                    queue.append(y)
        vertices.append(tuple(sorted(vs)))
        boundary.append(tuple(sorted(bd)))
    internal = [0] * len(vertices)
    cross = Counter()
    for sign, edges in ((1, BLUE), (-1, BAD)):
        for x, y in edges:
            cx, cy = comp[x], comp[y]
            if cx < 0 or cy < 0:
                continue
            if cx == cy:
                internal[cx] += sign
            else:
                cross[edge(cx, cy)] += sign
    loss = [sum(SIGNED_DEGREE[x] for x in vs) - 2 * internal[i] for i, vs in enumerate(vertices)]
    return OutsideSystem(comp, vertices, boundary, loss, cross)


class Dinic:
    def __init__(self, n):
        self.g = [[] for _ in range(n)]

    def add(self, u, v, cap):
        a = [v, cap, None]
        b = [u, 0, a]
        a[2] = b
        self.g[u].append(a)
        self.g[v].append(b)
        return a

    def maxflow(self, source, sink):
        flow = 0
        while True:
            level = [-1] * len(self.g)
            level[source] = 0
            q = deque([source])
            while q:
                u = q.popleft()
                for v, cap, _ in self.g[u]:
                    if cap and level[v] < 0:
                        level[v] = level[u] + 1
                        q.append(v)
            if level[sink] < 0:
                break
            it = [0] * len(self.g)

            def send(u, amount):
                if u == sink:
                    return amount
                while it[u] < len(self.g[u]):
                    arc = self.g[u][it[u]]
                    v, cap, rev = arc
                    if cap and level[v] == level[u] + 1:
                        got = send(v, min(amount, cap))
                        if got:
                            arc[1] -= got
                            rev[1] += got
                            return got
                    it[u] += 1
                return 0

            while True:
                got = send(source, 10**9)
                if not got:
                    break
                flow += got
        reachable = {source}
        q = deque([source])
        while q:
            u = q.popleft()
            for v, cap, _ in self.g[u]:
                if cap and v not in reachable:
                    reachable.add(v)
                    q.append(v)
        return flow, reachable


def tuple_rank(state):
    rank = 0
    scale = 1
    for value, radix in zip(state, RADICES):
        rank += value * scale
        scale *= radix
    return rank


def evaluate(state, certificate=False, include_common_blue=False):
    rows = [ROW_FAMILIES[i][state[i]] for i in range(len(BADS))]
    selected = set().union(*map(set, rows))
    support = {edge(row[i], row[i + 1]) for row in rows for i in range(4)}
    active_edges = {e for e in BLUE if e[0] in selected and e[1] in selected and e not in support}
    dsu = DSU()
    for x, y in active_edges:
        dsu.union(x, y)
    active_roots = {dsu.find(x) for x, y in BAD if x in selected and y in selected and dsu.find(x) == dsu.find(y)}
    active = {x for x in selected if dsu.find(x) in active_roots}
    component_label = {x: min(y for y in active if dsu.find(y) == dsu.find(x)) for x in active}

    occurrences = [[[] for _ in range(N)] for _ in range(N)]
    for atom, row in enumerate(rows):
        for x in row:
            for y in row:
                occurrences[x][y].append(atom)
    pair = [[len(occurrences[x][y]) for y in range(N)] for x in range(N)]
    obligations = []
    for owner in sorted(active):
        for other in range(N):
            for copy in range(max(0, pair[owner][other] - 1)):
                for half in range(2):
                    obligations.append((owner, other, occurrences[owner][other][copy + 1], copy + 1, copy, half, component_label[owner]))
    demand = Counter(d[0] for d in obligations)

    p4 = outside_system(selected)
    p5 = outside_system(active)
    eligible = {}
    for owner in demand:
        root = dsu.find(owner)
        owner_comp = component_label[owner]

        def component_ids(system):
            return tuple(i for i, bd in enumerate(system.boundary)
                         if any(a in active and dsu.find(a) == root and pair[owner][a] > 0 for a in bd))

        p4ids, p5ids = component_ids(p4), component_ids(p5)
        keys = set()
        for x in range(N):
            for y in range(N):
                if x == y or pair[x][y] != 0:
                    continue
                loss = SIGNED_DEGREE[x] + SIGNED_DEGREE[y] - 2 * EDGE_SIGN.get(edge(x, y), 0)
                rel = x == owner or (pair[owner][x] > 0 and pair[owner][y] > 0 and loss >= 0)
                if include_common_blue:
                    rel = rel or (
                        edge(x, owner) in BLUE
                        and edge(y, owner) in BLUE
                        and loss >= 2
                    )
                cx4, cy4 = p4.comp[x], p4.comp[y]
                if cx4 in p4ids and cy4 in p4ids and p4.union_loss(cx4, cy4) >= 0:
                    rel = True
                cx5, cy5 = p5.comp[x], p5.comp[y]
                if cx5 in p5ids and cy5 in p5ids and p5.union_loss(cx5, cy5) >= 0:
                    rel = True
                if not rel:
                    continue
                for half in (0, 1):
                    reserved = half == 0 and edge(x, y) in active_edges and x in active
                    if not reserved:
                        keys.add((x, y, half))
        eligible[owner] = keys

    # Every source base used by two halves must stay in one component.  On
    # this cage all positive-demand owners encountered by the certified trade
    # lie in one active component, so ordinary integral max flow is exact.
    demand_components = {component_label[o] for o in demand}
    if len(demand_components) > 1:
        raise RuntimeError(f"multi-component state requires MILP: {sorted(demand_components)}")
    owners = sorted(demand)
    keys = sorted(set().union(*(eligible[o] for o in owners))) if owners else []
    s = 0
    owner0 = 1
    key0 = owner0 + len(owners)
    t = key0 + len(keys)
    flow = Dinic(t + 1)
    owner_arcs = {}
    assignment_arcs = {}
    for i, owner in enumerate(owners):
        owner_arcs[owner] = flow.add(s, owner0 + i, demand[owner])
        for j, key in enumerate(keys):
            if key in eligible[owner]:
                assignment_arcs[(owner, key)] = flow.add(owner0 + i, key0 + j, 1)
    for j in range(len(keys)):
        flow.add(key0 + j, t, 1)
    matched, reachable = flow.maxflow(s, t)
    defect = len(obligations) - matched
    result = {
        "state": list(state), "rows": [list(row) for row in rows],
        "tuple_rank": tuple_rank(state), "demand": len(obligations),
        "matched": matched, "defect": defect,
        "active_vertices": sorted(active), "active_edges": sorted(map(list, active_edges)),
        "active_component_labels": sorted(demand_components),
        "owner_demand": {str(o): demand[o] for o in owners},
        "owner_available": {str(o): len(eligible[o]) for o in owners},
    }
    if certificate:
        assignments = []
        by_owner = {o: iter([d for d in obligations if d[0] == o]) for o in owners}
        for (owner, key), arc in assignment_arcs.items():
            if arc[2][1]:
                assignments.append({"obligation": list(next(by_owner[owner])), "source": list(key)})
        shore_owners = [owners[i] for i in range(len(owners)) if owner0 + i in reachable]
        reachable_keys = [keys[j] for j in range(len(keys)) if key0 + j in reachable]
        hall_neighborhood = sorted(set().union(*(eligible[o] for o in shore_owners))) if shore_owners else []
        cut_capacity = len(obligations) - sum(demand[o] for o in shore_owners) + len(hall_neighborhood)
        assert cut_capacity == matched
        result["assignments"] = assignments
        result["mincut"] = {
            "shore_owners": shore_owners,
            "reachable_source_keys": [list(k) for k in reachable_keys],
            "hall_neighborhood": [list(k) for k in hall_neighborhood],
            "shore_demand": sum(demand[o] for o in shore_owners),
            "shore_reach": len(hall_neighborhood),
            "capacity": cut_capacity,
        }
    return result


def search():
    cache = {}

    def ev(state):
        state = tuple(state)
        if state not in cache:
            cache[state] = evaluate(state)
        return cache[state]

    old = ev(DISPLAYED)
    best = old
    frontier = [DISPLAYED]
    visited = {DISPLAYED}
    # Exact breadth/beam search through simultaneous choices.  Retain the
    # lexicographically best states by (defect, tuple rank, demand).
    for depth in range(1, 7):
        candidates = []
        for state in frontier:
            for atom, radix in enumerate(RADICES):
                for choice in range(radix):
                    if choice == state[atom]:
                        continue
                    nxt = list(state)
                    nxt[atom] = choice
                    nxt = tuple(nxt)
                    if nxt in visited:
                        continue
                    visited.add(nxt)
                    try:
                        value = ev(nxt)
                    except RuntimeError:
                        continue
                    candidates.append(nxt)
                    if (value["defect"], value["tuple_rank"], value["demand"]) < (best["defect"], best["tuple_rank"], best["demand"]):
                        best = value
                    if value["defect"] == 0:
                        return old, value, len(cache), depth
        candidates.sort(key=lambda st: (ev(st)["defect"], ev(st)["tuple_rank"], ev(st)["demand"]))
        frontier = candidates[:400]
        if not frontier:
            break
    # Deterministic random restarts if the structured beam did not close.
    rng = random.Random(230024)
    state = tuple(best["state"])
    for step in range(20000):
        if step % 200 == 0:
            state = tuple(rng.randrange(r) for r in RADICES)
        nxt = list(state)
        atom = rng.randrange(len(RADICES))
        nxt[atom] = rng.randrange(RADICES[atom])
        nxt = tuple(nxt)
        try:
            value = ev(nxt)
        except RuntimeError:
            continue
        if value["defect"] == 0:
            return old, value, len(cache), "random"
        current = ev(state)
        if (value["defect"], value["demand"], value["tuple_rank"]) <= (current["defect"], current["demand"], current["tuple_rank"]):
            state = nxt
        if (value["defect"], value["tuple_rank"]) < (best["defect"], best["tuple_rank"]):
            best = value
    return old, best, len(cache), "exhausted-budget"


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay-state", type=Path)
    args = parser.parse_args()
    if args.replay_state:
        state = tuple(json.loads(args.replay_state.read_text())["new"]["state"])
        print(canonical_json(evaluate(state, certificate=True)), end="")
        return
    old, new, evaluated, depth = search()
    payload = {
        "schema": "r35-real24-no-common-blue-collision-trade-v1",
        "graph": {"n": N, "edges": sorted(map(list, EDGES)), "blue": sorted(map(list, BLUE)), "bad_order": list(map(list, BADS))},
        "row_family_sizes": list(RADICES), "displayed_state": list(DISPLAYED),
        "search": {"states_evaluated": evaluated, "closure_depth": depth},
        "old": evaluate(DISPLAYED, certificate=True),
        "new": evaluate(tuple(new["state"]), certificate=True),
    }
    payload["trade"] = {
        "changed_atoms": [i for i in range(len(BADS)) if payload["old"]["state"][i] != payload["new"]["state"][i]],
        "defect_improves": payload["new"]["defect"] < payload["old"]["defect"],
        "defect_nonincreasing": payload["new"]["defect"] <= payload["old"]["defect"],
        "tuple_rank_decreases": payload["new"]["tuple_rank"] < payload["old"]["tuple_rank"],
        "zero_defect_exists": payload["new"]["defect"] == 0,
    }
    text = canonical_json(payload)
    (HERE / "certificate.json").write_bytes(text.encode("ascii"))
    print(text, end="")
    print("certificate_sha256=" + hashlib.sha256(text.encode("ascii")).hexdigest())


if __name__ == "__main__":
    main()
