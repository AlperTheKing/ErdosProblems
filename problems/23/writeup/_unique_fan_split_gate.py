"""Exact-gate Codex's UNIQUE/FAN split of interval Hall (block 162). For unique-geo f, interval I=[a,b]:
active comps C (span cap I); base=sum(spanlen), surplus=sum(cap-spanlen). Demand split by contributor type:
  U(I)=sum over g!=f, len(cyc[g])=1, Q=cyc[g][0] of |Q cap {x_a..x_b}|   (unique contributors)
  F(I)=sum over g!=f, len(cyc[g])>=2, Q in cyc[g] of |Q cap {x_a..x_b}| / |cyc[g]|  (fan contributors)
Gate (1) UNIQUE-BASE: U(I) <= base(I).  (2) FAN-RESIDUAL: F(I) <= (base(I)-U(I)) + surplus(I).
Together => interval Hall U+F <= base+surplus = sum cap. Battery census N<=11 + structured + glued. Exact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_scan(n, adj, s, name, acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cdict={}
        for v in rest: cdict.setdefault(find(v),set()).add(v)
        comps=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: comps.append((min(A),max(A),len(C)))
        # precompute per-g hit positions
        ginfo=[]
        for g in M:
            if g==f: continue
            k=len(cyc[g]); ginfo.append((k,[set(pos[v] for v in Q if v in Pset) for Q in cyc[g]]))
        for a in range(L):
            for b in range(a,L):
                Iset=set(range(a,b+1))
                active=[(lo,hi,cap) for (lo,hi,cap) in comps if not (hi<a or lo>b)]
                base=sum(hi-lo+1 for (lo,hi,cap) in active)
                surplus=sum(cap-(hi-lo+1) for (lo,hi,cap) in active)
                U=0; Fv=F(0)
                for (k,qhits) in ginfo:
                    if k==1:
                        U+=len(qhits[0]&Iset)
                    else:
                        Fv+=F(sum(len(h&Iset) for h in qhits), k)
                acc['ints']+=1
                if U>base:
                    acc['uviol']+=1
                    if acc['ufirst'] is None: acc['ufirst']=(name,''.join(map(str,s)),f,(a,b),U,base)
                if Fv > (base-U)+surplus:
                    acc['fviol']+=1
                    if acc['ffirst'] is None: acc['ffirst']=(name,''.join(map(str,s)),f,(a,b),str(Fv),base,U,surplus)

if __name__=="__main__":
    print("=== UNIQUE/FAN split of interval Hall (block 162, exact) ===",flush=True)
    acc={'ints':0,'uviol':0,'fviol':0,'ufirst':None,'ffirst':None}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        u0=acc['uviol']; f0=acc['fviol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,acc)
        print(f"  census N={nn}: UNIQUE-BASE-viol={acc['uviol']-u0} FAN-RESIDUAL-viol={acc['fviol']-f0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]:",flush=True)
    for name,n,E in extra:
        u0=acc['uviol']; f0=acc['fviol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,acc)
        print(f"    {name}: UNIQUE-BASE-viol={acc['uviol']-u0} FAN-RESIDUAL-viol={acc['fviol']-f0}",flush=True)
    print(f"\n  TOTAL intervals={acc['ints']} UNIQUE-BASE-viol={acc['uviol']} FAN-RESIDUAL-viol={acc['fviol']}",flush=True)
    if acc['ufirst']: print(f"  UNIQUE-BASE first viol: {acc['ufirst']}",flush=True)
    if acc['ffirst']: print(f"  FAN-RESIDUAL first viol: {acc['ffirst']}",flush=True)
    print(f"  === {'BOTH HOLD => interval Hall via unique/fan split' if acc['uviol']==0 and acc['fviol']==0 else 'VIOLATION (see above)'} ===",flush=True)
