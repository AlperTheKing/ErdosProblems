"""R9 odd-K5 round: exact library.

Everything on an acceptance path is Fraction / integer arithmetic.
Floats only ever steer a search (local-search max-cut lower bounds), never accepted.

Objects
-------
bip(G, w)          exact min weight of a monochromatic edge set over ALL 2^(n-1) cuts
Lambda(G, w)       exact optimum of the fractional odd-cycle covering LP
                   min sum w_e y_e  s.t.  y(C) >= 1 for every odd cycle C, y >= 0
                   returned with a two-sided rational certificate (cover y, packing z)
psi(H, x)          = bip(H, w) with w_uv = x_u x_v            (definition of the round)
LambdaX(H, x)      = Lambda(H, w) with w_uv = x_u x_v
"""
from fractions import Fraction as F
import heapq, itertools, sys

# ---------------------------------------------------------------- graph6

def g6_decode(s):
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:  # 63 == '~'-63 -> long form
        n = (data[1] << 12) + (data[2] << 6) + data[3]
        rest = data[4:]
    else:
        n = data[0]
        rest = data[1:]
    bits = []
    for d in rest:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges

def g6_encode(n, edges):
    E = set()
    for (a, b) in edges:
        E.add((min(a, b), max(a, b)))
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in E else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out

# ---------------------------------------------------------------- basic

class G:
    def __init__(self, n, edges):
        self.n = n
        self.E = sorted({(min(a, b), max(a, b)) for (a, b) in edges})
        self.adj = [[] for _ in range(n)]
        for (a, b) in self.E:
            self.adj[a].append(b)
            self.adj[b].append(a)
    @property
    def m(self):
        return len(self.E)
    def deg(self, v):
        return len(self.adj[v])
    def triangle_free(self):
        S = [set(a) for a in self.adj]
        for (a, b) in self.E:
            if S[a] & S[b]:
                return False
        return True
    def is_bipartite(self):
        col = [-1] * self.n
        for s in range(self.n):
            if col[s] >= 0:
                continue
            col[s] = 0
            st = [s]
            while st:
                v = st.pop()
                for u in self.adj[v]:
                    if col[u] < 0:
                        col[u] = 1 - col[v]
                        st.append(u)
                    elif col[u] == col[v]:
                        return False
        return True
    def g6(self):
        return g6_encode(self.n, self.E)

def Kn(n):
    return G(n, [(i, j) for i in range(n) for j in range(i + 1, n)])

def Cn(n):
    return G(n, [(i, (i + 1) % n) for i in range(n)])

def subdivide(g, k):
    """replace every edge by a path with k internal vertices (length k+1).
    Returns (H, pathlist) where pathlist[e] = list of edges of H forming the path of e."""
    n = g.n
    edges = []
    paths = []
    nxt = n
    for (a, b) in g.E:
        chain = [a]
        for _ in range(k):
            chain.append(nxt)
            nxt += 1
        chain.append(b)
        pe = [(chain[i], chain[i + 1]) for i in range(len(chain) - 1)]
        edges.extend(pe)
        paths.append(pe)
    return G(nxt, edges), paths

# ---------------------------------------------------------------- bip (exact)

def bip(g, w=None):
    """min over all bipartitions of the total weight of monochromatic edges.
    w: dict on normalised edges (a<b) -> Fraction/int.  Default 1 each."""
    n = g.n
    if w is None:
        w = {e: 1 for e in g.E}
    best = None
    idx = [(a, b, w[(a, b)]) for (a, b) in g.E]
    for mask in range(1 << (n - 1)):   # vertex 0 fixed to side 0
        M = mask << 1
        tot = 0
        for (a, b, c) in idx:
            if ((M >> a) & 1) == ((M >> b) & 1):
                tot += c
                if best is not None and tot >= best:
                    break
        else:
            if best is None or tot < best:
                best = tot
    return best

def prodw(g, x):
    return {(a, b): x[a] * x[b] for (a, b) in g.E}

def psi(g, x):
    return bip(g, prodw(g, x))

# ---------------------------------------------------------------- odd cycles

