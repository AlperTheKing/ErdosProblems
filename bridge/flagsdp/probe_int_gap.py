"""
Census sweep N<=11 triangle-free connected: for each band-max graph compute
  R_frac = max over phi>=0  sum_e h_e m_phi(e) / (K sum phi)        [full GPI ratio]
  R_01   = max over S       sum_e h_e min_P|P cap S| / (K |S|)      [0/1 cut-Hall ratio]
GPI holds <=> R_frac <= 1. 0/1 sufficient <=> R_frac == R_01.
Report any graph with R_frac > R_01 + eps (fractional STRICTLY needed) and any with R_frac>1 (would be counterexample).
"""
import numpy as np, itertools
from scipy.optimize import linprog
from mycielskian_check import gamma_min_cut, all_shortest_geos, edges_of
import flag_engine

def build(N,adj,side,G,M):
    paths=[]; pe=[]; he=[]
    for ei,(u,v) in enumerate(M):
        geos=all_shortest_geos(N,adj,side,u,v); h=len(geos[0]); he.append(h)
        for P in geos: pe.append(ei); paths.append(P)
    K=N+(N*N-G)
    return paths,pe,he,K

def Rfrac(N,adj,side,G,M):
    paths,pe,he,K=build(N,adj,side,G,M)
    beta=len(M); nv=N+beta
    c=np.zeros(nv)
    for ei in range(beta): c[N+ei]=-he[ei]
    rows=[]
    for k,P in enumerate(paths):
        r=np.zeros(nv); r[N+pe[k]]=1.0
        for v in P: r[v]-=1.0
        rows.append(r)
    Aub=np.array(rows); bub=np.zeros(len(rows))
    Aeq=np.zeros((1,nv)); Aeq[0,:N]=1.0; beq=[1.0]
    bounds=[(0,None)]*N+[(None,None)]*beta
    res=linprog(c,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=beq,bounds=bounds,method="highs")
    return (-res.fun)/K, res.x[:N]

def R01(N,adj,side,G,M):
    paths,pe,he,K=build(N,adj,side,G,M)
    # group geodesics by edge
    by_e={}
    for k,P in enumerate(paths): by_e.setdefault(pe[k],[]).append(set(P))
    best=0.0; bestS=None
    # iterate over all subsets S is 2^N; cap N<=14 fine for N<=11
    for mask in range(1,1<<N):
        S=set(v for v in range(N) if (mask>>v)&1); s=len(S)
        tot=0
        for ei,Plist in by_e.items():
            tot+=he[ei]*min(len(P&S) for P in Plist)
        r=tot/(K*s)
        if r>best: best=r; bestS=S
    return best,bestS

if __name__=="__main__":
    worst_frac=0; worst_gap=0; ce=[]
    cnt=0
    for N in range(5,12):
        for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
            adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
            E=edges_of(adj)
            res,mc=gamma_min_cut(N,adj,E)
            if res is None: continue
            side,G,M=res
            if not M: continue
            cnt+=1
            rf,phi=Rfrac(N,adj,side,G,M)
            worst_frac=max(worst_frac,rf)
            if rf>1+1e-6: ce.append((N,G,rf))
            if N<=10:
                r01,S=R01(N,adj,side,G,M)
                gap=rf-r01
                if gap>worst_gap: worst_gap=gap; print(f"  new max gap N={N} G={G} Rfrac={rf:.5f} R01={r01:.5f} gap={gap:.5f}")
    print(f"\nScanned {cnt} band-max graphs. worst Rfrac={worst_frac:.6f} (>1 means GPI false). worst (Rfrac-R01)={worst_gap:.6f}")
    print("counterexamples Rfrac>1:", ce)
