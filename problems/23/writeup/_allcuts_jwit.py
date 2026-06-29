"""Check all gmin cuts of J??E@_ibE? for a unique row with Codex's profile d=[0,1/2,1/2,1/2,1]
(determines: cut-index mislabel vs scanner bug). Print every cut's bad edges + unique-row d profiles."""
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
g6="J??E@_ibE?"
n,E=dec(g6); adj,cuts=gmins(n,E)
print(f"g6={g6} N={n} #gmin-cuts={len(cuts)}")
for idx,cut in enumerate(cuts):
    st=struct_for_side(n,adj,cut)
    if st is None: print(f"  idx{idx} {''.join(map(str,cut))}: struct None"); continue
    M,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        Ps=cyc[g]; k=len(Ps); seen={}
        for P in Ps:
            for v in P: seen[v]=seen.get(v,F(0))+F(1,k)
        for v,pv in seen.items(): S[v]+=pv
    uni=[]
    for f in M:
        if len(cyc[f])==1:
            P=cyc[f][0]; uni.append((f, [str(S[v]-1) for v in P]))
    print(f"  idx{idx} {''.join(map(str,cut))}: M={sorted(M)} unique-rows-d={uni}")