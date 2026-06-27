# KEY TEST: across many TF graphs, is R_full = R_01 WHENEVER R_full/K is non-tiny?
# Compute the GAP (R_full - R_01) and correlate with R_full/K. The dichotomy predicts:
#   gap>0  ==>  R_full/K small.  Equivalently R_01/K >= R_full/K - eps in the tight regime.
import numpy as np, random
from scipy.optimize import linprog
from itertools import combinations
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
def geos_he(N,adj,side,M):
    geos=[]; he=[]
    for (u,v) in M:
        gs=all_shortest_geos(N,adj,side,u,v); geos.append(gs); he.append(len(gs[0]))
    return geos,he
def R_full(N,M,geos,he):
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
    return -res.fun
def R01(N,M,geos,he):
    best=0
    for k in range(1,N+1):
        for S in combinations(range(N),k):
            Sset=set(S)
            num=sum(he[e]*min(sum(1 for v in P if v in Sset) for P in geos[e]) for e in range(len(M)))
            best=max(best,num/k)
    return best
def rand_tf(N,p,seed):
    random.seed(seed); adj=[set() for _ in range(N)]
    edges=[(u,v) for u in range(N) for v in range(u+1,N)]; random.shuffle(edges)
    for (u,v) in edges:
        if random.random()<p and not (adj[u]&adj[v]): adj[u].add(v); adj[v].add(u)
    return adj
# track: for the case with the LARGEST R_full/K that also has a gap, report it.
worst=None
for seed in range(400):
    N=random.Random(seed).choice([10,11,12])  # small enough to enumerate S
    adj=rand_tf(N,random.Random(seed+7).choice([0.45,0.55,0.65]),seed)
    res,mc=gamma_min_cut(N,adj,edges_of(adj),cap=500)
    if not res: continue
    side,G,M=res
    if not M: continue
    geos,he=geos_he(N,adj,side,M)
    rf=R_full(N,M,geos,he); r01=R01(N,M,geos,he)
    K=N+N*N-G; gap=rf-r01
    if gap>1e-6:
        if worst is None or rf/K>worst[0]: worst=(rf/K,r01/K,gap,seed,N,G)
print("Among gapped(fractional) cases, the one with MAX R_full/K:")
if worst: print("  R_full/K=%.4f  R_01/K=%.4f  gap=%.4f  seed=%d N=%d Gam=%d"%worst)
else: print("  NO gapped cases found")
