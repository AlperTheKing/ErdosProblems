#!/usr/bin/env python3
"""STRATEGY D probe (Erdos #23 Step-2, lemma 16 / D25).

GOAL: understand what the cut-cone decomposition of the optimal toll w gives, and whether the
"equilibration" condition (every positive-coeff cut is equilibrated, every positive cycle edge is
geodesically nonredundant) yields an inequality BEYOND CD that sums to <= n^2/(25 t).

Lemma 16 dual (von Neumann minimax):
   kappa* = max_{w>=0, sum_a w_a=1}  min_{S min sig}  sum_{e in S} ( min_{C odd, C∩S={e}} w(C) ).
where w(C) = sum_{a in C} w_a, and the inner cycle C is a "private cycle" for e in S.

We compute kappa* directly on the K23-N13 obstruction and on C5[q], extract the optimizing toll w*,
and then:
 (1) decompose w* into the CUT CONE: w* = sum_W lambda_W * 1_{delta(W)} + (nonneg residual r on edges),
     minimizing residual; report the cuts used and lambda.
 (2) For the SELECTOR value f(w,S) = sum_{e in S} min_{C private} w(C), check which S achieves the min
     (signature rotation), and whether the optimal w concentrates on a K_{2,3} core.
 (3) Test the candidate "equilibration inequality": for the optimal w and the achieving signature S,
     is  sum_{e in S} (shortest private toll)  bounded by a CUT-CONE expression that telescopes to
     n^2/(25t)?  Specifically test  sum_{e in S} w(C_e) vs  (1/something) * sum_W lambda_W * |delta(W)|.
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
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append(es)
            elif w not in ps and w > start and len(path) < N:
                path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s, s, [s], {s})
    return out

def min_signatures(N, adj, edges, tau):
    mc, side = maxcut(N, adj)
    M0 = set(frozenset((u, v)) for (u, v) in edges if side[u] == side[v])
    sigs = set()
    for wm in range(1 << N):
        W = [(wm >> u) & 1 for u in range(N)]
        sig = frozenset(e for e in edges if (W[min(e)] ^ W[max(e)]) ^ (e in M0))
        if len(sig) == tau: sigs.add(sig)
    return list(sigs)

def lemma16_dual(N, A, label, verbose=True):
    """Solve kappa* as a primal congestion LP (gives kappa* and dual toll w via shadow prices)."""
    adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = maxcut(N, adj); tau = len(edges) - mc
    if tau == 0:
        if verbose: print(f"{label}: bipartite, skip")
        return None
    sigs = min_signatures(N, adj, edges, tau)
    cyc = all_odd_cycles_v(N, adj)
    edge_list = list(edges); eidx = {e: i for i, e in enumerate(edge_list)}
    # primal congestion LP (same as verify_D25_lemma16): vars w_{S,e,C}, p_S, kappa
    varlist = []
    for si, S in enumerate(sigs):
        for e in S:
            for ci, C in enumerate(cyc):
                inter = C & S
                if len(inter) == 1 and (e in inter):
                    varlist.append((si, e, ci))
    nv = len(varlist); nS = len(sigs)
    KAP = nv + nS; nvar = nv + nS + 1
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    row = np.zeros(nvar)
    for s in range(nS): row[nv+s] = 1.0
    A_eq.append(row); b_eq.append(1.0)
    se_groups = {}
    for vi, (si, e, ci) in enumerate(varlist): se_groups.setdefault((si, e), []).append(vi)
    for (si, e), vis in se_groups.items():
        row = np.zeros(nvar)
        for vi in vis: row[vi] = 1.0
        row[nv+si] = -1.0
        A_eq.append(row); b_eq.append(0.0)
    A_ub = []; b_ub = []; ub_edge = []
    for a in edges:
        row = np.zeros(nvar)
        for vi, (si, e, ci) in enumerate(varlist):
            if a in cyc[ci]: row[vi] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0); ub_edge.append(a)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nvar, method="highs")
    kappa = res.fun
    target = N*N/(25.0*tau)
    # dual toll w on the congestion constraints (one per edge); normalized to sum 1
    duals = res.ineqlin.marginals  # <= 0 for <= constraints; magnitude = w_a (up to sign)
    w = np.array([-d for d in duals])  # nonneg
    sw = w.sum()
    if sw > 1e-12: w = w / sw
    if verbose:
        print(f"{label:12s} n={N:3d} t={tau:3d} kappa*={kappa:.4f} n^2/(25t)={target:.4f} "
              f"ok={kappa<=target+1e-7}  #sig={nS} #cyc={len(cyc)}", flush=True)
        # show toll support
        supp = [(edge_list_sorted(a), round(w[i], 4)) for i, a in enumerate(ub_edge) if w[i] > 1e-6]
        supp.sort(key=lambda t: -t[1])
        print(f"   optimal toll w* support ({len([s for s in supp if s[1]>1e-6])} edges): {supp[:20]}", flush=True)
    return dict(N=N, tau=tau, kappa=kappa, target=target, edges=ub_edge, w=w, sigs=sigs, cyc=cyc, adj=adj)

def edge_list_sorted(e):
    return tuple(sorted(e))

def cutcone_decompose(info, label):
    """Decompose toll w* into the cut cone: minimize residual r s.t. w = sum_W lam_W 1_{delta(W)} + r, r>=0.
    Enumerate all vertex cuts delta(W) (2^{N-1} of them). LP: min sum r_a; w_a = sum_W lam_W [a in delta(W)] + r_a."""
    N = info['N']; adj = info['adj']; edges = info['edges']; w = info['w']
    ne = len(edges); eidx = {e: i for i, e in enumerate(edges)}
    # enumerate cuts (skip empty/full): columns
    cuts = []
    for wm in range(1, 1 << (N-1)):  # W with vertex 0 fixed out, avoids complement duplicate
        Wset = set(u for u in range(N) if (wm >> u) & 1)
        col = np.zeros(ne)
        any_edge = False
        for i, e in enumerate(edges):
            u, v = tuple(e)
            if (u in Wset) ^ (v in Wset): col[i] = 1.0; any_edge = True
        if any_edge: cuts.append((frozenset(Wset), col))
    ncut = len(cuts)
    # LP vars: lam (ncut) >=0, r (ne) >=0 ; min sum r ; equality w = C lam + r
    nvar = ncut + ne
    c = np.concatenate([np.zeros(ncut), np.ones(ne)])
    A_eq = np.zeros((ne, nvar)); b_eq = w.copy()
    for j, (Wset, col) in enumerate(cuts): A_eq[:, j] = col
    for i in range(ne): A_eq[i, ncut+i] = 1.0
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)]*nvar, method="highs")
    if not res.success:
        print(f"   [cutcone] LP failed: {res.message}"); return
    lam = res.x[:ncut]; r = res.x[ncut:]
    resid = r.sum()
    used = [(sorted(cuts[j][0]), round(lam[j], 4)) for j in range(ncut) if lam[j] > 1e-6]
    used.sort(key=lambda t: -t[1])
    print(f"   [cutcone] residual outside cut cone = {resid:.6f} (0 => w in cut cone). #cuts used={len(used)}", flush=True)
    for u in used[:12]:
        print(f"      cut W={u[0]} lam={u[1]}", flush=True)
    # KEY equilibration check: for each used cut W, is e_M(W) == e_B(W) (tight CD = equilibrated)?
    return lam, r, cuts

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

if __name__ == "__main__":
    print("=== STRATEGY D: cut-cone decomposition of the optimal lemma-16 toll ===", flush=True)
    for (N, A, lab) in [(*c5n(1), "C5"), (*gpt_k23(), "K23-N13"), (*c5n(2), "C5[2]")]:
        info = lemma16_dual(N, A, lab)
        if info is not None:
            cutcone_decompose(info, lab)
        print(flush=True)
    print("DONE", flush=True)
