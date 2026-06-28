"""Explore the (k2) inequality structure. For each overloaded o:
  N^2*(k2) = N^2*(N-T[o]) + N*sum_{q in Q} K[o,q] r[q] + sum_{q,q' in Q} K[o,q] K[q,q'] r[q']  >= 0
r[v]=N-T[v]. We want a manifestly nonneg rearrangement.
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

def k2val(K,T,O,Q,N,n,o):
    r=[F(N)-T[v] for v in range(n)]
    term0=N*N*r[o]
    term1=N*sum(K[o][q]*r[q] for q in Q)
    term2=sum(K[o][q]*K[q][qp]*r[qp] for q in Q for qp in Q)
    return term0+term1+term2, (term0,term1,term2)

if __name__=="__main__":
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?"]:
        n,E=dec(g6); info=loads(n,E); P,M,ell,K,T,O,Q,N,n=build(info)
        print(f"=== {g6} N={n} O={O} ===")
        for o in O:
            v,(t0,t1,t2)=k2val(K,T,O,Q,N,n,o)
            print(f"  o={o} T[o]={float(T[o]):.3f} k2*N^2={float(v):.4f} | t0={float(t0):.2f} t1={float(t1):.2f} t2={float(t2):.2f}")
