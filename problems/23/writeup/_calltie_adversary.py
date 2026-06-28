"""Adversarial search for the C-alltie CONTRAPOSITIVE scenario:
   a saturated v (T=N) with a dead B-neighbor z, lying in a Q-only K-component (disjoint from O), O nonempty.
Strategy: GLUE an overloaded gadget (to create O) with a SEPARATE saturated-with-dead-neighbor gadget,
sharing NO bad-edge geodesics (so the K-components stay separate). If C-alltie is a real theorem, the
gamma-min max-cut should refuse to realize this (merge components / kill overload), as with NO-Q-ONLY.

We build disjoint unions and 1-vertex/edge bridges and check ALL gamma-min cuts.
Also: directly construct a critical C5[t]-style component + bridge to a dead vertex.
Exact Fraction.
"""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def all_gmin(n, E):
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj); cand = []
    for side in cuts:
        if not Bconn(n, adj, side): continue
        Mloc = [(u, v) for u in range(n) for v in adj[u] if v > u and side[u] == side[v]]
        if not Mloc: continue
        G = 0; ok = True
        for (u, v) in Mloc:
            d = bdist_restr(adj, side, u, v)
            if d < 0: ok = False; break
            G += (d+1)**2
        if ok: cand.append((side, G))
    if not cand: return adj, []
    gm = min(G for _, G in cand)
    return adj, [(side, G) for side, G in cand if G == gm]

def scenario_check(name, n, E):
    adj, cuts = all_gmin(n, E)
    realized = 0
    for side, G in cuts:
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st
        N = n
        O = set(v for v in range(N) if T[v] > N)
        if not O: continue
        comp, find = kcomponents(n, cyc)
        for v in range(N):
            if T[v] != N: continue
            deadnb = [z for z in adj[v] if side[z] != side[v] and T[z] == 0]
            if not deadnb: continue
            Cv = comp[find(v)]
            if not (Cv & O):
                realized += 1
                print(f"  {name}: *** CONTRAPOSITIVE REALIZED v={v} dead nb={deadnb} Cv={sorted(Cv)} O={sorted(O)} side={side}")
    if realized == 0:
        print(f"  {name}: scenario NOT realized over {len(cuts)} gamma-min cuts (C-alltie holds)")
    return realized

def disjoint_union(graphs):
    """graphs: list of (n,E). Returns combined (N,E) with relabeled vertices."""
    N = 0; E = []
    for (n, Es) in graphs:
        E += [(a+N, b+N) for (a, b) in Es]
        N += n
    return N, E

if __name__ == "__main__":
    print("=== Adversarial C-alltie contrapositive search ===")
    # gadget A: overloaded -> creates O. e.g. C5 blow-up unequal or known overloaded graph.
    OVER = dec("I?BD@g]Qo")   # N=10 overloaded
    # gadget B: a graph with a saturated vertex adjacent to a degree-1 (will be dead) vertex.
    # C5 with a pendant: pendant is dead (no geodesic through it), its neighbor on C5...
    C5p = (6, [(0,1),(1,2),(2,3),(3,4),(4,0),(0,5)])  # pendant 5 on vertex 0
    # Try disjoint union OVER + C5p (no bridge): B disconnected -> rejected by Bconn. Add a bridge edge.
    nU, EU = disjoint_union([OVER, C5p])
    # bridge between the two components to make B-connectable: connect over-vertex 0 to C5p-vertex 0
    EU_bridge = EU + [(0, OVER[0]+0)]  # vertex 0 of OVER to vertex 0 of C5p (=OVER[0])
    scenario_check("OVER + C5pendant (bridged)", nU, EU_bridge)
    # Also bridge variants
    for bv in range(OVER[0], nU):
        EUb = EU + [(0, bv)]
        scenario_check(f"OVER+C5p bridge 0-{bv}", nU, EUb)
