"""G12 core: exact odd-cycle edge packing / covering (transversal) machinery.

All acceptance-path arithmetic is exact (fractions.Fraction / ints).

Objects
-------
bip(G)      = |E| - maxcut(G)  = min # edges meeting every odd cycle (odd-cycle edge transversal)
nu_star(G)  = max fractional odd-cycle packing  = max sum_C y_C  s.t.  sum_{C ni e} y_C <= 1, y >= 0
tau_star(G) = min fractional odd-cycle cover    = min sum_e x_e   s.t.  sum_{e in C} x_e >= 1, x >= 0
LP duality: nu_star = tau_star <= bip.

Author: agent G12.
"""
from fractions import Fraction
import heapq
import itertools

# ---------------------------------------------------------------- graph6 I/O
def graph6_to_edges(s):
    """Decode a graph6 string (no header) -> (n, sorted edge list)."""
    data = [ord(c) - 63 for c in s]
    if data[0] <= 62:
        n = data[0]
        idx = 1
    else:
        # 126 -> 63 63 ... ; we only need small n but implement the 4-byte form
        assert data[0] == 63
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        idx = 4
    bits = []
    for d in data[idx:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    edges = []
    p = 0
    for j in range(1, n):
        for i in range(j):
            if p < len(bits) and bits[p]:
                edges.append((i, j))
            p += 1
    return n, edges


def edges_to_adj(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_triangle_free(n, edges):
    adj = edges_to_adj(n, edges)
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True


# ---------------------------------------------------------------- bip (exact)
def bip_bruteforce(n, edges):
    """Exact bip = |E| - maxcut, brute force over 2^(n-1) cuts.  n <= ~24."""
    m = len(edges)
    best_mono = m
    for S in range(1 << (n - 1)):          # fix vertex n-1 outside S
        mono = 0
        for (u, v) in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                mono += 1
                if mono >= best_mono:
                    break
        if mono < best_mono:
            best_mono = mono
            if best_mono == 0:
                break
    return best_mono


def bip_bruteforce_fast(n, edges):
    """Same, bitmask/popcount version.  Returns exact integer."""
    nbr = [0] * n
    for u, v in edges:
        nbr[u] |= 1 << v
        nbr[v] |= 1 << u
    m = len(edges)
    best = m
    full = (1 << n) - 1
    for S in range(1 << (n - 1)):
        T = full ^ S
        cross = 0
        for u in range(n):
            if (S >> u) & 1:
                cross += bin(nbr[u] & T).count("1")
        mono = m - cross
        if mono < best:
            best = mono
            if best == 0:
                break
    return best


# ------------------------------------------------- odd cycle enumeration
def all_cycles(n, edges):
    """All simple cycles (>=3 vertices) as frozensets of edge indices.

    Standard 'smallest vertex is the root, second vertex < last vertex' DFS,
    which enumerates each cycle exactly once.
    """
    eidx = {}
    for i, (u, v) in enumerate(edges):
        eidx[(u, v)] = i
        eidx[(v, u)] = i
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    out = []
    for root in range(n):
        # DFS over paths starting at root using only vertices >= root
        stack = [(root, [root], {root})]
        while stack:
            cur, path, seen = stack.pop()
            for w in adj[cur]:
                if w < root:
                    continue
                if w == root:
                    if len(path) >= 3 and path[1] < path[-1]:
                        es = frozenset(eidx[(path[i], path[i + 1])]
                                       for i in range(len(path) - 1))
                        es = es | {eidx[(path[-1], root)]}
                        out.append((tuple(path), es))
                elif w not in seen:
                    stack.append((w, path + [w], seen | {w}))
    return out


def odd_cycles(n, edges):
    """List of frozensets of edge indices of all simple ODD cycles."""
    res = []
    for path, es in all_cycles(n, edges):
        if len(path) % 2 == 1:
            res.append(es)
    return res


# ------------------------------------------------- exact rational simplex
class SimplexFail(Exception):
    pass


def lp_max_exact(A, b, c, max_iter=200000):
    """Exact  max c^T y  s.t.  A y <= b,  y >= 0,  with b >= 0 (so y=0 feasible).

    A: list of rows (lists of Fractions/ints), b: list, c: list.
    Returns (value, y, x) with y primal optimal and x = dual optimal
    (x is the vector of reduced costs of the slack variables; it satisfies
     A^T x >= c, x >= 0, b^T x = value).
    Bland's rule => finite termination.
    """
    m = len(A)
    nvar = len(c)
    F = Fraction
    # tableau rows: [A | I | b]; objective row: [-c | 0 | 0]
    T = []
    for i in range(m):
        row = [F(v) for v in A[i]] + [F(1) if j == i else F(0) for j in range(m)] + [F(b[i])]
        T.append(row)
    obj = [-F(v) for v in c] + [F(0)] * m + [F(0)]
    basis = [nvar + i for i in range(m)]
    total = nvar + m
    it = 0
    while True:
        it += 1
        if it > max_iter:
            raise SimplexFail("iteration limit")
        # Bland: smallest index with negative reduced cost
        enter = -1
        for j in range(total):
            if obj[j] < 0:
                enter = j
                break
        if enter < 0:
            break
        # ratio test, Bland tie-break on basis variable index
        leave = -1
        best_ratio = None
        for i in range(m):
            if T[i][enter] > 0:
                r = T[i][-1] / T[i][enter]
                if best_ratio is None or r < best_ratio or (r == best_ratio and basis[i] < basis[leave]):
                    best_ratio = r
                    leave = i
        if leave < 0:
            raise SimplexFail("unbounded")
        piv = T[leave][enter]
        T[leave] = [v / piv for v in T[leave]]
        for i in range(m):
            if i != leave and T[i][enter] != 0:
                f = T[i][enter]
                T[i] = [a - f * bb for a, bb in zip(T[i], T[leave])]
        if obj[enter] != 0:
            f = obj[enter]
            obj = [a - f * bb for a, bb in zip(obj, T[leave])]
        basis[leave] = enter
    value = obj[-1]
    y = [F(0)] * nvar
    for i in range(m):
        if basis[i] < nvar:
            y[basis[i]] = T[i][-1]
    x = [obj[nvar + i] for i in range(m)]
    return value, y, x


# ------------------------------------------------- min odd cycle (separation)
def min_odd_cycle_weight(n, edges, w):
    """Exact minimum weight of an odd cycle, weights w >= 0 (Fractions/ints).

    Uses the bipartite double cover: min weight odd CLOSED WALK through v is
    dist_{G x K2}((v,0),(v,1)); with nonnegative weights every odd closed walk
    contains an odd cycle of no larger weight, so the two minima agree.
    Returns None if G is bipartite (no odd cycle).
    """
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, Fraction(w[i])))
        adj[v].append((u, Fraction(w[i])))
    best = None
    for s in range(n):
        # Dijkstra on the double cover, nodes (v, p)
        INF = None
        dist = {}
        pq = [(Fraction(0), s, 0)]
        while pq:
            d, v, p = heapq.heappop(pq)
            if (v, p) in dist:
                continue
            dist[(v, p)] = d
            if (v, p) == (s, 1):
                break
            for (u, wt) in adj[v]:
                if (u, 1 - p) not in dist:
                    heapq.heappush(pq, (d + wt, u, 1 - p))
        if (s, 1) in dist:
            d = dist[(s, 1)]
            if best is None or d < best:
                best = d
    return best


