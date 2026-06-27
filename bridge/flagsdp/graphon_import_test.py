#!/usr/bin/env python3
"""GRAPHON-IMPORT angle for the GPI (Erdos #23 delta=0).

Two dual objects on a triangle-free max-cut graph G (vertex = graphon atom, weight 1/N):

  (A) Step-1 graphon NRS rigidity dual:  the cut-pressure kernel P_ij = Pr[i,j same side]
      over all max cuts.  alpha* = min_{ij in E} P_ij.  Edge slack S_ij = A_ij(P_ij - alpha*) >= 0.
      Weighted-regular slack:  rho_i = sum_{j~i} (1/N)(P_ij - alpha*) >= 0,  rho_avg = (1/N) sum rho_i.
      Identity  F = alpha* D + rho_avg  (F=2beta/N^2, D=2e/N^2).  rho_i=0 for all i  <=> C5-type.

  (B) GPI dual potential phi*(v): the optimal vertex toll from the fractional vertex-load LP
      tau* = min_x max_v T_x(v) (T_x(v)=sum_{e,P: v in P} h_e x_{e,P}, h_e=geodesic length).
      Claim under test (the IMPORT): phi*(v) ~ rho_i(v), both = vertex-load excess T(v)-N at tightness.

This script computes BOTH on the same graphs and reports whether they coincide (up to scale/affine).
If they match, the graphon F>=2/25 => C5-blowup rigidity would TRANSFER to the GPI.
HONEST: we expect a MISMATCH in general (different LP optima); the point is to locate exactly
where the correspondence breaks, which is the crux of this angle.
"""
import sys, numpy as np
from fractions import Fraction as Fr
from scipy.optimize import linprog
sys.path.insert(0,'.')
from mycielskian_check import edges_of, gamma_min_cut, all_shortest_geos

def maxcut_opt(n, edges):
    best=-1; opt=[]
    for m in range(1<<(n-1)):
        c=sum(1 for (u,v) in edges if ((m>>u)&1)!=((m>>v)&1))
        if c>best: best=c; opt=[m]
        elif c==best: opt.append(m)
    return best,opt

def pressure_dual(n, edges):
    """Return (rho_i list as Fractions, alpha*, F, D, rho_avg) over ALL max cuts."""
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    mc,opt=maxcut_opt(n,edges); beta=len(edges)-mc; K=len(opt); w=Fr(1,n)
    Pe={}
    for (u,v) in edges:
        same=sum(1 for m in opt if ((m>>u)&1)==((m>>v)&1))
        Pe[(u,v)]=Fr(same,K)
    alpha=min(Pe.values())
    rho=[Fr(0)]*n
    for (u,v) in edges:
        s=Pe[(u,v)]-alpha
        rho[u]+=w*s; rho[v]+=w*s
    rho_avg=sum(rho)*w
    F=Fr(2*beta,n*n); D=Fr(2*len(edges),n*n)
    return rho, alpha, F, D, rho_avg, beta

def gpi_dual(name,N,adj,side,G,M):
    """Solve fractional vertex-load LP; return tau*, phi*, T_x(v) and saturated set."""
    paths=[]; pe=[]; he=[]; edge_paths=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v)
        h=len(geos[0]); he.append(h); idxs=[]
        for P in geos:
            idxs.append(len(paths)); paths.append(P); pe.append(ei)
        edge_paths.append(idxs)
    nvar=len(paths)+1; tau=len(paths)
    c=np.zeros(nvar); c[tau]=1.0
    Aeq=np.zeros((len(M),nvar)); beq=np.ones(len(M))
    for ei,idxs in enumerate(edge_paths):
        for k in idxs: Aeq[ei,k]=1.0
    Aub=np.zeros((N,nvar)); bub=np.zeros(N)
    for k,P in enumerate(paths):
        wgt=he[pe[k]]
        for v in P: Aub[v,k]+=wgt
    for v in range(N): Aub[v,tau]=-1.0
    res=linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                bounds=[(0,None)]*len(paths)+[(0,None)], method="highs")
    phi=None
    try: phi=-res.ineqlin.marginals
    except Exception: pass
    Tv=Aub[:, :len(paths)].dot(res.x[:len(paths)])
    return res.fun, phi, Tv

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if a.std()<1e-12 or b.std()<1e-12: return float('nan')
    return float(np.corrcoef(a,b)[0,1])

def run(name,N,adj_sets,side,G,M):
    edges=edges_of(adj_sets)
    rho,alpha,F,D,rho_avg,beta=pressure_dual(N,edges)
    tau,phi,Tv=gpi_dual(name,N,adj_sets,side,G,M)
    rho_f=[float(r) for r in rho]
    K=N+(N*N-G)
    print(f"\n=== {name}: N={N} beta={beta} Gamma={G} | F={float(F):.5f} K={K} tau*={tau:.4f} ===")
    print(f"   rho_avg={float(rho_avg):.5f} (0=C5-type)  alpha*={float(alpha)}")
    # vertex-load excess from GPI side: T(v)-N
    excess=[t-N for t in Tv]
    print(f"   rho_i      = {[round(x,4) for x in rho_f]}")
    if phi is not None:
        print(f"   phi*_i     = {[round(x,4) for x in phi]}")
    print(f"   T(v)-N     = {[round(x,4) for x in excess]}")
    if phi is not None:
        print(f"   corr(rho,phi*) = {corr(rho_f,phi):.4f}   corr(rho,T-N) = {corr(rho_f,excess):.4f}   corr(phi*,T-N) = {corr(phi,excess):.4f}")

# builders
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

def from_edges(name,n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    res,mc=gamma_min_cut(n,adj,edges_of(adj))
    if res is None: print(f"{name}: no connected-B max cut"); return None
    side,G,M=res
    return (name,n,adj,side,G,M)

if __name__=="__main__":
    for q in (2,3,4):
        n,adj,side,G,M=C5q(q); run(f"C5[{q}]",n,adj,side,G,M)
    # band / non-extremal cases
    cases=[]
    cases.append(("C7",7,[(i,(i+1)%7) for i in range(7)]))
    cases.append(("C9",9,[(i,(i+1)%9) for i in range(9)]))
    # Petersen
    pet=[(i,(i+1)%5) for i in range(5)]+[(5+i,5+((i+2)%5)) for i in range(5)]+[(i,5+i) for i in range(5)]
    cases.append(("Petersen",10,pet))
    # Grotzsch
    gro=[(i,(i+1)%5) for i in range(5)]
    for i in range(5): gro+=[(5+i,(i-1)%5),(5+i,(i+1)%5)]
    for i in range(5): gro.append((10,5+i))
    cases.append(("Grotzsch",11,gro))
    for nm,n,e in cases:
        r=from_edges(nm,n,e)
        if r: run(*r)
    print("\nDONE")
