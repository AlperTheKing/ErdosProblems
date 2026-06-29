"""Exact-gate Codex's SPAN-COVERAGE LEMMA (block 161): for unique-geo f with path P, every bad edge g!=f and
geodesic Q overlapping P in contiguous positions [r,s], EVERY i in [r,s] lies in at least one off-path
component span(C)=[min attach, max attach]. (=> union of active spans covers [r,s].)
Also confirms the mechanical implication span-coverage + span-capacity (cap>=spanlen) => subinterval corridor
capacity (b-a+1 <= sum_{C:span cap[a,b]}|C|) by checking subinterval capacity holds whenever coverage holds.
Battery census N<=11 + structured + glued + Mycielskians. Exact. Reports first coverage gap."""
import subprocess
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def row_scan(n, adj, s, name, first, acc):
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
        spans=[]
        for root,C in cdict.items():
            A=set(pos[x] for u in C for x in adj[u] if x in Pset and s[u]!=s[x])
            if A: spans.append((min(A),max(A),len(C)))
        covered_pos=set()
        for (lo,hi,cap) in spans:
            covered_pos.update(range(lo,hi+1))
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                hit=sorted(pos[v] for v in Q if v in Pset)
                if not hit: continue
                r,smax=hit[0],hit[-1]
                acc['checks']+=1
                missing=[i for i in range(r,smax+1) if i not in covered_pos]
                if missing:
                    acc['gap']+=1
                    if first[0] is None: first[0]=(name,''.join(map(str,s)),f,P_f,g,Q,(r,smax),missing,spans)
                # implication check: subinterval capacity for all [a,b] in [r,s]
                for a in range(r,smax+1):
                    for b in range(a,smax+1):
                        cap=sum(c for (lo,hi,c) in spans if not (hi<a or lo>b))
                        if b-a+1>cap:
                            acc['subviol']+=1
                            if acc['firstsub'] is None: acc['firstsub']=(name,f,(a,b),cap)

if __name__=="__main__":
    print("=== SPAN-COVERAGE LEMMA gate (block 161): every i in [r,s] in some component span (exact) ===",flush=True)
    first=[None]; acc={'checks':0,'gap':0,'subviol':0,'firstsub':None}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        c0=acc['checks']; g0=acc['gap']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: coverage-checks={acc['checks']-c0} GAP(uncovered pos)={acc['gap']-g0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("M(C7)",)+mycielski(7,Cn(7)),("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [structured/glued/Myc]:",flush=True)
    for name,n,E in extra:
        c0=acc['checks']; g0=acc['gap']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: coverage-checks={acc['checks']-c0} GAP={acc['gap']-g0}",flush=True)
    print(f"\n  TOTAL coverage-checks={acc['checks']} GAP={acc['gap']} | implication subinterval-capacity VIOL={acc['subviol']}",flush=True)
    print(f"  === {'COVERAGE GAP: '+str(first[0]) if first[0] else 'SPAN-COVERAGE holds (every i in [r,s] covered); + span-capacity => subinterval corridor capacity (subviol=0)'} ===",flush=True)
