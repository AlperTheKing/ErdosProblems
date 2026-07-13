"""Fixture loaders for the transversal-matroid hunt (exact, pure python).

Objects (each: n, shores (L,R), support edges (24), chosen atoms with complete
shortest-row families):
  - hit298 : t5_classifier_v_l9_r9_1000.json      (zero-vector hit #298)
  - hit264 : t5_live_x_classifier_v_l9_r9_5000.json (live-x zero-vector hit #264)
  - nearcand : R46 sec.8 18-vtx near-candidate (constructed; 30 atom triangles)
  - r46supp : R46 triangle-free support-level hit (graph6; atoms = its 25 selected? NOT
              available here -> we only use support graph + all distance-4 atoms lists)
  - t4abs  : abstract t=4 16/15 circuit (edge-set rows, no graph)
  - r34deg : abstract degenerate 5-atom/4-edge circuit (R34; identical singleton rows)
All arithmetic integer/rational. No floats anywhere.
"""

from __future__ import annotations

import json
from collections import deque
from itertools import combinations
from pathlib import Path

WS = Path(r"E:\Projects\ErdosProblems\tmp\fanout\r42_graph_specific_exclusion")


def norm(u, v):
    return (u, v) if u < v else (v, u)


# ---------------------------------------------------------------- graph6
def decode_graph6(s: str):
    data = [ord(c) - 63 for c in s]
    n = data[0]
    assert 0 <= n <= 62
    bits = []
    for byte in data[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    edges = []
    idx = 0
    for v in range(1, n):
        for u in range(v):
            if bits[idx]:
                edges.append((u, v))
            idx += 1
    return n, sorted(edges)


# ---------------------------------------------------------------- BFS rows
def adjacency(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return [sorted(a) for a in adj]


def bfs_dist(adj, src):
    n = len(adj)
    d = [-1] * n
    d[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] < 0:
                d[v] = d[u] + 1
                q.append(v)
    return d


def all_shortest_rows(adj, src, dst):
    """All shortest paths src->dst of length exactly 4, as vertex tuples."""
    d = bfs_dist(adj, src)
    assert d[dst] == 4
    out = []

    def dfs(path):
        u = path[-1]
        if len(path) == 5:
            if u == dst:
                out.append(tuple(path))
            return
        for v in adj[u]:
            if d[v] == d[u] + 1 and v not in path:
                dfs(path + (v,))

    dfs((src,))
    return sorted(out)


def row_edges(row):
    return frozenset(norm(row[k], row[k + 1]) for k in range(4))


class Circuit:
    """A support family: support edges + chosen atoms with complete row families."""

    def __init__(self, name, n, left, right, support_edges, atoms):
        # atoms: list of dicts {u, v, rows: [vertex tuples]} (u,v same shore)
        self.name = name
        self.n = n
        self.left = left      # list of left-shore vertices
        self.right = right
        self.support = sorted(norm(*e) for e in support_edges)
        self.support_set = set(self.support)
        self.atoms = atoms
        for a in atoms:
            a["rowEdges"] = [row_edges(r) for r in a["rows"]]
            a["footprint"] = frozenset().union(*a["rowEdges"]) if a["rows"] else frozenset()

    @property
    def n_atoms(self):
        return len(self.atoms)


def load_hit(path, name):
    src = json.loads(Path(path).read_text(encoding="utf-8"))
    hit = src["hit"]
    n, edges = decode_graph6(hit["graph6"])
    left_n, right_n = src["left"], src["right"]
    atoms = []
    for rec in hit["selectedAtoms"]:
        rows = sorted(tuple(r) for r in rec["rows"])
        atoms.append({"u": rec["u"], "v": rec["v"], "shore": rec["shore"], "rows": rows})
    c = Circuit(name, n, list(range(left_n)), list(range(left_n, left_n + right_n)),
                edges, atoms)
    c.meta = hit.get("selectionMeta", {})
    c.graph6 = hit["graph6"]
    # sanity: rows really are the complete shortest-row families
    adj = adjacency(n, c.support)
    for a in c.atoms:
        assert sorted(all_shortest_rows(adj, a["u"], a["v"])) == sorted(
            a["rows"]) or sorted(all_shortest_rows(adj, a["v"], a["u"])) == sorted(
            a["rows"]), (name, a["u"], a["v"])
    return c


def build_nearcand():
    """R46 sec 8: L = {v,m,a,b0..b4}, R = {x0..x4,y0..y4}; 24 edges:
    v,m -> all x_i; a -> x0..x3; a -> y_j; b_j -> y_j.
    25 atoms: v b_j, m b_j, b_i b_j, x4 y_j."""
    V, M, A = 0, 1, 2
    B = list(range(3, 8))          # b0..b4  (left shore)
    X = list(range(8, 13))         # x0..x4  (right shore)
    Y = list(range(13, 18))        # y0..y4  (right shore)
    edges = []
    for x in X:
        edges.append((V, x))
        edges.append((M, x))
    for x in X[:4]:
        edges.append((A, x))
    for y in Y:
        edges.append((A, y))
    for j in range(5):
        edges.append((B[j], Y[j]))
    assert len(edges) == 24
    n = 18
    adj = adjacency(n, edges)
    pairs = ([(V, b) for b in B] + [(M, b) for b in B]
             + [(b1, b2) for b1, b2 in combinations(B, 2)]
             + [(X[4], y) for y in Y])
    assert len(pairs) == 25
    atoms = []
    for u, v in pairs:
        rows = all_shortest_rows(adj, u, v)
        atoms.append({"u": u, "v": v,
                      "shore": "L" if u < 8 and v < 8 else "R",
                      "rows": rows})
    return Circuit("nearcand", n, list(range(8)), list(range(8, 18)), edges, atoms)


def build_r34deg():
    """R34 degenerate abstract circuit: 5 atoms sharing one singleton row
    (v,a,b,c,d): a path on 5 vertices, 4 edges; every footprint = all 4 edges.
    (Bare transversal circuit; real-graph impossible via anchoring.)"""
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
    row = (0, 1, 2, 3, 4)
    atoms = [{"u": 0, "v": 4, "shore": "?", "rows": [row]} for _ in range(5)]
    return Circuit("r34deg", 5, [0, 2, 4], [1, 3], edges, atoms)


def load_t4abs():
    src = json.loads((WS / "t4_support_circuit_hit.json").read_text())
    rows = src["rows"]  # 16 rows, each a 4-subset of 15 abstract edges
    # abstract: ground set 15 "edges" (indices); atoms = the 16 row-sets
    atoms = [{"u": -1, "v": -1, "shore": "?", "rows": [tuple(r)]} for r in rows]
    c = object.__new__(Circuit)
    c.name = "t4abs"
    c.n = 0
    c.left = []
    c.right = []
    c.support = list(range(15))
    c.support_set = set(c.support)
    c.atoms = atoms
    for a in c.atoms:
        a["rowEdges"] = [frozenset(a["rows"][0])]
        a["footprint"] = frozenset(a["rows"][0])
    return c


def load_all():
    out = {}
    out["hit298"] = load_hit(WS / "t5_classifier_v_l9_r9_1000.json", "hit298")
    out["hit264"] = load_hit(WS / "t5_live_x_classifier_v_l9_r9_5000.json", "hit264")
    out["nearcand"] = build_nearcand()
    out["r34deg"] = build_r34deg()
    out["t4abs"] = load_t4abs()
    return out


# ---------------------------------------------------------------- matching
def max_matching(left_ids, right_ids, adj_map):
    """Hopcroft-Karp-lite (Kuhn) exact bipartite matching.
    adj_map: left id -> iterable of right ids. Returns dict left->right."""
    match_l, match_r = {}, {}

    def try_kuhn(u, seen):
        for w in adj_map.get(u, ()):
            if w in seen:
                continue
            seen.add(w)
            if w not in match_r or try_kuhn(match_r[w], seen):
                match_l[u] = w
                match_r[w] = u
                return True
        return False

    for u in left_ids:
        try_kuhn(u, set())
    return match_l


if __name__ == "__main__":
    for name, c in load_all().items():
        rc = [len(a["rows"]) for a in c.atoms]
        print(name, "atoms", len(c.atoms), "support", len(c.support),
              "rowcounts", sorted(rc), "product~", 1 if not rc else
              __import__("math").prod(rc))
