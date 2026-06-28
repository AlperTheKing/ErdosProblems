"""Exploration (floats OK -- NOT a closure gate): toward proving SPEC rho(K)<=N via a model operator.
K[v,w]=sum_f p_f(v)p_f(w), rows sum to T[v]; want rho(K)<=N. Two concrete model ideas tested on the
extremal (C5[t], T==N), the N=22 sandwich-killer, and the NEW hard case Myc(Grotzsch) N=23:
  (M1) Laplacian remainder: is N*I - K - c*L_B PSD for some c>=0?  (L_B = B-graph Laplacian)
  (M2) Diagonal-load model: compare K to D^{1/2} R D^{1/2} where D=diag(T), R the 'normalized overlap'.
Report lambda_max(K), lambda_max of N*I-K (>=0 iff SPEC), and best Laplacian remainder min-eig over a c-grid."""
import numpy as np
from _h import dec, loads
from _schur_spec import pf_exact

def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

def buildK(info):
    P,M,ell,n=pf_exact(info); N=n
    K=np.zeros((n,n))
    for d in P:
        v=np.zeros(n)
        for vv,pp in d.items(): v[vv]=float(pp)
        K+=np.outer(v,v)
    T=K.sum(1)
    return K,T,N,n,info

def LB(info,n):
    # B-graph (max-cut edges) Laplacian
    B=info['Bset']; A=np.zeros((n,n))
    for a,b in B: A[a,b]=1; A[b,a]=1
    return np.diag(A.sum(1))-A

def probe(name,info):
    K,T,N,n,_=buildK(info)
    A=N*np.eye(n)-K
    ev=np.linalg.eigvalsh(K); evA=np.linalg.eigvalsh(A)
    L=LB(info,n)
    best=None;bestc=None
    for c in np.linspace(0,2,41):
        m=np.linalg.eigvalsh(A-c*L).min()
        if best is None or m>best: best=m;bestc=c
    # also try ADDING a multiple of L (since A rows can be negative on O, +cL may help)
    bestp=None;bestpc=None
    for c in np.linspace(0,2,41):
        m=np.linalg.eigvalsh(A+c*L).min()
        if bestp is None or m>bestp: bestp=m;bestpc=c
    print(f"{name}: n={n} maxT={T.max():.3f} (overload={ (T>N).sum() }) lam_max(K)={ev[-1]:.4f} (<=N={N}? {ev[-1]<=N+1e-9}) min-eig(N*I-K)={evA[0]:+.4f}")
    print(f"   A-c*L_B: best min-eig {best:+.4f} @c={bestc:.2f} | A+c*L_B: best {bestp:+.4f} @c={bestpc:.2f}")

if __name__=="__main__":
    # extremal C5[t]
    g6ext="J?AEB?oE?W?"   # T-const extremal at N=11 per memory
    n,E=dec(g6ext); probe("C5-extremal "+g6ext, loads(n,E))
    for g6 in ["G?bF`w","I?BD@g]Qo","I?ABCc]}?","J??CE?{{?]?"]:
        n,E=dec(g6); probe(g6, loads(n,E))
    # N=22 sandwich killer blow-up and N=23 Mycielski
    from _superphi import blow
    nn,EE=blow("J???E?pNu\\?",2); probe("J???E?pNu?[2] N=22", loads(nn,EE))
    C5n=5; C5E=[(i,(i+1)%5) for i in range(5)]
    n1,E1=mycielski(C5n,C5E); n2,E2=mycielski(n1,E1)
    probe("Myc(Grotzsch) N=23", loads(n2,E2))
