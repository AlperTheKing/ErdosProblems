"""Gate Codex's UNIQUE-PATH OVERLAP sublemma (block 139): for every UNIQUE-geodesic bad edge f
(len(cyc[f])==1, unique path P_f), sum_{v in P_f} S(v) <= N, S(v)=sum_g p_g(v). This is ROWSUM-O restricted
to unique-geo rows (p_f=1_{P_f}). Battery beyond Codex's N<=12 census: census N<=11, Mycielskians N<=23,
glued islands, explicit blow-ups. Report worst margin + any violation. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def check(n, adj, s, first):
    st=struct_for_side(n,adj,s)
    if st is None: return 0,0,None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    nrows=0; nfail=0; worst=None
    for f in M:
        if len(cyc[f])!=1: continue   # unique-geodesic only
        P=cyc[f][0]; val=sum(S[v] for v in P)
        nrows+=1; margin=F(n)-val
        if worst is None or margin<worst: worst=margin
        if val>n:
            nfail+=1
            if first[0] is None: first[0]=(s,f,P,str(val),n)
    return nrows,nfail,worst

def run(name,n,E,first):
    adj,cuts=gmins(n,E); R=Fl=0; wm=None
    for s in cuts:
        r,f,w=check(n,adj,s,first); R+=r; Fl+=f
        if w is not None and (wm is None or w<wm): wm=w
    return name,len(cuts),R,Fl,wm

if __name__=="__main__":
    print("=== UNIQUE-PATH OVERLAP gate: sum_{v in P_f} S(v) <= N for unique-geo f (exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        R=Fl=0; wm=None
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                r,f,w=check(n,adj,s,first); R+=r; Fl+=f
                if w is not None and (wm is None or w<wm): wm=w
        print(f"  census N={nn}: unique-rows={R} FAILS={Fl} worst-margin={wm}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CB@OBDOAp",)+dec("K??CB@OBDOAp"),
           ("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("M(C7)",)+mycielski(7,Cn(7)),
           ("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0)]
    print("  [witnesses/structured/N23]: name cuts unique-rows FAILS worst-margin",flush=True)
    for it in extra:
        print("   ",run(*it,first),flush=True)
    print(f"\n=== {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'NO VIOLATION (UNIQUE-PATH OVERLAP holds on full battery)'} ===",flush=True)
