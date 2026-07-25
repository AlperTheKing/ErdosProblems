"""audit_P4_core — INDEPENDENT exact re-implementation of the round-6 chain objects.

Written from the definitions in the task brief, not from P4_*.py.  Everything exact
(fractions.Fraction).  Points live on the grid Z_M / M subset of R/Z; a measure is a list of
Fractions summing to 1.

Definitions used (brief, items 1-6):
  adjacency        u ~ v  iff  circular distance d(u,v) > 1/3     (STRICT)
  psi(H,x)         min over ALL 2^(n-1) bipartitions of sum_{monochromatic uv} x_u x_v
  ARCBOUND         min over arc cuts (side = cyclic interval) of the same quantity
  g(b)             mu({y : d(b,y) > 1/3})
  W                (1/2) int g dmu  =  sum_{u<v, u~v} x_u x_v
  T                sum_{u<v, u~v} d(u,v) x_u x_v
  A                W - 2T
  m(b)             W - int_{N(b)} g dmu ,  N(b) = {y : d(b,y) > 1/3}
  bound_k          (sum_b x_b g(b)^k m(b)) / (sum_b x_b g(b)^k)
"""
from fractions import Fraction as F
from itertools import combinations


# ---------------------------------------------------------------- graph / geometry

def circ_dist_steps(u, v, M):
    d = abs(u - v) % M
    return min(d, M - d)


def dist(u, v, M):
    """exact circular distance in R/Z"""
    return F(circ_dist_steps(u, v, M), M)


def adj_matrix(M):
    """Gamma_M: u ~ v iff d(u,v) > 1/3, i.e. 3*steps > M."""
    return [[(u != v and 3 * circ_dist_steps(u, v, M) > M) for v in range(M)] for u in range(M)]


def far_set(b, M):
    """N(b) = {y : d(b,y) > 1/3} for b a grid point."""
    return [y for y in range(M) if y != b and 3 * circ_dist_steps(b, y, M) > M]


# ---------------------------------------------------------------- measure functionals

def normalise(w):
    q = sum(w)
    return [F(wi, q) for wi in w]


def W_of(x, adj):
    M = len(x)
    return sum(x[u] * x[v] for u, v in combinations(range(M), 2) if adj[u][v])


def T_of(x, adj, M):
    return sum(dist(u, v, M) * x[u] * x[v]
               for u, v in combinations(range(M), 2) if adj[u][v])


def g_of(x, adj):
    M = len(x)
    return [sum(x[y] for y in range(M) if adj[b][y]) for b in range(M)]


def A_of(x, adj, M):
    return W_of(x, adj) - 2 * T_of(x, adj, M)


def A_direct(x, adj, M):
    """A = int int_{d>1/3} (1/2 - d) dmu dmu  (ordered pairs)."""
    tot = F(0)
    for u in range(M):
        for v in range(M):
            if adj[u][v]:
                tot += (F(1, 2) - dist(u, v, M)) * x[u] * x[v]
    return tot


def mono(x, adj, inA):
    """monochromatic weight of the bipartition given by the boolean vector inA"""
    M = len(x)
    return sum(x[u] * x[v] for u, v in combinations(range(M), 2)
               if adj[u][v] and inA[u] == inA[v])


def m_of(b, x, adj, M):
    """m(b) = W - int_{N(b)} g dmu  (should equal mono(N(b)))"""
    g = g_of(x, adj)
    return W_of(x, adj) - sum(x[y] * g[y] for y in far_set(b, M))


def m_as_cut(b, x, adj, M):
    inA = [False] * M
    for y in far_set(b, M):
        inA[y] = True
    return mono(x, adj, inA)


def bound_k(k, x, adj, M):
    g = g_of(x, adj)
    ms = [m_of(b, x, adj, M) for b in range(M)]
    num = F(0)
    den = F(0)
    for b in range(M):
        if x[b] == 0:
            continue
        wgt = x[b] * (g[b] ** k if k > 0 else F(1))
        num += wgt * ms[b]
        den += wgt
    if den == 0:
        return None
    return num / den


