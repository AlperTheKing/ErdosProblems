"""Test candidate manifestly-nonneg lower bounds for F(o) = N^2*(k2 LHS) for overloaded o.
F(o) = N^2 r[o] + N sum_f a_f R_f + sum_{f,g} a_f O^Q_{fg} R_g
where a_f=p_f(o), R_f=sum_{q in Q} p_f(q) r[q] >=0 (r>=0 on Q, p_f>=0),
O^Q_{fg}=sum_{q in Q} p_f(q) p_g(q) >=0.

Candidate A (drop cross terms, keep diagonal of O^Q):
  F(o) >= N^2 r[o] + N sum_f a_f R_f + sum_f a_f O^Q_{ff} R_f   [drops f!=g cross >=0 terms? NO they're >=0 so dropping LOWERS]
Actually all terms in t2 are >=0, and all R_f>=0, so t1,t2 >=0. Only t0<0.
So we need: N sum_f a_f R_f + (t2>=0) >= -N^2 r[o] = N^2 (T[o]-N).

Try the pure t0+t1 bound (k=1): does N sum_f a_f R_f >= N^2(T[o]-N)?  i.e. sum_f a_f R_f >= N(T[o]-N).
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

def analyze(g6,info):
    P,M,ell,K,T,O,Q,N,n=build(info)
    r=[F(N)-T[v] for v in range(n)]
    Qs=set(Q)
    res=[]
    for o in O:
        af=[P[fi].get(o,F(0)) for fi in range(len(M))]
        Rf=[sum(P[fi].get(q,F(0))*r[q] for q in Q) for fi in range(len(M))]
        To=T[o]
        # k=1 quantity: sum_f a_f R_f  vs  N*(To-N)
        lhs1=sum(af[fi]*Rf[fi] for fi in range(len(M)))
        rhs1=N*(To-N)
        res.append((o,float(To),float(lhs1),float(rhs1),float(lhs1-rhs1)))
    return res

if __name__=="__main__":
    print("k=1 test: is sum_f a_f R_f >= N*(T[o]-N)?  margin = lhs1-rhs1")
    for g6 in GRAPHS:
        n,E=dec(g6); info=loads(n,E)
        for (o,To,l1,r1,m) in analyze(g6,info):
            print("  %s o=%d T=%.3f  lhs1=%.3f rhs1=%.3f margin=%.3f %s" % (g6,o,To,l1,r1,m,"NEG!" if m<0 else ""))
