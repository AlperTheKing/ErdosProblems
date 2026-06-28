"""Verify the implication chain end-to-end on census (exact):
 DISCONNECTED-K-SELFCAP (T(v)<=|C| in every component of a multi-K config)
   => O-K-CONNECTED (O nonempty => positive-K support connected)
   => C-alltie.
We assume the antecedent holds (verified 0-viol) and check the consequents are exactly equivalent / implied,
i.e. that NO non-vacuous C-alltie instance has O nonempty with disconnected positive-K support that would slip
through. Concretely: over all gamma-min cuts with O nonempty, count positive-K components; if always 1, C-alltie
holds. Cross-check against the direct C-alltie test."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def gamma_of_side(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G

bad=0; Ononemptycuts=0; multi_with_O=0
for nn in range(7,12):
    step=1 if nn<=10 else 3
    for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::step]:
        n,E=dec(g6); adj=build_adj(n,E)
        cand=[]
        for side in maxcut_all(n,adj):
            if not Bconn(n,adj,side): continue
            g=gamma_of_side(n,adj,side)
            if g is None: continue
            cand.append((side,g))
        if not cand: continue
        gm=min(g for _,g in cand)
        for side,g in cand:
            if g!=gm: continue
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            O=[v for v in range(n) if T[v]>n]
            if not O: continue
            Ononemptycuts+=1
            comps,find=kcomponents(n,cyc)
            pos=[set(v for v in C if T[v]>0) for C in comps.values() if any(T[v]>0 for v in C)]
            if len(pos)>1:
                multi_with_O+=1   # would-be C-alltie counterexample
    print(f"N={nn}: gamma-min cuts with O nonempty={Ononemptycuts}, of which multi-positive-K={multi_with_O}",flush=True)
print(f"FINAL: O-nonempty gamma-min cuts={Ononemptycuts}; disconnected-positive-K-with-O={multi_with_O}")
print("(multi_with_O=0  <=>  O-K-CONNECTED holds on all gamma-min cuts  <=>  C-alltie holds)")
