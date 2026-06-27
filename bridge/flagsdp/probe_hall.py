"""
Probe the EXACT fractional feasibility (GPI dual) optimal phi structure.
Feasibility of vertex-load LP (K = N + N^2 - Gamma) <=> for ALL phi>=0:
    sum_e h_e * m_phi(e)  <=  K * sum_v phi_v,   m_phi(e)=min_P sum_{v in P} phi(v).
0/1 case (phi=1_S): sum_e h_e min_P |P cap S| <= K|S|.
Q: is the worst phi ever strictly fractional (0/1 insufficient)? Solve dual LP, inspect phi.
"""
import numpy as np
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of

def build(N,adj,side,G,M):
    paths=[]; pe=[]; he=[]; edge_paths=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v); h=len(geos[0]); he.append(h)
        idxs=[]
        for P in geos: idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    K=N+(N*N-G)
    return paths,pe,he,edge_paths,K

def dual_phi(name,N,adj,side,G,M):
    paths,pe,he,edge_paths,K=build(N,adj,side,G,M)
    beta=len(M); nv=N+beta
    c=np.zeros(nv)
    for ei in range(beta): c[N+ei]=-he[ei]
    rows=[]; rhs=[]
    for k,P in enumerate(paths):
        r=np.zeros(nv); ei=pe[k]; r[N+ei]=1.0
        for v in P: r[v]-=1.0
        rows.append(r); rhs.append(0.0)
    Aub=np.array(rows); bub=np.array(rhs)
    Aeq=np.zeros((1,nv)); Aeq[0,:N]=1.0; beq=[1.0]
    bounds=[(0,None)]*N+[(None,None)]*beta
    res=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    phi=res.x[:N]; val=-res.fun; ratio=val/K
    is2 = (phi.max()>1e-9) and all(abs(p)<1e-7 or abs(p-phi.max())<1e-7 for p in phi)
    supp=int((phi>1e-7).sum())
    vals=sorted(set(round(p,4) for p in phi))
    print(f"{name}: N={N} G={G} K={K} | val={val:.6f} ratio={ratio:.6f} (<=1?{ratio<=1+1e-7}) two-valued?{is2} supp={supp}/{N} vals={vals[:8]}")
    return ratio

def C5q(q):
    n=5*q; vid=lambda i,j:i*q+j; side=[0]*n; adj=[set() for _ in range(n)]
    for i in range(5):
        for j in range(q): side[vid(i,j)]=(0 if i in (0,2,4) else 1)
    for i in range(5):
        for a in range(q):
            for b in range(q):
                u=vid(i,a); v=vid((i+1)%5,b); adj[u].add(v); adj[v].add(u)
    M=[(vid(4,a),vid(0,b)) for a in range(q) for b in range(q)]; G=25*len(M)
    return n,adj,side,G,M

if __name__=="__main__":
    for q in (2,3,4):
        n,adj,side,G,M=C5q(q); dual_phi(f"C5[{q}]",n,adj,side,G,M)
