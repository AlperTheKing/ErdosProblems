# Exact tools for LP/polyhedral lens on Erdos #23 (beta <= N^2/25, triangle-free).
# All arithmetic integer/Fraction. No floats anywhere.
import numpy as np
from fractions import Fraction
import random

# ---------- basic graph utils ----------
def edges_to_adj(n, edges):
    adj = [0]*n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj

def is_triangle_free(n, edges):
    adj = edges_to_adj(n, edges)
    return all((adj[u] & adj[v]) == 0 for u, v in edges)

def is_bipartite(n, edges):
    adj = edges_to_adj(n, edges)
    color = [-1]*n
    for s in range(n):
        if color[s] < 0:
            color[s] = 0
            stack = [s]
            while stack:
                x = stack.pop()
                m = adj[x]
                while m:
                    b = m & -m
                    y = b.bit_length() - 1
                    m ^= b
                    if color[y] < 0:
                        color[y] = color[x] ^ 1
                        stack.append(y)
                    elif color[y] == color[x]:
                        return False
    return True

def min_degree(n, edges):
    d = [0]*n
    for u, v in edges:
        d[u] += 1; d[v] += 1
    return min(d) if n else 0

# ---------- exact beta via full cut enumeration (vertex n-1 fixed) ----------
def beta_exact(n, edges):
    E = len(edges)
    total = 1 << (n - 1)
    best = E + 1
    bestS = 0
    CH = 1 << 20
    for start in range(0, total, CH):
        S = np.arange(start, min(start + CH, total), dtype=np.uint32)
        acc = np.zeros(S.shape, dtype=np.uint16)
        for u, v in edges:
            acc += (((S >> np.uint32(u)) & 1) == ((S >> np.uint32(v)) & 1))
        i = int(acc.argmin())
        if int(acc[i]) < best:
            best = int(acc[i]); bestS = int(S[i])
    return best, bestS

def uncut_of(n, edges, S):
    return sum(1 for u, v in edges if ((S >> u) & 1) == ((S >> v) & 1))

# ---------- F2 column space of adjacency matrix; min uncut over image cuts ----------
def f2_column_basis(n, edges):
    adj = edges_to_adj(n, edges)
    basis = {}
    for vec in adj:
        x = vec
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return list(basis.values())

def _span_reduce(vecs):
    basis = {}
    for vec in vecs:
        x = vec
        while x:
            h = x.bit_length() - 1
            if h in basis:
                x ^= basis[h]
            else:
                basis[h] = x
                break
    return list(basis.values())

def _min_uncut_span(n, edges, cols, rank_cap=22, shifts=(0,)):
    bs = _span_reduce(cols)
    if len(bs) > rank_cap:
        return None, None, len(bs)
    arr = np.zeros(1, dtype=np.uint64)
    for b in bs:
        arr = np.concatenate([arr, arr ^ np.uint64(b)])
    best = len(edges) + 1
    bestS = 0
    for sh in shifts:
        a2 = arr ^ np.uint64(sh)
        acc = np.zeros(a2.shape, dtype=np.uint16)
        for u, v in edges:
            acc += (((a2 >> np.uint64(u)) & np.uint64(1)) == ((a2 >> np.uint64(v)) & np.uint64(1)))
        i = int(acc.argmin())
        if int(acc[i]) < best:
            best = int(acc[i]); bestS = int(a2[i])
    return best, bestS, len(bs)

def min_uncut_over_image(n, edges, rank_cap=22):
    """min uncut over im(A) only (legacy)."""
    adj = edges_to_adj(n, edges)
    m, S, rk = _min_uncut_span(n, edges, adj, rank_cap)
    if m is None:
        raise ValueError("rank too large: %d" % rk)
    return m, S, rk

def min_uncut_union_family(n, edges, rank_cap=22):
    """min uncut over F(G) = im(A) union im(A+I). Returns (min, argS, rankA, rankAI, minA, minAI)."""
    adj = edges_to_adj(n, edges)
    closed = [adj[u] ^ (1 << u) for u in range(n)]
    mA, SA, rkA = _min_uncut_span(n, edges, adj, rank_cap)
    mI, SI, rkI = _min_uncut_span(n, edges, closed, rank_cap)
    cands = [(m, S) for m, S in [(mA, SA), (mI, SI)] if m is not None]
    if not cands:
        return None, None, rkA, rkI, mA, mI
    m, S = min(cands)
    return m, S, rkA, rkI, mA, mI

# ---------- graph constructors ----------
def cycle(k):
    return k, [(i, (i + 1) % k) for i in range(k)]

def blowup(bn, bedges, sizes):
    offs = [0]
    for s in sizes:
        offs.append(offs[-1] + s)
    n = offs[-1]
    edges = []
    for u, v in bedges:
        for a in range(offs[u], offs[u + 1]):
            for b in range(offs[v], offs[v + 1]):
                edges.append((min(a, b), max(a, b)))
    return n, edges

