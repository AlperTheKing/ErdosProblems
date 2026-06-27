import sys
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0,"E:/Projects/ErdosProblems/problems/23/writeup")
from verify_iii_independent import dec, maxcut_all, gmin, geos
# GPI fractional vertex-load LP: tau* = min over fractional shortest-cycle routings of max_v T(v),
# where each bad edge e routes 1 unit over its shortest geodesics; vertex load T(v)=sum_{e,P: v in V(P)} x_{e,P} h_e.
# Claim (Step-2 GPI / vertex-load theorem): tau* <= N + (N^2-Gamma);  tight (=N, all-saturated) iff C5[q].
def gpi_tau(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    # build routing variables: for each bad edge, list its shortest geodesics (vertex sets)
    cols=[]   # (edge_idx, frozenset(verts), h)
    edge_cols={}
    for ei,(u,v) in enumerate(M):
        Ps=geos(adj,side,u,v)
        edge_cols[ei]=[]
        for P in Ps:
            edge_cols[ei].append(len(cols))
            cols.append((ei, set(P), ell[(u,v)]))
    nx=len(cols); nvar=nx+1   # +tau
    c=np.zeros(nvar); c[-1]=1.0
    # A_eq: sum_j x_{e,j} = 1 for each bad edge
    A_eq=[]; b_eq=[]
    for ei in range(len(M)):
        row=np.zeros(nvar)
        for j in edge_cols[ei]: row[j]=1.0
        A_eq.append(row); b_eq.append(1.0)
    # A_ub: for each vertex v: sum_{cols with v in set} h*x - tau <= 0
    A_ub=[]; b_ub=[]
    for v in range(n):
        row=np.zeros(nvar)
        for j,(ei,vs,h) in enumerate(cols):
            if v in vs: row[j]=h
        row[-1]=-1.0
        A_ub.append(row); b_ub.append(0.0)
    bounds=[(0,None)]*nx + [(0,None)]
    res=linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=bounds, method='highs')
    if not res.success: return ('LPfail',G,n)
    tau=res.fun
    return (G, n, tau, n + (n*n-G))   # tau*, bound K=N+(N^2-Gamma)
def blow(t):
    nn=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%5)*t+b))
    return nn,E
def g6(s):
    return dec(s)
print("=== independent GPI vertex-load LP: tau* <= N+(N^2-Gamma), tight (=N) iff C5[q] ===")
for name,(n,E) in [("C5[2]",blow(2)),("C5[3]",blow(3)),("C5[4]",blow(4)),
                   ("n8",g6("G?`F`w")),
                   ("N11a",g6("J?BD@g]Qvo?")),("N11b",g6("J?AAD@ON@[?")),("N11c",g6("J?AAD@WM_{?"))]:
    r=gpi_tau(n,E)
    if r is None or r[0] in ('LPfail',): print(f"  {name}: {r}"); continue
    G,n2,tau,K=r
    print(f"  {name:6} N={n2} Gamma={G} | tau*={tau:.4f} | K=N+(N^2-Gamma)={K} | GPI tau*<=K: {tau<=K+1e-6} | tight(tau*==N): {abs(tau-n2)<1e-6}")
print("\nGPI holds iff tau*<=K everywhere; tight (tau*=N, all-vertex-saturated) ONLY at C5[q] = the rigidity.")
