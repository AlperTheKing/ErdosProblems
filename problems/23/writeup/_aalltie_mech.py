"""A-alltie mechanism probe.
Question 1: For a zero-mu edge uv with T(u)=N, is v ALWAYS K-isolated (no bad edge geodesic through v)?
            (equivalently T(v)=0).  This is A-alltie restated.
Question 2: Is A-alltie a PURELY LOCAL fact, or does it need gamma-minimality?
            Test A-alltie on NON-gamma-min connected max cuts (and even non-max cuts).
Question 3: The contrapositive. Suppose v has a bad-edge geodesic through it (T(v)>0) and uv is a B-edge.
            Take a geodesic P of bad edge g through v. v is interior or endpoint of g.
            Claim attempt: then either edge uv carries some mu (contradiction with zero-mu),
            OR u itself cannot be saturated. Probe which.
We dump, for zero-mu uv: T(u),T(v); and if T(v)>0, exhibit the bad edge g through v and its geodesic
            neighbors of v, checking if u is among g's geodesic support neighbors.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos
from _satzmu_conn import struct_for_side

def all_conn_maxcuts(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); out=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: out.append((side,G))
    return adj,out

def Acheck_side(n,adj,side):
    """return (cases, violations) for A-alltie on this specific cut."""
    st=struct_for_side(n,adj,side)
    if st is None: return 0,0
    M,ell,T,mu,cyc=st; N=n
    cases=0; viol=0
    for e,val in mu.items():
        if val!=0: continue
        u,v=e
        for (a,b) in ((u,v),(v,u)):
            if T[a]==N:
                cases+=1
                if T[b]!=0: viol+=1
    return cases,viol

if __name__=="__main__":
    print("=== A-alltie: gamma-min vs ALL connected max cuts (does it need gamma-minimality?) ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        gmin_c=0; gmin_v=0; allmax_c=0; allmax_v=0; nonmin_c=0; nonmin_v=0
        firstnonmin=None
        for g6 in outg:
            n,E=dec(g6); adj,cand=all_conn_maxcuts(n,E)
            if not cand: continue
            gm=min(G for _,G in cand)
            for side,G in cand:
                c,v=Acheck_side(n,adj,side)
                allmax_c+=c; allmax_v+=v
                if G==gm:
                    gmin_c+=c; gmin_v+=v
                else:
                    nonmin_c+=c; nonmin_v+=v
                    if v>0 and firstnonmin is None: firstnonmin=(g6,G,gm)
        print(f"  N={nn}: gamma-min cases={gmin_c} viol={gmin_v} | NON-min cases={nonmin_c} viol={nonmin_v} | all-max cases={allmax_c} viol={allmax_v}"
              + (f"  NONMIN-VIOL {firstnonmin}" if firstnonmin else ""), flush=True)
