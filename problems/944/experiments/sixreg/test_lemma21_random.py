"""Stress-test Lemma 2.1 (Kempe tether) as a stand-alone implication on random graphs:

For ANY graph G with chi(G)=4, any vertex v with d(v)=6, any proper 3-colouring phi of G-v
whose neighbour classes split 2+2+2: if the (phi(x),j)-Kempe component of the mate x'
contains no j-coloured neighbour of v, then chi(G - vx) <= 3.

Zero counterexamples expected. Reports how many times the implication was exercised.
"""
import random, sys

def is_3col(n, adj, skip=frozenset(), drop_edge=None):
    verts = [v for v in range(n) if v not in skip]
    # order by degree desc for speed
    verts.sort(key=lambda v: -len(adj[v]))
    col = {}
    def ok(v, c):
        for u in adj[v]:
            if u in skip: continue
            if drop_edge and ((v,u)==drop_edge or (u,v)==drop_edge): continue
            if col.get(u) == c: return False
        return True
    def bt(i):
        if i == len(verts): return True
        v = verts[i]
        for c in range(3):
            if ok(v, c):
                col[v] = c
                if bt(i+1): return True
                del col[v]
        return False
    return bt(0)

def colourings3_limit(n, adj, skip, limit=2000):
    verts = [v for v in range(n) if v not in skip]
    out = []
    col = {}
    def bt(i):
        if len(out) >= limit: return
        if i == len(verts):
            out.append(dict(col)); return
        v = verts[i]
        used = {col[u] for u in adj[v] if u not in skip and u in col}
        for c in range(3):
            if c not in used:
                col[v] = c; bt(i+1)
                if v in col: del col[v]
    bt(0)
    return out

rng = random.Random(944)
n_exercised = 0; n_graphs_used = 0; n_cex = 0
TRIALS = 4000
for trial in range(TRIALS):
    n = rng.choice([10, 11, 12])
    p = rng.uniform(0.38, 0.55)
    adj = [set() for _ in range(n)]
    for a in range(n):
        for b in range(a+1, n):
            if rng.random() < p: adj[a].add(b); adj[b].add(a)
    if is_3col(n, adj): continue            # chi >= 4 required
    if not is_3col(n, adj, skip=frozenset()) and is_3col(n, adj, skip=frozenset({0})) is None:
        pass
    # need chi exactly 4: check 4-colourable quickly via greedy fallback (skip check: chi>=4 suffices,
    # Lemma 2.1 contrapositive only uses "G-vx 3-colourable => vx critical-or-chi-drop"; we test the
    # 3-colourability conclusion directly, which is the mathematical content.)
    used_graph = False
    for v in range(n):
        if len(adj[v]) != 6: continue
        if not is_3col(n, adj, skip=frozenset({v})): continue
        for phi in colourings3_limit(n, adj, frozenset({v}), limit=400):
            classes = {c:[u for u in adj[v] if phi[u]==c] for c in range(3)}
            if sorted(len(x) for x in classes.values()) != [2,2,2]: continue
            for x in adj[v]:
                cx = phi[x]
                mate = [y for y in classes[cx] if y != x][0]
                for j in range(3):
                    if j == cx: continue
                    comp = {mate}; stack=[mate]
                    while stack:
                        z = stack.pop()
                        for w in adj[z]:
                            if w != v and w not in comp and phi.get(w) in (cx,j):
                                comp.add(w); stack.append(w)
                    if not any(w in comp for w in classes[j]):
                        # tether failure: Lemma 2.1 says G-vx is 3-colourable
                        n_exercised += 1; used_graph = True
                        if not is_3col(n, adj, drop_edge=(v,x)):
                            n_cex += 1
                            print(f"COUNTEREXAMPLE trial={trial} v={v} x={x} j={j}")
    if used_graph: n_graphs_used += 1

print(f"graphs with chi>=4 exercising the lemma: {n_graphs_used}")
print(f"tether-failure implications tested: {n_exercised}, counterexamples: {n_cex}")
print("LEMMA 2.1 PASSED" if n_cex == 0 else "LEMMA 2.1 FAILED")
sys.exit(1 if n_cex else 0)
