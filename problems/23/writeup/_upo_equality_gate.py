"""Exact-gate Codex's UPO equality-structure claim (block 155): every equality row UPO(f)=sum_{v in P}S(v)=N
(unique-geo f) is either (A) HAMILTON: |P|=N and no g!=f with positive overlap; or (B) SINGLE-NESTED: exactly
one g!=f with positive overlap, len(cyc[g])=1, its path subset of P. Battery: census N<=11 + structured + glued
+ Mycielskians. Exact Fraction. Reports first witness that is neither A nor B."""
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
        P_f=cyc[f][0]; Pset=set(P_f)
        upo=sum(S[v] for v in P_f)
        if upo!=n: continue   # equality rows only
        acc['eq']+=1
        # positive contributors g != f
        contribs=[]
        for g in M:
            if g==f: continue
            ov=sum(1 for Q in cyc[g] for v in Q if v in Pset)  # total overlap count over geodesics
            if ov>0: contribs.append(g)
        isA = (len(P_f)==n) and (len(contribs)==0)
        isB = (len(contribs)==1 and len(cyc[contribs[0]])==1 and set(cyc[contribs[0]][0])<=Pset)
        if not (isA or isB):
            acc['viol']+=1
            if first[0] is None:
                detail=[(g,len(cyc[g]),[Q for Q in cyc[g]]) for g in contribs]
                first[0]=(name,''.join(map(str,s)),f,P_f,str(upo),detail)
        else:
            acc['A' if isA else 'B']+=1

if __name__=="__main__":
    print("=== UPO EQUALITY-STRUCTURE gate (block 155): every UPO=N row is Hamilton(A) or single-nested(B) ===",flush=True)
    first=[None]; acc={'eq':0,'viol':0,'A':0,'B':0}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        e0=acc['eq']; v0=acc['viol']; a0=acc['A']; b0=acc['B']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: equality-rows={acc['eq']-e0} A(Hamilton)={acc['A']-a0} B(nested)={acc['B']-b0} VIOL={acc['viol']-v0}",flush=True)
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
        e0=acc['eq']; v0=acc['viol']; a0=acc['A']; b0=acc['B']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: equality-rows={acc['eq']-e0} A={acc['A']-a0} B={acc['B']-b0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL equality-rows={acc['eq']} (A={acc['A']} B={acc['B']}) VIOL={acc['viol']}",flush=True)
    print(f"  === {'FIRST WITNESS (neither A nor B): '+str(first[0]) if first[0] else 'ALL equality rows are Hamilton(A) or single-nested(B) -- equality structure holds'} ===",flush=True)
