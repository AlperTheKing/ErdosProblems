"""F(o)=N^2 r_o + sum_f a_f H_f,  H_f = sum_{q in Q} p_f(q) psi_q, psi_q=N r_q + (K_QQ r_Q)_q.
a_f=p_f(o). Need sum_f a_f H_f >= N^2(T_o-N) = N^2 * (-r_o).
Key: maybe H_f >= ell_f * N * something? Examine H_f / a_f and per-f.
Also examine psi_q: is psi_q >= 0? sign? And does sum_f a_f H_f relate to T_o cleanly.
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
        psi={q:N*r[q]+W[q] for q in Q}
        print("=== %s N=%d ===" % (g6,n))
        print("   psi_q (q in Q): %s" % {q:round(float(psi[q]),2) for q in Q})
        print("   r_q   (q in Q): %s" % {q:round(float(r[q]),2) for q in Q})
        for o in O:
            af=[P[fi].get(o,F(0)) for fi in range(len(M))]
            Hf=[sum(P[fi].get(q,F(0))*psi[q] for q in Q) for fi in range(len(M))]
            need=N*N*(T[o]-N)
            got=sum(af[fi]*Hf[fi] for fi in range(len(M)))
            print("  o=%d: need sum a_f H_f >= %.2f, got %.2f" % (o,float(need),float(got)))
            print("     H_f=%s a_f=%s  H_f/(N*ell_f)=%s" % ([round(float(x),2) for x in Hf],[round(float(x),2) for x in af],[round(float(Hf[fi]/(N*ell[M[fi]])),3) for fi in range(len(M))]))
