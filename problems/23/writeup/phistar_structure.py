#!/usr/bin/env python3
"""Co-develop with Step-2: characterize the GPI dual-optimal phi* structure + test Step-2's conjecture
phi*(v) ~ vertex-load excess (T(v)-min_v T) [== rho(v) == T(v)-N at tightness].
For each witness: solve the primal vertex-load LP, get optimal loads T(v) and dual phi*; then TEST whether the
ansatz phi(v) = (T(v) - c)_+ (c in {N, tau*, min T}) is DUAL-OPTIMAL, i.e. achieves the max ratio
R(phi)=sum_f ell(f) m_phi(f) / sum_v phi(v) = tau*. Also report the B-structure of the phi*-support (degree in B,
whether bad-edge endpoint / hub). Exact-test deliverable for Step-2's closed-form certificate search."""
import numpy as np
from scipy.optimize import linprog
from census_GPI import dec, maxcut_all, gmin, geos, blow

def analyze(n, E, name):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: print(f"  {name}: no gmin"); return
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
    x=res.x[:nx]
    T=np.array([sum(h*x[j] for j,(ei,vs,h) in enumerate(cols) if v in vs) for v in range(n)])
    phistar=-np.array(res.ineqlin.marginals)  # dual on load constraints
    # B-degree of each vertex (cut-edges)
    Bdeg=[sum(1 for w in adj[v] if side[w]!=side[v]) for v in range(n)]
    badverts=set([u for u,v in M]+[v for u,v in M])
    # ratio function for a candidate potential
    def ratio(phi):
        sp=phi.sum()
        if sp<1e-12: return 0.0
        lhs=sum(ell[M[ei]]*min(sum(phi[v] for v in cols[j][1]) for j in edge_cols[ei]) for ei in range(len(M)))
        return lhs/sp
    print(f"  {name}: N={n} Gamma={G} tau*={tau:.3f} K={K}")
    print(f"     T(v) (optimal loads): {[round(float(t),2) for t in T]}  (max={T.max():.2f}=tau*, min={T.min():.2f})")
    # Step-2 ansatz tests: phi = (T - c)_+
    for cname,cval in [("N",n),("tau*",tau),("minT",T.min()),("meanT",T.mean())]:
        phi=np.maximum(T-cval,0.0)
        R=ratio(phi); ok = R>=tau-1e-6
        print(f"     ansatz phi=(T-{cname})_+ : support={[v for v in range(n) if phi[v]>1e-9]}  ratio R={R:.3f} (=tau* dual-opt? {ok})")
    # characterize the solver's phi* support
    sup=[v for v in range(n) if phistar[v]>1e-9]
    print(f"     solver phi* support={sup}; their Bdeg={[Bdeg[v] for v in sup]}; bad-endpoint?={[v in badverts for v in sup]}")
    print(f"     excess (T-tau*)_+ support (overloaded verts)={[v for v in range(n) if T[v]>tau-1e-6]}")

print("=== phi* structure + Step-2 ansatz phi=(T-c)_+ dual-optimality test ===")
for q in (2,3): analyze(*blow(q), f"C5[{q}]")
analyze(*dec("G?\x60F\x60w"), "n8")
analyze(*dec("J?BD@g]Qvo?"), "N11a")
analyze(*dec("J?AAD@ON@[?"), "N11b")
analyze(*dec("J?AAD@WM_{?"), "N11c")
print("\nIf phi=(T-c)_+ achieves ratio=tau* for some structured c, that is a CLOSED-FORM dual certificate ansatz for Step-2.")
