#!/usr/bin/env python3
"""AUDIT GPT's bridge answer (chat 6a3b5aba): route A density-sensitive concurrent-flow theorem.
Tests:
 (T)   tau <= (N/5) sqrt(nu*)   <=>   nu* >= 25 tau^2 / N^2     [THE bridge conjecture -- the gate]
 (Sep) |D_W| + e_M(W,~W) <= e_B(W,~W)  for all W  (separator averaging lemma; GPT PROVED it)
 (rho) rho(B,M) <= max{1, N^2/(25 m)}  (QFC25; rho via edge-MCF min-congestion LP)  + routing chain nu*>=m/kappa
 (Def) the exact fractional-deficit identity holds (numerically)
"""
import itertools, math
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def all_odd_cycles(N, adj, maxlen=None):
    if maxlen is None: maxlen = N
    seen = set(); out = []
    def dfs(start, u, path, ps):
        for w in adj[u]:
            if w == start and len(path) >= 3 and len(path) % 2 == 1:
                es = frozenset(frozenset((path[i], path[(i+1) % len(path)])) for i in range(len(path)))
                if es not in seen: seen.add(es); out.append((tuple(path), es))
            elif w not in ps and w > start and len(path) < maxlen:
                path.append(w); ps.add(w); dfs(start, w, path, ps); path.pop(); ps.discard(w)
    for s in range(N): dfs(s, s, [s], {s})
    return out

