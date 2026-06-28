"""On the N=23 Mycielskian: compute K, N*I-K spectrum exactly-ish, and the structure.
Use a fixed reasonable max cut (the standard bipartite-ish 2-coloring won't work; Mycielskian
is not bipartite). Use local-search cut. Goal: understand what model operator is tight here
(smallest eigenvalue of N*I-K, the near-null vector)."""
from fractions import Fraction as F
from _layermax_stress import maxcut_local, myciel
from _h import geos, bdist_restr, Bconn
import numpy as np

def buildK_fixedcut(n,E,side):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    if not Bconn(n,adj,side): return None
    M=[(min(u,v),max(u,v)) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M: return None
    ell={}; P=[]
    for f in M:
        a,b=f
        d=bdist_restr(adj,side,a,b)
        if d<0: return None
        ell[f]=d+1
        Ps=geos(adj,side,a,b); nf=len(Ps)
        if nf==0: return None
        cnt={}
        for p in Ps:
            for v in p: cnt[v]=cnt.get(v,0)+1
        P.append({v:F(cnt[v],nf) for v in cnt})
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
    return K,T,S,P,M,ell,n,side

if __name__=="__main__":
    C5=(5,[(0,1),(1,2),(2,3),(3,4),(4,0)])
    g=C5
    for depth in [1,2]:
        g=myciel(*g)
    nn,E=g  # N=23
    adj=[set() for _ in range(nn)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    side,c=maxcut_local(nn,adj,restarts=200,seed=7)
    r=buildK_fixedcut(nn,E,side)
    if r is None:
        print('cut invalid'); exit()
    K,T,S,P,M,ell,n,side=r
    Kf=np.array([[float(x) for x in row] for row in K])
    N=n
    A=N*np.eye(n)-Kf
    w,V=np.linalg.eigh(A)
    print('N=%d, #bad=%d, ells=%s'%(n,len(M),sorted(set(ell.values()))))
    print('rho(K)=%.4f  (N=%d)'%(max(np.linalg.eigvalsh(Kf)),N))
    print('smallest eigs of N*I-K:',[round(x,4) for x in sorted(w)[:5]])
    print('T range: min=%s max=%s  #overloaded(T>N)=%d'%(str(min(T)),str(max(T)),sum(1 for t in T if t>N)))
    # near-null vector of A
    v0=V[:,0]
    order=np.argsort(-np.abs(v0))
    print('near-null vec biggest comps (vertex:val, T(vertex)):')
    for idx in order[:8]:
        print('   v=%d val=%.3f T=%s'%(idx,v0[idx],str(T[idx])))
