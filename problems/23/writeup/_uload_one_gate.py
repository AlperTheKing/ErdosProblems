"""Exact-gate Codex's ULOAD-ONE (block 165): for unique-geo f with path P, every position i:
  uload_unique(i) = #{g in M, g!=f, len(cyc[g])=1, x_i in cyc[g][0]} <= 1.
(=> with SPAN-COVERAGE => pointwise UNIQUE-BASE => UNIQUE-BASE.) Critical test: glued islands N=18 (many unique
rows, beyond Codex's N<=12 census). Battery census N<=11 + glued + witnesses. Exact. Reports first i with >=2."""
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
        P_f=cyc[f][0]; Pset=set(P_f); pos={x:i for i,x in enumerate(P_f)}
        uload=[0]*len(P_f)
        for g in M:
            if g==f or len(cyc[g])!=1: continue
            for v in cyc[g][0]:
                if v in Pset: uload[pos[v]]+=1
        for i,ul in enumerate(uload):
            acc['pos']+=1; acc['max']=max(acc['max'],ul)
            if ul>=2:
                acc['viol']+=1
                if first[0] is None:
                    contribs=[(g,cyc[g][0]) for g in M if g!=f and len(cyc[g])==1 and P_f[i] in cyc[g][0]]
                    first[0]=(name,''.join(map(str,s)),f,P_f,i,ul,contribs)

if __name__=="__main__":
    print("=== ULOAD-ONE gate (block 165): uload_unique(i) <= 1 (exact) ===",flush=True)
    first=[None]; acc={'pos':0,'viol':0,'max':0}
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        p0=acc['pos']; v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: row_scan(n,adj,s,g6,first,acc)
        print(f"  census N={nn}: positions={acc['pos']-p0} VIOL(uload>=2)={acc['viol']-v0}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0),
           ("C5|brg|M(C7)",)+bridge((5,Cn(5)),mycielski(7,Cn(7)),0,0),
           ("C7|brg|C7",)+bridge((7,Cn(7)),(7,Cn(7)),0,0)]
    print("  [glued/witness -- KEY beyond Codex census]:",flush=True)
    for name,n,E in extra:
        p0=acc['pos']; v0=acc['viol']; adj,cuts=gmins(n,E)
        for s in cuts: row_scan(n,adj,s,name,first,acc)
        print(f"    {name}: positions={acc['pos']-p0} VIOL={acc['viol']-v0}",flush=True)
    print(f"\n  TOTAL positions={acc['pos']} VIOL(uload>=2)={acc['viol']} max_uload={acc['max']}",flush=True)
    print(f"  === {'FIRST VIOLATION (uload>=2): '+str(first[0]) if first[0] else 'ULOAD-ONE holds (<=1 unique geodesic per corridor vertex) => with span-coverage, UNIQUE-BASE'} ===",flush=True)
