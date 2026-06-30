"""Slack chain Gamma vs ||T||^2/N vs rho(O) on two-lane using the EXPLICIT parity cut (no brute maxcut).
Confirmed gamma-min global-max by _verify_two_lane (CP-SAT). Quantify how much slack Gamma<=N^2 has
when SM and rho(O)<=N are FALSE."""
from fractions import Fraction as F
import numpy as np
from _satzmu_conn import struct_for_side

def two_lane(L):
    a=lambda i:(L+1)+i; b=lambda i:(L+1)+(L+1)+i
    n=3*(L+1); E=set()
    for i in range(L): E.add((i,i+1))
    for i in range(L+1):
        E.add((min(i,a(i)),max(i,a(i)))); E.add((min(i,b(i)),max(i,b(i))))
    for i in range(L):
        for u in (a(i),b(i)):
            for v in (a(i+1),b(i+1)): E.add((min(u,v),max(u,v)))
    for e in [(0,L-2),(0,L),(2,L-2),(2,L)]: E.add((min(e),max(e)))
    side=[0]*n
    for i in range(L+1): side[i]=i%2
    for i in range(L+1): side[a(i)]=1-(i%2); side[b(i)]=1-(i%2)
    return n,sorted(E),side

for L in (8,12,16,20,24):
    n,E,side=two_lane(L)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    st=struct_for_side(n,adj,side)
    M,ell,T,mu,cyc=st
    N=n
    Gamma=sum(ell[f]**2 for f in M)
    normT2=sum(t*t for t in T)
    # O matrix
    Mi=list(M)
    pf={}
    for f in M:
        Ps=cyc[f]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[f]=d
    O=[[sum(pf[Mi[i]].get(v,F(0))*pf[Mi[j]].get(v,F(0)) for v in range(n)) for j in range(len(Mi))] for i in range(len(Mi))]
    Of=np.array([[float(x) for x in row] for row in O])
    rho=max(abs(np.linalg.eigvals(Of)))
    print(f"two-lane L={L} N={N}: Gamma={Gamma} N^2={N*N} (G/N^2={float(F(Gamma,N*N)):.4f}) | "
          f"||T||^2={normT2} N*Gamma={N*Gamma} SM={normT2<=N*Gamma} (r={float(F(normT2,N*Gamma)):.4f}) | "
          f"rho(O)={rho:.3f} rho<=N={rho<=N} (r={rho/N:.4f}) | "
          f"GammaSqOverN={float(F(Gamma*Gamma,N))} vs ||T||^2={float(normT2)}")
