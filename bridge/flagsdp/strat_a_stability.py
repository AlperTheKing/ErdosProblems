"""STRATEGY A stability test for the Connected-B Gamma Lemma Gamma = sum_e (d_B(u,v)+1)^2 <= N^2.

STABILITY PREMISE TO TEST: graphs with Gamma/N^2 close to 1 are structurally close to C5[q].
Proxy for closeness: (a) most bad edges have ell=5; (b) the 5 B-distance shells from a bad-edge
endpoint are balanced (prod/amgm close to 1).  If Gamma/N^2 -> 1 forces both -> 1, the stability
premise of Strategy A holds.
"""
import itertools, numpy as np
from collections import deque
import flag_engine as fe

def adjset(N, A): return [set(v for v in range(N) if (A[u] >> v) & 1) for u in range(N)]

def maxcut(N, adj):
    best = -1; bs = None
    for m in range(1 << (N-1)):
        s = [(m >> u) & 1 for u in range(N)]
        c = sum(1 for u in range(N) for v in adj[u] if v > u and s[u] != s[v])
        if c > best: best = c; bs = s
    return best, bs

def gamma_and_stats(N, A):
    adj = adjset(N, A); mc, side = maxcut(N, adj)
    M = [(u, v) for u in range(N) for v in adj[u] if v > u and side[u] == side[v]]
    if not M: return None
    adjB = [set(v for v in adj[u] if side[u] != side[v]) for u in range(N)]
    G = 0.0; ells = []; shellbal = []
    for (u, v) in M:
        d = [-1]*N; d[u] = 0; q = deque([u])
        while q:
            x = q.popleft()
            for y in adjB[x]:
                if d[y] < 0: d[y] = d[x]+1; q.append(y)
        if d[v] < 0: return ('disc',)
        ell = d[v]+1; ells.append(ell); G += ell*ell
        shells = [sum(1 for w in range(N) if d[w] == i) for i in range(5)]
        if min(shells) > 0:
            prod = float(np.prod(shells)); amgm = (sum(shells)/5.0)**5
            shellbal.append(prod/amgm if amgm > 0 else 0.0)
    return G, N, ells, (float(np.mean(shellbal)) if shellbal else 0.0), len(M)

def c5n(k):
    N = 5*k; A = [0]*N; part = lambda v: v//k
    for u in range(N):
        for v in range(u+1, N):
            if (part(u)-part(v)) % 5 in (1, 4): A[u] |= 1 << v; A[v] |= 1 << u
    return N, A

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

def c5paths20():
    N = 20; A = [0]*N
    def add(a, b): A[a] |= 1 << b; A[b] |= 1 << a
    x = [0, 1, 2, 3, 4]
    for i in range(5): add(x[i], x[(i+1) % 5])
    nxt = 5
    for i in range(5):
        y, z, w = nxt, nxt+1, nxt+2; nxt += 3
        add(x[i], y); add(y, z); add(z, w); add(w, x[(i+1) % 5])
    return N, A

print("=== STRATEGY A stability: Gamma/N^2 vs C5[q]-proximity ===")
for (N, A, lab) in [(*c5n(1), "C5"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]"),
                    (*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*c5paths20(), "c5paths20")]:
    r = gamma_and_stats(N, A)
    if r is None or r[0] == 'disc': print(f"{lab}: skip"); continue
    G, n, ells, bal, m = r
    print(f"{lab:10s} N={n:3d} m={m:3d} Gamma={G:.0f} N^2={n*n} Gamma/N^2={G/(n*n):.4f} "
          f"mean-ell={np.mean(ells):.2f} shellbal(1=C5[q])={bal:.4f}")

print("--- exhaustive N<=9: does Gamma/N^2 -> 1 force shell-balance -> 1? ---")
hi = []
for N in [5, 6, 7, 8, 9]:
    rows = []
    for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
        r = gamma_and_stats(n, A)
        if r is None or r[0] == 'disc': continue
        G, nn, ells, bal, m = r
        rows.append((G/(nn*nn), bal, m, nn))
    if rows:
        rows.sort(reverse=True)
        top = rows[0]
        print(f"N={N}: max Gamma/N^2={top[0]:.4f} (m={top[2]}) shellbal={top[1]:.4f}; "
              f"#with Gamma/N^2>0.9: {sum(1 for x in rows if x[0] > 0.9)}")
        hi += [x for x in rows if x[0] > 0.95]
print(f"Graphs with Gamma/N^2>0.95: {len(hi)}; shell-balances: {sorted(set(round(x[1], 3) for x in hi))}")
