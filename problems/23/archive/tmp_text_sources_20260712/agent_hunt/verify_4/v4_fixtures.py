"""verify_4 independent fixture loader (adversarial re-implementation).

Written from scratch against the PRIMARY sources:
  - engine hit JSONs (t5_classifier_v_l9_r9_1000.json / t5_live_x_classifier_v_l9_r9_5000.json)
  - engine verification JSONs (owner / activeNeighbour / sigma / switch)
  - R46 sec.8 text for the 18-vtx near-candidate
  - R39 sec.4-5 text for the 8-vtx rotor
No code shared with tmp/agent_hunt/matroid/fixtures.py beyond the graph6 spec.
Integer arithmetic only.
"""

import json
from collections import deque
from itertools import combinations
from pathlib import Path

WS = Path(r"E:\Projects\ErdosProblems\tmp\fanout\r42_graph_specific_exclusion")


def g6_decode(s):
    """graph6 -> (n, sorted edge list); independent implementation."""
    vals = [ord(ch) - 63 for ch in s.strip()]
    assert all(0 <= v <= 63 for v in vals), "bad graph6 char"
    n = vals[0]
    assert n <= 62
    need = (n * (n - 1) // 2 + 5) // 6
    assert len(vals) == 1 + need, (len(vals), need)
    bits = []
    for v in vals[1:]:
        bits.extend(((v >> k) & 1) for k in (5, 4, 3, 2, 1, 0))
    edges = []
    i = 0
    for col in range(1, n):
        for row in range(col):
            if bits[i]:
                edges.append((row, col))
            i += 1
    return n, sorted(edges)


def norm(u, v):
    return (u, v) if u < v else (v, u)


def make_adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs(adj, s):
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in d:
                d[w] = d[u] + 1
                q.append(w)
    return d


def shortest4paths(adj, u, v):
    """all simple shortest paths u->v when d(u,v)=4, as 5-tuples."""
    d = bfs(adj, u)
    assert d.get(v) == 4, (u, v, d.get(v))
    out = []
    stack = [(u,)]
    while stack:
        p = stack.pop()
        last = p[-1]
        if len(p) == 5:
            if last == v:
                out.append(p)
            continue
        for w in adj[last]:
            if d.get(w) == len(p) and w not in p:
                stack.append(p + (w,))
    return sorted(out)


class Fix:
    def __init__(self, name, n, edges, atoms, left=None, right=None):
        self.name = name
        self.n = n
        self.support = sorted(norm(*e) for e in edges)
        self.support_set = set(self.support)
        self.atoms = atoms  # list of (u, v, rows) with rows = list of 5-tuples
        self.left = left
        self.right = right


def load_hit(hit_json, verif_json, name):
    src = json.loads((WS / hit_json).read_text())
    ver = json.loads((WS / verif_json).read_text())
    hit = src["hit"]
    n, edges = g6_decode(hit["graph6"])
    adj = make_adj(n, edges)
    atoms = []
    for rec in hit["selectedAtoms"]:
        u, v, rows = rec["u"], rec["v"], sorted(tuple(r) for r in rec["rows"])
        mine = shortest4paths(adj, u, v)
        rev = sorted(tuple(reversed(r)) for r in mine)
        assert rows == mine or rows == rev, (name, u, v, "row family mismatch")
        atoms.append((u, v, rows))
    f = Fix(name, n, edges, atoms)
    f.graph6 = hit["graph6"]
    f.sigma = ver["minimumDisplayedCutSigma"]
    f.switch = sorted(ver["minimumDisplayedCutSwitch"])
    f.owner = ver.get("owner")
    f.activeNbr = ver.get("activeNeighbour")
    # shores: bipartition check via BFS 2-coloring
    color = {0: 0}
    q = deque([0])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in color:
                color[w] = 1 - color[u]
                q.append(w)
            else:
                assert color[w] != color[u], "not bipartite"
    f.left = sorted(x for x in range(n) if color[x] == 0)
    f.right = sorted(x for x in range(n) if color[x] == 1)
    return f


def build_nearcand():
    """R46 sec 8 verbatim: L={v,m,a,b0..b4}, R={x0..x4,y0..y4};
    edges: v,m -> all x_i; a -> x0..x3; a -> y_j; b_j -> y_j.
    atoms: v b_j, m b_j, b_i b_j, x4 y_j (25 distance-4 same-shore pairs)."""
    v, m, a = 0, 1, 2
    b = list(range(3, 8))
    x = list(range(8, 13))
    y = list(range(13, 18))
    edges = ([(v, xi) for xi in x] + [(m, xi) for xi in x]
             + [(a, xi) for xi in x[:4]] + [(a, yj) for yj in y]
             + [(b[j], y[j]) for j in range(5)])
    assert len(edges) == 24
    adj = make_adj(18, edges)
    pairs = ([(v, bj) for bj in b] + [(m, bj) for bj in b]
             + list(combinations(b, 2)) + [(x[4], yj) for yj in y])
    assert len(pairs) == 25
    atoms = [(u, w, shortest4paths(adj, u, w)) for (u, w) in pairs]
    f = Fix("nearcand", 18, edges, atoms, left=list(range(8)),
            right=list(range(8, 18)))
    return f


def build_rotor8():
    """R39 sec 4-5 verbatim. Vertices a,b,p,q,x,y,m,v (0..7 in this order).
    Blue: ax, yb, pm, vq + square xm, my, yv, vx. Bads: ab, pq.
    Rows: ab -> A_m=(a,x,m,y,b), A_v=(a,x,v,y,b); pq -> B_x=(p,m,x,v,q),
    B_y=(p,m,y,v,q)."""
    a, b, p, q, x, y, m, v = range(8)
    names = dict(zip("a b p q x y m v".split(), range(8)))
    blue = [(a, x), (y, b), (p, m), (v, q), (x, m), (m, y), (y, v), (v, x)]
    A_m = (a, x, m, y, b)
    A_v = (a, x, v, y, b)
    B_x = (p, m, x, v, q)
    B_y = (p, m, y, v, q)
    atoms = [(a, b, [A_m, A_v]), (p, q, [B_x, B_y])]
    f = Fix("rotor8", 8, blue, atoms)
    f.names = names
    f.state_tuples = {          # R39 four-state orbit
        "w_mx": (0, 0),   # {A_m, B_x}
        "w_my": (0, 1),   # {A_m, B_y}
        "w_vy": (1, 1),   # {A_v, B_y}
        "w_vx": (1, 0),   # {A_v, B_x}
    }
    # verify each row is a path in blue
    bs = set(norm(*e) for e in blue)
    for (u, w, rows) in atoms:
        for r in rows:
            assert r[0] == u and r[-1] == w and len(set(r)) == 5
            for k in range(4):
                assert norm(r[k], r[k + 1]) in bs
    return f


def load_all():
    h298 = load_hit("t5_classifier_v_l9_r9_1000.json",
                    "t5_classifier_v_l9_r9_hit_verification.json", "hit298")
    h264 = load_hit("t5_live_x_classifier_v_l9_r9_5000.json",
                    "t5_live_x_classifier_v_l9_r9_hit_verification.json",
                    "hit264")
    return {"hit298": h298, "hit264": h264, "nearcand": build_nearcand(),
            "rotor8": build_rotor8()}


if __name__ == "__main__":
    for name, f in load_all().items():
        rc = [len(r) for (_, _, r) in f.atoms]
        print(name, "n", f.n, "|support|", len(f.support), "atoms",
              len(f.atoms), "rows total", sum(rc),
              "sigma", getattr(f, "sigma", None),
              "switch", getattr(f, "switch", None))
