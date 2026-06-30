"""DECISIVE: on the two-lane family (where rho(O)>N), does the WEAKER (SM) sum_v T^2 <= N*Gamma survive?
(SM) = Rayleigh of O AT ell specifically = ell^T O ell / ell^T ell <= N. Since rho(O)>N only means the TOP
eigenvector exceeds N; ell may still give Rayleigh <= N. (SM) directly gives Gamma<=N^2 by Cauchy-Schwarz, so if
(SM) survives two-lane it is the correct minimal target (weaker than rho(O)<=N, no SBC needed).
EXACT per graph: Gamma vs N^2 ; (SM) sum T^2 vs N*Gamma ; Cycle-SM max_f (O ell)_f/(N ell_f) ; rho(O) float;
SBC rho(O)+m vs N+N^2/25 ; m=|M|."""
from fractions import Fraction as F
import numpy as np
from _satzmu_conn import struct_for_side
from _h import Bconn
from _verify_two_lane import build_two_lane

def analyze(L):
    n,E,side,bad=build_two_lane(L)
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N=n
    if not Bconn(n,adj,side): print("L=%d not Bconn"%L); return
    st=struct_for_side(n,adj,side)
    if st is None: print("L=%d struct None"%L); return
    M,ell,T,mu,cyc=st
    m=len(M)
    # exact p_f, O
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    O=[[F(0)]*m for _ in range(m)]
    for i,f in enumerate(M):
        for j,g in enumerate(M):
            O[i][j]=sum(pf[f].get(v,F(0))*pf[g].get(v,F(0)) for v in pf[f])
    Gamma=sum(T)                      # = sum ell^2
    sumT2=sum(t*t for t in T)         # = ell^T O ell
    NG=F(N)*Gamma
    lvec=[F(ell[f]) for f in M]
    # Cycle-SM max ratio (O ell)_f/(N ell_f)
    csm=F(-1)
    for i in range(m):
        Oli=sum(O[i][j]*lvec[j] for j in range(m))
        r=Oli/(F(N)*lvec[i])
        if r>csm: csm=r
    Of=np.array([[float(x) for x in r] for r in O]); rho=max(abs(np.linalg.eigvals(Of)))
    sbc_lhs=rho+m; sbc_rhs=N+N*N/25.0
    print("L=%2d N=%2d m=%d Gamma=%d N^2=%d  Gamma<=N^2:%s"%(L,N,m,Gamma,N*N,Gamma<=N*N))
    print("    (SM) sumT^2=%s  N*Gamma=%s  sumT^2<=N*Gamma : %s  (ratio=%s)"%(
        str(sumT2),str(NG),"HOLDS" if sumT2<=NG else "*** FAILS ***",str(float(sumT2/NG))[:7]))
    print("    Cycle-SM max_f (O ell)_f/(N ell_f) = %s = %s  (<=1 => rho(O)<=N) : %s"%(
        str(csm),str(float(csm))[:7],"HOLDS" if csm<=1 else "FAILS (rho(O)>N)"))
    print("    rho(O)=%.4f  N=%d  rho(O)<=N:%s   SBC rho+m=%.3f <= N+N^2/25=%.3f : %s"%(
        rho,N,"yes" if rho<=N else "NO",sbc_lhs,sbc_rhs,"HOLDS" if sbc_lhs<=sbc_rhs else "FAILS"))

if __name__=="__main__":
    for L in (8,12,16,20):
        analyze(L)
