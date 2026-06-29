"""GPT-Pro's PRIMITIVE lemma NET (distinct from the refuted GET!):
  E_P(I) <= #{C: span(C) meets I}
where E_P(I) is the endpoint-tax over P-CONTAINED ATOMS ONLY: for each bad edge g!=f and each geodesic Q
of g with Q a subpath of P (vertex set subset of P), weight 1/|cyc(g)|, overlap interval J(Q)=positions of Q
on P; E_P(I) = sum of weights over P-contained atoms with J(Q) meeting I.
[The refuted GET summed over ALL atoms incl. non-contained; the witness's overloading edges were
NON-contained, so that refutation may NOT apply to NET. Re-test exactly on gamma-min.]
Battery: census N<=11 gamma-min + glued + Grotzsch + Myc(Grotzsch). Exact Fraction. Report first E_P>c."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def check_cut(n,adj,s,name,acc):
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        # P-contained atoms only
        atoms=[]  # (lo,hi,weight)
        for g in M:
            if g==f: continue
            k=len(cyc[g])
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    J=sorted(pos[v] for v in Q)
                    atoms.append((J[0],J[-1],F(1,k)))
        # off-path components & spans
        rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
        def find(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for u in rest:
            for w in adj[u]:
                if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
        cd={}
        for v in rest: cd.setdefault(find(v),set()).add(v)
        spans=[]
        for r,C in cd.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: spans.append((min(A),max(A)))
        for a in range(L):
            for b in range(a,L):
                EP=sum(w for (lo,hi,w) in atoms if not (hi<a or lo>b))
                cI=sum(1 for (lo,hi) in spans if not (hi<a or lo>b))
                acc['ints']+=1
                if EP>cI:
                    acc['viol']+=1
                    if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,(a,b),str(EP),cI)

def run():
    acc={'ints':0,'viol':0,'first':None}
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        i0=acc['ints']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} gmin: intervals(+{acc['ints']-i0}) NET-viol(+{acc['viol']-v0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                        ("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); i0=acc['ints']; v0=acc['viol']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gmin: intervals(+{acc['ints']-i0}) NET-viol(+{acc['viol']-v0})",flush=True)
    print(f"\n  TOTAL intervals={acc['ints']} NET-violations(E_P>c)={acc['viol']}",flush=True)
    if acc['first']: print(f"  first NET violation: {acc['first']}",flush=True)
    print(f"  === {'NET FALSE on gamma-min (E_P>c): GPT-Pro primitive lemma dead too' if acc['viol'] else 'NET HOLDS on gamma-min: E_P(I)<=#components (P-contained endpoint-tax) -- GPT-Pro primitive lemma SURVIVES'} ===",flush=True)

if __name__=="__main__": run()