def min_odd_cycle(g, y):
    """exact minimum weight of an odd cycle, weights y (dict edge->Fraction>=0).
    Double cover + Dijkstra over Fractions.  Returns (value, cycle_edge_list) or (None,None)."""
    n = g.n
    INF = None
    best = None
    bestcyc = None
    for s in range(n):
        # dijkstra in the double cover from (s,0)
        dist = {}
        par = {}
        pq = [(F(0), s, 0)]
        dist[(s, 0)] = F(0)
        while pq:
            d, v, p = heapq.heappop(pq)
            if dist.get((v, p)) != d:
                continue
            if v == s and p == 1:
                break
            for u in g.adj[v]:
                if u < s:
                    continue  # canonical: cycles through the smallest-index vertex s
                e = (min(u, v), max(u, v))
                nd = d + y[e]
                key = (u, 1 - p)
                if key not in dist or nd < dist[key]:
                    dist[key] = nd
                    par[key] = (v, p)
                    heapq.heappush(pq, (nd, u, 1 - p))
        if (s, 1) in dist:
            d = dist[(s, 1)]
            if best is None or d < best:
                # walk back
                cyc = []
                cur = (s, 1)
                while cur != (s, 0):
                    pv = par[cur]
                    cyc.append((min(cur[0], pv[0]), max(cur[0], pv[0])))
                    cur = pv
                best = d
                bestcyc = cyc
    return best, bestcyc

def all_cycles(g, maxlen=None, only_odd=True):
    """enumerate all simple cycles (as sorted edge tuples).  Exponential; small graphs only."""
    n = g.n
    out = set()
    for s in range(n):
        # paths starting at s using only vertices >= s
        stack = [(s, [s], {s})]
        while stack:
            v, path, seen = stack.pop()
            for u in g.adj[v]:
                if u < s:
                    continue
                if u == s and len(path) >= 3:
                    if (not only_odd) or (len(path) % 2 == 1):
                        es = tuple(sorted((min(path[i], path[i + 1]), max(path[i], path[i + 1]))
                                          for i in range(len(path) - 1)) +
                                   [(min(path[-1], s), max(path[-1], s))])
                        out.add(tuple(sorted(es)))
                elif u not in seen:
                    if maxlen is None or len(path) < maxlen:
                        stack.append((u, path + [u], seen | {u}))
    return sorted(out)

# ---------------------------------------------------------------- exact simplex

def simplex_max(Amat, b, c):
    """max c.x s.t. A x <= b, x >= 0, with b >= 0.  Exact Fractions, Bland's rule.
    Returns (value, x, dualy)."""
    m = len(Amat)
    n = len(c)
    # tableau: rows 0..m-1 constraints, last row objective
    T = [[F(Amat[i][j]) for j in range(n)] + [F(1) if k == i else F(0) for k in range(m)] + [F(b[i])]
         for i in range(m)]
    obj = [-F(c[j]) for j in range(n)] + [F(0)] * m + [F(0)]
    basis = [n + i for i in range(m)]
    while True:
        piv = -1
        for j in range(n + m):
            if obj[j] < 0:
                piv = j
                break
        if piv < 0:
            break
        ratio = None
        row = -1
        for i in range(m):
            if T[i][piv] > 0:
                r = T[i][-1] / T[i][piv]
                if ratio is None or r < ratio or (r == ratio and basis[i] < basis[row]):
                    ratio = r
                    row = i
        if row < 0:
            raise RuntimeError("unbounded")
        pv = T[row][piv]
        T[row] = [z / pv for z in T[row]]
        for i in range(m):
            if i != row and T[i][piv] != 0:
                f = T[i][piv]
                T[i] = [T[i][k] - f * T[row][k] for k in range(n + m + 1)]
        if obj[piv] != 0:
            f = obj[piv]
            obj = [obj[k] - f * T[row][k] for k in range(n + m + 1)]
        basis[row] = piv
    x = [F(0)] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = T[i][-1]
    dual = [obj[n + i] for i in range(m)]
    return obj[-1], x, dual

# ---------------------------------------------------------------- Lambda (exact LP)

