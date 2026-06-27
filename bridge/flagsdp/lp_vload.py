#!/usr/bin/env python3
"""GPT's section-9 diagnostic: solve the FRACTIONAL vertex-load LP  tau* = min_x max_v T_x(v)  exactly
(LP over fractional shortest-geodesic routings), compare to K=N+(N^2-Gamma). Expect tau*=N at tight (C5[q]),
tau*<K sub-tight. Also report the dual potential phi* (the geodesic-potential certificate) + saturated set.
This tests the Geodesic-Potential Inequality / vertex-load theorem fractionally."""
import sys, numpy as np
from scipy.optimize import linprog
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def solve(name,N,adj,side,G,M):
    # variables: x_{e,P} for each bad edge e and shortest geodesic P, plus tau (last var)
    paths=[]; pe=[]   # paths[k]=vertex list; pe[k]=bad-edge index
    he=[]; edge_paths=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v)
        h=len(geos[0]); he.append(h)
        idxs=[]
        for P in geos:
            idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    nvar=len(paths)+1; tau=len(paths)
    # objective: minimize tau
    c=np.zeros(nvar); c[tau]=1.0
    # equality: for each bad edge, sum_P x=1
    Aeq=np.zeros((len(M),nvar)); beq=np.ones(len(M))
    for ei,idxs in enumerate(edge_paths):
        for k in idxs: Aeq[ei,k]=1.0
    # inequality: for each vertex v, sum_{k: v in paths[k]} he[pe[k]] x_k - tau <= 0
    Aub=np.zeros((N,nvar)); bub=np.zeros(N)
    for k,P in enumerate(paths):
        w=he[pe[k]]
        for v in P: Aub[v,k]+=w
    for v in range(N): Aub[v,tau]=-1.0
    res=linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=[(0,None)]*len(paths)+[(0,None)], method="highs")
    K=N+(N*N-G)
    tau_star=res.fun
    # dual potential phi = -marginals of the vertex (Aub) constraints (linprog 'highs' ineqlin.marginals)
    phi=None
    try:
        phi=-res.ineqlin.marginals  # >=0 for <= constraints at optimum
    except Exception: pass
    Tv=Aub[:, :len(paths)].dot(res.x[:len(paths)])
    sat=[v for v in range(N) if abs(Tv[v]-tau_star)<1e-7]
    print(f"\n=== {name}: N={N} beta={len(M)} Gamma={G} deficit={N*N-G} | K=N+(N^2-Gamma)={K} ===")
    print(f"    fractional tau* = {tau_star:.6f}  <= K={K}? {tau_star<=K+1e-6}  | tight expectation tau*==N={N}? {abs(tau_star-N)<1e-6}")
    if phi is not None:
        unif = (phi.max()-phi.min())<1e-6 if phi.size else False
        print(f"    dual potential phi*: uniform? {unif}  (min={phi.min():.4f} max={phi.max():.4f}); #saturated vertices |Z|={len(sat)}/{N}")

if __name__=="__main__":
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
    def decode_g6(s):
        data=[ord(c)-63 for c in s]; n=data[0]; bits=[]
        for d in data[1:]:
            for k in range(5,-1,-1): bits.append((d>>k)&1)
        adj=[set() for _ in range(n)]; idx=0
        for j in range(1,n):
            for i in range(j):
                if idx<len(bits) and bits[idx]: adj[i].add(j); adj[j].add(i)
                idx+=1
        return n,adj
    for q in (2,3,4):
        n,adj,side,G,M=C5q(q); solve(f"C5[{q}]",n,adj,side,G,M)
    n,adj=decode_g6("G?`F`w"); res,mc=gamma_min_cut(n,[set(a) for a in adj],edges_of([set(a) for a in adj]))
    side,G,M=res; solve("n8 band-max",n,[set(a) for a in adj],side,G,M)
    print("\nDONE")
