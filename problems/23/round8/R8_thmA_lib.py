"""
R8_thmA_lib.py -- exact tooling for auditing "Theorem A".

THEOREM A (claim under audit): for every triangle-free graph G and every x >= 0
on V(G) with sum_v x_v = 1,
        Lambda(G,x) := tau*_w  <=  1/25,
where w_uv = x_u*x_v and tau*_w is the value of the LP

        min  sum_e w_e y_e
        s.t. sum_{e in C} y_e >= 1  for every ODD cycle C of G,   y >= 0.

Its LP dual is the maximum fractional odd-cycle packing

        max  sum_C z_C
        s.t. sum_{C ni e} z_C <= w_e  for every edge e,            z >= 0.

Everything on an acceptance path is exact rational arithmetic (fractions.Fraction).

Key facts used (proved in R8_thmA_audit.md):
  * y is feasible  <=>  in the bipartite double cover of G with edge lengths y,
    dist((v,0),(v,1)) >= 1 for every vertex v.  This gives an EXACT separation
    oracle that never enumerates cycles, hence is immune to the
    "missing Hamiltonian odd cycles" enumeration bug.
"""

from fractions import Fraction
import heapq
import itertools
import random


# ----------------------------------------------------------------------------
# graphs
# ----------------------------------------------------------------------------

class Graph:
    def __init__(self, n, edges):
        self.n = n
        es = set()
        for (u, v) in edges:
            if u == v:
                raise ValueError("loop")
            es.add((min(u, v), max(u, v)))
        self.edges = sorted(es)
        self.eidx = {e: i for i, e in enumerate(self.edges)}
        self.adj = [set() for _ in range(n)]
        for (u, v) in self.edges:
            self.adj[u].add(v)
            self.adj[v].add(u)
        self.m = len(self.edges)

    def has_triangle(self):
        for (u, v) in self.edges:
            if self.adj[u] & self.adj[v]:
                return True
        return False

    def is_bipartite(self):
        color = [None] * self.n
        for s in range(self.n):
            if color[s] is not None:
                continue
            color[s] = 0
            stack = [s]
            while stack:
                u = stack.pop()
                for v in self.adj[u]:
                    if color[v] is None:
                        color[v] = 1 - color[u]
                        stack.append(v)
                    elif color[v] == color[u]:
                        return False
        return True

    def subgraph(self, keep):
        """induced subgraph on sorted list `keep`; returns (Graph, index map)"""
        idx = {v: i for i, v in enumerate(keep)}
        es = [(idx[u], idx[v]) for (u, v) in self.edges if u in idx and v in idx]
        return Graph(len(keep), es), idx

    def odd_girth(self):
        """length of shortest odd cycle (None if bipartite). BFS based."""
        best = None
        for s in range(self.n):
            dist = [None] * self.n
            dist[s] = 0
            q = [s]
            while q:
                nq = []
                for u in q:
                    for v in self.adj[u]:
                        if dist[v] is None:
                            dist[v] = dist[u] + 1
                            nq.append(v)
                        elif dist[v] == dist[u]:
                            cand = dist[u] + dist[v] + 1
                            if best is None or cand < best:
                                best = cand
                q = nq
        return best

    def graph6(self):
        n = self.n
        assert 0 < n < 63
        bits = []
        for j in range(1, n):
            for i in range(j):
                bits.append(1 if (i, j) in self.eidx else 0)
        while len(bits) % 6:
            bits.append(0)
        out = chr(n + 63)
        for k in range(0, len(bits), 6):
            val = 0
            for b in bits[k:k + 6]:
                val = 2 * val + b
            out += chr(val + 63)
        return out


# ----------------------------------------------------------------------------
# cycle enumeration (used ONLY for cross-checks; the LP never relies on it)
# ----------------------------------------------------------------------------

def all_cycles(g):
    """All simple cycles as vertex lists, each cycle exactly once.

    Cycle is rooted at its minimum vertex s and oriented so that the second
    vertex is smaller than the last one.  Includes Hamiltonian cycles.
    """
    out = []
    adj = [sorted(a) for a in g.adj]
    for s in range(g.n):
        path = [s]
        used = [False] * g.n
        used[s] = True

        def dfs():
            last = path[-1]
            for w in adj[last]:
                if w < s:
                    continue
                if w == s:
                    if len(path) >= 3 and path[1] < path[-1]:
                        out.append(list(path))
                elif not used[w]:
                    used[w] = True
                    path.append(w)
                    dfs()
                    path.pop()
                    used[w] = False

        dfs()
    return out


def all_odd_cycles(g):
    return [c for c in all_cycles(g) if len(c) % 2 == 1]


