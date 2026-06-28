"""Reformulate (k2) in terms of p_f. For fixed overloaded o:
 a_f = p_f(o).  K[o,q]=sum_f a_f p_f(q).
 N^2 r[o] + N sum_q K[o,q] r[q] + sum_{q,q'} K[o,q] K[q,q'] r[q']
We want manifestly nonneg form. Note r[o]<0; r[q]>=0 on Q.
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
        ells=[ell[m] for m in M]
        print("=== %s N=%d O=%s ===" % (g6,n,O))
        Qs=set(Q)
        for o in O:
            af=[P[fi].get(o,F(0)) for fi in range(len(M))]
            So=sum(af); To=T[o]
            Rf=[sum(P[fi].get(q,F(0))*r[q] for q in Q) for fi in range(len(M))]
            t1=N*sum(af[fi]*Rf[fi] for fi in range(len(M)))
            t0=N*N*r[o]
            W=[sum(K[q][qp]*r[qp] for qp in Q) for q in range(n)]
            t2=sum(af[fi]*sum(P[fi].get(q,F(0))*W[q] for q in Q) for fi in range(len(M)))
            tot=t0+t1+t2
            print("  o=%d: S(o)=%.3f T(o)=%.3f r[o]=%.3f tot=%.3f" % (o,float(So),float(To),float(r[o]),float(tot)))
            print("     Rf=%s" % [round(float(x),3) for x in Rf])
            print("     af=%s  ellf=%s" % ([round(float(x),3) for x in af], ells))
