r"""CLAUDE-INDEPENDENT verification of the workflow's 24-vertex bare-SSE counterexample (2026-07-08).
Third implementation (the workflow used two of its own; this one is written fresh from the CONSTRUCTION SPEC,
not from their code): K33 cluster l={0,1,2}, r={3,4,5} (9 bad edges l_i-r_j); waist u=6,w=7,v=8 with edges
l-u (3), u-w, w-v, v-r (3) [8 double-star edges]; anchor web aL=9-11, zL=12-14, m=15-17, zR=18-20, aR=21-23
with COMPLETE 3x3 links l-aL, aL-zL, zL-m, m-zR, zR-aR, aR-r (54 edges). Total 24 vtx, 71 edges.
CLAIMS to verify exactly: (1) triangle-free; (2) true max cut = 62 = |E|-9 and UNIQUE (mod global flip)
=> trivially Gamma-min; (3) at that cut the bad set = exactly the 9 K33 edges, each ell=5 with UNIQUE
geodesic l_i-u-w-v-r_j (|P_e|=4); (4) E_short(S) = the 8 double-star edges => |S|=9 > 8 = |E_short(S)|:
a Hall VIOLATION at a genuine Gamma-min max cut in one component; (5) B-connectivity. numpy chunked 2^23.
If ALL pass: bare Ell5SupportExpansion is FALSE in real graphs; the BANKED form is the only viable target.
Run from problems/23/writeup.
"""
from collections import deque
import numpy as np

n = 24
l = [0, 1, 2]; r = [3, 4, 5]; u, w, v = 6, 7, 8
aL = [9, 10, 11]; zL = [12, 13, 14]; m = [15, 16, 17]; zR = [18, 19, 20]; aR = [21, 22, 23]

E = []
def link(A, B):
    for x in A:
        for y in B:
            E.append((min(x, y), max(x, y)))
for x in l: E.append((min(x, u), max(x, u)))
E.append((u, w)); E.append((w, v))
for y in r: E.append((min(v, y), max(v, y)))
link(l, r)                      # 9 bad-intended K33 edges
link(l, aL); link(aL, zL); link(zL, m); link(m, zR); link(zR, aR); link(aR, r)
E = sorted(set(E))
print("n=%d |E|=%d (want 71)" % (n, len(E)))

adj = [set() for _ in range(n)]
for a, b in E:
    adj[a].add(b); adj[b].add(a)

# 1. triangle-free
tri = 0
for a in range(n):
    for b in adj[a]:
        if b > a and adj[a] & adj[b]:
            tri += 1
print("1. triangle-free:", tri == 0)

# 2. exhaustive max cut, vertex 0 fixed side 0, chunked
NS = 1 << (n - 1)
CH = 1 << 22
best = -1; count = 0; keep = []
for start in range(0, NS, CH):
    stop = min(start + CH, NS)
    s_arr = np.arange(start, stop, dtype=np.uint32)
    tot = np.zeros(stop - start, dtype=np.int16)
    for (a, b) in E:
        if a == 0:
            tot += ((s_arr >> np.uint32(b - 1)) & 1).astype(np.int16)
        else:
            tot += (((s_arr >> np.uint32(a - 1)) ^ (s_arr >> np.uint32(b - 1))) & 1).astype(np.int16)
    cmax = int(tot.max())
    if cmax > best:
        best = cmax; count = 0; keep = []
    if cmax == best:
        idx = np.where(tot == best)[0]
        count += len(idx)
        for s in idx[:10]:
            keep.append(start + int(s))
print("2. true max cut = %d (want 62 = 71-9) ; #maxcuts (v0 fixed) = %d (want 1 = unique)" % (best, count))

side = [0] * n
if keep:
    s0 = keep[0]
    for x in range(1, n):
        side[x] = (s0 >> (x - 1)) & 1
bad = [(a, b) for (a, b) in E if side[a] == side[b]]
K33 = sorted((min(x, y), max(x, y)) for x in l for y in r)
print("3. bad set = K33 cluster edges:", sorted(bad) == K33, "(#bad=%d)" % len(bad))

adjB = [set() for _ in range(n)]
for a, b in E:
    if side[a] != side[b]:
        adjB[a].add(b); adjB[b].add(a)

def bfs(s):
    d = {s: 0}; Q = deque([s])
    while Q:
        x = Q.popleft()
        for y in adjB[x]:
            if y not in d:
                d[y] = d[x] + 1; Q.append(y)
    return d

def geo_edges(s, t):
    ds = bfs(s); dt = bfs(t)
    D = ds.get(t)
    if D is None:
        return None, None
    edges = set()
    for x in list(ds):
        if x in dt and ds[x] + dt[x] == D:
            for y in adjB[x]:
                if y in ds and y in dt and ds[y] == ds[x] + 1 and ds[y] + dt[y] == D:
                    edges.add((min(x, y), max(x, y)))
    return D, frozenset(edges)

ok_ell = True; Eshort = set(); bconn = True
for (a, b) in bad:
    D, P = geo_edges(a, b)
    if D is None:
        bconn = False; continue
    if D != 4 or len(P) != 4:
        ok_ell = False
        print("   atom %s: dist=%s |P|=%s (want 4, 4)" % ((a, b), D, len(P)))
    Eshort |= P
dstar = sorted([(min(x, u), max(x, u)) for x in l] + [(u, w), (w, v)] + [(min(v, y), max(v, y)) for y in r])
print("4. all ell=5 unique-geodesic:", ok_ell, "| B-connected:", bconn)
print("   E_short(S) = double-star 8 edges:", sorted(Eshort) == dstar, "(|E_short|=%d)" % len(Eshort))
print("   HALL: |S|=%d vs |E_short|=%d -> VIOLATION=%s" % (len(bad), len(Eshort), len(bad) > len(Eshort)))
verdict = (tri == 0 and best == 62 and count == 1 and sorted(bad) == K33 and ok_ell and bconn
           and sorted(Eshort) == dstar and len(bad) > len(Eshort))
print("=" * 72)
print("VERDICT:", "CONFIRMED -- bare SSE is FALSE at a genuine UNIQUE (Gamma-min) max cut of a real "
      "24-vtx triangle-free graph; banked form is the ONLY viable target" if verdict
      else "MISMATCH -- workflow CE does not check out; re-examine before any ledger update")
