"""Try to express F(o) (the N^2-scaled k2 LHS) as a NONNEG combination of manifestly-nonneg
generators, with the SAME structural coefficients across all instances. We don't fit per-instance;
instead we look for a structural identity:  F(o) = sum (nonneg generator) that holds as a polynomial.

Strategy: F(o) = N^2 r_o + N L1 + L2.  N^2 r_o = N^2(N - T_o) = N^2 N - N^2 sum_f ell_f a_f.
Use S(o)=sum_f a_f <= N, i.e. (N - S(o)) >= 0.
Identity attempt:
  N^2 r_o = N^2(N - T_o).
  Write N^2(N-T_o) = N^2(N - S(o)) - N^2(T_o - S(o)) = N^2(N-S(o)) - N^2 sum_f (ell_f-1) a_f.
  First piece N^2(N-S(o)) >= 0 (good). Second piece = -N^2 sum_f (ell_f-1) a_f (bad, negative).
So  F(o) = [N^2(N-S(o))]  - N^2 sum_f (ell_f-1) a_f  + N L1 + L2.
Need: N L1 + L2 >= N^2 sum_f (ell_f-1) a_f.  (dropping the manifestly>=0 piece N^2(N-S(o)))
=> SUFFICIENT: N L1 + L2 >= N^2 sum_f (ell_f-1) a_f.    [call this (SUF1)]
Check (SUF1) and per-edge version  N R_f + (L2 contribution)/a_f >= N^2 (ell_f-1).
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
    O=[v for v in range(n) if T[v]>N]
    Q=[v for v in range(n) if T[v]<=N]
    return P,M,ell,K,T,O,Q,N,n

def check_suf1(Nmax,Nmin=5,stride=1):
    worst=None; fails=0; ntot=0
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            P,M,ell,K,T,O,Q,N,n=build(info)
            if not O: continue
            r=[F(N)-T[v] for v in range(n)]
            W={q:sum(K[q][qp]*r[qp] for qp in Q) for q in Q}
            for o in O:
                af=[P[fi].get(o,F(0)) for fi in range(len(M))]
                L1=sum(af[fi]*sum(P[fi].get(q,F(0))*r[q] for q in Q) for fi in range(len(M)))
                L2=sum(af[fi]*sum(P[fi].get(q,F(0))*W[q] for q in Q) for fi in range(len(M)))
                lhs=N*L1+L2
                rhs=N*N*sum((ell[M[fi]]-1)*af[fi] for fi in range(len(M)))
                ntot+=1
                marg=lhs-rhs
                if marg<0: fails+=1
                if worst is None or marg<worst[0]: worst=(marg,g6,n,o)
    print("(SUF1) N L1+L2 >= N^2 sum_f (ell_f-1)a_f : tested %d, fails=%d, worst margin=%.4f @%s" % (ntot,fails,float(worst[0]),worst[1:]))

if __name__=="__main__":
    check_suf1(9,5,1)
