"""Test at N=26 (exact maxcut_all): can a NON-JUNCTION chord layout (single long chord, or disjoint/nested)
be a genuine connected-B GLOBAL max cut with a unique-path interval-Hall failure?  If NO non-junction
layout is ever global-max-with-IH-failure (while the chaining k-chord IS), that confirms the (B*) mechanism:
global maximality forbids non-junction overload. Slow (2^25 per layout) -- run few layouts."""
from fractions import Fraction as F
from _h import maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def build(pend, chords):
    E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for (a,b) in chords: E.append((min(a,b),max(a,b)))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))
def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def ih_fail_and_junction(n,adj,s):
    st=struct_for_side(n,adj,s)
    if st is None: return (False,False)
    M,elld,T,mu,cyc=st
    S=[F(0)]*n
    for g in M:
        kk=len(cyc[g])
        for P in cyc[g]:
            for v in P: S[v]+=F(1,kk)
    anyfail=False; anyjct=False
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        Pcont=set()
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset: Pcont.add((min(g),max(g))); break
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        comps=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        fail=False
        for a in range(L):
            for b in range(a,L):
                dem=sum(dvec[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                if dem>cap: fail=True; break
            if fail: break
        if fail:
            anyfail=True
            for i in range(L):
                x=P_f[i]
                inc=[(min(x,w),max(x,w)) for w in adj[x] if s[w]==s[x] and w in pos and (min(x,w),max(x,w)) in Pcont]
                left=[e for e in inc if pos[e[0] if e[1]==x else e[1]]<i]
                right=[e for e in inc if pos[e[0] if e[1]==x else e[1]]>i]
                if left and right: anyjct=True; break
    return (anyfail,anyjct)

def analyze(name,pend,chords):
    n,E=build(pend,chords); adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    if not tri_free(n,adj): print(f"  {name} n={n}: NOT tri-free",flush=True); return
    allcuts=maxcut_all(n,adj); mc=cutsize(n,adj,list(allcuts[0]))
    s=[v%2 for v in range(n)]; ps=cutsize(n,adj,s)
    isglobalmax=(ps==mc); bc=Bconn(n,adj,s)
    fail,jct=(False,False)
    if isglobalmax and bc: fail,jct=ih_fail_and_junction(n,adj,s)
    print(f"  {name} n={n} parity-cut={ps} GLOBALmax={mc} is-global-max={isglobalmax} Bconn={bc} IH-FAIL={fail} junction={jct}",flush=True)
    if isglobalmax and bc and fail and not jct:
        print(f"     *** (B*) COUNTEREXAMPLE: global-max + IH-fail + NO junction => descent route needs revision ***",flush=True)

if __name__=="__main__":
    import sys
    print("=== N=26 exact: non-junction layouts vs global-max + IH-failure (slow) ===",flush=True)
    # chaining (known global-max, junction) as control:
    analyze("chain-k3-c4",12,[(0,4),(4,8),(8,12)])
    # single long pass-through chord (no junction possible):
    analyze("single-(2,10)",12,[(2,10)])
    analyze("single-(0,8)",12,[(0,8)])
    # disjoint (no shared endpoint):
    analyze("disjoint-(0,4)(8,12)",12,[(0,4),(8,12)])
    # nested (no shared endpoint):
    analyze("nested-(0,8)(2,6)",12,[(0,8),(2,6)])
