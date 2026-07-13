from collections import deque
from itertools import combinations

# Core: s,t,a1,a2,a3,b1,b2,b3; one private leaf per core vertex.
names = ["s", "t", "a1", "a2", "a3", "b1", "b2", "b3"]
core = {name: i for i, name in enumerate(names)}
leaves = {name: i + 8 for i, name in enumerate(names)}
N = 16

def edge(u, v):
    return (u, v) if u < v else (v, u)

P = [core[x] for x in ("s", "a1", "a2", "a3", "t")]
Q = [core[x] for x in ("s", "b1", "b2", "b3", "t")]
path_edges = {edge(u, v) for row in (P, Q) for u, v in zip(row, row[1:])}
pendants = {edge(core[x], leaves[x]) for x in names}
bad0 = {edge(core["s"], core["t"])}
E = path_edges | pendants | bad0
B0 = path_edges | pendants
assert len(E) == 17 and len(B0) == 16

def crossing(e, mask):
    u, v = e
    return ((mask >> u) & 1) != ((mask >> v) & 1)

def graph_adj(edges):
    adj = [[] for _ in range(N)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj

def connected(edges):
    adj = graph_adj(edges)
    seen = {0}
    q = [0]
    for u in q:
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == N

def distance(edges, s, t):
    adj = graph_adj(edges)
    d = [-1] * N
    d[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        if u == t:
            return d[u]
        for v in adj[u]:
            if d[v] < 0:
                d[v] = d[u] + 1
                q.append(v)
    return None

def gamma_for_cut(mask):
    blue = {e for e in E if crossing(e, mask)}
    if not connected(blue):
        return None
    bad = E - blue
    total = 0
    for u, v in bad:
        d = distance(blue, u, v)
        assert d is not None
        total += (d + 1) ** 2
    return total

# Triangle-free exact gate.
triangles = []
adjE = graph_adj(E)
for a, b, c in combinations(range(N), 3):
    if b in adjE[a] and c in adjE[a] and c in adjE[b]:
        triangles.append((a, b, c))
assert not triangles
assert connected(B0)

# Exhaust all cuts; fix vertex 0 to shore 0 to quotient global complementation.
best_cut = -1
max_masks = []
for mask in range(1 << N):
    if mask & 1:
        continue
    value = sum(crossing(e, mask) for e in E)
    if value > best_cut:
        best_cut = value
        max_masks = [mask]
    elif value == best_cut:
        max_masks.append(mask)
assert best_cut == 16

gamma_values = []
for mask in max_masks:
    g = gamma_for_cut(mask)
    if g is not None:
        gamma_values.append((g, mask))
assert gamma_values
min_gamma = min(g for g, _ in gamma_values)
assert min_gamma == 25

# Displayed cut: core shore {s,t,a2,b2}; leaves opposite parents.
shore = {core[x] for x in ("s", "t", "a2", "b2")}
for x in names:
    if core[x] not in shore:
        shore.add(leaves[x])
displayed = sum(1 << v for v in shore)
assert sum(crossing(e, displayed) for e in E) == 16
assert gamma_for_cut(displayed) == 25

# Complete shortest s-t path database in displayed blue graph.
def all_shortest_paths(edges, s, t):
    adj = graph_adj(edges)
    dist = [-1] * N
    dist[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    out = []
    path = [s]
    def dfs(u):
        if u == t:
            out.append(tuple(path))
            return
        for v in sorted(adj[u]):
            if dist[v] == dist[u] + 1 and dist[v] <= dist[t]:
                path.append(v)
                dfs(v)
                path.pop()
    dfs(s)
    return dist[t], out

dist_st, rows = all_shortest_paths(B0, core["s"], core["t"])
assert dist_st == 4
assert set(rows) == {tuple(P), tuple(Q)}
shape = tuple(P[i] == Q[i] for i in (1, 2, 3))
assert shape == (False, False, False)

# Every switch loss is nonnegative; exact four-corner pair margin is therefore nonnegative.
def loss(mask):
    return sum(crossing(e, mask) for e in B0) - sum(crossing(e, mask) for e in bad0)
losses = [loss(mask) for mask in range(1 << N)]
assert min(losses) == 0

row_union = sorted(set(P) | set(Q))
row_masks = []
for small in range(1 << len(row_union)):
    row_masks.append(sum(1 << row_union[i] for i in range(len(row_union)) if (small >> i) & 1))
min_pair_margin = None
min_pair = None
for X in row_masks:
    for Y in row_masks:
        margin = loss(X & Y) + loss(X | Y)
        if min_pair_margin is None or margin < min_pair_margin:
            min_pair_margin = margin
            min_pair = (X, Y)
assert min_pair_margin == 0

print(f"vertices={N} edges={len(E)} triangles={len(triangles)}")
print(f"maxcut={best_cut} maxcut_orbits={len(max_masks)} connected_maxcuts={len(gamma_values)}")
print(f"min_connected_maxcut_gamma={min_gamma} displayed_gamma={gamma_for_cut(displayed)}")
print(f"shortest_st_distance={dist_st} shortest_rows={len(rows)} shape={shape}")
print(f"min_switch_loss={min(losses)} row_union_pair_count={len(row_masks)**2} min_pair_margin={min_pair_margin}")
print("PASS_R57_CURRENT_INTERFACE_COUNTEREXAMPLE")