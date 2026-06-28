"""Re-cut experiment for C-alltie via gamma-minimality.
Hypothesis to refute: C=Kcomp(v) disjoint from O, v in C saturated (T(v)=N), z dead B-neighbor of v outside...
actually z may be in C or not. Test the RE-CUT: flip a vertex subset and recompute (cut size, connectivity, Gamma).

We focus on the N=12 caveat (only census realizer) and the C5+Myc(C7) gadget, plus we synthesize
a hypothetical Q-only critical component by construction and try flips.

For each gamma-min cut realizing the hypothesis, enumerate candidate flips:
 (a) flip exactly Kcomp(v)  [if it were Q-only]
 (b) flip {z} (the dead vertex)
 (c) flip {z} union (its dead-net component in B)
and report new cut size (must stay = maxcut), new B-connectivity, new Gamma (Fraction).
"""
from fractions import Fraction as F
from collections import deque
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def cutsize(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])

def gamma_of(n,adj,side):
    """Return (Gamma, ok) for a connected-B max cut side; ok=False if B disconnected or some bad edge has no geodesic."""
    if not Bconn(n,adj,side): return None,False
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None,False
        G+=(d+1)**2
    return G,True

def maxcut_value(n,adj):
    cuts=maxcut_all(n,adj)
    return cutsize(n,adj,cuts[0])

def analyze_graph(name,n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    mc=maxcut_value(n,adj)
    cuts=maxcut_all(n,adj); cand=[]
    for side in cuts:
        g,ok=gamma_of(n,adj,side)
        if ok: cand.append((tuple(side),g))
    if not cand:
        print(f"[{name}] no connected max cut"); return
    gm=min(g for _,g in cand)
    print(f"[{name}] N={n} maxcut={mc} Gamma_min={gm} #gmin-conn-cuts={sum(1 for _,g in cand if g==gm)}")
    for side,g in cand:
        if g!=gm: continue
        st=struct_for_side(n,adj,list(side))
        if st is None: continue
        M,ell,T,mu,cyc=st; N=n
        O=set(v for v in range(N) if T[v]>N)
        if not O: continue
        comp,find=kcomponents(n,cyc)
        cases=[(v,z) for v in range(N) if T[v]==N for z in adj[v] if side[z]!=side[v] and T[z]==0]
        if not cases: continue
        print(f"  side={side} O={sorted(O)} sat={[v for v in range(N) if T[v]==N]} dead={[v for v in range(N) if T[v]==0]}")
        for v,z in cases:
            Cv=comp[find(v)]
            print(f"   case v={v} z={z} Kcomp(v)={sorted(Cv)} meetsO={bool(Cv&O)}")
            # try flips
            for label,flip in [("flip {z}",{z}),
                               ("flip Kcomp(v)",set(Cv)),
                               ("flip dead-Bcomp(z)",dead_Bcomp(n,adj,side,T,z))]:
                ns=list(side)
                for w in flip: ns[w]^=1
                cs=cutsize(n,adj,ns)
                g2,ok=gamma_of(n,adj,ns)
                print(f"      {label}: newcut={cs}(max={mc}{' OK' if cs==mc else ' NOT-MAX'}) "
                      f"connB+geo={ok} newGamma={g2 if ok else 'NA'} dG={(g2-gm) if (ok and g2 is not None) else 'NA'}")

def dead_Bcomp(n,adj,side,T,z):
    """B-connected component of z within the dead (T=0) vertex set."""
    seen={z}; q=deque([z])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in seen and T[w]==0:
                seen.add(w); q.append(w)
    return seen

if __name__=="__main__":
    g6='J?AADBWM_}?'; n0,E0=dec(g6); E12=list(E0)+[(8,11)]
    analyze_graph("N=12 leaf caveat",12,E12)
