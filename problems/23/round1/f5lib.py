"""
F5 library for Erdos #23 (bip(G) <= N^2/25 for triangle-free G).

EXACT arithmetic only (Fraction / int).  No floats anywhere on an acceptance path.

Contents
  - graph6 parsing
  - bip(G) by exhaustive bipartition search (exact integer)
  - enumeration of all simple odd cycles (as edge-index sets)
  - exact rational simplex (Bland's rule)
  - tau_star(G) = value of the fractional odd-cycle edge-cover LP
                = nu_star(G) = fractional odd-cycle packing (LP duality)
    together with an exact primal (cover y) and dual (packing z) certificate.
"""
from fractions import Fraction
from itertools import combinations

# ---------------------------------------------------------------- graph6 ----

def parse_graph6(s):
    """Return (n, edges) with edges a sorted list of (u,v), u<v."""
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    data = [ord(c) - 63 for c in s]
    if data[0] <= 62:
        n = data[0]
        idx = 1
    else:
        # 126 marker
        n = (data[1] << 12) + (data[2] << 6) + data[3]
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


def adj_masks(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def is_triangle_free(n, edges):
    adj = adj_masks(n, edges)
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True


# ------------------------------------------------------------------ bip ----

def bip(n, edges):
    """Exact min number of monochromatic edges over all bipartitions."""
    adj = adj_masks(n, edges)
    full = (1 << n) - 1
    best = len(edges)
    # vertex 0 always on side S  (halves the search, no loss)
    for rest in range(1 << (n - 1)):
        S = 1 | (rest << 1)
        T = full ^ S
        mono = 0
        for v in range(n):
            if (S >> v) & 1:
                mono += (adj[v] & S).bit_count()
            else:
                mono += (adj[v] & T).bit_count()
        mono >>= 1
        if mono < best:
            best = mono
            if best == 0:
                break
    return best


def best_cut(n, edges):
    """Return (bip, S) with S a bitmask attaining the minimum."""
    adj = adj_masks(n, edges)
    full = (1 << n) - 1
    best = len(edges) + 1
    arg = 0
    for rest in range(1 << (n - 1)):
        S = 1 | (rest << 1)
        T = full ^ S
        mono = 0
        for v in range(n):
            if (S >> v) & 1:
                mono += (adj[v] & S).bit_count()
            else:
                mono += (adj[v] & T).bit_count()
        mono >>= 1
        if mono < best:
            best = mono
            arg = S
    return best, arg


# ---------------------------------------------------------- odd cycles ----

def all_odd_cycles(n, edges):
    """All simple odd cycles, each returned as a frozenset of edge indices.

    Standard DFS enumeration: a cycle is generated once, rooted at its minimum
    vertex, with the second vertex smaller than the last vertex.
    """
    eidx = {}
    for i, (u, v) in enumerate(edges):
        eidx[(u, v)] = i
        eidx[(v, u)] = i
    nbr = [[] for _ in range(n)]
    for u, v in edges:
        nbr[u].append(v)
        nbr[v].append(u)
    out = []
    for start in range(n):
        # path stored as list of vertices
        path = [start]
        onpath = 1 << start

        def dfs(u):
            for w in nbr[u]:
                if w < start:
                    continue
                if w == start:
                    if len(path) >= 3 and len(path) % 2 == 1:
                        # canonical: path[1] < path[-1]
                        if path[1] < path[-1]:
                            es = frozenset(
                                eidx[(path[i], path[(i + 1) % len(path)])]
                                for i in range(len(path)))
                            out.append(es)
                    continue
                if (onpath >> w) & 1:
                    continue
                path.append(w)
                nonlocal_push(w)
                dfs(w)
                nonlocal_pop(w)
                path.pop()

        def nonlocal_push(w):
            nonlocal onpath
            onpath |= 1 << w

        def nonlocal_pop(w):
            nonlocal onpath
            onpath &= ~(1 << w)

        dfs(start)
    return out


# --------------------------------------------------------- exact simplex ----

def simplex_max(A, b, c):
    """max c^T x  s.t.  A x <= b, x >= 0, with b >= 0 (entrywise).

    All inputs Fractions/ints.  Bland's rule => finite termination.
    Returns (value, x, y) with y the optimal dual (min b^T y, A^T y >= c, y>=0).
    """
    m = len(A)
    nv = len(c)
    T = []
    for i in range(m):
        row = [Fraction(x) for x in A[i]]
        row += [Fraction(1) if k == i else Fraction(0) for k in range(m)]
        row.append(Fraction(b[i]))
        T.append(row)
    obj = [Fraction(x) for x in c] + [Fraction(0)] * m + [Fraction(0)]
    basis = list(range(nv, nv + m))
    W = nv + m + 1
    while True:
        e = -1
        for j in range(nv + m):
            if obj[j] > 0:
                e = j
                break
        if e < 0:
            break
        l = -1
        best = None
        for i in range(m):
            if T[i][e] > 0:
                r = T[i][W - 1] / T[i][e]
                if best is None or r < best or (r == best and basis[i] < basis[l]):
                    best = r
                    l = i
        if l < 0:
            raise RuntimeError("unbounded")
        piv = T[l][e]
        Tl = [v / piv for v in T[l]]
        T[l] = Tl
        for i in range(m):
            if i != l:
                f = T[i][e]
                if f != 0:
                    Ti = T[i]
                    T[i] = [Ti[j] - f * Tl[j] for j in range(W)]
        f = obj[e]
        if f != 0:
            obj = [obj[j] - f * Tl[j] for j in range(W)]
        basis[l] = e
    value = -obj[W - 1]
    x = [Fraction(0)] * nv
    for i in range(m):
        if basis[i] < nv:
            x[basis[i]] = T[i][W - 1]
    y = [-obj[nv + i] for i in range(m)]
    return value, x, y


# ------------------------------------------------- odd-cycle cover LP ----

def tau_star(n, edges, cycles=None):
    """Exact value of  min sum_e y_e  s.t.  sum_{e in C} y_e >= 1 for every odd
    cycle C,  y >= 0.   Equals (LP duality) the max fractional odd-cycle packing.

    Returns (value, y_cover, z_packing, cycles).
    Certificates are exact Fractions and are re-verified by the caller.
    """
    if cycles is None:
        cycles = all_odd_cycles(n, edges)
    if not cycles:
        return Fraction(0), [Fraction(0)] * len(edges), [], []
    m = len(edges)
    # Solve the PACKING LP (few rows = |E|, many columns = cycles):
    #   max 1^T z   s.t.  sum_{C ni e} z_C <= 1  for each edge e,  z >= 0
    A = [[Fraction(1) if e in C else Fraction(0) for C in cycles] for e in range(m)]
    b = [Fraction(1)] * m
    c = [Fraction(1)] * len(cycles)
    val, z, y = simplex_max(A, b, c)
    return val, y, z, cycles


def verify_cover(edges, cycles, y):
    """Exact check that y is a feasible fractional odd-cycle cover."""
    for yi in y:
        if yi < 0:
            return False
    for C in cycles:
        if sum(y[e] for e in C) < 1:
            return False
    return True


def verify_packing(m, cycles, z):
    """Exact check that z is a feasible fractional odd-cycle packing."""
    load = [Fraction(0)] * m
    for zi, C in zip(z, cycles):
        if zi < 0:
            return False
        for e in C:
            load[e] += zi
    return all(l <= 1 for l in load)
