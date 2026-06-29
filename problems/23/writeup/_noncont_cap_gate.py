"""Exact-gate Codex's DECOMPOSITION lemma (block 176): D_noncont(I) <= cap(I) for every unique f, interval I.
D_noncont(I) = sum over g!=f NOT P-contained (no geodesic subset of P) of sum_{i in [a,b]} p_g(x_i).
cap(I) = sum_{C: span(C) intersects I} |C|. If holds: non-contained demand always covered by capacity, so any
interval-Hall failure is driven by P-contained nested rows (handled by singleton Gamma-descent).
Battery: census N<=11 gamma-min + k-chord non-gamma cuts + glued islands. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def kchord(k, clen=4):
    pend=clen*k; E=[(i,i+1) for i in range(pend)]
    nint=pend+1; ext=list(range(pend+1, pend+1+nint)); det=[0]+ext+[pend]
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    for j in range(k): E.append((clen*j, clen*j+clen))
    E.append((0,pend))
    return pend+1+nint, sorted(set((min(a,b),max(a,b)) for a,b in E))

def check_cut(n,adj,s,name,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        # P-contained classification
        noncont=[]
        for g in M:
            if g==f: continue
            contained = any(set(Q)<=Pset for Q in cyc[g])
            if not contained: noncont.append(g)
        # noncont mass per position
        nc_at=[F(0)]*L
        for g in noncont:
            d=pf[g]
            for v,pv in d.items():
                if v in Pset: nc_at[pos[v]]+=pv
        # components
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
        for a in range(L):
            for b in range(a,L):
                Dnc=sum(nc_at[i] for i in range(a,b+1))
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                acc['ints']+=1
                if Dnc>cap:
                    acc['viol']+=1
                    if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,(a,b),str(Dnc),cap)

if __name__=="__main__":
    print("=== D_noncont(I) <= cap(I) decomposition gate (block 176, exact) ===",flush=True)
    acc={'ints':0,'viol':0,'first':None}
    # k-chord non-gamma parity cuts
    for clen in (4,6):
        for k in (3,6,9):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]; i0=acc['ints']; v0=acc['viol']
            check_cut(n,adj,s,f"k{k}c{clen}-parity",acc)
            print(f"  kchord k={k} clen={clen} N={n} parity: intervals={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    # census N<=11 gamma-min
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        i0=acc['ints']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} gamma-min: intervals={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E); i0=acc['ints']; v0=acc['viol']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gamma-min: intervals={acc['ints']-i0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL intervals={acc['ints']} VIOL={acc['viol']}",flush=True)
    print(f"  === {'VIOLATION: '+str(acc['first']) if acc['first'] else 'D_noncont <= cap holds: noncontained demand always covered by capacity (proof split valid)'} ===",flush=True)
