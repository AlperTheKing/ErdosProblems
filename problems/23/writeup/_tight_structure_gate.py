"""Exact-gate Codex's EQUALITY-STRUCTURE strengthening (block 153): for every POSITIVE TIGHT interval I=[a,b]
(lhs(I)=sum_{[a,b]}d_i > 0 and lhs(I)=cap(I)=sum_{C:span cap I}|C|) of a unique-geo row, conjecture:
  qcount(I)=#{(g,Q): g!=f, Q in cyc(g), Q cap {x_a..x_b} != empty} = 1,
  gcount(I)=#distinct such g = 1,  ccount(I)=#{C: span(C) cap I != empty} = 1.
Battery: census N<=11 + K??CB@OBDOAp + K??CE@A{?]Fc + glued + Mycielskians. Exact. Reports first witness != 1/1/1."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_scan(n, adj, s, name, first, acc):
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
        dvec=[S[P_f[i]]-1 for i in range(L)]
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cdict={}
        for v in rest: cdict.setdefault(find(v),set()).add(v)
        compinfo=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: compinfo.append((min(A),max(A),len(C)))
        for a in range(L):
            for b in range(a,L):
                lhs=sum(dvec[i] for i in range(a,b+1))
                if lhs<=0: continue
                cap=sum(c for (lo,hi,c) in compinfo if not (hi<a or lo>b))
                if lhs!=cap: continue
                # positive tight
                acc['tight']+=1
                qcount=0; gset=set()
                for g in M:
                    if g==f: continue
                    for Q in cyc[g]:
                        if any(pos.get(v,-99) in range(a,b+1) for v in Q):
                            qcount+=1; gset.add(g)
                gcount=len(gset)
                ccount=sum(1 for (lo,hi,c) in compinfo if not (hi<a or lo>b))
                if not (qcount==1 and gcount==1 and ccount==1):
                    acc['viol']+=1
                    if first[0] is None:
                        first[0]=(name,''.join(map(str,s)),f,P_f,(a,b),str(lhs),cap,qcount,gcount,ccount)

if __name__=="__main__":
    print("=== POSITIVE-TIGHT interval equality-structure gate (block 153, exact) ===",flush=True)
    first=[None]; acc={'tight':0,'viol':0}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['tight']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: positive-tight-intervals={acc['tight']-a0} viol(!=1/1/1)={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("M(C7)",)+mycielski(7,Cn(7)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued/Myc]:",flush=True)
    for name,n,E in extra:
        a0=acc['tight']; v0=acc['viol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: positive-tight={acc['tight']-a0} viol={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL positive-tight intervals={acc['tight']}, viol(qcount/gcount/ccount != 1/1/1)={acc['viol']}",flush=True)
    print(f"  === {'FIRST WITNESS: '+str(first[0]) if first[0] else 'ALL positive-tight intervals have qcount=gcount=ccount=1 (equality structure holds)'} ===",flush=True)
