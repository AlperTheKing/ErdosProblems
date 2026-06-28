"""Build the BETWEEN matrix M_btw (x^T M_btw x = sum_f BETWEEN_f(x)) and test whether
M_btw >= diag(T-N) (i.e. N*I - diag(T) + M_btw >= 0). If TRUE universally it gives a cleaner
sufficient condition than full B0, dropping within-layer variance. STRESS on Mycielskians (N=23,47).
BETWEEN_f = ell * m^T (I - J/ell) m, m_i = sum_{v in I_i} p_f(v) x_v = (col vector c_{f,i})^T x.
So BETWEEN_f = sum_i ell*(c_{f,i} c_{f,i}^T) - (1/ell)*ell*(sum_i c_{f,i})(sum_i c_{f,i})^T
            = ell*sum_i c_{f,i}c_{f,i}^T - p_f p_f^T   (since sum_i c_{f,i} = p_f).
=> M_btw = sum_f [ ell(f) sum_i c_{f,i} c_{f,i}^T  - p_f p_f^T ] = D_layer - K,
where D_layer = sum_f ell(f) sum_i c_{f,i} c_{f,i}^T.  And note c_{f,i} c_{f,i}^T is supported on layer i x layer i.
So WITHIN was the difference diag(T)-D_layer? check: B0=diag(T)-K. M_btw=D_layer-K. So WITHIN-matrix = diag(T)-D_layer.
Thus 'BETWEEN-only suffices' <=> M_btw=D_layer-K >= diag(T-N) <=> N*I - K >= diag(T)-D_layer = (within-layer Gram).
Equivalently N*I - D_layer + (N*I-... ) -- just test eig of (M_btw - diag(T-N)) = N*I - K - (diag(T)-D_layer)
  = N*I - D_layer  ... wait: M_btw-diag(T-N) = (D_layer-K) - diag(T)+N I = N I - K - (diag(T)-D_layer).
Let me just build D_layer and M_btw directly and report lambda_min(M_btw - diag(T-N))."""
from fractions import Fraction as F
from _h import dec, loads, blow
from _schur_spec import pf_exact
from _layermax_stress import maxcut_local, myciel
from _myc_spec import buildK_fixedcut
from collections import deque
import numpy as np

def build_matrices(P,M,ell,n,adj,side):
    # layer vectors c_{f,i}: dict v->p_f(v) for v in layer i
    K=np.zeros((n,n)); Dlayer=np.zeros((n,n)); T=np.zeros(n)
    for fi,f in enumerate(M):
        a,b=f
        d={a:0}; q=deque([a])
        while q:
            u=q.popleft()
            for w in adj[u]:
                if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
        pf=P[fi]; L=ell[f]
        layers={}
        for v in pf: layers.setdefault(d[v],[]).append(v)
        # p_f as vector
        pvec=np.zeros(n)
        for v in pf: pvec[v]=float(pf[v])
        K+=np.outer(pvec,pvec)
        for v in pf: T[v]+=L*float(pf[v])
        for i in range(L):
            c=np.zeros(n)
            for v in layers.get(i,[]): c[v]=float(pf[v])
            Dlayer+=L*np.outer(c,c)
    return K,Dlayer,T

def report(P,M,ell,n,adj,side,label):
    K,Dlayer,T=build_matrices(P,M,ell,n,adj,side)
    N=n
    Mbtw=Dlayer-K
    A_full = N*np.eye(n)-K
    A_btw  = Mbtw - np.diag(T-N)   # = N*I - K - (diag(T)-Dlayer)
    lf=min(np.linalg.eigvalsh(A_full))
    lb=min(np.linalg.eigvalsh(A_btw))
    rho=max(np.linalg.eigvalsh(K))
    print('%-16s N=%d: rho(K)=%.4f  lam_min(N I-K)=%.4f  lam_min(BETWEEN-cert)=%.4f %s'%(
        label,n,rho,lf,lb,'(BETWEEN OK)' if lb>=-1e-9 else '(BETWEEN FAILS)'))
    return lb

if __name__=="__main__":
    # C5[t]
    for t in [2,3,4]:
        nn,EE=blow(t); info=loads(nn,EE)
        P,M,ell,n=pf_exact(info)
        report(P,M,ell,n,info['adj'],info['side'],'C5[%d]'%t)
    # Mycielskians
    C5=(5,[(0,1),(1,2),(2,3),(3,4),(4,0)])
    g=C5
    for depth in [1,2,3]:
        g=myciel(*g); nn,E=g
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        side,c=maxcut_local(nn,adj,restarts=150,seed=depth*11)
        r=buildK_fixedcut(nn,E,side)
        if r is None: print('Myc depth %d: cut invalid'%depth); continue
        K,T,S,P,M,ell,n,side=r
        report(P,M,ell,n,adj,side,'Myc(d=%d)N=%d'%(depth,n))
