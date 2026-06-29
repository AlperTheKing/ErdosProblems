"""Comprehensive: which unique-path lemmas survive at N=26 on the GAMMA-MIN cuts of GPT-Pro's graph?
Check per gamma-min cut, per unique row: UPO (sum_P S<=N), pointwise UNIQUE-BASE (uload(i)<=cover(i)),
UNIQUE-BASE (U(I)<=base(I)), span-coverage, ULOAD-ONE (uload<=1). Report which hold/fail. This pins down which
lemmas are census-blind (die at N=26) vs real."""
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
adj2,cuts=gmins(n,E)
print(f"N={n} gamma-min cuts={len(cuts)}")
res={'upo':0,'uload_one':0,'pointwise_ub':0,'unique_base':0,'span_cov':0,'unique_rows':0}
for s in cuts:
    st=struct_for_side(n,adj2,s)
    if st is None: continue
    M,ell,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        Ps=cyc[g]; k=len(Ps); seen={}
        for P in Ps:
            for v in P: seen[v]=seen.get(v,F(0))+F(1,k)
        for v,pv in seen.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        res['unique_rows']+=1
        P=cyc[f][0]; L=len(P); pos={x:i for i,x in enumerate(P)}; Pset=set(P)
        # UPO
        if sum(S[v] for v in P)>n: res['upo']+=1
        # components/spans
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj2[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        spans=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj2[u] if x in Pset and s[u]!=s[x])
            if A: spans.append((min(A),max(A),len(C)))
        # uload, cover
        uload=[0]*L
        for g in M:
            if g==f or len(cyc[g])!=1: continue
            for v in cyc[g][0]:
                if v in Pset: uload[pos[v]]+=1
        cover=[sum(1 for (lo,hi,c) in spans if lo<=i<=hi) for i in range(L)]
        if max(uload)>1: res['uload_one']+=1
        if any(uload[i]>cover[i] for i in range(L)): res['pointwise_ub']+=1
        # span-coverage: for each g-corridor, every pos covered
        covered=set()
        for (lo,hi,c) in spans: covered.update(range(lo,hi+1))
        sc_fail=False
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                hit=[pos[v] for v in Q if v in Pset]
                if hit:
                    for i in range(min(hit),max(hit)+1):
                        if i not in covered: sc_fail=True
        if sc_fail: res['span_cov']+=1
        # UNIQUE-BASE per interval
        ub_fail=False
        for a in range(L):
            for b in range(a,L):
                U=0
                for g in M:
                    if g==f or len(cyc[g])!=1: continue
                    U+=sum(1 for v in cyc[g][0] if v in Pset and a<=pos[v]<=b)
                base=sum(hi-lo+1 for (lo,hi,c) in spans if not (hi<a or lo>b))
                if U>base: ub_fail=True
        if ub_fail: res['unique_base']+=1
print(f"unique-rows checked: {res['unique_rows']}")
print(f"  UPO violations:            {res['upo']}")
print(f"  ULOAD-ONE failures:        {res['uload_one']}  <- {'DEAD at N=26' if res['uload_one'] else 'holds'}")
print(f"  pointwise UNIQUE-BASE fail:{res['pointwise_ub']}  <- {'DEAD' if res['pointwise_ub'] else 'HOLDS (uload<=cover, cover>=2 where needed)'}")
print(f"  UNIQUE-BASE (interval) fail:{res['unique_base']}  <- {'DEAD' if res['unique_base'] else 'HOLDS'}")
print(f"  span-coverage failures:    {res['span_cov']}  <- {'DEAD' if res['span_cov'] else 'holds'}")
