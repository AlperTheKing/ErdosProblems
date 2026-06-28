"""Explore model operators Mod with rho(Mod)=N dominating K=sum_f p_f p_f^T (K <= Mod as PSD).
Candidates:
  (a) diag(T) (since K1=T; but diag(T) >= K iff K weakly diag dominant -- false generally)
  (b) N*I (the target: N*I-K>=0 is exactly SPEC)
  (c) odd-cycle circulant model.
We compute eig(K) and structural quantities to find the right Mod."""
from fractions import Fraction as F
from _h import dec, loads, blow
from _schur_spec import pf_exact
import numpy as np

def buildKTS(info):
    P,M,ell,n=pf_exact(info)
    K=[[F(0)]*n for _ in range(n)]
    for d in P:
        items=list(d.items())
        for a in range(len(items)):
            va,pa=items[a]
            for b in range(len(items)):
                vb,pb=items[b]
                K[va][vb]+=pa*pb
    T=[sum(ell[M[fi]]*P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    S=[sum(P[fi].get(v,F(0)) for fi in range(len(M))) for v in range(n)]
    return K,T,S,P,M,ell,n

def myciel(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    NN=2*n+1; EE=list(E)
    for i in range(n):
        for j in adj[i]:
            if j>i: EE.append((i, n+j)); EE.append((j, n+i))
    for i in range(n): EE.append((n+i, 2*n))
    EE=list(set((min(a,b),max(a,b)) for a,b in EE))
    return NN,EE

if __name__=="__main__":
    # On C5[t] extremal: check eig(K), Perron vector (should be const), and gap
    for t in [1,2,3,4]:
        nn,EE=blow(t); info=loads(nn,EE)
        K,T,S,P,M,ell,n=buildKTS(info)
        Kf=np.array([[float(x) for x in row] for row in K])
        w,V=np.linalg.eigh(Kf)
        idx=np.argsort(w)[::-1]
        print('C5[%d] N=%2d: eig(K) top5=%s'%(t,n,[round(w[i],3) for i in idx[:5]]))
        # Perron vector
        pv=V[:,idx[0]]
        print('         Perron vec (should be const): min/max=%.4f/%.4f'%(pv.min()/pv.max() if pv.max()!=0 else 0,1))
        print('         T values:',sorted(set(round(float(x),3) for x in T)))
