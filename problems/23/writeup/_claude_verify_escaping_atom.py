r"""Exact verification of GPT-Pro's explicit ESCAPING-ATOM pattern (2026-07-09), the concrete construction showing the
local NoEscapingAtom lemma is FALSE (both GPT-Pro's 14-vtx pattern and the workflow's n=14 witness). Confirms:
triangle-free; e,f,h are monochromatic (bad) edges each with blue-distance 4 (ell=5); W={a,b,c,y,w} has door signature
delta_B(W)={x-a,z-c}, delta_M(W)={x-y,z-w}; and h=x-z is an ESCAPING atom (both endpoints OUTSIDE W, yet its shortest
blue geodesic x-a-b-c-z passes through W's interior a,b,c) -- so the ledger split does not follow from local geometry.
EXACT (integer BFS, no float). Run from problems/23/writeup."""
from collections import deque

V = ['x','z','y','w','a','b','c','r1','r2','r3','r4','r5','r6','r7']
side = {v: 0 for v in ['x','z','y','w','b','r2','r4','r6']}   # 0 = Red
for v in ['a','c','r1','r3','r5','r7']:
    side[v] = 1                                               # 1 = Blue
B = [('x','a'),('a','b'),('b','c'),('c','y'),('z','c'),('a','w'),
     ('x','r1'),('r1','r2'),('r2','r3'),('r3','r4'),('r4','r5'),('r5','r6'),('r6','r7'),('r7','z')]
M = [('x','y'),('z','w'),('x','z')]   # e, f, h
e, f, h = M

adjB = {v: set() for v in V}
for u, w in B:
    adjB[u].add(w); adjB[w].add(u)
adjAll = {v: set() for v in V}
for u, w in B + M:
    adjAll[u].add(w); adjAll[w].add(u)

def blue_dist(s, t):
    dist = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if w not in dist:
                dist[w] = dist[u] + 1; q.append(w)
    return dist.get(t, None)

def blue_geodesic_vertices(s, t):
    """All vertices on some shortest blue path s->t (via forward+backward BFS layers)."""
    ds = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if w not in ds:
                ds[w] = ds[u] + 1; q.append(w)
    D = ds.get(t)
    if D is None:
        return set()
    dt = {t: 0}; q = deque([t])
    while q:
        u = q.popleft()
        for w in adjB[u]:
            if w not in dt:
                dt[w] = dt[u] + 1; q.append(w)
    return {v for v in V if ds.get(v) is not None and dt.get(v) is not None and ds[v] + dt[v] == D}

print("=== GPT-Pro escaping-atom pattern: exact verification ===")
# 1. B is bipartite / all B edges bichromatic
b_ok = all(side[u] != side[w] for u, w in B)
print("B bichromatic (proper cut edges):", b_ok)

# 2. triangle-free (B ∪ M)
tri = []
for i in range(len(V)):
    for j in range(i+1, len(V)):
        for k in range(j+1, len(V)):
            a1, b1, c1 = V[i], V[j], V[k]
            if b1 in adjAll[a1] and c1 in adjAll[a1] and c1 in adjAll[b1]:
                tri.append((a1, b1, c1))
print("triangle-free:", len(tri) == 0, ("triangles: %s" % tri) if tri else "")

# 3. bad edges monochromatic + ell = blue_dist+1
print("bad edges (monochromatic, ell = blue-dist+1):")
for (u, w) in M:
    mono = side[u] == side[w]
    d = blue_dist(u, w)
    ell = None if d is None else d + 1
    print("  %s-%s mono=%s blue_dist=%s ell=%s" % (u, w, mono, d, ell))

# 4. door signature of W = {a,b,c,y,w}
W = {'a', 'b', 'c', 'y', 'w'}
def crossing(edges):
    return sorted([(u, w) for (u, w) in edges if (u in W) != (w in W)])
dB = crossing(B); dM = crossing(M)
print("W =", sorted(W))
print("  delta_B(W) =", dB, " (want [('x','a'),('z','c')] up to order)")
print("  delta_M(W) =", dM, " (want [('x','y'),('z','w')] up to order)")

# 5. h = x-z is ESCAPING: both endpoints outside W, shortest support hits W interior
geo_h = blue_geodesic_vertices('x', 'z')
interiorW = W - {'a', 'c'}   # W minus the door-incident vertices a,c -> {b,y,w}; 'interior' crossing = support meets W
h_endpoints_out = ('x' not in W) and ('z' not in W)
support_in_W = geo_h & W
print("h = x-z geodesic-support vertices:", sorted(geo_h))
print("  h endpoints outside W:", h_endpoints_out, " | support-cap-W:", sorted(support_in_W))
escaping = h_endpoints_out and len(support_in_W) > 0
print("  => h is an ESCAPING atom (endpoints out, support crosses W):", escaping)

# verdict
ok_dB = set(map(frozenset, dB)) == {frozenset(('x','a')), frozenset(('z','c'))}
ok_dM = set(map(frozenset, dM)) == {frozenset(('x','y')), frozenset(('z','w'))}
all_ell5 = all((blue_dist(u,w) == 4) for (u,w) in M)
print("=" * 60)
print("VERDICT: triangle-free=%s, all-bad-ell=5=%s, door-sig(dB)=%s door-sig(dM)=%s, h-escaping=%s"
      % (len(tri)==0, all_ell5, ok_dB, ok_dM, escaping))
if len(tri)==0 and all_ell5 and ok_dB and ok_dM and escaping:
    print("CONFIRMED: the local NoEscapingAtom lemma is FALSE -- a triangle-free balanced-neutral ell=5 lens W admits")
    print("an escaping atom h=x-z (support through W, endpoints outside). Local geometry alone cannot give ledger")
    print("separation; the crux MUST use the minimal-negative-balance ledger. (This config is NOT deficient-minimal,")
    print("so it does NOT refute the full theorem -- consistent with both GPT-Pro and the 9-angle workflow.)")
else:
    print("MISMATCH -- re-examine GPT-Pro's construction.")