def maxcut(N, adj):
    best = -1; bs = None
    for mask in range(1 << (N-1)):
        side = [(mask >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and side[u] != side[v])
        if c > best: best = c; bs = side
    return best, bs

def nu_star_full(N, adj, edges):
    cyc = all_odd_cycles(N, adj)
    if not cyc: return 0.0, [], np.array([])
    eidx = {e: i for i, e in enumerate(edges)}; nC = len(cyc); nE = len(edges)
    Aub = np.zeros((nE, nC))
    for j, (_, es) in enumerate(cyc):
        for e in es: Aub[eidx[e], j] = 1.0
    res = linprog(-np.ones(nC), A_ub=Aub, b_ub=np.ones(nE), bounds=[(0, None)]*nC, method="highs")
    return -res.fun, cyc, res.x

def components_minusW(N, adjB, W):
    comp = {}; cid = 0
    for s in range(N):
        if s in W or s in comp: continue
        stack = [s]; comp[s] = cid
        while stack:
            u = stack.pop()
            for v in adjB[u]:
                if v not in W and v not in comp: comp[v] = cid; stack.append(v)
        cid += 1
    return comp

def test_T(instances):
    print("=== (T) tau <= (N/5) sqrt(nu*)  [gate] ===", flush=True)
    worst = 0.0; worst_inst = None; viol = 0
    for (N, A, label) in instances:
        adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
        if not edges: continue
        mc, side = maxcut(N, adj); tau = len(edges) - mc
        if tau == 0: continue
        nu, _, _ = nu_star_full(N, adj, edges)
        rhs = (N/5.0)*math.sqrt(nu)              # (T) bound on tau
        ratio = tau/rhs if rhs > 0 else 0
        if tau > rhs + 1e-7: viol += 1
        if ratio > worst: worst = ratio; worst_inst = (label, N, tau, nu, rhs)
        if label: print(f"  {label:18s} N={N:2d} tau={tau:3d} nu*={nu:7.3f} (N/5)sqrt(nu*)={rhs:7.3f} tau/rhs={ratio:.4f}", flush=True)
    print(f"  >>> worst tau/((N/5)sqrt(nu*)) = {worst:.4f}  viol={viol}  at {worst_inst}", flush=True)
    return worst, viol

def test_T_exhaustive(Ns):
    print("=== (T) exhaustive over all triangle-free graphs ===", flush=True)
    gworst = 0.0; gviol = 0
    for N in Ns:
        states = fe.enumerate_graphs(N, triangle_free=True); worst = 0.0; viol = 0
        for (n, A) in states:
            adj = adjset(n, A); edges = [frozenset((u, v)) for u in range(n) for v in adj[u] if v > u]
            if not edges: continue
            mc, side = maxcut(n, adj); tau = len(edges) - mc
            if tau == 0: continue
            nu, _, _ = nu_star_full(n, adj, edges)
            rhs = (n/5.0)*math.sqrt(nu); ratio = tau/rhs if rhs > 0 else 0
            if tau > rhs + 1e-7: viol += 1
            worst = max(worst, ratio)
        print(f"  N={N}: {len(states)} graphs, worst tau/rhs={worst:.4f}, (T) violations={viol}", flush=True)
        gworst = max(gworst, worst); gviol += viol
    print(f"  >>> overall worst={gworst:.4f}  total (T) violations={gviol}", flush=True)
    return gworst, gviol

def test_Sep(Ns):
    print("=== (Sep) |D_W| + e_M(W,~W) <= e_B(W,~W) for ALL W ===", flush=True)
    gviol = 0
    for N in Ns:
        states = fe.enumerate_graphs(N, triangle_free=True); viol = 0
        for (n, A) in states:
            adj = adjset(n, A); edges = [(u, v) for u in range(n) for v in adj[u] if v > u]
            if not edges: continue
            mc, side = maxcut(n, adj)
            M = [(u, v) for (u, v) in edges if side[u] == side[v]]
            Bset = [(u, v) for (u, v) in edges if side[u] != side[v]]
            adjB = [set() for _ in range(n)]
            for (u, v) in Bset: adjB[u].add(v); adjB[v].add(u)
            for wm in range(1 << n):
                W = set(u for u in range(n) if (wm >> u) & 1)
                comp = components_minusW(n, adjB, W)
                DW = sum(1 for (u, v) in M if u not in W and v not in W and comp.get(u, -1) != comp.get(v, -2))
                eMW = sum(1 for (u, v) in M if (u in W) != (v in W))
                eBW = sum(1 for (u, v) in Bset if (u in W) != (v in W))
                if DW + eMW > eBW: viol += 1
        print(f"  N={N}: {len(states)} graphs, (Sep) violations={viol}", flush=True)
        gviol += viol
    print(f"  >>> total (Sep) violations={gviol}", flush=True)
    return gviol

def rho_mcf(N, adjB, demands):
    """min-max congestion concurrent flow: route 1 unit per demand in B, min max undirected-edge load."""
    Bedges = sorted(set(frozenset((u, v)) for u in range(N) for v in adjB[u] if v > u), key=lambda e: tuple(sorted(e)))
    Be = [tuple(sorted(e)) for e in Bedges]; nB = len(Be); K = len(demands)
    # directed arcs
    arcs = []
    for (x, y) in Be: arcs.append((x, y)); arcs.append((y, x))
    nA = len(arcs); arc_idx = {a: i for i, a in enumerate(arcs)}
    # vars: f[k, a] for each demand k, arc a  (>=0), plus kappa
    nf = K*nA; nvar = nf + 1
    def fvar(k, ai): return k*nA + ai
    KAP = nf
    # objective: min kappa
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    # conservation: for each demand k, each vertex v: out - in = b (1 at src, -1 at sink, 0 else)
    for k, (s, t) in enumerate(demands):
        for v in range(N):
            row = np.zeros(nvar)
            for ai, (a, b) in enumerate(arcs):
                if a == v: row[fvar(k, ai)] += 1.0
                if b == v: row[fvar(k, ai)] -= 1.0
            A_eq.append(row); b_eq.append(1.0 if v == s else (-1.0 if v == t else 0.0))
    A_ub = []; b_ub = []
    # congestion: for each undirected B-edge, sum over demands of (both directions) <= kappa
    for ei, (x, y) in enumerate(Be):
        row = np.zeros(nvar)
        a1 = arc_idx[(x, y)]; a2 = arc_idx[(y, x)]
        for k in range(K): row[fvar(k, a1)] += 1.0; row[fvar(k, a2)] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nf + [(0, None)], method="highs")
    return res.fun

