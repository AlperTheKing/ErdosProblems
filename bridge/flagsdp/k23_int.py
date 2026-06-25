import numpy as np, heapq
from itertools import combinations
import verify_D25_lemma16 as L
from check_uniform_worst import int_cost

n, A = L.gpt_k23()
adj = L.adjset(n, A)
edges = [frozenset((u,v)) for u in range(n) for v in adj[u] if v>u]
mc, side = L.maxcut(n, adj); tau = len(edges)-mc
sigs = L.min_signatures(n, adj, edges, tau)
print(f"K23: n={n} tau={tau} m={len(edges)}")
# the known worst toll support: uniform on 10 edges. Reconstruct from strategy probe? Just brute small E0.
# Test all E0 up to size 11 would be huge (C(18,10)). Instead test the bound on a RANDOM + structured sample
# and report the max ratio, plus specifically the central-K23 6 edges (0-2,0-3,0-4,1-2,1-3,1-4).
import random
random.seed(1)
best=0; bestE0=None
# structured: central 6 edges
central = frozenset([frozenset((0,2)),frozenset((0,3)),frozenset((0,4)),frozenset((1,2)),frozenset((1,3)),frozenset((1,4))])
for E0 in [central]:
    ic=int_cost(n,E0,edges,sigs); bound=n*n*len(E0)/(25*tau)
    print(f"  central6: cost={ic} bound={bound:.3f} ratio={ic/bound:.4f}")
# sample subsets of various sizes
for sz in range(1,15):
    locbest=0; locE0=None
    trials = 400 if len(edges)>12 else 100
    for _ in range(trials):
        E0=frozenset(random.sample(edges,sz))
        ic=int_cost(n,E0,edges,sigs); bound=n*n*sz/(25*tau)
        r=ic/bound
        if r>locbest: locbest=r; locE0=E0
        if r>best: best=r; bestE0=E0
    print(f"  size {sz}: sampled worst ratio={locbest:.4f}")
print(f">>> K23 overall sampled worst ratio={best:.4f}  (<=1 means INT holds)  bestE0size={len(bestE0) if bestE0 else 0}")
