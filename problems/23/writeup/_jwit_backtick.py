"""Confirm the J??E discrepancy resolution: decode the g6 WITH the literal backtick and check it matches Codex
(M=[(6,8),(8,10)], f=(6,8) d=[0,1/2,1/2,1/2,1]). Closes the discrepancy -> pipelines agree, was g6 corruption."""
from fractions import Fraction as F
from _h import dec
from _satzmu_conn import struct_for_side
g6 = "J??E@_ibE" + chr(96) + "?"   # chr(96) = backtick
print(f"g6 = {g6!r}")
n,E=dec(g6)
E=sorted(tuple(sorted(e)) for e in E)
print(f"N={n} |E|={len(E)} edges={E}")
s=[1,1,1,1,1,1,0,0,0,0,0]
bad=[(u,v) for (u,v) in E if s[u]==s[v]]
print(f"side {s} same-side(bad) edges: {bad}")
st=struct_for_side(n,[set(y for x,y in [] )]*0 or [set() for _ in range(n)],s)  # placeholder
adj=[set() for _ in range(n)]
for u,v in E: adj[u].add(v); adj[v].add(u)
st=struct_for_side(n,adj,s)
M,ell,T,mu,cyc=st
print(f"M={sorted(M)} cyc-sizes={{f:len(cyc[f]) for f in sorted(M)}}")
S=[F(0)]*n
for g in M:
    Ps=cyc[g]; k=len(Ps); seen={}
    for P in Ps:
        for v in P: seen[v]=seen.get(v,F(0))+F(1,k)
    for v,pv in seen.items(): S[v]+=pv
for f in sorted(M):
    if len(cyc[f])==1:
        P=cyc[f][0]
        print(f"  unique f={f} P={P} d={[str(S[v]-1) for v in P]}")
print("=> matches Codex (M two edges, f=(6,8) d=[0,1/2,1/2,1/2,1])? confirm above")
