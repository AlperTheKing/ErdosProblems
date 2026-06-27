#!/usr/bin/env python3
"""Hand-construct a config where peeling forces condition (i) CD to FAIL on the remainder.
We want: after removing a bad edge's shortest geodesic C, some S in keep has delta_M'(S)>delta_B'(S).
That needs the remainder's B' to be 'cut-loose' (an alternative cut beats it locally) while M'
still has edges. We try small explicit gadgets and also a randomized local search over small
triangle-free graphs maximizing the ratio subject to: NO safe peel AND (i) in every failure set.
"""
import random
from peel_check import (gamma_of, Bconnected, maxcut_all, bdistB,
                        shortest_path_B, cut_dom, is_triangle_free)

def best_side(n,adj):
    mc,cuts=maxcut_all(n,adj)
    best=None
    for sd in cuts:
        if not Bconnected(n,adj,sd): continue
        G,M=gamma_of(n,adj,sd)
        if G is None: continue
        if best is None or G<best[0]: best=(G,M,sd)
    return best

def failmodes(n,adj,side,G,M):
    out=[]
    for (u,v) in M:
        P=shortest_path_B(n,adj,side,u,v)
        if P is None: out.append({"noP"}); continue
        C=set(P); s=len(C); keep=[x for x in range(n) if x not in C]
        if not keep: out.append({"all"}); continue
        Mp=[(a,b) for (a,b) in M if a in keep and b in keep]
        Gp=0; ok=True
        for (a,b) in Mp:
            d=bdistB(n,adj,side,a,banned=C).get(b,-1)
            if d<0: ok=False; break
            Gp+=(d+1)**2
        f=set()
        if not ok: f.add("ii")
        else:
            L=G-Gp; bound=2*s*n-s*s
            if L>bound: f.add("iii")
            cd=cut_dom(keep,n,adj,side,Mp)
            if cd is False: f.add("i")
            elif cd is None: f.add("keep")
        out.append(f if f else {"SAFE"})
    return out

def evaluate(n,adj):
    if not is_triangle_free(n,adj): return None
    b=best_side(n,adj)
    if b is None: return None
    G,M,sd=b
    if len(M)<2: return None
    fm=failmodes(n,adj,sd,G,M)
    any_safe=any(f=={"SAFE"} for f in fm)
    i_binding_everywhere=(not any_safe) and all(("i" in f) for f in fm)
    return G,len(M),sd,fm,any_safe,i_binding_everywhere

def rand_search(n, iters, seed, p_edge=0.45):
    random.seed(seed)
    best=None  # (i_everywhere, ratio, adj)
    bestI=None # specifically i-binding-everywhere with max ratio
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    for it in range(iters):
        adj=[set() for _ in range(n)]
        for (i,j) in pairs:
            if random.random()<p_edge:
                # keep triangle-free greedily
                if not (adj[i]&adj[j]):
                    adj[i].add(j); adj[j].add(i)
        ev=evaluate(n,adj)
        if ev is None: continue
        G,m,sd,fm,any_safe,ibe=ev
        ratio=G/(n*n)
        if (not any_safe):
            if best is None or ratio>best[1]:
                best=(ibe,ratio,[set(a) for a in adj],fm)
        if ibe:
            if bestI is None or ratio>bestI[1]:
                bestI=(ibe,ratio,[set(a) for a in adj],fm)
    return best,bestI

if __name__=="__main__":
    import sys
    n=int(sys.argv[1]) if len(sys.argv)>1 else 12
    iters=int(sys.argv[2]) if len(sys.argv)>2 else 60000
    seed=int(sys.argv[3]) if len(sys.argv)>3 else 0
    best,bestI=rand_search(n,iters,seed)
    if best:
        ibe,ratio,adj,fm=best
        edges=[(i,j) for i in range(n) for j in adj[i] if j>i]
        print(f"[best no-safe-peel] n={n} ratio={ratio:.4f} i_everywhere={ibe} modes={[sorted(x) for x in fm]}")
        print(f"   edges={edges}")
    else:
        print(f"n={n}: no no-safe-peel m>=2 instance found in {iters} random tries (seed {seed})")
    if bestI:
        ibe,ratio,adj,fm=bestI
        edges=[(i,j) for i in range(n) for j in adj[i] if j>i]
        print(f"[(i)-binding-everywhere] n={n} ratio={ratio:.4f} modes={[sorted(x) for x in fm]}")
        print(f"   edges={edges}")
    else:
        print(f"n={n}: NO instance where (i)CD is binding on EVERY bad edge (in {iters} tries)")
