import sys, numpy as np
sys.path.insert(0,'.')
from scipy.optimize import linprog
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def rho_star(N,adj,side,M):
    geos={e:all_shortest_geos(N,adj,side,*e) for e in M}
    he={e:len(geos[e][0]) for e in M}
    ne=len(M); nv=N+ne
    c=np.zeros(nv)
    for i,e in enumerate(M): c[N+i]=-he[e]
    rows=[]; rhs=[]
    for i,e in enumerate(M):
        for P in geos[e]:
            row=np.zeros(nv); row[N+i]=1.0
            for v in P: row[v]-=1.0
            rows.append(row); rhs.append(0.0)
    Aub=np.array(rows); bub=np.array(rhs)
    Aeq=np.zeros((1,nv)); Aeq[0,:N]=1.0; beq=[1.0]
    bounds=[(0,None)]*N+[(None,None)]*ne
    res=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    return -res.fun, res.x[:N]

# Witnesses
C5=[(i,(i+1)%5) for i in range(5)]
grot_N, grot_adj = mycielskian(5, C5)
grot_edges=edges_of(grot_adj)
pet_adj=[set() for _ in range(10)]
for i in range(5):
    for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet_adj[a].add(b); pet_adj[b].add(a)
pet_edges=edges_of(pet_adj)

for name, (N,adj) in [("M(Petersen)", mycielskian(10,pet_edges)),
                      ("M(Grotzsch)", mycielskian(11,grot_edges))]:
    E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None:
        print(f"{name}: no connected-B maxcut found"); continue
    side,Gam,M=res
    K=N+N*N-Gam
    rho,phi=rho_star(N,adj,side,M)
    nz=phi[phi>1e-7]
    is_cut = nz.size>0 and (nz.max()-nz.min())<1e-6*max(1,nz.max())
    print(f"{name}: N={N} Gamma={Gam} N^2={N*N} deficit={N*N-Gam} K={K}")
    print(f"   rho*={rho:.5f}  rho*<=K? {rho<=K+1e-6}  normslack=(K-rho)/K={(K-rho)/K:.5f}")
    print(f"   maximizer is 0/1 cut? {is_cut}  #distinct nonzero levels={len(set(round(x,5) for x in nz))}")
