"""Verify Codex's contiguity lemma on structured graphs beyond his N<=12 census (glued islands, nested witness):
if f has unique geodesic P_f, every g-geodesic Q meets P_f in a contiguous interval of P_f's vertex order."""
from _h import dec
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def contig_ok(P_f, Q):
    pos={v:i for i,v in enumerate(P_f)}
    idx=sorted(pos[v] for v in Q if v in pos)
    if len(idx)<=1: return True
    return idx==list(range(idx[0], idx[0]+len(idx)))

def run(name,n,E):
    adj,cuts=gmins(n,E); urows=0; comps=0; fail=None
    for s in cuts:
        st=struct_for_side(n,adj,s)
        if st is None: continue
        M,ell,T,mu,cyc=st
        for f in M:
            if len(cyc[f])!=1: continue
            P_f=cyc[f][0]; urows+=1
            for g in M:
                for Q in cyc[g]:
                    comps+=1
                    if not contig_ok(P_f,Q): fail=(name,f,g,P_f,Q)
    print(f"  {name}: N={n} unique_rows={urows} comparisons={comps} fail={fail}")

def bridge(b1,b2,u,v):
    n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]

if __name__=="__main__":
    print("=== contiguity check on structured graphs (beyond Codex N<=12 census) ===")
    run("K??CB@OBDOAp", *dec("K??CB@OBDOAp"))
    run("K??CE@A{?]Fc", *dec("K??CE@A{?]Fc"))
    run("C7|brg|Grotzsch", *bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0))
    run("C9|brg|C9", *bridge((9,Cn(9)),(9,Cn(9)),0,0))
