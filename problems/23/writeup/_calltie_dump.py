"""Dump full structure of a non-vacuous C-alltie witness to understand the mechanism.
For J??CBAPFvo? cut with saturated v=9, dead z=5:
 - full T vector, O set
 - the bad edges through v (=> Kcomp(v))
 - which bad edge's geodesic actually carries v's load into O
 - the path from v to O in the K-graph
"""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side, kcomponents

def dump(g6, target_v=None, target_z=None):
    n, E = dec(g6)
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj)
    # find gamma-min cuts
    cand = []
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
    gm = min(G for _, G in cand)
    for side, G in cand:
        if G != gm: continue
        st = struct_for_side(n, adj, side)
        if st is None: continue
        M, ell, T, mu, cyc = st
        N = n
        O = set(v for v in range(N) if T[v] > N)
        if not O: continue
        comp, find = kcomponents(n, cyc)
        supp = {f: set(v for P in Ps for v in P) for f, Ps in cyc.items()}
        # find C-alltie cases
        cases = []
        for v in range(N):
            if T[v] != N: continue
            for z in adj[v]:
                if side[z] != side[v] and T[z] == 0:
                    cases.append((v, z))
        if not cases: continue
        if target_v is not None and (target_v, target_z) not in cases: continue
        print(f"\n=== {g6} side={side} Gamma={G} ===")
        print(f"  T = {[ (v, float(T[v])) for v in range(N)]}")
        print(f"  O = {sorted(O)}  (T>N={N})")
        print(f"  dead (T=0) = {sorted(v for v in range(N) if T[v]==0)}")
        print(f"  bad edges M = {M}, ell = {ell}")
        for (v, z) in cases:
            Cv = comp[find(v)]
            print(f"  -- case sat v={v} (T={float(T[v])}) ~B~ dead z={z} (T={float(T[z])})")
            print(f"     Kcomp(v) = {sorted(Cv)}  meets O = {bool(Cv & O)}  O in Cv = {sorted(Cv & O)}")
            through = [f for f in M if v in supp[f]]
            print(f"     bad edges with v in support: {through}")
            for f in through:
                print(f"        f={f} ell={ell[f]} supp={sorted(supp[f])}  meets O={sorted(supp[f]&O)}  p_f(v)={float([pf for pf in [sum(1 for P in cyc[f] if v in P)] ][0])}/{len(cyc[f])}")

if __name__ == "__main__":
    dump("J??CBAPFvo?", 9, 5)
