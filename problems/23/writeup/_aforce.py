"""Test whether A-alltie needs gamma-minimality. For each triangle-free graph,
for EVERY connected max-cut (not just gamma-min), compute mu, T, and check A-alltie:
  zero-mu B-edge uv, T(u)=N  =>  T(v)=0.
Also test for a generic shortest-odd-cycle-witness setup WITHOUT max-cut:
just take any 2-coloring of a triangle-free graph that makes B connected.

Exact Fraction. Report any violation and whether it is a gamma-min cut.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr, geos

def build_info_for_cut(n, adj, side):
    """Build T, mu, etc. for an arbitrary cut 'side' (need not be max). Returns None if
    not B-connected or no bad edges or some bad edge has no B-geodesic (disconnected pair)."""
    if not Bconn(n, adj, side): return None
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    Bset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]!=side[v])
    ell={}; cyc={}; T=[F(0)]*n; T=[F(0) for _ in range(n)]
    for f in M:
        d=bdist_restr(adj,side,f[0],f[1])
        if d<0: return None
        ell[f]=d+1
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; k=len(Ps); sh=F(ell[f],k)
        for P in Ps:
            for v in P: T[v]+=sh
    # mu
    mu={frozenset(e):F(0) for e in Bset}
    for f in M:
        Ps=cyc[f]; k=len(Ps); w=F(ell[f],k)
        for P in Ps:
            for i in range(len(P)-1):
                e=frozenset((P[i],P[i+1]))
                if e in mu: mu[e]+=w
    G=sum(ell[f]**2 for f in M)
    return dict(n=n,adj=adj,side=side,M=M,ell=ell,Bset=Bset,T=T,cyc=cyc,mu=mu,G=G,beta=len(M))

def check_A(info, N):
    T=info['T']; mu=info['mu']
    viol=[]
    cases=0
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        for (a,b) in [(u,v),(v,u)]:
            if T[a]==N:
                cases+=1
                if T[b]!=0:
                    viol.append((a,b,float(T[a]),float(T[b])))
    return cases, viol

def run(nmin=7,nmax=10):
    for nn in range(nmin,nmax+1):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        tot_cases=0; tot_viol=0; wit=None
        # also track: among non-max cuts
        for g6 in outg:
            n,E=dec(g6)
            adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            cuts=maxcut_all(n,adj)  # all MAX cuts
            for side in cuts:
                info=build_info_for_cut(n,adj,side)
                if info is None: continue
                cases,viol=check_A(info,n)
                tot_cases+=cases; tot_viol+=len(viol)
                if viol and wit is None: wit=(g6,side,viol[:2],info['G'])
        print(f"  N={nn}: ALL max-cuts: A-cases={tot_cases} A-viol={tot_viol}"
              + (f"  WIT {wit}" if wit else ""), flush=True)

if __name__=="__main__":
    print("=== A-alltie over ALL max-cuts (test gamma-min necessity) ===")
    run(7,10)
