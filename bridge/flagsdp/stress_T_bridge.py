#!/usr/bin/env python3
"""ADVERSARIAL stress-test of the bridge conjecture (T): tau <= (N/5) sqrt(nu*)  <=>  nu* >= 25 tau^2/N^2.
Try to FALSIFY it on hard triangle-free graphs. ratio := 25 tau^2 / (N^2 nu*); (T) holds iff ratio <= 1.
ENUMERATION NOTE: capping odd-cycle length UNDERestimates nu*, which makes (T') HARDER -> a pass is SOUND;
a near/over violation triggers a cap escalation (true nu* only larger). MaxCut exact for N<=18.
"""
import itertools, math, random
import numpy as np
from scipy.optimize import linprog

random.seed(12345)

def adj_from_edges(N, E):
    adj = [set() for _ in range(N)]
    for (u, v) in E: adj[u].add(v); adj[v].add(u)
    return adj

def is_triangle_free(N, adj):
    for u in range(N):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]): return False
    return True

def maxcut_exact(N, adj):
    best = -1
    for mask in range(1 << (N-1)):
        c = 0
        for u in range(N):
            su = (mask >> u) & 1
            for v in adj[u]:
                if v > u and su != ((mask >> v) & 1): c += 1
        if c > best: best = c
    return best

def maxcut_heur(N, adj, iters=4000):
    best = -1
    for _ in range(iters):
        side = [random.randint(0, 1) for _ in range(N)]
        improved = True
        while improved:
            improved = False
            for u in range(N):
                same = sum(1 for v in adj[u] if side[v] == side[u])
                diff = sum(1 for v in adj[u] if side[v] != side[u])
                if same > diff: side[u] ^= 1; improved = True
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        best = max(best, c)
    return best

def odd_cycles_capped(N, adj, maxlen):
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append(es)
            elif w not in ps and w > start and len(path) < maxlen:
                path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s, s, [s], {s})
    return out

def nu_star(N, adj, edges, maxlen):
    cyc = odd_cycles_capped(N, adj, maxlen)
    if not cyc: return 0.0, 0
    eidx = {e: i for i, e in enumerate(edges)}
    Aub = np.zeros((len(edges), len(cyc)))
    for j, es in enumerate(cyc):
        for e in es: Aub[eidx[e], j] = 1.0
    res = linprog(-np.ones(len(cyc)), A_ub=Aub, b_ub=np.ones(len(edges)), bounds=[(0, None)]*len(cyc), method="highs")
    return -res.fun, len(cyc)

def evaluate(N, E, label):
    adj = adj_from_edges(N, E)
    if not is_triangle_free(N, adj): return None
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    if not edges: return None
    if N <= 18: mc = maxcut_exact(N, adj); exact = True
    else: mc = maxcut_heur(N, adj); exact = False
    tau = len(edges) - mc
    if tau == 0: return None
    cap = min(N, 11)
    nu, nC = nu_star(N, adj, edges, cap)
    ratio = 25.0*tau*tau/(N*N*nu) if nu > 0 else 9e9
    # escalate cap if near/over violation
    while ratio > 0.999 and cap < N:
        cap += 2; nu, nC = nu_star(N, adj, edges, min(cap, N)); ratio = 25.0*tau*tau/(N*N*nu) if nu > 0 else 9e9
    return dict(label=label, N=N, e=len(edges), tau=tau, nu=nu, ratio=ratio, exact=exact, nC=nC)

# ---- named hard triangle-free graphs ----
def grotzsch():
    # Mycielskian of C5: vertices 0..4 (C5), 5..9 (shadows), 10 (apex)
    E = []
    for i in range(5): E.append((i, (i+1) % 5))           # C5
    for i in range(5):
        for j in [(i+1) % 5, (i-1) % 5]: E.append((5+i, j))  # shadow u_i ~ neighbors of v_i
        E.append((10, 5+i))                                # apex ~ all shadows
    return 11, E

def mycielski(N0, E0):
    # Mycielskian of graph (N0,E0): v_i, u_i, apex w
    N = 2*N0+1; w = 2*N0; E = list(E0)
    adj0 = adj_from_edges(N0, E0)
    for i in range(N0):
        for j in adj0[i]:
            E.append((N0+i, j))      # u_i ~ N(v_i)
        E.append((w, N0+i))          # w ~ u_i
    # dedup
    E = list({tuple(sorted(e)) for e in E})
    return N, E

def cycle(n): return n, [(i, (i+1) % n) for i in range(n)]

