"""Examine the layer structure at overloaded o, and the quadratic term's role.
For fixed o, edge f passes through o in layer i*(f). a_f=p_f(o).
Goal: understand the exact mechanism making k=2 work.

We compute, per overloaded o, a full breakdown and also test:
  the 'self-consistency' bound. Define for each f: c_f = sum_{q in Q} p_f(q) (Q-mass of f).
  Note sum_v p_f(v)=ell_f, so c_f = ell_f - a_f - (other-O-mass of f).
  R_f = sum_{q in Q} p_f(q) r[q] <= ? and >= ?
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
        Os=set(O); Qs=set(Q)
        print("=== %s N=%d O=%s ===" % (g6,n,O))
        # sum_v r[v]:
        print("   sum_v r = N^2-Gamma = %.3f (>=0 slack)" % float(sum(r)))
        for o in O:
            af=[P[fi].get(o,F(0)) for fi in range(len(M))]
            cf=[sum(P[fi].get(q,F(0)) for q in Q) for fi in range(len(M))]  # Q-mass
            Rf=[sum(P[fi].get(q,F(0))*r[q] for q in Q) for fi in range(len(M))]
            ratio=[float(Rf[fi]/cf[fi]) if cf[fi]>0 else None for fi in range(len(M))]
            # avg r over Q (uniform):
            sumrQ=sum(r[q] for q in Q); nQ=len(Q)
            print("  o=%d S(o)=%.3f T(o)=%.3f" % (o,float(sum(af)),float(T[o])))
            print("     af=%s" % [round(float(x),3) for x in af])
            print("     cf(Q-mass)=%s ellf=%s" % ([round(float(x),3) for x in cf],[ell[m] for m in M]))
            print("     Rf=%s  Rf/cf=%s  avg_r_Q=%.3f" % ([round(float(x),3) for x in Rf],[round(x,3) if x else x for x in ratio],float(sumrQ/nQ)))