def var_g(x, adj):
    g = g_of(x, adj)
    M = len(x)
    mean = sum(x[b] * g[b] for b in range(M))
    return sum(x[b] * (g[b] - mean) ** 2 for b in range(M))


# ---------------------------------------------------------------- cut families

def arcbound(x, adj, M):
    """min over ALL arc cuts (side = any cyclic interval, any start, any length)"""
    best = None
    for i in range(M):
        inA = [False] * M
        for l in range(M + 1):
            if l > 0:
                inA[(i + l - 1) % M] = True
            v = mono(x, adj, inA)
            if best is None or v < best:
                best = v
    return best


def arcs_of_window(x, adj, M, lengths):
    """min over arc cuts whose side is a window of exactly `l` consecutive vertices, l in lengths"""
    best = None
    for i in range(M):
        for l in lengths:
            inA = [False] * M
            for t in range(l):
                inA[(i + t) % M] = True
            v = mono(x, adj, inA)
            if best is None or v < best:
                best = v
    return best


def _windows(M, npts_max):
    out = []
    for i in range(M):
        for l in range(1, npts_max + 1):
            inA = [False] * M
            for t in range(l):
                inA[(i + t) % M] = True
            out.append(inA)
    return out


def sliding_third_arcs(M):
    """every set of grid points realisable as N(b) = (b+1/3, b+2/3) for SOME b in R/Z:
    a window of l consecutive grid points spans (l-1)/M, and fits in an open arc of length 1/3
    iff 3(l-1) < M."""
    npts = (M - 1) // 3 + 1
    return _windows(M, npts)


def sliding_half_arcs(M):
    """every set of grid points realisable as a half-open arc [a, a+1/2):
    window of l points spans (l-1)/M <= 1/2 - (something) ; fits iff 2(l-1) < M."""
    npts = (M - 1) // 2 + 1
    return _windows(M, npts)


def psi_bruteforce(x, adj, M):
    """min over ALL bipartitions, restricted to the support (vertices of weight 0 are irrelevant:
    they contribute nothing whichever side they go to)."""
    supp = [i for i in range(M) if x[i] != 0]
    n = len(supp)
    best = None
    for mask in range(1 << (n - 1)):        # fix supp[0] in side A
        inA = [False] * M
        inA[supp[0]] = True
        for j in range(1, n):
            if (mask >> (j - 1)) & 1:
                inA[supp[j]] = True
        v = mono(x, adj, inA)
        if best is None or v < best:
            best = v
    return best


# ---------------------------------------------------------------- generic graphs

def psi_graph(adjG, x):
    """psi for an arbitrary graph given as an adjacency matrix"""
    n = len(x)
    best = None
    for mask in range(1 << (n - 1)):
        inA = [(mask >> j) & 1 for j in range(n - 1)] + [0]
        v = sum(x[u] * x[v] for u, v in combinations(range(n), 2)
                if adjG[u][v] and inA[u] == inA[v])
        if best is None or v < best:
            best = v
    return best


def bip_graph(adjG):
    """|E| - maxcut, integer"""
    n = len(adjG)
    E = sum(1 for u, v in combinations(range(n), 2) if adjG[u][v])
    best = None
    for mask in range(1 << (n - 1)):
        inA = [(mask >> j) & 1 for j in range(n - 1)] + [0]
        m = sum(1 for u, v in combinations(range(n), 2) if adjG[u][v] and inA[u] == inA[v])
        if best is None or m < best:
            best = m
    return best, E


def blowup(adjG, sizes):
    """adjacency matrix of H[n]"""
    idx = []
    for v, s in enumerate(sizes):
        idx += [v] * s
    N = len(idx)
    return [[adjG[idx[a]][idx[b]] if a != b else False for b in range(N)] for a in range(N)], idx


def triangle_free(adjG):
    n = len(adjG)
    for a, b, c in combinations(range(n), 3):
        if adjG[a][b] and adjG[b][c] and adjG[a][c]:
            return False
    return True
