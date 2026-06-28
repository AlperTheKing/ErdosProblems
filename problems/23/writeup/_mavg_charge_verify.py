"""Independently verify the workflow's two checkable claims on the FULL uncapped gate:
(1) M-avg: sum_v S(v)^2 <= N*|M|  (= average ROWSUM <= N; Gram-trace 1^T O 1 = ||S||^2).
(2) CHARGE reformulation: sum_{v in supp(f)} max(0, p_f(v)S(v)-1) <= N - |supp(f)|  (corridor-hub overload
    <= count of off-corridor vertices) -- exact-equivalent route to ROWSUM-O via cardinality, per bad edge.
Census N=7..11 (ALL gamma-min cuts, NO CAP), witness K??CE@A{?]Fc, blow-ups, glued islands. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def build_S_pf(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    return M,ell,cyc,S,pf

def checks(n, adj, s):
    r=build_S_pf(n,adj,s)
    if r is None: return None
    M,ell,cyc,S,pf=r
    # (1) M-avg
    Q=sum(S[v]**2 for v in range(n)); mavg_ok = Q <= F(n)*len(M)
    # also confirm Gram-trace identity sum_f ROWSUM = Q
    sumrow=F(0); charge_ok=True; rowsumO_ok=True
    for f in M:
        d=pf[f]; ROW=sum(d[v]*S[v] for v in d); sumrow+=ROW
        if ROW>n: rowsumO_ok=False
        supp=set(d); over=sum(max(F(0), d[v]*S[v]-1) for v in supp)
        if not (over <= F(n)-len(supp)): charge_ok=False
    gram_ok = (sumrow==Q)
    return mavg_ok, charge_ok, rowsumO_ok, gram_ok, (Q, F(n)*len(M))

def run(name, n, E, allcuts=True):
    adj,cuts=gmins(n,E)
    if not cuts: return (name,0,0,0,0,0)
    mf=cf=rf=gf=0; tot=0
    for s in cuts:
        res=checks(n,adj,s)
        if res is None: continue
        tot+=1
        mavg_ok,charge_ok,rowsumO_ok,gram_ok,_=res
        mf+=not mavg_ok; cf+=not charge_ok; rf+=not rowsumO_ok; gf+=not gram_ok
    return (name,tot,mf,cf,rf,gf)

if __name__=="__main__":
    print("=== verify M-avg + CHARGE reformulation (exact, uncapped) ===",flush=True)
    print("  [census] name tot mavg-FAIL charge-FAIL rowsumO-FAIL gram-identity-FAIL",flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        T=mf=cf=rf=gf=0
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                res=checks(n,adj,s)
                if res is None: continue
                T+=1
                mavg_ok,charge_ok,rowsumO_ok,gram_ok,_=res
                mf+=not mavg_ok; cf+=not charge_ok; rf+=not rowsumO_ok; gf+=not gram_ok
        print(f"  N={nn}: cuts={T} mavg-FAIL={mf} charge-FAIL={cf} rowsumO-FAIL={rf} gram-FAIL={gf}",flush=True)
    # witness + structured
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    extra=[("K??CE@A{?]Fc",)+dec("K??CE@A{?]Fc"),
           ("Grotzsch",)+mycielski(5,Cn(5)),
           ("M(C7)",)+mycielski(7,Cn(7)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)]
    print("  [structured/witness]",flush=True)
    for it in extra:
        print("   ",run(*it),flush=True)
