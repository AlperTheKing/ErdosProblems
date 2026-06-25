#!/usr/bin/env python3
"""STRATEGY 7 KEY LEMMA probe: the density factor via Cauchy on the dual metric's cut decomposition.

We test the precise certificate inequality. Setup (rho>=1 regime, normalize sum_b ell*_b = 1):
 - optimal dual metric ell*, induced sp-metric D on M-pairs.
 - cut decomposition a_S>=0 with sum_S a_S 1[S separates (u,v)] = D(u,v) on M-pairs (exists by L1-on-M).
 - rho = sum_M D = sum_S a_S e_M(S,~S).

The bound rho <= N^2/(25m) should follow from a Cauchy-Schwarz on the cut-weights a_S and the
'separator profiles' via (Sep).  CANDIDATE KEY INEQUALITY (mirror of nu*<=N^2/25):
   Define for the cut family {S : a_S>0} the vertex-incidence  mu_v = sum_{S: v in S} a_S  (or symmetric).
   Then (Sep)/CD gives capacity constraints, and a Cauchy on mu reproduces 25.

Rather than guess, let me MEASURE the structure of the optimal cut decomposition on the obstruction:
  - how many cuts, their e_B / e_M values, and the per-vertex separator load.
"""
import itertools, math, heapq
import numpy as np
from scipy.optimize import linprog
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

def rho_and_ell(N, adj, side):
    M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    Bset = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] != side[v]]
    m = len(M)
    if m == 0:
        return None
    adjB = [set() for _ in range(N)]
    for (u, v) in Bset:
        adjB[u].add(v); adjB[v].add(u)
    def simple_paths(s, t, maxlen=12):
        out = []
        def dfs(u, path, vis):
            if u == t:
                out.append(list(path)); return
            if len(path) > maxlen:
                return
            for w in adjB[u]:
                if w not in vis:
                    vis.add(w); path.append(w); dfs(w, path, vis); path.pop(); vis.discard(w)
        dfs(s, [s], {s}); return out
    paths = [simple_paths(s, t) for (s, t) in M]
    offs = []; cur = 0
    for k, plist in enumerate(paths):
        offs.append(cur); cur += len(plist)
    nf = cur; KAP = nf; nvar = nf + 1
    def vi(k, pi):
        return offs[k] + pi
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    for k, plist in enumerate(paths):
        row = np.zeros(nvar)
        for pi in range(len(plist)):
            row[vi(k, pi)] = 1.0
        A_eq.append(row); b_eq.append(1.0)
    A_ub = []; b_ub = []
    for e in Bset:
        row = np.zeros(nvar)
        for k, plist in enumerate(paths):
            for pi, p in enumerate(plist):
                pe = set(tuple(sorted((p[i], p[i+1]))) for i in range(len(p)-1))
                if e in pe:
                    row[vi(k, pi)] += 1.0
        row[KAP] = -1.0; A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nf + [(0, None)], method="highs")
    rho = res.fun
    ell = -res.ineqlin.marginals
    ell = ell / max(np.sum(ell), 1e-12)  # normalize sum ell = 1
    return rho, M, Bset, ell, m

def sp_metric(N, Bset, ell):
    adj = {}
    for (x, y), w in zip(Bset, ell):
        adj.setdefault(x, []).append((y, w)); adj.setdefault(y, []).append((x, w))
    D = np.full((N, N), 1e18)
    for s in range(N):
        D[s, s] = 0.0; pq = [(0.0, s)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > D[s, u]:
                continue
            for v, w in adj.get(u, []):
                nd = d + w
                if nd < D[s, v]:
                    D[s, v] = nd; heapq.heappush(pq, (nd, v))
    return D

def cut_decomp_on_M(N, M, Bset, D):
    """min sum_S a_S e_B(S) s.t. cut-rep = D on M pairs; return (value, {mask:a_S>0})."""
    masks = list(range(1, 1 << (N-1)))
    cols = []; obj = []
    for mask in masks:
        S = [(mask >> u) & 1 for u in range(N)]
        col = np.array([1.0 if S[u] != S[v] else 0.0 for (u, v) in M])
        eB = sum(1 for (u, v) in Bset if S[u] != S[v])
        cols.append(col); obj.append(float(eB))
    Amat = np.array(cols).T
    obj = np.array(obj)
    b = np.array([D[u, v] for (u, v) in M])
    res = linprog(obj, A_eq=Amat, b_eq=b, bounds=[(0, None)]*len(masks), method="highs")
    if not res.success:
        return None
    a = res.x
    used = {masks[i]: a[i] for i in range(len(masks)) if a[i] > 1e-9}
    return res.fun, used

def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v):
        A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4):
            add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4):
                A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

print("=== structure of optimal cut decomposition on M-pairs (obstruction + extremal) ===", flush=True)
for (label, N, A) in [("C5[2]", *c5n(2)), ("K23-N13", *gpt_k23())]:
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    r = rho_and_ell(N, adj, side)
    if r is None:
        continue
    rho, M, Bset, ell, m = r
    D = sp_metric(N, Bset, ell)
    cc = cut_decomp_on_M(N, M, Bset, D)
    if cc is None:
        print(f"  {label}: NO L1 rep on M (should not happen for rho>=1)"); continue
    val, used = cc
    # per-cut data
    print(f"  {label}: N={N} m={m} rho={rho:.4f} cutcost={val:.4f} (=rho?) #cuts={len(used)}", flush=True)
    # vertex separator load: mu_v = sum over used cuts S with a_S of (1 if v in smaller side)
    sum_aS = sum(used.values())
    sum_aS_eB = 0.0; sum_aS_eM = 0.0
    for mask, aS in used.items():
        S = [(mask >> u) & 1 for u in range(N)]
        eB = sum(1 for (u, v) in Bset if S[u] != S[v])
        eM = sum(1 for (u, v) in M if S[u] != S[v])
        sum_aS_eB += aS*eB; sum_aS_eM += aS*eM
        print(f"      a_S={aS:.4f} |S|={sum(S)} e_B(S)={eB} e_M(S)={eM} CD_ok={eM<=eB}", flush=True)
    print(f"      sum a_S e_M = {sum_aS_eM:.4f} (=sum_M D=rho), sum a_S e_B = {sum_aS_eB:.4f}, "
          f"sum a_S = {sum_aS:.4f}", flush=True)
print("DONE", flush=True)
