"""Probe: SUM-SBC = ell^T O ell <= A*||ell||^2 (A=N+N^2/25-m).
Compare the Rayleigh quotient at ell against rho(O) and against A, esp. on two-lane where rho(O)>N.
Also verify identity sum_v T^2 == ell^T O ell exactly.
EXACT Fraction."""
from fractions import Fraction as F
import numpy as np
from _satzmu_conn import struct_for_side
from _h import Bconn
from _verify_two_lane import build_two_lane

def pf_of(M,cyc):
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    return pf

def analyze(name,n,adj,side):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M); A=F(N)+F(N*N,25)-m
    pf=pf_of(M,cyc)
    # O
    idx=list(M)
    O=[[F(0)]*m for _ in range(m)]
    for i,f in enumerate(idx):
        for j,g in enumerate(idx):
            O[i][j]=sum(pf[f].get(v,F(0))*pf[g].get(v,F(0)) for v in pf[f])
    L=[ell[f] for f in idx]
    # ell^T O ell
    lOl=sum(L[i]*L[j]*O[i][j] for i in range(m) for j in range(m))
    sumT2=sum(T[v]*T[v] for v in range(n))
    Gamma=sum(L[i]*L[i] for i in range(m))   # = ||ell||^2
    assert lOl==sumT2, (name,lOl,sumT2)
    # Rayleigh at ell:
    Rl=lOl/Gamma
    Of=np.array([[float(x) for x in r] for r in O])
    rho=max(np.linalg.eigvals(Of).real) if m>0 else 0.0
    sumsbc = lOl<=A*Gamma
    print(f"  {name}: N={N} m={m} Gamma={Gamma} A={str(A)}={float(A):.3f}  Ray(ell)={float(Rl):.4f} rho={rho:.4f} N={N}  "
          f"SUM-SBC {'OK' if sumsbc else 'FAIL'} (lOl={str(lOl)} A*Gamma={float(A*Gamma):.2f})  rho>N:{rho>N}")
    return sumsbc

if __name__=="__main__":
    for L in (8,12,16,20):
        n,E,side,bad=build_two_lane(L)
        adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        analyze("twolane%d"%L,n,adj,side)
