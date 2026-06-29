"""URGENT: verify GPT-Pro's claimed UPO counterexample (N=26): path 0..12, long detour 0-13-..-25-12,
four chords (0,4),(4,8),(8,12),(0,12); parity cut side(v)=v%2. GPT-Pro claims UPO (sum_{v in P_f}S(v)<=N)
FALSE for this fixed max cut. UPO is 0-fail on my whole battery, so check: (1) triangle-free? (2) is parity cut
a MAXIMUM cut? (3) connected-B? gamma-min? (4) does UPO actually fail on parity cut, and on the gamma-min cut?"""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side
from _stark1 import gmins

n=26
E=[]
for i in range(12): E.append((i,i+1))           # path 0..12
det=[0,13,14,15,16,17,18,19,20,21,22,23,24,25,12]
for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))  # detour 0-13-..-25-12
E += [(0,4),(4,8),(8,12),(0,12)]                # four chords
E=sorted(set(E))
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
print(f"N={n} |E|={len(E)}")
# (1) triangle-free
tri=[(a,b,c) for a,b in E for c in adj[a]&adj[b]]
print(f"triangle-free: {len(tri)==0}{'' if not tri else ' TRIANGLES:'+str(tri[:3])}")
# parity cut
side=[v%2 for v in range(n)]
def cutsize(s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
mc=max(cutsize(s) for s in maxcut_all(n,adj))
print(f"parity-cut size={cutsize(side)} | MAXCUT={mc} | parity is max? {cutsize(side)==mc}")
print(f"parity-cut Bconn={Bconn(n,adj,side)}")
# bad edges of parity cut
M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
print(f"parity-cut bad edges M={M}")
# (4) UPO on parity cut (if struct valid)
st=struct_for_side(n,adj,side)
if st is None:
    print("parity-cut: struct_for_side None (geodesic disconnected) -> NOT a valid bad-edge structure")
else:
    M2,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M2:
        Ps=cyc[g]; k=len(Ps); seen={}
        for P in Ps:
            for v in P: seen[v]=seen.get(v,F(0))+F(1,k)
        for v,pv in seen.items(): S[v]+=pv
    print(f"parity-cut struct: M={sorted(M2)} cyc-sizes={{f:len(cyc[f]) for f in sorted(M2)}}")
    for f in sorted(M2):
        Pf=cyc[f][0] if len(cyc[f])==1 else None
        row=sum(S[v]*(sum(1 for P in cyc[f] if v in P)/F(len(cyc[f]))) for v in set(x for P in cyc[f] for x in P))
        if Pf is not None:
            upo=sum(S[v] for v in Pf)
            print(f"  UNIQUE f={f} P={Pf} sum_v-in-P S(v) = {upo} = {float(upo)} (N={n}) UPO-holds={upo<=n}{'  *** UPO VIOLATED ***' if upo>n else ''}")
        else:
            print(f"  MULTI  f={f} #geo={len(cyc[f])} ROWSUM={row}={float(row)} <=N? {row<=n}")
# (3) gamma-min cuts -- what MY pipeline actually uses
adj2,cuts=gmins(n,E)
print(f"\ngmins: {len(cuts)} gamma-min connected-B MAX cuts; parity side in gmins? {side in cuts}")
# check UPO/ROWSUM on every gamma-min cut
worst=F(0)
for s in cuts:
    st=struct_for_side(n,adj2,s)
    if st is None: continue
    M2,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M2:
        Ps=cyc[g]; k=len(Ps); seen={}
        for P in Ps:
            for v in P: seen[v]=seen.get(v,F(0))+F(1,k)
        for v,pv in seen.items(): S[v]+=pv
    for f in M2:
        supp=set(x for P in cyc[f] for x in P)
        d={}
        for P in cyc[f]:
            for v in P: d[v]=d.get(v,F(0))+F(1,len(cyc[f]))
        row=sum(d[v]*S[v] for v in d)
        if row>worst: worst=row
print(f"gamma-min cuts: worst ROWSUM over all f = {worst}={float(worst)} (N={n}) ROWSUM-O holds on gamma-min? {worst<=n}")