def Lambda(g, w=None, verbose=False):
    """exact fractional odd-cycle cover optimum with a two-sided certificate.
    Row generation: dual LP  max 1.z  s.t.  sum_{C ni e} z_C <= w_e,  z >= 0.
    Returns dict(value, y (cover), z (packing on the generated cycles), cycles)."""
    if w is None:
        w = {e: F(1) for e in g.E}
    w = {e: F(w[e]) for e in w}
    if g.is_bipartite():
        return dict(value=F(0), y={e: F(0) for e in g.E}, z={}, cycles=[])
    edges = g.E
    eidx = {e: i for i, e in enumerate(edges)}
    cycles = []
    # seed with one minimum odd cycle under unit weights
    v0, c0 = min_odd_cycle(g, {e: F(1) for e in edges})
    cycles.append(tuple(sorted(c0)))
    while True:
        # dual LP: variables z_C, constraints per edge
        A = [[F(1) if edges[i] in set(C) else F(0) for C in cycles] for i in range(len(edges))]
        b = [w[e] for e in edges]
        c = [F(1)] * len(cycles)
        val, z, dual = simplex_max(A, b, c)
        y = {edges[i]: dual[i] for i in range(len(edges))}
        mv, mc = min_odd_cycle(g, y)
        if verbose:
            print("  rows", len(cycles), "val", val, "sep", mv)
        if mv >= 1:
            return dict(value=val, y=y, z={cycles[k]: z[k] for k in range(len(cycles)) if z[k] != 0},
                        cycles=cycles)
        t = tuple(sorted(mc))
        if t in set(cycles):
            raise RuntimeError("separation returned a repeated cycle")
        cycles.append(t)

def LambdaX(g, x):
    return Lambda(g, prodw(g, x))

def verify_Lambda(g, res, w=None):
    """independent exact check: y covers every odd cycle (via the exact oracle),
    z is a feasible packing, and the two values agree."""
    if w is None:
        w = {e: F(1) for e in g.E}
    y = res['y']
    for e in g.E:
        assert y[e] >= 0, "negative cover"
    mv, _ = min_odd_cycle(g, y)
    if mv is not None:
        assert mv >= 1, f"cover infeasible, min odd cycle {mv}"
    cost = sum(F(w[e]) * y[e] for e in g.E)
    load = {e: F(0) for e in g.E}
    for C, zc in res['z'].items():
        assert zc >= 0
        for e in C:
            load[e] += zc
    for e in g.E:
        assert load[e] <= F(w[e]), f"packing overloads {e}"
    pval = sum(res['z'].values())
    assert cost == pval == res['value'], (cost, pval, res['value'])
    return True

# ---------------------------------------------------------------- misc

def odd_girth(g):
    best = None
    for s in range(g.n):
        dist = [[-1, -1] for _ in range(g.n)]
        dist[s][0] = 0
        dq = [(s, 0)]
        while dq:
            nxt = []
            for (v, p) in dq:
                for u in g.adj[v]:
                    if dist[u][1 - p] < 0:
                        dist[u][1 - p] = dist[v][p] + 1
                        nxt.append((u, 1 - p))
                    elif u == s and 1 - p == 1:
                        pass
            dq = nxt
        if dist[s][1] > 0:
            if best is None or dist[s][1] < best:
                best = dist[s][1]
    return best

def maxcut_local(g, iters=200, seed=1):
    """float-free-ish local search giving a LOWER bound on maxcut (hence an UPPER bound on bip).
    Only ever used as a lower bound on maxcut, which is verified exactly by counting."""
    import random
    rnd = random.Random(seed)
    n = g.n
    best = -1
    bestS = None
    for it in range(iters):
        side = [rnd.randint(0, 1) for _ in range(n)]
        improved = True
        while improved:
            improved = False
            order = list(range(n))
            rnd.shuffle(order)
            for v in order:
                same = sum(1 for u in g.adj[v] if side[u] == side[v])
                diff = g.deg(v) - same
                if same > diff:
                    side[v] ^= 1
                    improved = True
        cut = sum(1 for (a, b) in g.E if side[a] != side[b])
        if cut > best:
            best = cut
            bestS = side[:]
    return best, bestS

def cut_value(g, side):
    return sum(1 for (a, b) in g.E if side[a] != side[b])
