"""M-matrix criterion: A=NI-K is a symmetric Z-matrix (offdiag -K<=0).
A PSD  <=>  exists x>0 with Kx <= N x entrywise (A x >=0).  [Z-matrix => M-matrix iff such x exists]
SEARCH for a CONSTRUCTIBLE positive x with (Kx)_v <= N x_v for all v.
Candidates:
  x=1 (=> need T<=N, fails on O)
  x_v = something larger where load is high. Try x = T/N? x = 1 + c*(T-meanT)?
  x = Perron(K) (works iff SPEC, circular but check it's positive & gap)
Also: directly solve the LP 'find x>=eps, Kx<=Nx' via linprog and report if feasible + the x.
"""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _schur_spec import pf_exact

def build(info):
    P,M,ell,n=pf_exact(info); N=n
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        it=list(d.items())
        for a in range(len(it)):
            va,pa=it[a]
            for b in range(len(it)):
                vb,pb=it[b]; K[va][vb]+=pa*pb
    T=[sum(K[v][w] for w in range(n)) for v in range(n)]
    return P,M,ell,K,T,N,n

GRAPHS=["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]

def feasible_x(K,N,n):
    """LP: find x with x>=1, Kx<=Nx, minimize sum x. Use scipy."""
    import numpy as np
    from scipy.optimize import linprog
    Kf=np.array([[float(K[i][j]) for j in range(n)] for i in range(n)])
    # constraints: (K - N I) x <= 0  ; x>=1
    A_ub=Kf-N*np.eye(n)
    b_ub=np.zeros(n)
    bounds=[(1,None)]*n
    res=linprog(c=np.ones(n),A_ub=A_ub,b_ub=b_ub,bounds=bounds,method='highs')
    return res

if __name__=="__main__":
    for g6 in GRAPHS:
        n,E=dec(g6); info=loads(n,E); P,M,ell,K,T,N,n=build(info)
        res=feasible_x(K,N,n)
        print("=== %s N=%d ===" % (g6,n))
        if res.success:
            x=res.x
            print("  feasible x found (min sum). x=%s" % [round(v,3) for v in x])
            # verify Kx<=Nx
            import numpy as np
            Kf=np.array([[float(K[i][j]) for j in range(n)] for i in range(n)])
            slack=N*x-Kf@x
            print("  min slack (Nx-Kx)=%.4f (>=0 ok)  x range=[%.3f,%.3f]" % (slack.min(),x.min(),x.max()))
            # correlate x with T
            print("  T=%s" % [round(float(t),2) for t in T])
        else:
            print("  INFEASIBLE: %s" % res.message)
