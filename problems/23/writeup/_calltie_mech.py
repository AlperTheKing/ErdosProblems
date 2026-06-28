"""Mechanism probe for a DIRECT C-alltie proof.
For each non-vacuous C-alltie case (sat v, dead z B-neighbor), examine:
 (a) Kcomp(v)=C. Is C the unique load-bearing component? Is there EVER a 2nd nontrivial K-comp?
 (b) Is v EVER in a Q-only K-component (the contrapositive scenario)? -> search all cuts.
 (c) The 'critical-test': could C be critical (T==N on all of C)? Compute min/max T on C.
 (d) Handshake at v: 2N - D(v), and the per-edge mu distribution. The dead edge (v,z) has mu=0.
     How much of v's saturated load (N) routes to neighbors NOT equal to z?
 (e) KEY: among bad edges f with v in supp(p_f), is v always an ENDPOINT of at least one f whose
     OTHER endpoint or whose geodesic reaches O? Quantify 'load pushed toward O'.
Exact Fraction over all gamma-min cuts, census N<=11 + Mycielskians.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, loads
from _satzmu_conn import struct_for_side, kcomponents

def mycielski(n, E):
    adj = [set() for _ in range(n)]
    for a, b in E: adj[a].add(b); adj[b].add(a)
    N2 = 2*n+1; E2 = list(E)
    for u in range(n):
        for v in adj[u]:
            if v > u: E2.append((u, n+v)); E2.append((v, n+u))
    for u in range(n): E2.append((n+u, 2*n))
    return N2, E2

def analyze_side(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell, T, mu, cyc = st
    N = n
    O = set(v for v in range(N) if T[v] > N)
    comp, find = kcomponents(n, cyc)
    supp = {f: set(v for P in Ps for v in P) for f, Ps in cyc.items()}
    # all nontrivial K-components (size>1)
    comps = {}
    for v in range(N): comps.setdefault(find(v), set()).add(v)
    nontriv = [sorted(c) for c in comps.values() if len(c) > 1]
    info = dict(N=N, O=O, T=T, M=M, ell=ell, comps=nontriv, find=find, comp=comps, supp=supp, cyc=cyc, mu=mu)
    return info

def report(name, n, E, allcuts=True):
    adj = [set() for _ in range(n)]
    for x, y in E: adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj)
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
    if not cand:
        print(f"  {name}: no valid cut"); return
    gm = min(G for _, G in cand)
    n_qonly_comps = 0; n_sat_dead = 0
    for side, G in cand:
        if G != gm: continue
        I = analyze_side(n, adj, side)
        if I is None: continue
        N = I['N']; O = I['O']; T = I['T']
        # any nontrivial K-comp disjoint from O?
        for C in I['comps']:
            if not (set(C) & O):
                n_qonly_comps += 1
                Tc = [T[w] for w in C]
                print(f"  {name}: *** Q-ONLY nontrivial K-comp C={C} minT={float(min(Tc))} maxT={float(max(Tc))} (O={sorted(O)})")
        # sat-v ~ dead-z structure
        for v in range(N):
            if T[v] != N or not O: continue
            deadnb = [z for z in adj[v] if side[z] != side[v] and T[z] == 0]
            if not deadnb: continue
            n_sat_dead += 1
            Cv = I['comp'][I['find'](v)]
            # endpoint bad edges of v reaching O
            endpt = [f for f in I['M'] if v in f]
            endpt_to_O = [f for f in endpt if I['supp'][f] & O]
            print(f"  {name}: sat v={v} deadnb={deadnb} |Cv|={len(Cv)} CvmeetsO={bool(Cv&O)} "
                  f"#endpt-bad-edges={len(endpt)} #endpt-reaching-O={len(endpt_to_O)} endptO={endpt_to_O}")
    if n_qonly_comps == 0 and allcuts:
        pass

if __name__ == "__main__":
    print("=== C-alltie mechanism: named + Mycielskians ===")
    for g6 in ["J??CBAPFvo?"]:
        n, E = dec(g6); report(g6, n, E)
    # Mycielskians (single loads-cut, too big for all-cuts)
    C5 = (5, [(i, (i+1) % 5) for i in range(5)])
    n1, E1 = mycielski(*C5)
    n2, E2 = mycielski(n1, E1)
    for name, (nn, EE) in [("Grotzsch11", (n1, E1)), ("MycGrotzsch23", (n2, E2))]:
        info = loads(nn, EE)
        if info is None: print(f"  {name}: loads None"); continue
        I = analyze_side(info['n'], info['adj'], info['side'])
        N = I['N']; O = I['O']; T = I['T']
        sat_dead = []
        for v in range(N):
            if T[v] != N or not O: continue
            deadnb = [z for z in info['adj'][v] if info['side'][z] != info['side'][v] and T[z] == 0]
            if deadnb:
                Cv = I['comp'][I['find'](v)]
                sat_dead.append((v, deadnb, bool(Cv & O)))
        qonly = [C for C in I['comps'] if not (set(C) & O)]
        print(f"  {name} (N={N}): |O|={len(O)} O={sorted(O)} nontriv-Kcomps={len(I['comps'])} Q-only-nontriv={len(qonly)} sat-with-deadnb={sat_dead}")
