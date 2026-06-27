import numpy as np, random
from scipy.optimize import linprog
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
def R_full(N,adj,side,M):
    geos=[]; he=[]
    for (u,v) in M:
        gs=all_shortest_geos(N,adj,side,u,v); geos.append(gs); he.append(len(gs[0]))
    beta=len(M); nphi=N; nvar=nphi+beta
    c=np.zeros(nvar)
    for e in range(beta): c[nphi+e]=-he[e]
    rows=[]; rhs=[]
    for e in range(beta):
        for P in geos[e]:
            row=np.zeros(nvar); row[nphi+e]=1.0
            for v in P: row[v]-=1.0
            rows.append(row); rhs.append(0.0)
    row=np.zeros(nvar)
    for v in range(N): row[v]=1.0
    rows.append(row); rhs.append(1.0)
    res=linprog(c,A_ub=np.array(rows),b_ub=np.array(rhs),bounds=[(0,None)]*nvar,method="highs")
    return -res.fun,res.x[:nphi]
def rand_tf(N,p,seed):
    random.seed(seed); adj=[set() for _ in range(N)]
    edges=[(u,v) for u in range(N) for v in range(u+1,N)]; random.shuffle(edges)
    for (u,v) in edges:
        if random.random()<p and not (adj[u]&adj[v]): adj[u].add(v); adj[v].add(u)
    return adj
nfrac=0; checked=0; worstratio=0
for seed in range(150):
    N=random.Random(seed).choice([12,14,16])
    adj=rand_tf(N,0.5,seed)
    res,mc=gamma_min_cut(N,adj,edges_of(adj),cap=800)
    if not res: continue
    side,G,M=res
    if not M: continue
    rf,phi=R_full(N,adj,side,M)
    mx=phi.max() if phi.size else 0
    vals=sorted(set(round(p/mx,4) for p in phi if p>1e-7)) if mx>1e-9 else []
    checked+=1
    K=N+N*N-G
    worstratio=max(worstratio,rf/K)
    if len(vals)>1:
        nfrac+=1
        print("FRACTIONAL optimum: seed=%d N=%d Gam=%d rf/K=%.4f vals=%s"%(seed,N,G,rf/K,vals[:6]))
print("checked=%d fractional-optimum cases=%d worst rf/K=%.4f"%(checked,nfrac,worstratio))
