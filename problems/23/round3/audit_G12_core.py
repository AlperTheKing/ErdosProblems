"""AUDIT of G12 -- INDEPENDENT re-implementation.

Nothing here imports G12_core or any other G12_* file.  Own graph6 decoder,
own exhaustive max-cut, own cycle enumeration, own exact rational simplex,
own certificate checker.  Every acceptance path uses Fraction / int only.

Conventions
    bip(G) = |E| - maxcut(G) = min # monochromatic edges over all 2-colourings
    nu*(G) = max fractional odd-cycle EDGE packing
    tau*(G)= min fractional odd-cycle EDGE cover ;  nu* = tau* <= bip.
"""
from fractions import Fraction as Fr
from itertools import combinations


# ------------------------------------------------------------------ graph6
def g6(s):
    """graph6 -> (n, edges).  Written from the format spec, upper-triangle
    column-major order (i<j), bit for pair (i,j) at position j*(j-1)/2 + i."""
    v = [ord(c) - 63 for c in s]
    if v[0] == 63:
        n = (v[1] << 12) + (v[2] << 6) + v[3]
        rest = v[4:]
    else:
        n = v[0]
        rest = v[1:]
    need = n * (n - 1) // 2
    bitstr = "".join(format(x, "06b") for x in rest)
    assert len(bitstr) >= need, (s, len(bitstr), need)
    E = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bitstr[k] == "1":
                E.append((i, j))
            k += 1
    return n, E


def adjmask(n, E):
    a = [0] * n
    for u, v in E:
        a[u] |= 1 << v
        a[v] |= 1 << u
    return a


def degrees(n, E):
    d = [0] * n
    for u, v in E:
        d[u] += 1
        d[v] += 1
    return d


def triangle_free(n, E):
    a = adjmask(n, E)
    for u, v in E:
        if a[u] & a[v]:
            return False
    return True


def girth(n, E):
    """BFS from every vertex; exact girth (None if forest)."""
    a = [[] for _ in range(n)]
    for u, v in E:
        a[u].append(v)
        a[v].append(u)
    best = None
    for s in range(n):
        dist = {s: 0}
        par = {s: -1}
        q = [s]
        while q:
            nq = []
            for x in q:
                for y in a[x]:
                    if y == par[x]:
                        continue
                    if y in dist:
                        c = dist[x] + dist[y] + 1
                        if best is None or c < best:
                            best = c
                    else:
                        dist[y] = dist[x] + 1
                        par[y] = x
                        nq.append(y)
            q = nq
    return best


# ------------------------------------------------------------------ bip
def bip(n, E):
    """Exhaustive over all 2^(n-1) bipartitions; exact integer."""
    a = adjmask(n, E)
    m = len(E)
    best = m
    for S in range(1 << (n - 1)):
        T = ((1 << n) - 1) ^ S
        cross = 0
        x = S
        while x:
            b = x & -x
            u = b.bit_length() - 1
            cross += bin(a[u] & T).count("1")
            x ^= b
        if m - cross < best:
            best = m - cross
            if best == 0:
                break
    return best


def is_bipartite(n, E):
    col = [-1] * n
    a = [[] for _ in range(n)]
    for u, v in E:
        a[u].append(v)
        a[v].append(u)
    for s in range(n):
        if col[s] >= 0:
            continue
        col[s] = 0
        q = [s]
        while q:
            x = q.pop()
            for y in a[x]:
                if col[y] < 0:
                    col[y] = 1 - col[x]
                    q.append(y)
                elif col[y] == col[x]:
                    return False
    return True


# ------------------------------------------------------- cycle enumeration
def simple_cycles(n, E, maxlen=None, only_odd=False):
    """All simple cycles as (vertex tuple, frozenset of edge indices).

    Canonical form: root = minimum vertex of the cycle, and the neighbour of
    the root visited first is smaller than the one visited last.  Each cycle
    appears exactly once.  Independent of the target's routine (recursive).
    """
    ei = {}
    for i, (u, v) in enumerate(E):
        ei[(u, v)] = i
        ei[(v, u)] = i
    a = [[] for _ in range(n)]
    for u, v in E:
        a[u].append(v)
        a[v].append(u)
    for x in a:
        x.sort()
    out = []

    def walk(root, path, used):
        cur = path[-1]
        for w in a[cur]:
            if w == root and len(path) >= 3:
                if path[1] < path[-1]:
                    if (maxlen is None or len(path) <= maxlen) and \
                       (not only_odd or len(path) % 2 == 1):
                        es = frozenset(ei[(path[i], path[i + 1])]
                                       for i in range(len(path) - 1)) | {ei[(cur, root)]}
                        out.append((tuple(path), es))
                continue
            if w <= root or (used >> w) & 1:
                continue
            if maxlen is not None and len(path) + 1 > maxlen:
                continue
            walk(root, path + [w], used | (1 << w))

    for r in range(n):
        walk(r, [r], 1 << r)
    return out


