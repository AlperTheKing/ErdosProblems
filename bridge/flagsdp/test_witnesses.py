"""Test uniform routing on the high-chromatic Mycielskian witnesses M(C5)=Grotzsch (N=11),
M(Petersen) (N=21), M(Grotzsch) (N=23) -- the band extremizers used elsewhere in #23.
These are the hardest-known finite cases."""
import numpy as np
from mycielskian_check import mycielskian, edges_of, gamma_min_cut, all_shortest_geos

def load_uniform(N,adj,side,M):
    T=np.zeros(N)
    for (u,v) in M:
        geos=all_shortest_geos(N,adj,side,u,v)
        if not geos: return None
        w=1.0/len(geos); h=len(geos[0])
        for P in geos:
            for x in P: T[x]+=h*w
    return T

def run(name,N,adj):
    E=edges_of(adj)
    res,mc=gamma_min_cut(N,adj,E)
    if res is None: print(f"{name}: no valid cut"); return
    side,G,M=res; T=load_uniform(N,adj,side,M)
    if T is None: print(f"{name}: routing failed"); return
    K=N+(N*N-G); gap=T.max()-K
    print(f"{name}: N={N} beta={len(M)} Gamma={G} K={K} maxT={T.max():.4f} gap={gap:.4f} {'VIOLATION' if gap>1e-9 else 'ok'} argmax={int(T.argmax())}")

C5=[(i,(i+1)%5) for i in range(5)]
N,adj=mycielskian(5,C5); run("M(C5)=Grotzsch",N,adj)
pet=[set() for _ in range(10)]
for i in range(5):
    for (a,b) in [(i,(i+1)%5),(5+i,5+(i+2)%5),(i,5+i)]: pet[a].add(b); pet[b].add(a)
N,adj=mycielskian(10,edges_of(pet)); run("M(Petersen)",N,adj)
gN,gadj=mycielskian(5,C5)
N,adj=mycielskian(11,edges_of(gadj)); run("M(Grotzsch)",N,adj)