def petersen():
    edges = [(i, (i + 1) % 5) for i in range(5)]
    edges += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    edges += [(i, 5 + i) for i in range(5)]
    return 10, [(min(u, v), max(u, v)) for u, v in edges]

def gen_petersen(k, step):
    edges = [(i, (i + 1) % k) for i in range(k)]
    edges += [(k + i, k + (i + step) % k) for i in range(k)]
    edges += [(i, k + i) for i in range(k)]
    ded = set((min(u, v), max(u, v)) for u, v in edges)
    return 2 * k, sorted(ded)

def wagner():  # V8 = Andrasfai(3): C8 + diameters
    edges = [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]
    return 8, [(min(u, v), max(u, v)) for u, v in edges]

def circulant(k, conn):
    ded = set()
    for i in range(k):
        for s in conn:
            ded.add((min(i, (i + s) % k), max(i, (i + s) % k)))
    return k, sorted(ded)

def clebsch():
    # F2^4 Cayley graph, connection set = {e1,e2,e3,e4, 1111}
    C = [1, 2, 4, 8, 15]
    ded = set()
    for x in range(16):
        for c in C:
            y = x ^ c
            ded.add((min(x, y), max(x, y)))
    return 16, sorted(ded)

def mycielski(n, edges):
    # vertices 0..n-1 orig, n..2n-1 copies, 2n apex
    E = list(edges)
    for u, v in edges:
        E.append((min(u, n + v), max(u, n + v)))
        E.append((min(v, n + u), max(v, n + u)))
    for i in range(n):
        E.append((n + i, 2 * n))
    return 2 * n + 1, sorted(set(E))

def prism_c5():  # C5 x K2 cartesian
    edges = [(i, (i + 1) % 5) for i in range(5)]
    edges += [(5 + i, 5 + (i + 1) % 5) for i in range(5)]
    edges += [(i, 5 + i) for i in range(5)]
    return 10, [(min(u, v), max(u, v)) for u, v in edges]

def random_maximal_trianglefree(n, seed, force_c5=True):
    rng = random.Random(seed)
    edges = set()
    adj = [0]*n
    def add(u, v):
        edges.add((min(u, v), max(u, v)))
        adj[u] |= 1 << v; adj[v] |= 1 << u
    if force_c5:
        for i in range(5):
            add(i, (i + 1) % 5)
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(pairs)
    for u, v in pairs:
        if (u, v) in edges:
            continue
        if adj[u] & adj[v]:
            continue
        add(u, v)
    return n, sorted(edges)

def random_trianglefree_sparse(n, m, seed):
    rng = random.Random(seed)
    edges = set(); adj = [0]*n
    tries = 0
    while len(edges) < m and tries < 100000:
        tries += 1
        u = rng.randrange(n); v = rng.randrange(n)
        if u == v: continue
        a, b = min(u, v), max(u, v)
        if (a, b) in edges: continue
        if adj[u] & adj[v]: continue
        edges.add((a, b)); adj[u] |= 1 << v; adj[v] |= 1 << u
    return n, sorted(edges)

# ---------- odd cycle enumeration (small graphs) ----------
def hoffman_singleton():
    # P_h pentagons (h,j): j~j+-1 ; Q_i pentagrams (i,k): k~k+-2 ; P(h,j)~Q(i,k) iff k = h*i + j mod 5
    def P(h, j): return 5 * h + j
    def Q(i, k): return 25 + 5 * i + k
    E = set()
    for h in range(5):
        for j in range(5):
            E.add(tuple(sorted((P(h, j), P(h, (j + 1) % 5)))))
    for i in range(5):
        for k in range(5):
            E.add(tuple(sorted((Q(i, k), Q(i, (k + 2) % 5)))))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.add(tuple(sorted((P(h, j), Q(i, (h * i + j) % 5)))))
    return 50, sorted(E)

def kneser73():
    from itertools import combinations
    verts = list(combinations(range(7), 3))
    idx = {v: i for i, v in enumerate(verts)}
    E = []
    for a in range(len(verts)):
        for b in range(a + 1, len(verts)):
            if not set(verts[a]) & set(verts[b]):
                E.append((a, b))
    return 35, E

def all_odd_cycles(n, edges, maxlen=None):
    adjL = [[] for _ in range(n)]
    for u, v in edges:
        adjL[u].append(v); adjL[v].append(u)
    if maxlen is None:
        maxlen = n
    cycles = set()
    def dfs(start, cur, visited, path):
        for nxt in adjL[cur]:
            if nxt == start and len(path) >= 3:
                if len(path) % 2 == 1:
                    es = frozenset((min(path[i], path[(i + 1) % len(path)]),
                                    max(path[i], path[(i + 1) % len(path)])) for i in range(len(path)))
                    cycles.add(es)
            elif nxt > start and not (visited >> nxt) & 1 and len(path) < maxlen:
                dfs(start, nxt, visited | (1 << nxt), path + [nxt])
    for s in range(n):
        dfs(s, s, 1 << s, [s])
    return [sorted(c) for c in cycles]
