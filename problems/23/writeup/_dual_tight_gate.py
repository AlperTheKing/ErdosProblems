"""Exact-gate Codex's DUAL-TIGHTNESS statement (block 158): for the geodesic-interval packing flow, every
zero-slack nonempty demand subset X (cap(N(X))=demand(X)) is the SINGLE-NESTED equality pattern: |X|=1 with
integer demand 5, exactly one touched component of cap 5, that demand's geodesic wholly in P_f, and UPO(f)=N.
Subset exhaustion 2^|demands|; skip rows with |demands|>MAXD. Battery: census N<=11 + structured + glued.
Exact Fraction. Reports first zero-slack subset that is NOT the single-nested pattern."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
MAXD=18

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
        P_f=cyc[f][0]; pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        upo=sum(S[v] for v in P_f); upoN=(upo==n)
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
        demands=[]; intervals=[]; dpaths=[]
        for g in M:
            if g==f: continue
            k=len(cyc[g])
            for Q in cyc[g]:
                hit=sorted(pos[v] for v in Q if v in Pset)
                if not hit: continue
                demands.append(F(len(hit),k)); intervals.append((hit[0],hit[-1])); dpaths.append((g,Q,set(Q)<=Pset))
        nd=len(demands)
        if nd==0: continue
        if nd>MAXD: acc['skip']+=1; continue
        # adjacency demand i -> components
        adjc=[]
        for (r,smax) in intervals:
            adjc.append(set(j for j,(lo,hi,c) in enumerate(compinfo) if not (hi<r or lo>smax)))
        caps=[c for (lo,hi,c) in compinfo]
        for r in range(1,nd+1):
            for X in itertools.combinations(range(nd),r):
                NX=set()
                for i in X: NX|=adjc[i]
                slack=sum(caps[j] for j in NX)-sum(demands[i] for i in X)
                if slack==0:
                    acc['zero']+=1
                    # single-nested pattern check
                    ok = (len(X)==1 and demands[X[0]]==5 and len(NX)==1
                          and caps[next(iter(NX))]==5 and dpaths[X[0]][2] and upoN)
                    if not ok:
                        acc['viol']+=1
                        if first[0] is None:
                            first[0]=(name,''.join(map(str,s)),f,P_f,X,[str(demands[i]) for i in X],
                                      sorted(NX),[caps[j] for j in NX],upoN)
    return

if __name__=="__main__":
    print("=== DUAL-TIGHTNESS gate (block 158): every zero-slack demand subset = single-nested pattern ===",flush=True)
    first=[None]; acc={'zero':0,'viol':0,'skip':0}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        z0=acc['zero']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: zero-slack-subsets={acc['zero']-z0} VIOL(not single-nested)={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued]:",flush=True)
    for name,n,E in extra:
        z0=acc['zero']; v0=acc['viol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: zero-slack-subsets={acc['zero']-z0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL zero-slack-subsets={acc['zero']} VIOL={acc['viol']} skipped(|demands|>{MAXD})={acc['skip']}",flush=True)
    print(f"  === {'FIRST WITNESS: '+str(first[0]) if first[0] else 'ALL zero-slack demand subsets are the single-nested pattern -- dual tightness holds'} ===",flush=True)
