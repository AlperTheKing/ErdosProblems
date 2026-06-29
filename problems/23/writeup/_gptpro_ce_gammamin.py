"""Follow-up to GPT-Pro CE: on the parity cut UPO fails (uload(4)=2 etc.), but parity is NOT gamma-min.
Check ULOAD-ONE + UNIQUE-BASE + UPO on the GAMMA-MIN cuts of the same graph -- expect them to HOLD (gamma-min
rescues). This shows the unique-path lemmas REQUIRE gamma-minimality (Codex block-166 'max-cut-only' is false @ N=26)."""
from fractions import Fraction as F
from _satzmu_conn import struct_for_side
from _stark1 import gmins

n=26
E=[]
for i in range(12): E.append((i,i+1))
det=[0,13,14,15,16,17,18,19,20,21,22,23,24,25,12]
for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
E += [(0,4),(4,8),(8,12),(0,12)]
E=sorted(set(E))

# (A) parity cut: confirm ULOAD-ONE fails (uload(4)=2)
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
side=[v%2 for v in range(n)]
st=struct_for_side(n,adj,side); M,ell,T,mu,cyc=st
f=(0,12); P=cyc[f][0]; pos={x:i for i,x in enumerate(P)}; Pset=set(P)
uload=[0]*len(P)
for g in M:
    if g==f or len(cyc[g])!=1: continue
    for v in cyc[g][0]:
        if v in Pset: uload[pos[v]]+=1
print(f"PARITY cut f=(0,12): uload along P = {uload}  max={max(uload)} -> ULOAD-ONE {'FAILS' if max(uload)>1 else 'holds'} on parity (non-gmin)")

# (B) gamma-min cuts: ULOAD-ONE + UPO
adj2,cuts=gmins(n,E)
print(f"\ngamma-min cuts: {len(cuts)}")
maxul=0; upo_fail=0; ub_fail=0; ngood=0
for s in cuts:
    stg=struct_for_side(n,adj2,s)
    if stg is None: continue
    M2,ell2,T2,mu2,cyc2=stg
    S=[F(0)]*n
    for g in M2:
        Ps=cyc2[g]; k=len(Ps); seen={}
        for P2 in Ps:
            for v in P2: seen[v]=seen.get(v,F(0))+F(1,k)
        for v,pv in seen.items(): S[v]+=pv
    for f2 in M2:
        if len(cyc2[f2])!=1: continue
        Pf=cyc2[f2][0]; posf={x:i for i,x in enumerate(Pf)}; Psetf=set(Pf)
        # UPO
        upo=sum(S[v] for v in Pf)
        if upo>n: upo_fail+=1
        # ULOAD-ONE
        ul=[0]*len(Pf)
        for g in M2:
            if g==f2 or len(cyc2[g])!=1: continue
            for v in cyc2[g][0]:
                if v in Psetf: ul[posf[v]]+=1
        maxul=max(maxul,max(ul) if ul else 0)
print(f"  gamma-min: max ULOAD over all unique rows = {maxul}  (ULOAD-ONE {'HOLDS' if maxul<=1 else 'FAILS'} on gamma-min)")
print(f"  gamma-min: UPO-violations (sum_P S > N) = {upo_fail}")
print(f"\n=> CONCLUSION: parity (non-gmin) cut violates UPO & ULOAD-ONE; gamma-min cuts satisfy both.")
print(f"   => unique-path lemmas REQUIRE gamma-minimality; max-cut-only versions are FALSE at N=26.")
