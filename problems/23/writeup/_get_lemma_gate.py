"""Exact-gate GPT-Pro's proof structure (gap-load + endpoint-tax GET). For unique f, path P, interval I=[a,b]:
demand D(I)=sum_{i in I}(S(x_i)-1) = G(I)+E(I) where, over g!=f and geodesics Q with overlap interval J(Q)=
positions of Q cap P:
  G(I)=sum_{g,Q}(1/|cyc(g)|)*(|J(Q) cap I| - 1)_+   [gap-load]
  E(I)=sum_{g,Q}(1/|cyc(g)|)*1[J(Q) cap I != empty]  [endpoint-tax]
Components C: span [lo,hi], cap |C|. c(I)=#{C: span cap I != empty}.
TEST: (a) identity D=G+E; (b) GAP: G(I) <= sum_{C: span cap I}(|C|-1) [GPT-Pro claims max-cut]; (c) GET:
E(I) <= c(I) [GPT-Pro claims gamma-min]; (d) D(I) <= cap(I) [interval Hall]. On gamma-min (census,glued): GET
should HOLD. On non-gamma k-chord parity: GET should FAIL (E>c). Exact Fraction."""
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

def check(n,adj,s,name,acc,is_gmin):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        dvec=[S[v]-1 for v in P_f]
        # geodesic atoms (g!=f, Q): J=sorted positions, weight 1/|cyc(g)|
        atoms=[]
        for g in M:
            if g==f: continue
            k=len(cyc[g])
            for Q in cyc[g]:
                J=sorted(pos[v] for v in Q if v in Pset)
                if J: atoms.append((J[0],J[-1],F(1,k)))
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
                D=sum(dvec[i] for i in range(a,b+1))
                G=F(0); E=F(0)
                for (r,smax,w) in atoms:
                    ov=min(b,smax)-max(a,r)+1
                    if ov>0: G+=w*(ov-1); E+=w
                cap=sum(c for (lo,hi,c) in comps if not (hi<a or lo>b))
                cI=sum(1 for (lo,hi,c) in comps if not (hi<a or lo>b))
                gapcap=sum(c-1 for (lo,hi,c) in comps if not (hi<a or lo>b))
                acc['n']+=1
                if D!=G+E: acc['idfail']+=1
                if G>gapcap: acc['gapfail']+=1
                if E>cI:
                    acc['getfail']+=1
                    acc['get_on_gmin' if is_gmin else 'get_on_nongmin']+=1
                if D>cap: acc['ihfail']+=1

if __name__=="__main__":
    print("=== GPT-Pro structure gate: D=G+E, GAP G<=sum(|C|-1), GET E<=c(I), interval Hall D<=cap ===",flush=True)
    acc={'n':0,'idfail':0,'gapfail':0,'getfail':0,'ihfail':0,'get_on_gmin':0,'get_on_nongmin':0}
    print("  [non-gamma k-chord parity -- GET should FAIL here]:",flush=True)
    for clen in (4,6):
        for k in (3,6):
            n,E=kchord(k,clen); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            s=[v%2 for v in range(n)]; g0=acc['getfail']; ih0=acc['ihfail']; gp0=acc['gapfail']
            check(n,adj,s,f"k{k}c{clen}",acc,is_gmin=False)
            print(f"    kchord k={k} clen={clen} N={n}: GET-fail(+{acc['getfail']-g0}) GAP-fail(+{acc['gapfail']-gp0}) IH-fail(+{acc['ihfail']-ih0})",flush=True)
    print("  [gamma-min census + glued -- GET should HOLD]:",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        g0=acc['getfail']; gp0=acc['gapfail']; ih0=acc['ihfail']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check(n,adj,s,g6,acc,is_gmin=True)
        print(f"    census N={nn} gmin: GET-fail(+{acc['getfail']-g0}) GAP-fail(+{acc['gapfail']-gp0}) IH-fail(+{acc['ihfail']-ih0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    for name,(nn,E) in [("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]:
        adj,cuts=gmins(nn,E); g0=acc['getfail']
        for s in cuts: check(nn,adj,s,name,acc,is_gmin=True)
        print(f"    {name} N={nn} gmin: GET-fail(+{acc['getfail']-g0})",flush=True)
    print(f"\n  TOTALS: intervals={acc['n']} identity-fail={acc['idfail']} GAP-fail={acc['gapfail']} GET-fail={acc['getfail']} IH-fail={acc['ihfail']}",flush=True)
    print(f"  GET failures on GAMMA-MIN cuts = {acc['get_on_gmin']} (should be 0); on non-gamma = {acc['get_on_nongmin']} (expect >0)",flush=True)
    print(f"  === GPT-Pro structure: identity {'OK' if acc['idfail']==0 else 'BAD'}; GAP(max-cut) {'HOLDS' if acc['gapfail']==0 else 'FAILS'}; GET on gamma-min {'HOLDS' if acc['get_on_gmin']==0 else 'FAILS'} ===",flush=True)
