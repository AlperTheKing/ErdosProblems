#!/usr/bin/env python3
"""AUDIT GPT's D25 route (chat 6a3b5aba), the OPEN CORE = congestion lemma (16):
For a 2-connected critical atom K (tau=t, n vertices), is there a distribution p over (minimum signature S,
private-cycle assignment e->C_e with C_e∩S={e}) such that for EVERY edge a:
        E_p |{e in S : a in C_e}|  <=  n^2/(25 t)  ?
If yes, the constructed packing y_C=(25t/n^2)E_p|{e:C_e=C}| is feasible with value 25t^2/n^2 => nu*(K)>=25t^2/n^2.
We solve the min-max-congestion LP:
   min kappa  s.t.  sum_S p_S = 1;  for each (S,e in S): sum_C w_{S,e,C} = p_S;
                    for each edge a: sum_{(S,e,C): a in C} w_{S,e,C} <= kappa;  w>=0.
Check kappa* <= n^2/(25 t).
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

def all_odd_cycles_v(N, adj):
    """odd cycles as (frozenset of edges)."""
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append(es)
            elif w not in ps and w > start and len(path) < N: path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s, s, [s], {s})
    return out

def is_bipartite_after_removal(N, adj, removed):
    col = [-1]*N
    for s in range(N):
        if col[s] != -1: continue
        col[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if frozenset((u, v)) in removed: continue
                if col[v] == -1: col[v] = col[u]^1; q.append(v)
                elif col[v] == col[u]: return False
    return True

def min_signatures(N, adj, edges, tau):
    """all minimum signatures = size-tau edge sets whose removal bipartites K. Enumerate via W-switching from
    one max-cut mono set (all signatures are M XOR delta(W))."""
    mc, side = maxcut(N, adj)
    M0 = set(frozenset((u, v)) for (u, v) in edges if side[u] == side[v])
    sigs = set()
    for wm in range(1 << N):
        W = [(wm >> u) & 1 for u in range(N)]
        sig = frozenset(e for e in edges if (W[min(e)] ^ W[max(e)]) ^ (e in M0))   # M0 XOR delta(W)
        if len(sig) == tau: sigs.add(sig)
    return list(sigs)

def lemma16(N, A, label):
    adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj); tau = len(edges) - mc
    if tau == 0: print(f"{label}: bipartite, skip"); return
    sigs = min_signatures(N, adj, edges, tau)
    cyc = all_odd_cycles_v(N, adj)
    # private cycles per (S,e): odd cycles C with C∩S = {e}
    # build LP variables: (si, e, ci) where C∩S={e}
    varlist = []   # (si, e, ci)
    for si, S in enumerate(sigs):
        for e in S:
            for ci, C in enumerate(cyc):
                inter = C & S
                if len(inter) == 1 and (e in inter):
                    varlist.append((si, e, ci))
    if not varlist:
        print(f"{label}: NO private cycles found (selector fails?)"); return
    nv = len(varlist); nS = len(sigs)
    # vars: w[0..nv-1], p[0..nS-1], kappa  (last)
    NP = nv; PP = nv + nS; KAP = nv + nS
    nvar = nv + nS + 1
    vidx = {v: i for i, v in enumerate(varlist)}
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    # sum p = 1
    row = np.zeros(nvar)
    for s in range(nS): row[nv+s] = 1.0
    A_eq.append(row); b_eq.append(1.0)
    # for each (S,e): sum_C w = p_S
    se_groups = {}
    for vi, (si, e, ci) in enumerate(varlist): se_groups.setdefault((si, e), []).append(vi)
    for (si, e), vis in se_groups.items():
        row = np.zeros(nvar)
        for vi in vis: row[vi] = 1.0
        row[nv+si] = -1.0
        A_eq.append(row); b_eq.append(0.0)
    # load(a) <= kappa : for each edge a
    A_ub = []; b_ub = []
    for a in edges:
        row = np.zeros(nvar)
        for vi, (si, e, ci) in enumerate(varlist):
            if a in cyc[ci]: row[vi] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*(nvar-1)+[(0, None)], method="highs")
    kappa = res.fun if res.success else float('inf')
    target = N*N/(25.0*tau)
    print(f"{label:14s} n={N:3d} t={tau:3d} #minsig={nS:4d} #oddcyc={len(cyc):4d} kappa*={kappa:.4f} "
          f"n^2/(25t)={target:.4f} LEMMA16:{kappa <= target+1e-7} | value=25t^2/n^2={25*tau*tau/(N*N):.4f}", flush=True)

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
def c5(): return c5n(1)

if __name__ == "__main__":
    print("=== AUDIT congestion lemma (16): min-max private-cycle congestion <= n^2/(25t) ? ===", flush=True)
    lemma16(*c5(), "C5")
    lemma16(*c5n(2), "C5[2]")
    lemma16(*petersen(), "Petersen")
    lemma16(*gpt_k23(), "K23-N13")
    lemma16(*c5n(3), "C5[3]")
    print("DONE", flush=True)
