"""Measure quadratic quantities for route (b) SOS design across battery samples.
For each config compute (centered x_v = T_v - N):
  Q1 = Gamma*(N^2/25 - beta)   [the RHS budget]
  nx2 = ||x||^2
  Dcut = sum_{cut uv}(x_u-x_v)^2 ; Dbad = sum_{bad uv}(x_u-x_v)^2
  TVcut, TVbad
  S = slack
Goal: see whether a fixed-coefficient quadratic certificate exists.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, Bconn, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def quants(n,adj,side):
    if not Bconn(n,adj,side): return None
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    N=n; m=len(M); Gamma=sum(ell[f]**2 for f in M)
    x=[T[v]-N for v in range(n)]
    nx2=sum(xi*xi for xi in x)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    Dcut=Dbad=F(0); TVcut=TVbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                dd=(x[u]-x[v]); ad=abs(dd)
                if side[u]!=side[v]: Dcut+=dd*dd; TVcut+=ad
                else: Dbad+=dd*dd; TVbad+=ad
    Q1=Gamma*(F(N*N,25)-m)
    sumTTN=sum(T[v]*(T[v]-N) for v in range(n))
    S=Q1-sumTTN-F(N,5)*(TVcut-TVbad)
    return dict(N=N,m=m,Gamma=Gamma,Q1=Q1,nx2=nx2,Dcut=Dcut,Dbad=Dbad,
                TVcut=TVcut,TVbad=TVbad,S=S,maxx=max(abs(xi) for xi in x))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

CONFIGS=[]
for parts in [[1,1,1,1,1],[2,2,2,2,2],[3,3,3,3,3],[2,2,2,2,3],[1,5,2,2,5],
              [1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[1,1,1,1,1,1,1]]:
    CONFIGS.append(("nu%s"%parts,)+blowup(parts))

if __name__=="__main__":
    print("%-16s %4s %4s %8s %10s %8s %8s %8s %8s %8s"%(
        "name","N","beta","Gamma","Q1","nx2","Dcut","Dbad","TVcut","S"))
    rows=[]
    for nm,n,E in CONFIGS:
        adj,cuts=gmins(n,E)
        if not cuts: continue
        q=quants(n,adj,cuts[0])
        if q is None: continue
        rows.append((nm,q))
        print("%-16s %4d %4d %8s %10s %8s %8s %8s %8s %8s"%(
            nm,q['N'],q['m'],q['Gamma'],q['Q1'],q['nx2'],q['Dcut'],q['Dbad'],
            q['TVcut'],float(q['S'])))
    # Mycielskians
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:1]:
            q=quants(nn,adj,s)
            if q: print("%-16s %4d %4d %8s %10s %8s %8s %8s %8s %8s"%(
                nm,q['N'],q['m'],q['Gamma'],q['Q1'],q['nx2'],q['Dcut'],q['Dbad'],q['TVcut'],float(q['S'])))
