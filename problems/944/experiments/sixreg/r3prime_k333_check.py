# R3-prime avenue-B: verify the minimal dense instance K_{3,3,3} minus 3 disjoint
# edges {a1b1, a2c1, b2c2}: rainbow-rigid on deficient non-triangle (a1,b1,c1),
# and ALL THREE full vertices (a3,b3,c3) are frozen.
# Vertices: a1,a2,a3=0,1,2  b1,b2,b3=3,4,5  c1,c2,c3=6,7,8
from itertools import product, combinations

n = 9
A, B, C = [0,1,2], [3,4,5], [6,7,8]
edges = set()
for x in A:
    for y in B: edges.add((x,y))
for x in A:
    for y in C: edges.add((x,y))
for x in B:
    for y in C: edges.add((x,y))
removed = {(0,3),(1,6),(4,7)}
edges -= removed
edges = sorted(edges)
adj = [set() for _ in range(n)]
for (x,y) in edges:
    adj[x].add(y); adj[y].add(x)

deg = [len(adj[v]) for v in range(n)]
print("edges:", len(edges), " (3n-3 =", 3*n-3, ")")
print("degrees:", deg, " deficient:", [v for v in range(n) if deg[v]<6],
      " full:", [v for v in range(n) if deg[v]==6])
assert sum(6-d for d in deg) == 6 and max(deg) <= 6

def colourings(adjacency, verts):
    """all proper 3-colourings (dict) of induced graph on verts"""
    verts = list(verts)
    out = []
    def bt(i, col):
        if i == len(verts):
            out.append(dict(col)); return
        v = verts[i]
        for c in range(3):
            if all(col.get(u, -1) != c for u in adjacency[v]):
                col[v] = c
                bt(i+1, col)
                del col[v]
    bt(0, {})
    return out

cols = colourings(adj, range(n))
print("number of proper 3-colourings of K:", len(cols))
# unique up to S3?
parts = set()
for col in cols:
    classes = frozenset(frozenset(v for v in range(n) if col[v]==c) for c in range(3))
    parts.add(classes)
print("distinct colour partitions:", len(parts))

z = (0,3,6)   # a1, b1, c1 ; a1-b1 removed => non-adjacent => non-triangle
print("z pairs adjacency:", [(p,q,(min(p,q),max(p,q)) in set(edges)) for p,q in combinations(z,2)])
rigid = all(len({col[z[0]],col[z[1]],col[z[2]]}) == 3 for col in cols)
print("rainbow-rigid on (a1,b1,c1):", rigid)

# frozen check for full vertices
for v in [2,5,8]:
    rest = [u for u in range(n) if u != v]
    adj2 = [set(x for x in adj[u] if x != v) for u in range(n)]
    cols2 = colourings(adj2, rest)
    ok = False
    traces = set()
    for col in cols2:
        tr = tuple(sorted([sum(1 for u in adj[v] if col[u]==c) for c in range(3)]))
        traces.add(tr)
        if tr == (2,2,2): ok = True
    print(f"full v={v}: colourings of K-v: {len(cols2)}, traces {sorted(traces)}, "
          f"{'UNFROZEN' if ok else 'FROZEN'}")

# shore axiom: e(X) <= 3|X|-4 for 2<=|X|<=n-2
worst = None
viol = 0
es = set(edges)
for k in range(2, n-1):
    for X in combinations(range(n), k):
        Xs = set(X)
        eX = sum(1 for (x,y) in edges if x in Xs and y in Xs)
        slack = 3*k-4 - eX
        if worst is None or slack < worst[0]: worst = (slack, k, eX)
        if slack < 0: viol += 1
print("shore axiom violations:", viol, " tightest slack(3|X|-4-e(X)):", worst)