# ------------------------------------------------------- exact LP (simplex)
def simplex_max(A, b, c, itmax=500000):
    """max c.y  s.t. A y <= b (b >= 0), y >= 0.  Exact Fractions, Bland's rule.
    Returns (opt, y, x) with x the dual (shadow prices of the rows)."""
    m, k = len(A), len(c)
    T = [[Fr(A[i][j]) for j in range(k)] + [Fr(1) if t == i else Fr(0) for t in range(m)]
         + [Fr(b[i])] for i in range(m)]
    z = [Fr(-cc) for cc in c] + [Fr(0)] * (m + 1)
    basis = list(range(k, k + m))
    for _ in range(itmax):
        piv = -1
        for j in range(k + m):
            if z[j] < 0:
                piv = j
                break
        if piv < 0:
            break
        lv, ratio = -1, None
        for i in range(m):
            if T[i][piv] > 0:
                r = T[i][-1] / T[i][piv]
                if ratio is None or r < ratio or (r == ratio and basis[i] < basis[lv]):
                    ratio, lv = r, i
        if lv < 0:
            raise RuntimeError("unbounded")
        p = T[lv][piv]
        T[lv] = [t / p for t in T[lv]]
        for i in range(m):
            if i != lv and T[i][piv] != 0:
                f = T[i][piv]
                T[i] = [t - f * s for t, s in zip(T[i], T[lv])]
        if z[piv] != 0:
            f = z[piv]
            z = [t - f * s for t, s in zip(z, T[lv])]
        basis[lv] = piv
    else:
        raise RuntimeError("iteration limit")
    y = [Fr(0)] * k
    for i in range(m):
        if basis[i] < k:
            y[basis[i]] = T[i][-1]
    x = [z[k + i] for i in range(m)]
    return z[-1], y, x


# ------------------------------------------------------- nu* with certificate
def nu_star_certified(n, E, columns=None, dual_check_cycles=None):
    """Exact nu*.  `columns` = list of frozensets of edge indices used as packing
    columns (default: all odd cycles).  `dual_check_cycles` = the cycle family the
    dual must cover (default: all odd cycles).  Returns dict with exact proof data:
      lower  = value of an exactly-verified feasible packing (nu* >= lower)
      upper  = value of an exactly-verified feasible cover  (nu* <= upper)
    """
    allodd = [es for _, es in simple_cycles(n, E, only_odd=True)]
    if dual_check_cycles is None:
        dual_check_cycles = allodd
    if columns is None:
        columns = allodd
    m = len(E)
    if not columns:
        return dict(lower=Fr(0), upper=Fr(0), value=Fr(0), n_odd=len(allodd),
                    y=[], x=[Fr(0)] * m, cols=[])
    A = [[1 if e in Cc else 0 for Cc in columns] for e in range(m)]
    val, y, x = simplex_max(A, [1] * m, [1] * len(columns))
    # --- exact certificate checks, done here and not inside the solver ---
    assert all(t >= 0 for t in y)
    load = [sum(y[j] for j, Cc in enumerate(columns) if e in Cc) for e in range(m)]
    assert all(t <= 1 for t in load), "packing infeasible"
    lower = sum(y)
    assert lower == val
    assert all(t >= 0 for t in x)
    dual_ok = all(sum(x[e] for e in Cc) >= 1 for Cc in dual_check_cycles)
    upper = sum(x) if dual_ok else None
    return dict(lower=lower, upper=upper, value=(val if dual_ok else None),
                n_odd=len(allodd), y=y, x=x, cols=columns, load=load)


def check_cover(n, E, x, odd=None):
    """Exactly verify that x is a feasible fractional odd-cycle cover."""
    if odd is None:
        odd = [es for _, es in simple_cycles(n, E, only_odd=True)]
    return all(t >= 0 for t in x) and all(sum(x[e] for e in Cc) >= 1 for Cc in odd)


# ------------------------------------------------------------------ blow-up
def blowup(n, E, sizes):
    off, s = [], 0
    for t in sizes:
        off.append(s)
        s += t
    out = []
    for u, v in E:
        for i in range(sizes[u]):
            for j in range(sizes[v]):
                out.append((off[u] + i, off[v] + j))
    return s, sorted(out)


C5 = (5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)])
