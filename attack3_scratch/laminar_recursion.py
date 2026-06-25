import itertools, math
import numpy as np
from scipy.optimize import linprog
import sys
sys.path.insert(0, r'E:\Projects\ErdosProblems\bridge\flagsdp')
import flag_engine as fe

def adjset(N, A):
    return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best:
            best = c; bs = side
    return best, bs

def rho_mcf(N, adjB, demands):
    Be = sorted(set((min(u, v), max(u, v)) for u in range(N) for v in adjB[u]))
    K = len(demands)
    arcs = []
    for (x, y) in Be:
        arcs.append((x, y)); arcs.append((y, x))
    nA = len(arcs); arc_idx = {a: i for i, a in enumerate(arcs)}
    nf = K*nA; nvar = nf + 1
    def fvar(k, ai): return k*nA + ai
    KAP = nf
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    for k, (s, t) in enumerate(demands):
        for v in range(N):
            row = np.zeros(nvar)
            for ai, (a, b) in enumerate(arcs):
                if a == v: row[fvar(k, ai)] += 1.0
                if b == v: row[fvar(k, ai)] -= 1.0
            A_eq.append(row); b_eq.append(1.0 if v == s else (-1.0 if v == t else 0.0))
    A_ub = []; b_ub = []
    for (x, y) in Be:
        row = np.zeros(nvar)
        a1 = arc_idx[(x, y)]; a2 = arc_idx[(y, x)]
        for k in range(K):
            row[fvar(k, a1)] += 1.0; row[fvar(k, a2)] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nf + [(0, None)], method="highs")
    return res.fun

for N in [5, 6, 7, 8, 9]:
    states = fe.enumerate_graphs(N, triangle_free=True)
    worst_rho = 0; worst = None; count_rho_gt1 = 0; total = 0
    worst_margin = None; min_margin = 1e9
    for (n, A) in states:
        adj = adjset(n, A); edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
        if not edges: continue
        mc, side = maxcut(n, adj)
        M = [(min(u, v), max(u, v)) for (u, v) in edges if side[u] == side[v]]
        if not M: continue
        adjB = [set() for _ in range(n)]
        for (u, v) in edges:
            if side[u] != side[v]:
                adjB[u].add(v); adjB[v].add(u)
        m = len(M)
        rho = rho_mcf(n, adjB, M)
        total += 1
        bound = max(1.0, n*n/(25.0*m))
        margin = bound - rho
        if margin < min_margin:
            min_margin = margin; worst_margin = (n, m, round(rho, 4), round(bound, 4))
        if rho > 1.0 + 1e-7: count_rho_gt1 += 1
        if rho > worst_rho:
            worst_rho = rho; worst = (n, m, round(rho, 4), round(bound, 4))
    print(f"N={N}: {total} w/ M!=0. max rho={worst_rho:.4f} at {worst}; "
          f"#(rho>1)={count_rho_gt1}; min margin(bound-rho)={min_margin:.4f} at {worst_margin}", flush=True)
print("DONE", flush=True)
