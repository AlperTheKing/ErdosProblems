#!/usr/bin/env python3
"""NEW non-certificate structural attack on the Connected-B Gamma Lemma Gamma=sum_e ell_e^2 <= N^2.
CHARGING: ell_e^2 = ell_e * |C_e| where C_e is a shortest odd cycle through bad edge e (|C_e|=ell_e).
Distribute charge ell_e to each vertex of C_e. With a fractional choice f_{e,C} (sum_C f=1) over shortest
odd cycles, the load on vertex v is  L(v) = sum_e ell_e * sum_{C ni v} f_{e,C}.  Always sum_v L(v) = Gamma.
IF a choice gives  max_v L(v) <= N , then Gamma = sum_v L(v) <= N*N = N^2.  Test the min-max charging LP:
   minimize kappa s.t. L(v) <= kappa for all v, sum_C f_{e,C}=1, f>=0.   Check kappa* <= N  (tight at C5[q]).
This is a load-balancing statement, NOT a cut/dual certificate -- a genuinely different route.
"""
import itertools
import numpy as np
from collections import deque
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]
def maxcut(N, adj):
    best = -1; bs = None
    for m in range(1 << (N-1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and s[u] != s[v])
        if c > best: best = c; bs = s
    return best, bs

def shortest_odd_cycles_through(N, adj, e, Lmax):
    """all odd cycles of length == girth-through-e that contain bad edge e=(p,q), as vertex frozensets.
    Here ell_e = d_B+1; the shortest odd cycle through e uses e + a shortest B-path between its endpoints."""
    p, q = e
    # B = adj minus bad edges? For the cycle e + B-geodesic: we need shortest paths between p,q NOT using e,
    # of even length d (so cycle length d+1 odd). We search odd cycles through e of minimal length.
    best = [None]
    cycles = []
    # DFS odd cycles containing edge (p,q): path from p to q (not via edge e) of even length, total odd.
    def dfs(u, target, path, ps, maxlen):
        if u == target and len(path) >= 3 and len(path) % 2 == 1:
            cycles.append(frozenset(path)); return
        if len(path) > maxlen: return
        for w in adj[u]:
            if u == p and w == q and len(path) == 1: continue   # don't immediately reuse edge e
            if w == q and u != p and len(path) % 2 == 0:
                cycles.append(frozenset(path+[q]));
            if w not in ps and len(path) < maxlen:
                ps.add(w); path.append(w); dfs(w, target, path, ps, maxlen); path.pop(); ps.discard(w)
    # simpler: enumerate all odd cycles containing both p and q adjacent via e, of length ell_e
    # use BFS for d_B(p,q) ignoring edge e
    return None  # replaced below

def all_odd_cycles_vsets(N, adj, Lmax):
    out = {}
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                vs = frozenset(path)
                edges = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                out[vs] = (len(path), edges)
            elif w not in ps and w > start and len(path) < Lmax:
                path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s, s, [s], {s})
    return out  # vset -> (length, edgeset)

def charging_lp(N, A):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    M = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u and side[max(u,v)] == side[min(u,v)]]
    # recompute M properly
    M = [(u, v) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    if not M: return None
    cyc = all_odd_cycles_vsets(N, adj, N)   # vset->(len,edges)
    # for each bad edge e, its shortest odd cycles = min-length odd cycles whose edgeset contains e
    fe_ = e_ = None
    per_e = []
    for (u, v) in M:
        ee = frozenset((u, v))
        cand = [(vs, L) for vs, (L, es) in cyc.items() if ee in es]
        if not cand: return ('disc',)
        Lmin = min(L for vs, L in cand)
        sc = [vs for vs, L in cand if L == Lmin]   # shortest odd cycles through e, length Lmin=ell_e
        per_e.append((Lmin, sc))
    m = len(M)
    # LP variables: f[e,c] for each (e, cycle index), plus kappa
    varlist = []
    for ei, (Le, sc) in enumerate(per_e):
        for ci, vs in enumerate(sc): varlist.append((ei, ci, vs, Le))
    nf = len(varlist); KAP = nf; nvar = nf + 1
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    # sum_c f_{e,c} = 1
    groups = {}
    for vi, (ei, ci, vs, Le) in enumerate(varlist): groups.setdefault(ei, []).append(vi)
    for ei, vis in groups.items():
        row = np.zeros(nvar)
        for vi in vis: row[vi] = 1.0
        A_eq.append(row); b_eq.append(1.0)
    # L(v) = sum_{(e,c): v in vs} Le * f <= kappa  for each vertex v
    A_ub = []; b_ub = []
    for v in range(N):
        row = np.zeros(nvar)
        for vi, (ei, ci, vs, Le) in enumerate(varlist):
            if v in vs: row[vi] += Le
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nf + [(0, None)], method="highs")
    kappa = res.fun if res.success else float('inf')
    Gamma = sum(Le*Le for (Le, sc) in per_e)
    return kappa, N, Gamma, m

# builders
def c5n(k):
    Nn = 5*k; A = [0]*Nn; part = lambda v: v//k
    for u in range(Nn):
        for v in range(u+1, Nn):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return Nn, A
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

def run_named():
    for (N, A, lab) in [(*c5n(1), "C5"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"),
                        (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13")]:
        r = charging_lp(N, A)
        if r is None or r[0] == 'disc': print(f"{lab}: skip"); continue
        kappa, n, Gamma, m = r
        print(f"{lab:10s} N={n:3d} m={m:3d} Gamma={Gamma:.0f} charging kappa*={kappa:.4f} N={n} kappa<=N:{kappa<=n+1e-7} "
              f"(=> Gamma<=N^2:{kappa<=n+1e-7})", flush=True)

def run_exhaustive(Ns):
    worst = 0.0; viol = 0; tot = 0
    for N in Ns:
        wN = 0.0; vN = 0
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            r = charging_lp(n, A)
            if r is None or (isinstance(r, tuple) and r and r[0] == 'disc'): continue
            kappa, nn, Gamma, m = r
            if m == 0: continue
            tot += 1; ratio = kappa/nn
            if kappa > nn + 1e-6: vN += 1; viol += 1
            wN = max(wN, ratio); worst = max(worst, ratio)
        print(f"N={N}: charging kappa*>N VIOLATIONS={vN}, worst kappa*/N={wN:.4f}", flush=True)
    print(f">>> total {tot}, VIOLATIONS={viol}, overall worst kappa*/N={worst:.4f}", flush=True)

if __name__ == "__main__":
    print("=== NEW: charging LP  min max_v L(v)  vs N  (<= N => Gamma<=N^2) ===", flush=True)
    run_named()
    print("--- exhaustive N<=9 ---", flush=True)
    run_exhaustive([5, 6, 7, 8, 9])
    print("DONE", flush=True)
