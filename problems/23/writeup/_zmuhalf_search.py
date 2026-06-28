"""Adversarial search for ZMU-HALF violations: max(T(u),T(v))/N > 1/2 on a both-positive zero-mu edge.
Search random triangle-free graphs (various N up to ~24) and record the worst ratio.
Also: report the worst ratio and whether it ever exceeds 1/2 (would refute ZMU-HALF).
Exact Fraction; uses gmin cut from loads()."""
import random
from fractions import Fraction as F
from _h import loads
from _zmu import mu_edges

def rand_trifree(N, p, seed):
    rnd=random.Random(seed)
    adj=[set() for _ in range(N)]
    E=[]
    pairs=[(i,j) for i in range(N) for j in range(i+1,N)]
    rnd.shuffle(pairs)
    for i,j in pairs:
        if rnd.random()>p: continue
        # triangle-free: no common neighbor
        if adj[i]&adj[j]: continue
        adj[i].add(j); adj[j].add(i); E.append((i,j))
    return E

def worst_ratio(N,E):
    info=loads(N,E)
    if info is None: return None
    T=info['T']
    mu=mu_edges(info)
    best=F(0); wit=None
    for e,val in mu.items():
        if val!=0: continue
        u,v=tuple(e)
        if T[u]>0 and T[v]>0:
            mx=max(T[u],T[v])
            r=F(mx, N)
            if r>best: best=r; wit=(u,v,str(T[u]),str(T[v]),N)
    return best, wit

if __name__=="__main__":
    print("=== adversarial ZMU-HALF search: worst max(Tu,Tv)/N on both-pos zero-mu edges ===")
    globalbest=F(0); gwit=None; gN=None; ncases=0
    for N in range(10,25):
        for p in [0.3,0.4,0.5,0.6]:
            for seed in range(60):
                E=rand_trifree(N,p,seed*1000+N*7+int(p*100))
                r=worst_ratio(N,E)
                if r is None: continue
                best,wit=r
                if best>0: ncases+=1
                if best>globalbest: globalbest=best; gwit=wit; gN=N
        print(f"  up to N={N}: worst ratio so far={float(globalbest)}={globalbest} (>1/2? {globalbest>F(1,2)}) wit={gwit}", flush=True)
    print(f"TOTAL both-pos cases seen={ncases}; WORST max(Tu,Tv)/N={float(globalbest)}={globalbest}; exceeds 1/2: {globalbest>F(1,2)}")