def test_rho(instances):
    print("=== (rho/QFC25) rho(B,M) <= max{1, N^2/(25 m)} + routing nu*>=m/kappa ===", flush=True)
    for (N, A, label) in instances:
        adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
        if not edges: continue
        mc, side = maxcut(N, adj)
        M = [tuple(sorted((u, v))) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
        adjB = [set() for _ in range(N)]
        for u in range(N):
            for v in adj[u]:
                if side[u] != side[v]: adjB[u].add(v)
        m = len(M)
        if m == 0: continue
        rho = rho_mcf(N, adjB, M)
        bound = max(1.0, N*N/(25.0*m))
        nu, _, _ = nu_star_full(N, adj, edges)
        kappa = max(1.0, rho)
        print(f"  {label:18s} N={N} m=tau={m} rho={rho:.4f} max(1,N^2/25m)={bound:.4f} OK={rho<=bound+1e-7} | "
              f"nu*={nu:.3f} m/kappa={m/kappa:.3f} nu*>=m/kappa={nu>=m/kappa-1e-6}", flush=True)

def test_Def(instances):
    print("=== (Def) exact fractional-deficit identity ===", flush=True)
    for (N, A, label) in instances:
        adj = adjset(N, A); edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
        if not edges: continue
        deg = [len(adj[u]) for u in range(N)]
        nu, cyc, y = nu_star_full(N, adj, edges)
        if nu <= 1e-9: continue
        # vertex sets per cycle
        vsets = []
        for (path, es) in cyc: vsets.append(set(path))
        lam = [0.0]*N; q = {e: 0.0 for e in edges}; L = 0.0
        for j, (path, es) in enumerate(cyc):
            w = y[j]
            if w < 1e-12: continue
            L += w*(len(path)-1)
            for v in set(path): lam[v] += w
            for e in es: q[e] += w
        t = L/nu
        a = [deg[v] - 2*lam[v] for v in range(N)]
        A_ = sum(a[v]*lam[v] for v in range(N))
        S_ = 0.0
        for j, (path, es) in enumerate(cyc):
            w = y[j]
            if w < 1e-12: continue
            sC = (N/2.0)*(len(path)-1) - sum(deg[v] for v in path)
            S_ += w*sC
        mean = (nu+L)/N
        Vv = sum((lam[v]-mean)**2 for v in range(N))
        lhs = N*N/25.0 - nu
        rhs = N*N*(t-4)*(4*t-1)/(100*(t+1)**2) + (N/(nu*(t+1)**2))*(Vv + (A_+S_)/2.0)
        print(f"  {label:18s} N={N} t={t:.3f} LHS(N^2/25-nu)={lhs:.5f} RHS={rhs:.5f} diff={abs(lhs-rhs):.2e}", flush=True)

def petersen():
    verts = list(itertools.combinations(range(5), 2)); A = [0]*10
    for i, a in enumerate(verts):
        for j, b in enumerate(verts):
            if i < j and not set(a) & set(b): A[i] |= 1 << j; A[j] |= 1 << i
    return 10, A

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

def gpt_k23():
    N = 13; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    for i in (0, 1):
        for j in (2, 3, 4): add(i, j)
    nxt = 5
    for (x, y) in [(0, 1), (2, 3), (2, 4), (3, 4)]:
        a, b = nxt, nxt+1; nxt += 2; add(x, a); add(a, b); add(b, y)
    return N, A

def c5paths20():
    N = 20; A = [0]*N
    def add(u, v): A[u] |= 1 << v; A[v] |= 1 << u
    x = lambda i: i % 5; y = lambda i: 5+(i % 5); z = lambda i: 10+(i % 5); w = lambda i: 15+(i % 5)
    for i in range(5):
        add(x(i), x(i+1)); add(x(i), y(i)); add(y(i), z(i)); add(z(i), w(i)); add(w(i), x(i+1))
    return N, A

if __name__ == "__main__":
    named = [(*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*c5paths20(), "C5paths-N20"),
             (*c5n(1), "C5[1]"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]")]
    wN, vN = test_T(named)
    wE, vE = test_T_exhaustive([5, 6, 7, 8, 9])
    sv = test_Sep([5, 6, 7, 8])
    test_rho(named)
    test_Def(named)
    print(f"\nSUMMARY: (T) worst ratio named={wN:.4f}/exhaustive={wE:.4f} viol={vN+vE}; (Sep) viol={sv}", flush=True)
    print("DONE", flush=True)
