"""Probe: when T(u)=N and uv is zero-mu, do ALL bad edges f through u satisfy p_f(u)=1?
And separately: what is the set of bad edges g whose geodesics could possibly pass through v
(v = the far end of the zero-mu corridor)?  We want to show that set is empty (T(v)=0).

ALSO test the candidate CLEAN LEMMA:
  (PF1-at-sat)  If T(u)=N then for every bad edge f with p_f(u)>0, p_f(u)=1
                (u lies on EVERY shortest geodesic of f).
If true, this is a strong structural fact about saturated vertices and may not need the zero-mu edge.
Test over census loads-cut + all gamma-min cuts.
Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side

def pf_of(N,M,cyc):
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps)
        for v in range(N):
            c=sum(1 for P in Ps if v in P)
            if c: pf[(f,v)]=F(c,k)
    return pf

def check_side(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st; N=n
    pf=pf_of(N,M,cyc)
    # PF1-at-sat: for every u with T[u]=N, every incident bad edge has p_f(u)=1
    pf1_viol=0; pf1_cases=0
    for u in range(N):
        if T[u]!=N: continue
        for f in M:
            if (f,u) in pf:
                pf1_cases+=1
                if pf[(f,u)]!=1: pf1_viol+=1
    return pf1_cases, pf1_viol

def all_gmin(n,E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not M: continue
        G=0; ok=True
        for (u,v) in M:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((side,G))
    if not cand: return adj,[]
    gm=min(G for _,G in cand)
    return adj,[s for s,G in cand if G==gm]

if __name__=="__main__":
    print("=== PF1-at-sat: T(u)=N => every incident bad edge has p_f(u)=1 (lies on every geodesic) ===")
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot_c=0; tot_v=0; firstv=None
        for g6 in outg:
            n,E=dec(g6); adj,sides=all_gmin(n,E)
            for side in sides:
                r=check_side(n,adj,side)
                if r is None: continue
                tot_c+=r[0]; tot_v+=r[1]
                if r[1]>0 and firstv is None: firstv=g6
        print(f"  N={nn} (all gamma-min cuts): PF1-cases={tot_c} violations={tot_v}"+(f"  WITNESS {firstv}" if firstv else ""), flush=True)
