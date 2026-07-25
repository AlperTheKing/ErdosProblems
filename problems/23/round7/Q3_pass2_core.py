"""Q3 PASS 2 -- independent exact engine for Erdos #23 stability work.

Written from scratch (graph6 decoder from the format spec, bip by explicit
enumeration of all 2^(n-1) cuts, distance to the C5-blow-up family by exact
branch and bound over phi : V -> Z_5).  Every acceptance path is integer /
Fraction arithmetic.  numpy is used only for int64 bookkeeping of exact
integer sums, never for a float comparison.
"""
from fractions import Fraction
from itertools import combinations
import numpy as np

# ---------------------------------------------------------------- graph6

def g6_decode(line):
    """graph6 -> (n, list of edges).  Written from the McKay format spec."""
    s = line.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    b = [ord(c) - 63 for c in s]
    if b[0] <= 62:
        n = b[0]
        rest = b[1:]
    elif b[1] <= 62:                      # 126 then 3 bytes
        n = (b[1] << 12) | (b[2] << 6) | b[3]
        rest = b[4:]
    else:                                  # 126 126 then 6 bytes
        n = 0
        for k in range(2, 8):
            n = (n << 6) | b[k]
        rest = b[8:]
    bits = []
    for x in rest:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def g6_encode(n, edges):
    es = set(map(lambda e: (min(e), max(e)), edges))
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in es else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out


def adj_matrix(n, edges):
    A = np.zeros((n, n), dtype=np.int64)
    for u, v in edges:
        A[u, v] = 1
        A[v, u] = 1
    return A


def adj_masks(n, edges):
    m = [0] * n
    for u, v in edges:
        m[u] |= 1 << v
        m[v] |= 1 << u
    return m

# ---------------------------------------------------------------- checks

def is_triangle_free(n, edges):
    m = adj_masks(n, edges)
    for u, v in edges:
        if m[u] & m[v]:
            return False
    return True


def is_maximal_triangle_free(n, edges):
    """triangle free and every non-edge creates a triangle."""
    if not is_triangle_free(n, edges):
        return False
    m = adj_masks(n, edges)
    for u in range(n):
        for v in range(u + 1, n):
            if not (m[u] >> v) & 1:
                if not (m[u] & m[v]):
                    return False
    return True

# ---------------------------------------------------------------- bip

_CUTCACHE = {}


def _cutmat(n):
    if n not in _CUTCACHE:
        half = 1 << (n - 1)
        X = np.zeros((half, n), dtype=np.int64)
        for s in range(half):
            for v in range(n):
                X[s, v] = (s >> v) & 1
        _CUTCACHE[n] = (X, 1 - X)
    return _CUTCACHE[n]


def bip_unweighted(n, edges):
    """exact integer bip = |E| - maxcut, by enumerating all 2^(n-1) cuts."""
    A = adj_matrix(n, edges)
    X, Y = _cutmat(n)
    s1 = ((X @ A) * X).sum(axis=1)
    s2 = ((Y @ A) * Y).sum(axis=1)
    mono = (s1 + s2) // 2
    return int(mono.min())


def bip_weighted(n, edges, w):
    """exact min over cuts of sum of w_u w_v over monochromatic edges.
    w is a list of ints or Fractions.  Returns the same type."""
    best = None
    half = 1 << (n - 1)
    for s in range(half):
        tot = 0
        for u, v in edges:
            if ((s >> u) & 1) == ((s >> v) & 1):
                tot += w[u] * w[v]
        if best is None or tot < best:
            best = tot
    return best


def mono_mass(edges, w, side):
    """monochromatic mass of a given cut (side = list/dict of 0/1)."""
    tot = 0
    for u, v in edges:
        if side[u] == side[v]:
            tot += w[u] * w[v]
    return tot

# ------------------------------------------- distance to C5 blow-up family


def blowup_edge(a, b):
    d = (a - b) % 5
    return d == 1 or d == 4