# ------------------------------------------------- nu* by full enumeration
def nu_star_enumerate(n, edges, verbose=False):
    """Exact nu* = tau* via full odd-cycle enumeration + exact simplex.

    Returns dict with value (Fraction), packing y, cover x, and the certificate
    checks (all exact).
    """
    cycs = odd_cycles(n, edges)
    if not cycs:
        return dict(value=Fraction(0), ncycles=0, y=[], x=[Fraction(0)] * len(edges),
                    primal_ok=True, dual_ok=True)
    m = len(edges)
    A = [[1 if e in C else 0 for C in cycs] for e in range(m)]
    b = [1] * m
    c = [1] * len(cycs)
    val, y, x = lp_max_exact(A, b, c)
    # exact certificate checks
    load = [sum(y[j] for j, C in enumerate(cycs) if e in C) for e in range(m)]
    primal_ok = all(v >= 0 for v in y) and all(l <= 1 for l in load)
    dual_ok = all(v >= 0 for v in x) and all(sum(x[e] for e in C) >= 1 for C in cycs)
    assert sum(y) == val and sum(x) == val
    return dict(value=val, ncycles=len(cycs), y=y, x=x, cycles=cycs,
                primal_ok=primal_ok, dual_ok=dual_ok)


# ------------------------------------------------- nu* by cutting planes
def nu_star_cutting(n, edges, verbose=False, max_rounds=400):
    """Exact nu* via cutting planes: start from a few odd cycles, repeatedly
    solve the restricted LP exactly, and separate with min_odd_cycle_weight.

    The dual x of the restricted LP is a valid fractional cover of ALL odd
    cycles iff min_odd_cycle_weight(x) >= 1; when that holds, the restricted
    optimum equals nu*(G) exactly (the primal packing stays feasible for the
    full LP because it only uses cycles in the restricted set).
    """
    cycs = []
    seen = set()
    # seed: shortest odd cycle under unit weights
    w = [1] * len(edges)
    if min_odd_cycle_weight(n, edges, w) is None:
        return dict(value=Fraction(0), ncycles=0, y=[], x=[Fraction(0)] * len(edges),
                    certified=True, cycles=[])
    for rnd in range(max_rounds):
        if not cycs:
            C = shortest_odd_cycle_edges(n, edges, [Fraction(1)] * len(edges))
            cycs.append(C)
            seen.add(C)
            continue
        m = len(edges)
        A = [[1 if e in C else 0 for C in cycs] for e in range(m)]
        val, y, x = lp_max_exact(A, [1] * m, [1] * len(cycs))
        mw = min_odd_cycle_weight(n, edges, x)
        if mw is None or mw >= 1:
            load = [sum(y[j] for j, C in enumerate(cycs) if e in C) for e in range(m)]
            assert all(l <= 1 for l in load) and all(v >= 0 for v in y)
            assert all(v >= 0 for v in x)
            return dict(value=val, ncycles=len(cycs), y=y, x=x,
                        certified=True, cycles=list(cycs))
        C = shortest_odd_cycle_edges(n, edges, x)
        if C in seen:
            raise SimplexFail("separation returned a repeated cycle")
        seen.add(C)
        cycs.append(C)
    raise SimplexFail("cutting planes did not terminate")


