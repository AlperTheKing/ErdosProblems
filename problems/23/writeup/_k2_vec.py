"""Vector form. For fixed overloaded o, u_q=K[o,q] (q in Q), u>=0.
F(o)=N^2 r[o] + N <u,r_Q> + <u, K_QQ r_Q>,  r_Q>=0, r[o]=N-T[o]<0.
Quantities:
  U = sum_q u_q = sum_{q in Q} K[o,q] = T[o]-sum_{o'} K[o,o'] = T[o]-(diag+otherO)
  Koo = K[o,o] = sum_f a_f^2
  T[o] = sum_q K[o,q] over ALL q incl O = U + sum_{o' in O} K[o,o'].
Test candidate clean bounds. Also dump K_QQ row sums (should be <=T[q]<=N).
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
        print("=== %s N=%d O=%s ===" % (g6,n,O))
        for o in O:
            u={q:K[o][q] for q in Q}
            U=sum(u.values())
            t0=N*N*r[o]; t1=N*sum(u[q]*r[q] for q in Q)
            W={q:sum(K[q][qp]*r[qp] for qp in Q) for q in Q}
            t2=sum(u[q]*W[q] for q in Q)
            # K_QQ rowsums:
            kqqrs={q:sum(K[q][qp] for qp in Q) for q in Q}
            # <u,r_Q>, and bound: u_q<=K[o,o]? no. max u_q:
            print("  o=%d T[o]=%.3f r[o]=%.3f U=sum_Q u=%.3f  Koo=%.3f" % (o,float(T[o]),float(r[o]),float(U),float(K[o][o])))
            print("     t0=%.2f t1=%.2f t2=%.2f F=%.3f" % (float(t0),float(t1),float(t2),float(t0+t1+t2)))
            # average r weighted by u: <u,r>/U
            print("     <u,r>/U=%.3f  max_q r[q](Q)=%.3f  W range=[%.3f,%.3f]" % (float(sum(u[q]*r[q] for q in Q)/U), float(max(r[q] for q in Q)), float(min(W.values())), float(max(W.values()))))
