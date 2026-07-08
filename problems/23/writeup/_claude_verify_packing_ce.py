r"""Exact verification of GPT-Pro's 18-vtx counterexample to the unit odd-cycle packing mirror (reply 6,
2026-07-08). Claims: triangle-free; the given cut is a GENUINE max cut (brute 2^17); Gamma-minimal (every
B-connected max cut has 2 bad edges => Gamma>=50, this one =50); e=x-y, f=z-w both ell=5 with UNIQUE shortest
geodesics x-a-b-c-y and z-a-b-d-w sharing edge a-b => unit 5-cycle packing forces load 2 on a-b (t*=2) while
Hall holds with slack (|S|=2 <= |E_short|=7). A pass = the packing mirror (+factor-4) is refuted on a real
Gamma-min max cut; the b-matching Hall target is untouched. Exact integer/BFS. Run from problems/23/writeup."""
from itertools import product
from collections import deque

V = ['x', 'b', 'y', 'z', 'w', 'u2', 'u4', 'v2', 'v4', 'a', 'c', 'd', 'u1', 'u3', 'u5', 'v1', 'v3', 'v5']
idx = {v: i for i, v in enumerate(V)}
RED = {'x', 'b', 'y', 'z', 'w', 'u2', 'u4', 'v2', 'v4'}
B = [('x', 'a'), ('a', 'b'), ('b', 'c'), ('c', 'y'),
     ('z', 'a'), ('b', 'd'), ('d', 'w'),
     ('x', 'u1'), ('u1', 'u2'), ('u2', 'u3'), ('u3', 'u4'), ('u4', 'u5'), ('u5', 'y'),
     ('z', 'v1'), ('v1', 'v2'), ('v2', 'v3'), ('v3', 'v4'), ('v4', 'v5'), ('v5', 'w')]
M = [('x', 'y'), ('z', 'w')]
E = B + M
n = len(V)
side = [0 if v in RED else 1 for v in V]

adjAll = {v: set() for v in V}
for u, w in E:
    adjAll[u].add(w); adjAll[w].add(u)

# 1. cut consistency: B bichromatic, M monochromatic
b_ok = all(side[idx[u]] != side[idx[w]] for u, w in B)
m_ok = all(side[idx[u]] == side[idx[w]] for u, w in M)
print("1. B bichromatic:", b_ok, "| M monochromatic:", m_ok)

# 2. triangle-free
tri = []
for i in range(n):
    for j in range(i + 1, n):
        for k in range(j + 1, n):
            a1, b1, c1 = V[i], V[j], V[k]
            if b1 in adjAll[a1] and c1 in adjAll[a1] and c1 in adjAll[b1]:
                tri.append((a1, b1, c1))
print("2. triangle-free:", len(tri) == 0, tri if tri else '')

# 3. max cut brute force (vertex 0 fixed)
def cutsize(bits):
    return sum(1 for u, w in E if bits[idx[u]] != bits[idx[w]])
best = -1
given = tuple(side)
gval = cutsize(given)
nmax = 0
for tail in product((0, 1), repeat=n - 1):
    bits = (0,) + tail
    c = cutsize(bits)
    if c > best:
        best = c; nmax = 1
    elif c == best:
        nmax += 1
print("3. given cut=%d ; true max=%d ; #maxcuts(mod flip)=%d ; given-is-max=%s" % (gval, best, nmax, gval == best))

# 4. Gamma-min: every max cut has >= 2 bad edges each ell>=5 => Gamma >= 50 = given
def blue_adj(bits):
    ab = {v: set() for v in V}
    for u, w in B + M:
        if bits[idx[u]] != bits[idx[w]]:
            ab[u].add(w); ab[w].add(u)
    return ab
def bfs_ell(ab, s, t):
    d = {s: 0}; Q = deque([s])
    while Q:
        u = Q.popleft()
        for w in ab[u]:
            if w not in d:
                d[w] = d[u] + 1; Q.append(w)
    return None if t not in d else d[t] + 1
gmin_ok = True
worst = None
for tail in product((0, 1), repeat=n - 1):
    bits = (0,) + tail
    if cutsize(bits) != best:
        continue
    bad = [(u, w) for u, w in E if bits[idx[u]] == bits[idx[w]]]
    ab = blue_adj(bits)
    G = 0
    connected = True
    for u, w in bad:
        l = bfs_ell(ab, u, w)
        if l is None:
            connected = False; break
        G += l * l
    if not connected:
        continue
    if worst is None or G < worst:
        worst = G
print("4. min Gamma over B-connected max cuts = %s ; given Gamma = 50 ; Gamma-min-ok = %s" % (worst, worst == 50))

# 5. geodesics of e and f at the given cut: unique, share a-b
ab = blue_adj(given)
def all_geodesics(ab, s, t):
    ds = {s: 0}; Q = deque([s])
    while Q:
        u = Q.popleft()
        for w in ab[u]:
            if w not in ds: ds[w] = ds[u] + 1; Q.append(w)
    D = ds.get(t)
    paths = []
    def back(v, path):
        if v == s:
            paths.append(list(reversed(path + [s]))); return
        for w in ab[v]:
            if ds.get(w) == ds[v] - 1:
                back(w, path + [v])
    back(t, [])
    return D, paths
De, ge = all_geodesics(ab, 'x', 'y')
Df, gf = all_geodesics(ab, 'z', 'w')
print("5. ell(e)=%d (#geos %d: %s) | ell(f)=%d (#geos %d: %s)" % (De + 1, len(ge), ge, Df + 1, len(gf), gf))
share = set()
if len(ge) == 1 and len(gf) == 1:
    Ee = set((min(ge[0][i], ge[0][i+1], key=str), max(ge[0][i], ge[0][i+1], key=str)) for i in range(len(ge[0]) - 1))
    Ef = set((min(gf[0][i], gf[0][i+1], key=str), max(gf[0][i], gf[0][i+1], key=str)) for i in range(len(gf[0]) - 1))
    share = Ee & Ef
    print("   shared support edges:", share, "| |E_short(S)| =", len(Ee | Ef))
unique_share_ab = (len(ge) == 1 and len(gf) == 1 and share == {('a', 'b')})
hall = (len(ge) == 1 and len(gf) == 1 and 2 <= len(Ee | Ef))
tstar2 = unique_share_ab   # unique geodesics + shared edge => any unit packing loads a-b with 2
print("6. unique geodesics sharing exactly a-b:", unique_share_ab, "=> t*=2 (packing refuted);",
      "Hall 2<=%d: %s" % (len(Ee | Ef) if len(ge) == 1 else -1, hall))
print("=" * 60)
verdict = b_ok and m_ok and not tri and gval == best and worst == 50 and De + 1 == 5 and Df + 1 == 5 and unique_share_ab and hall
print("VERDICT:", "CONFIRMED -- unit odd-cycle packing mirror REFUTED at a genuine Gamma-min max cut; "
      "factor-4 dead (4*2=8 > 7); b-matching Hall untouched" if verdict else "MISMATCH -- re-examine claims")
