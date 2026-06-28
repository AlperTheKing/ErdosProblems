"""At the Mycielskian N=23 (where between-only fails by 2.22), examine WHY the within-layer variance
is needed. Test the within-layer ANTI-CORRELATION: in each layer I_i(f), is the betweenness weight p_f(v)
small where the load T(v) is large? (so that the p_f-weighted load is below the layer-max).
Compute for the worst (bottom-eigvector) direction x: per-layer, the covariance between p_f and x^2.
Also: confirm whether the bottom eigenvector x of N*I-K concentrates on overloaded vertices and how the
within-layer variance pays for it."""
from fractions import Fraction as F
from _layermax_stress import maxcut_local, myciel
from _myc_spec import buildK_fixedcut
from collections import deque
import numpy as np

def layers_for(P,M,ell,adj,side,fi):
    f=M[fi]; a,b=f
    d={a:0}; q=deque([a])
    while q:
        u=q.popleft()
        for w in adj[u]:
            if side[u]!=side[w] and w not in d: d[w]=d[u]+1; q.append(w)
    pf=P[fi]; L=ell[f]
    layers={}
    for v in pf: layers.setdefault(d[v],[]).append(v)
    return [layers.get(i,[]) for i in range(L)], pf, L

if __name__=="__main__":
    C5=(5,[(0,1),(1,2),(2,3),(3,4),(4,0)])
    g=myciel(*C5); g=myciel(*g); nn,E=g
    adj=[set() for _ in range(nn)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    side,c=maxcut_local(nn,adj,restarts=200,seed=22)
    K,T,S,P,M,ell,n,side=buildK_fixedcut(nn,E,side)
    N=n
    Kf=np.array([[float(x) for x in row] for row in K])
    A=N*np.eye(n)-Kf
    w,V=np.linalg.eigh(A)
    x=V[:,0]
    print('N=%d bottom eig=%.4f'%(n,w[0]))
    Tf=[float(t) for t in T]
    over=[v for v in range(n) if Tf[v]>N+1e-9]
    print('overloaded:',[(v,round(Tf[v],2)) for v in over])
    print('bottom eigvec on overloaded:',[(v,round(x[v],3)) for v in over])
    print('|x| max on overloaded?', max(abs(x[v]) for v in over), 'vs overall max', max(abs(x)))
    # For each bad edge, layer count and how many layers have >1 vertex (within-layer freedom)
    multi_layers=0; total_layers=0
    for fi in range(len(M)):
        layers,pf,L=layers_for(P,M,ell,adj,side,fi)
        for lyr in layers:
            total_layers+=1
            if len(lyr)>1: multi_layers+=1
    print('layers with >1 vertex (within-layer var possible): %d / %d'%(multi_layers,total_layers))
    # within-layer variance contribution to B0 at x
    B0x = sum(Kf[v][ww]*(x[v]-x[ww])**2 for v in range(n) for ww in range(v+1,n))
    rhs = sum((Tf[v]-N)*x[v]**2 for v in range(n))
    print('x^T B0 x = %.4f, RHS sum(T-N)x^2 = %.4f, slack=%.4f'%(B0x,rhs,B0x-rhs))
    # decompose B0x into within and between
    within_tot=0.0; between_tot=0.0
    for fi in range(len(M)):
        layers,pf,L=layers_for(P,M,ell,adj,side,fi)
        m=[sum(float(pf[v])*x[v] for v in lyr) for lyr in layers]
        q=[sum(float(pf[v])*x[v]**2 for v in lyr) for lyr in layers]
        within_tot+=L*sum(q[i]-m[i]**2 for i in range(L))
        mbar=sum(m)/L
        between_tot+=L*sum((m[i]-mbar)**2 for i in range(L))
    print('within-layer total=%.4f  between-layer total=%.4f  (sum=%.4f should=B0x)'%(within_tot,between_tot,within_tot+between_tot))
    print('RHS needs %.4f; between alone gives %.4f (deficit %.4f covered by within %.4f)'%(rhs,between_tot,rhs-between_tot,within_tot))