def shortest_odd_cycle_edges(n, edges, w):
    """Return the vertex list of a minimum-w-weight odd cycle (w >= 0)."""
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, Fraction(w[i])))
        adj[v].append((u, Fraction(w[i])))
    eidx = {}
    for i, (u, v) in enumerate(edges):
        eidx[(u, v)] = i
        eidx[(v, u)] = i
    best = None
    bestwalk = None
    for s in range(n):
        dist = {}
        par = {}
        pq = [(Fraction(0), s, 0, -1)]
        while pq:
            d, v, p, pv = heapq.heappop(pq)
            if (v, p) in dist:
                continue
            dist[(v, p)] = d
            par[(v, p)] = pv
            if (v, p) == (s, 1):
                break
            for (u, wt) in adj[v]:
                if (u, 1 - p) not in dist:
                    heapq.heappush(pq, (d + wt, u, 1 - p, v))
        if (s, 1) in dist and (best is None or dist[(s, 1)] < best):
            best = dist[(s, 1)]
            walk = [s]
            cur = (s, 1)
            while par[cur] != -1:
                pv = par[cur]
                walk.append(pv)
                cur = (pv, 1 - cur[1])
            bestwalk = walk          # closed odd walk s ... s (as a vertex list)
    verts = extract_odd_cycle_vertices(bestwalk)
    return frozenset(eidx[(verts[i], verts[(i + 1) % len(verts)])] for i in range(len(verts)))


def extract_odd_cycle_vertices(walk):
    """walk = [v0, v1, ..., vk] with v0 == vk and k odd.  Return the vertex list
    of a simple odd cycle using only edges of the walk (weight cannot increase)."""
    seq = list(walk)
    assert seq[0] == seq[-1] and (len(seq) - 1) % 2 == 1
    while True:
        body = seq[:-1]
        if len(set(body)) == len(body):
            return body
        pos = {}
        for k, v in enumerate(body):
            if v in pos:
                i, j = pos[v], k
                inner = seq[i:j + 1]                 # closed walk
                outer = seq[:i + 1] + seq[j + 1:]    # closed walk
                seq = inner if (len(inner) - 1) % 2 == 1 else outer
                break
            pos[v] = k


# ------------------------------------------------- blow-ups
def blowup(n, edges, sizes):
    """Blow up graph (n,edges) with part sizes; returns (N, edge list)."""
    off = [0]
    for s in sizes:
        off.append(off[-1] + s)
    N = off[-1]
    E = []
    for (u, v) in edges:
        for a in range(sizes[u]):
            for b in range(sizes[v]):
                E.append((off[u] + a, off[v] + b))
    return N, E


def C5():
    return 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