def dist_exact_bb(n, edges, ub=None):
    """exact min over phi:V->Z5 of |E \\ E(B_phi)| + |E(B_phi) \\ E|.
    Branch and bound; phi(0)=0 fixed (rotation symmetry)."""
    E = set()
    for u, v in edges:
        E.add((min(u, v), max(u, v)))
    cost = [[0] * 5 for _ in range(5)]           # placeholder
    # pairwise cost c(u,v,a,b) = 1 if [uv in E] != [blowup_edge(a,b)]
    same = [[1 if blowup_edge(a, b) else 0 for b in range(5)] for a in range(5)]
    best = [ub if ub is not None else 10 ** 9]
    phi = [-1] * n

    def lower_bound(k, cur):
        # for each unassigned vertex, min over its colour of cost against assigned
        lb = cur
        for v in range(k, n):
            mv = None
            for a in range(5):
                c = 0
                for u in range(k):
                    e = 1 if (min(u, v), max(u, v)) in E else 0
                    if e != same[phi[u]][a]:
                        c += 1
                if mv is None or c < mv:
                    mv = c
            lb += mv
        return lb

    def rec(k, cur):
        if cur >= best[0]:
            return
        if k == n:
            best[0] = cur
            return
        if lower_bound(k, cur) >= best[0]:
            return
        rng = [0] if k == 0 else range(5)
        cand = []
        for a in rng:
            c = 0
            for u in range(k):
                e = 1 if (min(u, k), max(u, k)) in E else 0
                if e != same[phi[u]][a]:
                    c += 1
            cand.append((c, a))
        cand.sort()
        for c, a in cand:
            phi[k] = a
            rec(k + 1, cur + c)
            phi[k] = -1

    rec(0, 0)
    return best[0]


def dist_greedy_ub(n, edges, tries=400, seed=1):
    """random restarts + local search, gives an upper bound for the B&B."""
    rng = np.random.default_rng(seed)
    E = np.zeros((n, n), dtype=np.int64)
    for u, v in edges:
        E[u, v] = E[v, u] = 1
    same = np.array([[1 if blowup_edge(a, b) else 0 for b in range(5)]
                     for a in range(5)], dtype=np.int64)
    best = None
    for _ in range(tries):
        phi = rng.integers(0, 5, size=n)
        improved = True
        while improved:
            improved = False
            for v in range(n):
                costs = []
                for a in range(5):
                    c = 0
                    for u in range(n):
                        if u == v:
                            continue
                        c += int(E[u, v] != same[phi[u], a])
                    costs.append(c)
                a = int(np.argmin(costs))
                if a != phi[v]:
                    phi[v] = a
                    improved = True
        tot = 0
        for u in range(n):
            for v in range(u + 1, n):
                tot += int(E[u, v] != same[phi[u], phi[v]])
        if best is None or tot < best:
            best = tot
    return best


def dist_exact(n, edges):
    ub = dist_greedy_ub(n, edges)
    return dist_exact_bb(n, edges, ub=ub + 1)

# ---------------------------------------------------------------- families


def c5_blowup(sizes):
    """C5[sizes] as (n, edges)."""
    n = sum(sizes)
    start = []
    acc = 0
    for s in sizes:
        start.append(acc)
        acc += s
    edges = []
    for i in range(5):
        j = (i + 1) % 5
        for a in range(sizes[i]):
            for b in range(sizes[j]):
                edges.append((start[i] + a, start[j] + b))
    return n, edges


def prism():
    """pentagonal prism C5 [] K2 : outer o_j = j, inner i_j = 5+j."""
    edges = []
    for j in range(5):
        edges.append((j, (j + 1) % 5))
        edges.append((5 + j, 5 + (j + 1) % 5))
        edges.append((j, 5 + j))
    return 10, edges


def petersen():
    edges = []
    for j in range(5):
        edges.append((j, (j + 1) % 5))
        edges.append((5 + j, 5 + (j + 2) % 5))
        edges.append((j, 5 + j))
    return 10, edges


def circle_graph(m, n=None):
    """Gamma_m : vertices 0..m-1 on Z_m, u~v iff circular distance > m/3."""
    if n is None:
        n = m
    edges = []
    for u in range(m):
        for v in range(u + 1, m):
            d = min((u - v) % m, (v - u) % m)
            if 3 * d > m:
                edges.append((u, v))
    return m, edges


def read_g6_file(path, limit=None):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(g6_decode(line))
            if limit and len(out) >= limit:
                break
    return out
