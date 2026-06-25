#!/usr/bin/env python3
"""AUDIT GPT's corrected route PCF25 (chat 6a3b5aba):
   mu(B,M) >= 25 m^2 / N^2 ,
where mu = MAX-THROUGHPUT multiflow: route a fraction f_e<=1 of each bad-edge demand over simple B-paths,
unit capacity per B-edge, maximize total routed sum_e f_e. Each routed path e gives an odd cycle (one M-edge)
=> nu* >= mu. Verify (a) mu >= 25m^2/N^2, (b) nu* >= mu, on named instances + a small dilution J_2 (which
killed the congestion route).
"""
import itertools
import numpy as np
from collections import deque
from scipy.optimize import linprog

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]
def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best: best = c; bs = side
    return best, bs

def all_odd_cycles(N, adj):
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append(es)
            elif w not in ps and w > start and len(path) < N: path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s, s, [s], {s})
    return out
def nu_star(N, adj, edges):
    cyc = all_odd_cycles(N, adj)
    if not cyc: return 0.0
    eidx = {e: i for i, e in enumerate(edges)}; Aub = np.zeros((len(edges), len(cyc)))
    for j, es in enumerate(cyc):
        for e in es: Aub[eidx[e], j] = 1.0
    res = linprog(-np.ones(len(cyc)), A_ub=Aub, b_ub=np.ones(len(edges)), bounds=[(0, None)]*len(cyc), method="highs")
    return -res.fun

def mu_throughput(N, adj, side):
    B = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    if not M: return 0.0, 0
    arcs = []
    for (x, y) in B: arcs.append((x, y)); arcs.append((y, x))
    nA = len(arcs); aidx = {a: i for i, a in enumerate(arcs)}; K = len(M)
    # vars: x[k,arc] (K*nA) then f[k] (K)
    nx = K*nA; nvar = nx + K
    def xi(k, ai): return k*nA + ai
    def fi(k): return nx + k
    c = np.zeros(nvar)
    for k in range(K): c[fi(k)] = -1.0     # maximize sum f
    A_eq = []; b_eq = []
    for k, (s, t) in enumerate(M):
        for v in range(N):
            row = np.zeros(nvar)
            for ai, (a, b) in enumerate(arcs):
                if a == v: row[xi(k, ai)] += 1.0
                if b == v: row[xi(k, ai)] -= 1.0
            if v == s: row[fi(k)] -= 1.0
            elif v == t: row[fi(k)] += 1.0
            A_eq.append(row); b_eq.append(0.0)
    A_ub = []; b_ub = []
    Bset = sorted(set(B))
    for (x, y) in Bset:
        row = np.zeros(nvar); a1 = aidx[(x, y)]; a2 = aidx[(y, x)]
        for k in range(K): row[xi(k, a1)] += 1.0; row[xi(k, a2)] += 1.0
        A_ub.append(row); b_ub.append(1.0)
    bounds = [(0, None)]*nx + [(0, 1)]*K
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq), bounds=bounds, method="highs")
    return -res.fun, K

def analyze(N, A, label, do_nu=True):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mu, m = mu_throughput(N, adj, side)
    if m == 0: return
    target = 25.0*m*m/(N*N)
    nu = nu_star(N, adj, edges) if do_nu else float('nan')
    okP = mu >= target - 1e-6
    okN = (nu >= mu - 1e-6) if do_nu else True
    print(f"{label:14s} N={N:3d} m={m:3d} mu={mu:7.3f} 25m^2/N^2={target:7.3f} PCF25:{okP} | nu*={nu:7.3f} nu*>=mu:{okN}", flush=True)

# builders
def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A
def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A
def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A
def c5paths20():
    N = 20; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    x = lambda i: i % 5; y = lambda i: 5+(i % 5); z = lambda i: 10+(i % 5); w = lambda i: 15+(i % 5)
    for i in range(5):
        add(x(i), x(i+1)); add(x(i), y(i)); add(y(i), z(i)); add(z(i), w(i)); add(w(i), x(i+1))
    return N, A
def dilution_J(t):
    """H = K23-N13 + C5[t], joined by ONE bridge edge crossing both cuts (GPT's J_t)."""
    NH, AH = gpt_k23(); NC, AC = c5n(t)
    N = NH + NC; A = [0]*N
    for u in range(NH):
        for v in range(NH):
            if (AH[u] >> v) & 1: A[u] |= 1 << v
    for u in range(NC):
        for v in range(NC):
            if (AC[u] >> v) & 1: A[NH+u] |= 1 << (NH+v)
    # bridge: H vertex 0 (a U-branch, side X) to a C5[t] vertex on side Y. C5[t] part0 vtx=0 in X; part1 vtx=t in Y.
    # pick H vtx that is on side... just connect H-vertex 5 (a subdivision vtx) to C-vertex (NH+ t) ensuring cross-cut.
    h = 5; c = NH + t   # c in part1 (Y side typically); h subdivision vertex
    A[h] |= 1 << c; A[c] |= 1 << h
    return N, A

if __name__ == "__main__":
    print("=== AUDIT PCF25: mu(B,M) >= 25 m^2/N^2  and  nu* >= mu ===", flush=True)
    analyze(*petersen(), "Petersen")
    analyze(*gpt_k23(), "K23-N13")
    analyze(*c5n(2), "C5[2]")
    analyze(*c5n(3), "C5[3]")
    analyze(*c5paths20(), "C5paths-N20")
    analyze(*dilution_J(2), "J_2(dilution)")
    analyze(*dilution_J(3), "J_3(dilution)", do_nu=False)
    print("DONE", flush=True)
