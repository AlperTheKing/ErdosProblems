#!/usr/bin/env python3
"""Extract the GPI LP-DUAL optimum phi* (optimal vertex tolls) + active structure at the key witnesses.
At C5[q] the dual optimum is UNIFORM (phi*(v)=const, every load constraint active = the rigidity). Off C5[q]
the structure of phi* and which load constraints saturate shows HOW the slack K-tau* = (N+N^2-Gamma)-tau*
distributes -- the information a DIRECT GPI proof needs (and tests Step-2's conjecture rho(v) <-> T(v)-N).
Self-contained reuse of census_GPI machinery."""
import numpy as np
from scipy.optimize import linprog
from census_GPI import dec, maxcut_all, gmin, geos, blow

def gpi_dual(n,E,name):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: print(f"  {name}: no connected-B gmin"); return
    side,G,M,ell=r
    cols=[]; edge_cols={}
    for ei,(u,v) in enumerate(M):
        edge_cols[ei]=[]
        for P in geos(adj,side,u,v):
            edge_cols[ei].append(len(cols)); cols.append((ei,set(P),ell[(u,v)]))
    nx=len(cols); nvar=nx+1
    c=np.zeros(nvar); c[-1]=1.0
    A_eq=[]; b_eq=[]
    for ei in range(len(M)):
        row=np.zeros(nvar)
        for j in edge_cols[ei]: row[j]=1.0
        A_eq.append(row); b_eq.append(1.0)
    A_ub=[]; b_ub=[]
    for v in range(n):
        row=np.zeros(nvar)
        for j,(ei,vs,h) in enumerate(cols):
            if v in vs: row[j]=h
        row[-1]=-1.0; A_ub.append(row); b_ub.append(0.0)
    bounds=[(0,None)]*nx+[(0,None)]
    res=linprog(c,A_ub=np.array(A_ub),b_ub=np.array(b_ub),A_eq=np.array(A_eq),b_eq=np.array(b_eq),bounds=bounds,method='highs')
    if not res.success: print(f"  {name}: LP fail"); return
    tau=res.fun; K=n+(n*n-G)
    # primal load per vertex T(v) at optimum
    x=res.x[:nx]
    T=[sum(h*x[j] for j,(ei,vs,h) in enumerate(cols) if v in vs) for v in range(n)]
    # dual: marginals on the load constraints (A_ub) = phi*(v) (signed; linprog convention <=0)
    phi=-np.array(res.ineqlin.marginals)   # tolls on T(v)<=tau ; nonneg
    sphi=phi.sum()
    phi_n = phi/ sphi if sphi>1e-12 else phi
    # GPI dual value check: sum_e ell_e * m_phi(e) vs (N+N^2-Gamma)*sum phi   (must be <=, equality at tau*)
    def m_phi(ei):
        return min(sum(phi[v] for v in cols[j][1]) for j in edge_cols[ei])
    lhs=sum(ell[M[ei]]*m_phi(ei) for ei in range(len(M)))
    rhs=K*sphi
    sat=[v for v in range(n) if abs(T[v]-tau)<1e-6]
    print(f"  {name:7} N={n} Gamma={G} K={K} tau*={tau:.3f}  slack K-tau*={K-tau:.3f}")
    print(f"          saturated load verts T(v)=tau*: {len(sat)}/{n}  {sat}")
    print(f"          phi* (normalized sum=1): {[round(float(p),3) for p in phi_n]}")
    print(f"          uniform-phi*? {'YES (rigidity)' if max(phi_n)-min(phi_n)<1e-6 else 'no (non-uniform)'}")
    print(f"          GPI dual: sum ell*m_phi={lhs:.4f} <= K*sum_phi={rhs:.4f}  ratio={lhs/rhs if rhs>1e-12 else float('nan'):.4f} (=1 iff tau*=K)")

print("=== GPI dual-optimum phi* extraction at key witnesses ===")
gpi_dual(*blow(2),"C5[2]")
gpi_dual(*dec("G?`F`w"),"n8")
gpi_dual(*dec("J?BD@g]Qvo?"),"N11a")
gpi_dual(*dec("J?AAD@ON@[?"),"N11b")
gpi_dual(*dec("J?AAD@WM_{?"),"N11c")
print("\nAt C5[q]: phi* uniform, all loads saturated, ratio=1 (GPI tight = rigidity).")
print("Off C5[q]: phi* non-uniform / partial saturation, ratio<1 -- shows where the N^2-Gamma slack lives.")
