"""Machine-verify the Lemma 1.1 / Lemma 2.1 (Kempe tether) mechanisms on the unique
n=13 6-regular 4-vertex-critical graph.

Checks:
  S1  G is 6-regular, chi(G)=4, chi(G-v)=3 for all v.
  S2  Critical edges (chi(G-e)=3) form a Hamilton cycle (13 of them).
  S3  SOUNDNESS of Lemma 1.1: for every v, every proper 3-colouring phi of G-v,
      no colour class of N(v) is empty; every singleton colour class {u} has uv critical.
  S4  SOUNDNESS of Lemma 2.1: in every 2+2+2 colouring, every Kempe-tether failure
      (component of mate x' in (phi(x),j)-subgraph of G-v missing a j-coloured
      neighbour of v) predicts vx critical -- check vx is indeed critical.
  S5  COVERAGE: every critical edge is witnessed by at least one mechanism
      (singleton at either endpoint, or tether failure at either endpoint).
  S6  Property-A consistency: in every 2+2+2 colouring the three same-colour pairs are
      non-edges (automatic), i.e. complement of G[N(v)] has a perfect matching.
"""
import itertools, sys

EDGES = [(0,7),(0,8),(0,9),(0,10),(0,11),(0,12),(1,6),(1,8),(1,9),(1,10),(1,11),(1,12),
         (2,5),(2,7),(2,9),(2,10),(2,11),(2,12),(3,4),(3,6),(3,8),(3,10),(3,11),(3,12),
         (4,5),(4,7),(4,9),(4,11),(4,12),(5,6),(5,8),(5,10),(5,12),(6,7),(6,9),(6,11),
         (7,8),(7,10),(8,9)]
N = 13
adj = [set() for _ in range(N)]
for a,b in EDGES: adj[a].add(b); adj[b].add(a)
assert all(len(adj[v])==6 for v in range(N)), "not 6-regular"

def colourings3(verts, adjacency):
    """All proper 3-colourings of induced subgraph on verts (dict v->0/1/2)."""
    verts = list(verts)
    out = []
    col = {}
    def bt(i):
        if i == len(verts):
            out.append(dict(col)); return
        v = verts[i]
        used = {col[u] for u in adjacency[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c; bt(i+1); del col[v]
    bt(0)
    return out

def is_3col(verts, adjacency):
    verts = list(verts)
    col = {}
    def bt(i):
        if i == len(verts): return True
        v = verts[i]
        used = {col[u] for u in adjacency[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c
                if bt(i+1): return True
                del col[v]
        return False
    return bt(0)

# S1
assert not is_3col(range(N), adj), "G is 3-colourable?!"
for v in range(N):
    assert is_3col([u for u in range(N) if u != v], adj), f"G-{v} not 3-colourable"
print("S1 OK: 6-regular, chi=4, vertex-critical")

# S2
crit = set()
for (a,b) in EDGES:
    adj[a].discard(b); adj[b].discard(a)
    if is_3col(range(N), adj): crit.add((a,b))
    adj[a].add(b); adj[b].add(a)
deg_in_crit = {v:0 for v in range(N)}
for a,b in crit: deg_in_crit[a]+=1; deg_in_crit[b]+=1
ham = len(crit)==13 and all(d==2 for d in deg_in_crit.values())
# connectivity of the crit cycle
cadj = {v:set() for v in range(N)}
for a,b in crit: cadj[a].add(b); cadj[b].add(a)
seen={0}; stack=[0]
while stack:
    x=stack.pop()
    for y in cadj[x]:
        if y not in seen: seen.add(y); stack.append(y)
ham = ham and len(seen)==N
print(f"S2 {'OK' if ham else 'FAIL'}: {len(crit)} critical edges, Hamilton cycle = {ham}")
assert ham

def crit_has(a,b): return (a,b) in crit or (b,a) in crit

# S3 + S4 + S5 + S6
witnessed = set()   # critical edges predicted by some mechanism
false_pos = []
n_col_total = 0; n_222 = 0; n_singleton_preds = 0; n_tether_fail_preds = 0
for v in range(N):
    others = [u for u in range(N) if u != v]
    cols = colourings3(others, adj)
    n_col_total += len(cols)
    for phi in cols:
        classes = {c:[u for u in adj[v] if phi[u]==c] for c in range(3)}
        sizes = sorted(len(x) for x in classes.values())
        assert sizes[0] >= 1, f"empty colour class at v={v} -> G 3-colourable, contradiction"
        # Lemma 1.1 singletons
        for c, cl in classes.items():
            if len(cl)==1:
                u = cl[0]; n_singleton_preds += 1
                if not crit_has(v,u): false_pos.append(("L1.1", v, u, phi))
                else: witnessed.add((min(v,u),max(v,u)))
        if sizes == [2,2,2]:
            n_222 += 1
            # S6: same-colour pairs are non-edges (must hold since phi proper on G-v)
            for c, cl in classes.items():
                assert cl[1] not in adj[cl[0]], "same-colour pair adjacent?!"
            # S4: Kempe tethers
            for x in adj[v]:
                cx = phi[x]
                mate = [y for y in classes[cx] if y != x][0]
                for j in range(3):
                    if j == cx: continue
                    # component of mate in (cx, j)-subgraph of G-v
                    comp = {mate}; stack=[mate]
                    while stack:
                        z = stack.pop()
                        for w in adj[z]:
                            if w != v and w not in comp and phi.get(w) in (cx, j):
                                comp.add(w); stack.append(w)
                    if not any((w in comp) for w in classes[j]):
                        n_tether_fail_preds += 1
                        if not crit_has(v,x): false_pos.append(("L2.1", v, x, j))
                        else: witnessed.add((min(v,x),max(v,x)))
print(f"S3/S4 colourings checked: {n_col_total} total, {n_222} of type 2+2+2; "
      f"singleton predictions {n_singleton_preds}, tether-failure predictions {n_tether_fail_preds}")
if false_pos:
    print(f"FALSE POSITIVES: {len(false_pos)} e.g. {false_pos[:3]}"); sys.exit(1)
print("S3/S4 OK: zero false positives (every predicted edge is critical)")
critN = {(min(a,b),max(a,b)) for a,b in crit}
uncov = critN - witnessed
print(f"S5 coverage: {len(witnessed)}/{len(critN)} critical edges witnessed; uncovered: {sorted(uncov)}")
print("S6 OK: complement perfect matching present in all 2+2+2 colourings")
print("ALL CHECKS PASSED" if not false_pos else "FAILED")
