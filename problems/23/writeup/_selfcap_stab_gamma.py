"""Verify the two load-bearing claims for the FROZEN-gamma-min lemma:

(STAB-GAMMA) Under any boundary-frozen re-cut of C (flip only interior(C) = C-vertices with NO B-neighbor
outside C) that remains a MAX cut and keeps B connected: the global Gamma = Gamma_C(new) + Gamma_rest, where
Gamma_rest is UNCHANGED. Equivalently every bad edge of the re-cut global graph either lies wholly in C or
wholly in V\C, and the geodesic B-distance for a bad edge in V\C is unchanged (doesn't route through C),
and for a bad edge in C is computable inside C. Test this on the ACTUAL component cuts: enumerate ALL
boundary-frozen re-cuts of C that stay global-max + B-connected, and check global Gamma - Gamma_rest_original
== Gamma_C(new) computed purely inside C.

If this holds, then: induced cut minimizes Gamma_C among boundary-frozen connected-max re-cuts of C
(by GLOBAL gamma-minimality), RIGOROUSLY.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from collections import deque
from _satzmu_conn import struct_for_side, kcomponents

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
def gamma_of(n,adj,side):
    if not Bconn(n,adj,side): return None
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G
def gamma_inside(adj,side,Cset):
    # bad edges with both endpoints in Cset; B-distance restricted to Cset
    bads=[(u,v) for u in Cset for v in adj[u] if v in Cset and v>u and side[u]==side[v]]
    G=0
    for (u,v) in bads:
        d={u:0}; q=deque([u])
        while q:
            a=q.popleft()
            for b in adj[a]:
                if b in Cset and side[a]!=side[b] and b not in d: d[b]=d[a]+1; q.append(b)
        if v not in d: return None
        G+=(d[v]+1)**2
    return G

viol=0; tested=0; rest_change=0
for nn in [10,11]:
    step=1 if nn==10 else 23
    for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::step]:
        n,E=dec(g6); adj=build_adj(n,E)
        maxc=max(cutsize(n,adj,s) for s in maxcut_all(n,adj))
        for side in maxcut_all(n,adj):
            if cutsize(n,adj,side)!=maxc: continue
            if not Bconn(n,adj,side): continue
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            comps,find=kcomponents(n,cyc)
            pos=[set(v for v in C if T[v]>0) for C in comps.values() if any(T[v]>0 for v in C)]
            if len(pos)<=1: continue
            G0=gamma_of(n,adj,side)
            for Cset in pos:
                # Gamma_rest_original = G0 - gamma_inside(C)
                gin0=gamma_inside(adj,side,Cset)
                grest = G0 - gin0
                # interior vertices of C
                interior=[v for v in Cset if all((w in Cset) or side[v]==side[w] for w in adj[v])]
                # actually interior = no B-neighbor outside C:
                interior=[v for v in Cset if not any(w not in Cset and side[v]!=side[w] for w in adj[v])]
                import itertools
                for r in range(len(interior)+1):
                    for sub in itertools.combinations(interior, r):
                        ns=side[:]
                        for v in sub: ns[v]^=1
                        if cutsize(n,adj,ns)!=maxc: continue
                        if not Bconn(n,adj,ns): continue
                        Gn=gamma_of(n,adj,ns)
                        if Gn is None: continue
                        ginN=gamma_inside(adj,ns,Cset)
                        if ginN is None: viol+=1; continue
                        tested+=1
                        # check global Gamma == Gamma_rest_original + Gamma_inside(new)
                        if Gn != grest + ginN:
                            viol+=1
                            if viol<=3: print(f"  VIOL {g6} C={sorted(Cset)} sub={sub} Gn={Gn} grest+ginN={grest+ginN}")
            break
    print(f"N={nn} done (tested={tested} viol={viol})",flush=True)
print(f"TOTAL boundary-frozen re-cuts tested={tested}  STAB-GAMMA violations={viol}")
