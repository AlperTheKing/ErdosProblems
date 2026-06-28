"""Full term balance of F(o) under the split:
F(o) = A - B + N L1 + L2,  A=N^2(N-S(o))>=0, B=N^2 sum_f(ell_f-1)a_f >=0.
Print A,B,N*L1,L2 magnitudes to see the true balance.
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

GRAPHS=["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]
if __name__=="__main__":
    for g6 in GRAPHS:
        n,E=dec(g6); info=loads(n,E); P,M,ell,K,T,O,Q,N,n=build(info)
        r=[F(N)-T[v] for v in range(n)]
        W={q:sum(K[q][qp]*r[qp] for qp in Q) for q in Q}
        print("=== %s N=%d ===" % (g6,n))
        for o in O:
            af=[P[fi].get(o,F(0)) for fi in range(len(M))]
            So=sum(af)
            L1=sum(af[fi]*sum(P[fi].get(q,F(0))*r[q] for q in Q) for fi in range(len(M)))
            L2=sum(af[fi]*sum(P[fi].get(q,F(0))*W[q] for q in Q) for fi in range(len(M)))
            A=N*N*(N-So); B=N*N*sum((ell[M[fi]]-1)*af[fi] for fi in range(len(M)))
            tot=A-B+N*L1+L2
            print("  o=%d: A=%.1f B=%.1f N*L1=%.1f L2=%.1f | tot=%.2f" % (o,float(A),float(B),float(N*L1),float(L2),float(tot)))
