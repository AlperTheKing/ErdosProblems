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
max_frac_ratio=0; bigcount=0
for seed in range(800):
    N=random.Random(seed).choice([10,12,14])
    adj=rand_tf(N,random.Random(seed+9).choice([0.45,0.55,0.65]),seed)
    res,mc=gamma_min_cut(N,adj,edges_of(adj),cap=600)
    if not res: continue
    side,G,M=res
    if not M: continue
    rf,phi=R_full(N,adj,side,M)
    mx=phi.max() if phi.size else 0
    vals=sorted(set(round(p/mx,4) for p in phi if p>1e-7)) if mx>1e-9 else []
    K=N+N*N-G
    if len(vals)>1:
        max_frac_ratio=max(max_frac_ratio,rf/K)
        if rf/K>0.3: bigcount+=1; print("HIGH-ratio fractional: seed=%d N=%d rf/K=%.4f"%(seed,N,rf/K))
print("max rf/K among FRACTIONAL-optimum cases = %.4f  (#with rf/K>0.3: %d)"%(max_frac_ratio,bigcount))