def cycle_edges(cyc):
    L = len(cyc)
    return [(min(cyc[i], cyc[(i + 1) % L]), max(cyc[i], cyc[(i + 1) % L]))
            for i in range(L)]


# ----------------------------------------------------------------------------
# exact separation: shortest odd cycle under nonnegative edge lengths y
# ----------------------------------------------------------------------------

def shortest_odd_cycle(g, y, limit=None):
    """y: list of lengths (Fraction or float) indexed like g.edges, y >= 0.

    Returns (length, cycle_as_vertex_list) of a MINIMUM y-length odd cycle, or
    (None, None) if G has no odd cycle.  If `limit` is given, may return early
    with any odd cycle of length < limit (still exact about the value found).

    Method: Dijkstra in the bipartite double cover from (s,0) to (s,1) for every
    s; the resulting closed odd walk is contracted to a simple odd cycle of no
    larger y-length.  No cycle enumeration involved.
    """
    n = g.n
    inc = [[] for _ in range(n)]           # v -> list of (u, edge index)
    for i, (u, v) in enumerate(g.edges):
        inc[u].append((v, i))
        inc[v].append((u, i))

    zero = y[0] * 0 if g.m else 0
    best = None
    best_cyc = None
    for s in range(n):
        # nodes are 2*v + parity
        dist = [None] * (2 * n)
        par = [None] * (2 * n)
        dist[2 * s] = zero
        pq = [(dist[2 * s], 2 * s)]
        target = 2 * s + 1
        while pq:
            d, node = heapq.heappop(pq)
            if dist[node] is None or d > dist[node]:
                continue
            if node == target:
                break
            v, p = divmod(node, 2)
            for (u, ei) in inc[v]:
                nd = d + y[ei]
                nnode = 2 * u + (1 - p)
                if dist[nnode] is None or nd < dist[nnode]:
                    dist[nnode] = nd
                    par[nnode] = (node, ei)
                    heapq.heappush(pq, (nd, nnode))
        if dist[target] is None:
            continue
        if best is not None and dist[target] >= best:
            continue
        # rebuild walk
        walk = []
        node = target
        while node != 2 * s:
            pnode, ei = par[node]
            walk.append(node // 2)
            node = pnode
        walk.append(s)
        walk.reverse()          # v_0 = s ... v_L = s  (closed odd walk)
        cyc = _extract_odd_cycle(walk)
        L = sum(y[g.eidx[e]] for e in cycle_edges(cyc))
        assert L <= dist[target], (L, dist[target])
        if best is None or L < best:
            best = L
            best_cyc = cyc
            if limit is not None and best < limit:
                return best, best_cyc
    return best, best_cyc


def _extract_odd_cycle(walk):
    """walk[0] == walk[-1], odd number of steps -> simple odd cycle (vertices)."""
    stack = []
    pos = {}
    for v in walk[:-1] + [walk[0]]:
        if v in pos:
            j = pos[v]
            seg = stack[j:]
            if len(seg) % 2 == 1:
                return seg
            for u in seg[1:]:
                del pos[u]
            del stack[j + 1:]
        else:
            pos[v] = len(stack)
            stack.append(v)
    raise AssertionError("no odd cycle extracted")


# ----------------------------------------------------------------------------
# exact simplex:  max c^T z  s.t.  A z <= b,  z >= 0,  with b >= 0
# ----------------------------------------------------------------------------

def simplex_max(A, b, c):
    """A: m x n list of lists of Fraction; b: m Fractions >= 0; c: n Fractions.

    Returns (value, z, u) with u the optimal dual (u >= 0, A^T u >= c).
    Bland's rule, so no cycling.
    """
    m = len(b)
    n = len(c)
    # tableau rows: [A | I | b], last row [-c | 0 | 0]
    T = [list(A[i]) + [Fraction(1) if j == i else Fraction(0) for j in range(m)] + [b[i]]
         for i in range(m)]
    T.append([-ci for ci in c] + [Fraction(0)] * m + [Fraction(0)])
    basis = [n + i for i in range(m)]
    total = n + m
    it = 0
    while True:
        it += 1
        if it > 200000:
            raise RuntimeError("simplex iteration limit")
        col = -1
        for j in range(total):
            if T[m][j] < 0:
                col = j
                break
        if col < 0:
            break
        row = -1
        bestratio = None
        for i in range(m):
            if T[i][col] > 0:
                r = T[i][total] / T[i][col]
                if bestratio is None or r < bestratio or (r == bestratio and basis[i] < basis[row]):
                    bestratio = r
                    row = i
        if row < 0:
            raise RuntimeError("unbounded LP")
        piv = T[row][col]
        T[row] = [t / piv for t in T[row]]
        for i in range(m + 1):
            if i != row and T[i][col] != 0:
                f = T[i][col]
                Ti, Tr = T[i], T[row]
                T[i] = [Ti[j] - f * Tr[j] for j in range(total + 1)]
        basis[row] = col
    z = [Fraction(0)] * n
    for i in range(m):
        if basis[i] < n:
            z[basis[i]] = T[i][total]
    u = [T[m][n + i] for i in range(m)]
    val = T[m][total]
    return val, z, u


# ----------------------------------------------------------------------------
# exact Lambda(G,x) by cutting planes + exact certificates
# ----------------------------------------------------------------------------

class LambdaResult:
    def __init__(self, value, y, z, cycles, g, w):
        self.value = value      # Fraction, exact
        self.y = y              # optimal fractional cover (Fractions), on g.edges
        self.z = z              # optimal fractional packing (Fractions), on cycles
        self.cycles = cycles
        self.g = g
        self.w = w

    def verify(self):
        """Full independent exact verification of optimality. Returns dict."""
        g, y, z, w = self.g, self.y, self.z, self.w
        # primal feasibility: every odd cycle has y-length >= 1
        L, cyc = shortest_odd_cycle(g, y)
        prim_ok = (L is None) or (L >= 1)
        prim_val = sum(w[i] * y[i] for i in range(g.m))
        # dual feasibility: capacities
        load = [Fraction(0)] * g.m
        for zc, C in zip(z, self.cycles):
            if zc:
                for e in cycle_edges(C):
                    load[g.eidx[e]] += zc
        dual_ok = all(load[i] <= w[i] for i in range(g.m))
        dual_val = sum(z)
        return {
            "primal_feasible": prim_ok,
            "primal_value": prim_val,
            "dual_feasible": dual_ok,
            "dual_value": dual_val,
            "match": prim_val == dual_val,
            "value": self.value,
            "shortest_odd_cycle_len": L,
        }


def exact_lambda(g, x, seed_cycles=None, verbose=False):
    """x: list of Fraction >= 0 (need not sum to 1; caller normalises).

    Returns LambdaResult with exact optimal value.  Vertices of weight 0 and the
    edges they carry are removed first (they have w_e = 0, i.e. free to cover).
    """
    keep = [v for v in range(g.n) if x[v] > 0]
    h, idx = g.subgraph(keep)
    xs = [x[v] for v in keep]
    w = [Fraction(0)] * h.m
    for i, (u, v) in enumerate(h.edges):
        w[i] = xs[u] * xs[v]
    if h.is_bipartite():
        return LambdaResult(Fraction(0), [Fraction(0)] * h.m, [], [], h, w)

    cycles = []
    seen = set()

    def add_cycle(C):
        key = frozenset(cycle_edges(C))
        if key in seen:
            return False
        seen.add(key)
        cycles.append(C)
        return True

    if seed_cycles:
        for C in seed_cycles:
            Cm = [idx[v] for v in C if v in idx]
            if len(Cm) == len(C):
                add_cycle(Cm)
    if not cycles:
        L, C = shortest_odd_cycle(h, [Fraction(0)] * h.m)
        add_cycle(C)

    while True:
        A = [[Fraction(0)] * len(cycles) for _ in range(h.m)]
        for j, C in enumerate(cycles):
            for e in cycle_edges(C):
                A[h.eidx[e]][j] = Fraction(1)
        c = [Fraction(1)] * len(cycles)
        val, z, u = simplex_max(A, w, c)
        # u is the fractional cover y
        L, C = shortest_odd_cycle(h, u)
        if verbose:
            print("  cutting plane: |cycles|=%d val=%s shortest=%s" % (len(cycles), val, L))
        if L is None or L >= 1:
            return LambdaResult(val, u, z, cycles, h, w)
        if not add_cycle(C):
            raise RuntimeError("separation returned a known cycle; stalled")


# ----------------------------------------------------------------------------
# psi(G,x) = exact min monochromatic weight over cuts (brute force)
# ----------------------------------------------------------------------------

def exact_psi(g, x):
    best = None
    bestS = None
    for mask in range(1 << (g.n - 1)):
        tot = Fraction(0)
        for (u, v) in g.edges:
            bu = (mask >> u) & 1 if u < g.n - 1 else 0
            bv = (mask >> v) & 1 if v < g.n - 1 else 0
            if bu == bv:
                tot += x[u] * x[v]
                if best is not None and tot > best:
                    break
        else:
            if best is None or tot < best:
                best = tot
                bestS = mask
    return best, bestS


# ----------------------------------------------------------------------------
# float fast path (search only; never an acceptance path)
# ----------------------------------------------------------------------------

def float_lambda(g, x, cycles=None, tol=1e-12):
    """Fast float LP value of Lambda via cutting planes (scipy/HiGHS)."""
    import numpy as np
    from scipy.optimize import linprog
    w = np.array([x[u] * x[v] for (u, v) in g.edges], dtype=float)
    if cycles is None:
        cycles = []
    rows = []
    for C in cycles:
        r = np.zeros(g.m)
        for e in cycle_edges(C):
            r[g.eidx[e]] = 1.0
        rows.append(r)
    if not rows:
        L, C = shortest_odd_cycle(g, [0.0] * g.m)
        if C is None:
            return 0.0, [], None
        r = np.zeros(g.m)
        for e in cycle_edges(C):
            r[g.eidx[e]] = 1.0
        rows.append(r)
        cycles = [C]
    used = set(frozenset(cycle_edges(C)) for C in cycles)
    for _ in range(4000):
        A = -np.array(rows)
        b = -np.ones(len(rows))
        res = linprog(w, A_ub=A, b_ub=b, bounds=[(0, None)] * g.m, method="highs")
        if not res.success:
            raise RuntimeError("float LP failed: " + str(res.message))
        y = np.maximum(res.x, 0.0)
        L, C = shortest_odd_cycle(g, list(y))
        if L is None or L >= 1 - 1e-9:
            return float(res.fun), cycles, y
        key = frozenset(cycle_edges(C))
        if key in used:
            return float(res.fun), cycles, y
        used.add(key)
        cycles = cycles + [C]
        r = np.zeros(g.m)
        for e in cycle_edges(C):
            r[g.eidx[e]] = 1.0
        rows.append(r)
    raise RuntimeError("cutting plane did not converge")


# ----------------------------------------------------------------------------
# graph library
# ----------------------------------------------------------------------------

def cycle_graph(n):
    return Graph(n, [(i, (i + 1) % n) for i in range(n)])


def blowup_C5(sizes):
    parts = []
    k = 0
    for s in sizes:
        parts.append(list(range(k, k + s)))
        k += s
    edges = []
    for i in range(5):
        for u in parts[i]:
            for v in parts[(i + 1) % 5]:
                edges.append((u, v))
    return Graph(k, edges), parts


def petersen():
    edges = [(i, (i + 1) % 5) for i in range(5)]
    edges += [(i, i + 5) for i in range(5)]
    edges += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return Graph(10, edges)


def grotzsch():
    # Mycielskian of C5: vertices 0..4 = C5, 5..9 = shadows, 10 = apex
    edges = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        edges.append((5 + i, (i + 1) % 5))
        edges.append((5 + i, (i - 1) % 5))
        edges.append((10, 5 + i))
    return Graph(11, edges)


def circle_graph(n, m):
    """u ~ v iff 3*circdist(u,v) > m.  Andrasfai-type circulant."""
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            d = min(v - u, n - (v - u))
            if 3 * d > m:
                edges.append((u, v))
    return Graph(n, edges)


def andrasfai(k):
    """And(k) = circulant on 3k-1 vertices, u~v iff |u-v| = 1 mod 3 (circulant
    C_{3k-1}(1,4,7,...)).  And(2) = C5, And(3) = Moebius-Kantor/Wagner-like."""
    n = 3 * k - 1
    conn = [j for j in range(1, n // 2 + 1) if j % 3 == 1]
    edges = []
    for u in range(n):
        for j in conn:
            v = (u + j) % n
            if u != v:
                edges.append((min(u, v), max(u, v)))
    return Graph(n, edges)


def wagner():
    """Wagner graph / Moebius-Kantor V8: circle graph on 8 with 3*d > 8."""
    return circle_graph(8, 8)


def mycielskian(g):
    n = g.n
    edges = list(g.edges)
    for (u, v) in g.edges:
        edges.append((u, n + v))
        edges.append((v, n + u))
    for i in range(n):
        edges.append((n + i, 2 * n))
    return Graph(2 * n + 1, edges)


def kneser(n, k):
    sets = list(itertools.combinations(range(n), k))
    idx = {s: i for i, s in enumerate(sets)}
    edges = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            if not (set(sets[i]) & set(sets[j])):
                edges.append((i, j))
    return Graph(len(sets), edges)


def random_maximal_triangle_free(n, rng):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    adj = [set() for _ in range(n)]
    edges = []
    for (u, v) in pairs:
        if adj[u] & adj[v]:
            continue
        adj[u].add(v)
        adj[v].add(u)
        edges.append((u, v))
    return Graph(n, edges)


def canon_key(g):
    """cheap isomorphism key (degree-refinement based); collisions possible."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(g.n))
    G.add_edges_from(g.edges)
    return nx.weisfeiler_lehman_graph_hash(G, iterations=4)