def subdivided_k5(sub):
    # K5 on 0..4; subdivide each edge into a path with 'sub' internal vertices (sub even keeps odd cycles odd-length>=5-ish)
    N = 5; E = []; nxt = 5
    for a in range(5):
        for b in range(a+1, 5):
            prev = a
            for _ in range(sub):
                E.append((prev, nxt)); prev = nxt; nxt += 1
            E.append((prev, b))
    return nxt, E

def c5_blowup(parts):
    # parts = [s0..s4]; complete bipartite between consecutive classes
    offs = [0];
    for s in parts: offs.append(offs[-1]+s)
    N = offs[5]; E = []
    cls = lambda i: list(range(offs[i], offs[i+1]))
    for i in range(5):
        for u in cls(i):
            for v in cls((i+1) % 5): E.append((u, v))
    return N, E

def perturb(N, E, add=0, rem=0):
    adj = adj_from_edges(N, E); Es = set(tuple(sorted(e)) for e in E)
    Es = set(Es)
    # remove
    El = list(Es); random.shuffle(El)
    for e in El[:rem]: Es.discard(e)
    # add edges that keep triangle-free
    tries = 0
    while add > 0 and tries < 2000:
        tries += 1
        u, v = random.sample(range(N), 2); e = tuple(sorted((u, v)))
        if e in Es: continue
        a = adj_from_edges(N, [x for x in Es]+[e])
        if is_triangle_free(N, a): Es.add(e); add -= 1
    return N, list(Es)

def random_tf(N, target_density):
    pairs = [(u, v) for u in range(N) for v in range(u+1, N)]; random.shuffle(pairs)
    E = []
    for (u, v) in pairs:
        a = adj_from_edges(N, E+[(u, v)])
        if is_triangle_free(N, a): E.append((u, v))
        if len(E) >= target_density: break
    return N, E

if __name__ == "__main__":
    results = []
    named = [("Grotzsch", *grotzsch()[::-1]) if False else ("Grotzsch",)+grotzsch(),
             ("Myciel-C7",)+mycielski(*cycle(7)), ("Myciel-C9",)+mycielski(*cycle(9)),
             ("subdivK5-1",)+subdivided_k5(1), ("subdivK5-2",)+subdivided_k5(2), ("subdivK5-3",)+subdivided_k5(3),
             ("C5[2,2,2,2,2]",)+c5_blowup([2,2,2,2,2]), ("C5[3,3,3,3,3]",)+c5_blowup([3,3,3,3,3]),
             ("C5[3,2,3,2,3]",)+c5_blowup([3,2,3,2,3]), ("C5[4,3,3,3,2]",)+c5_blowup([4,3,3,3,2]),
             ("C5[2,2,2,2,3]",)+c5_blowup([2,2,2,2,3])]
    for (lab, N, E) in named:
        r = evaluate(N, E, lab)
        if r: results.append(r)
    # perturbed blowups (near the tight case)
    for k in [2, 3]:
        N0, E0 = c5_blowup([k]*5)
        for (ad, rm) in [(1, 0), (2, 0), (0, 1), (1, 1), (3, 1)]:
            N, E = perturb(N0, E0, add=ad, rem=rm)
            r = evaluate(N, E, f"C5[{k}]+{ad}-{rm}")
            if r: results.append(r)
    # random triangle-free
    for N in [10, 11, 12, 13, 14, 15, 16]:
        for d in [int(N*N*0.18), int(N*N*0.22), int(N*N*0.25)]:
            for s in range(3):
                Nn, E = random_tf(N, d)
                r = evaluate(Nn, E, f"rand-N{N}-d{d}-{s}")
                if r: results.append(r)
    results.sort(key=lambda r: -r["ratio"])
    print(f"{'label':18s} {'N':>3} {'e':>3} {'tau':>4} {'nu*':>7} {'ratio=25t^2/N^2nu':>9} {'exact':>5}")
    over = 0
    for r in results[:40]:
        flag = "  <<< (T) VIOLATION" if r["ratio"] > 1.0+1e-6 else ""
        if r["ratio"] > 1.0+1e-6: over += 1
        print(f"{r['label']:18s} {r['N']:3d} {r['e']:3d} {r['tau']:4d} {r['nu']:7.3f} {r['ratio']:9.4f} {str(r['exact']):>5}{flag}")
    print(f"\n#instances={len(results)}  max ratio={results[0]['ratio']:.4f} at {results[0]['label']}  (T) VIOLATIONS={over}")
    print("(T) holds iff all ratios <= 1; tight (=1) expected only at balanced C5[n].")
    print("DONE")
