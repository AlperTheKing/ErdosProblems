"""P4 audit core: an INDEPENDENT re-implementation of every object in the round-6 chain.

Nothing here is imported from round5; the point of the audit is to re-derive.
All arithmetic is exact (fractions.Fraction).

Conventions fixed here and used everywhere below
------------------------------------------------
* circle = R/Z, circular distance d(x,y) = min(|x-y|, 1-|x-y|)  in [0, 1/2].
* ADJACENCY IS STRICT:  x ~ y  iff  d(x,y) > 1/3.
  This is forced: with the non-strict convention d >= 1/3 the three points 0, 1/3, 2/3 would be
  pairwise adjacent, i.e. the circle graph would contain a triangle.  See P4_a_blowup.py.
* mu is a finitely supported probability measure: list of (pos, wt), pos distinct in [0,1).
* W       = sum over UNORDERED adjacent pairs of x_u x_v            (= (1/2) int g dmu)
* g(x)    = mu(open far arc of x) = mu({y : d(x,y) > 1/3})
* T       = sum over UNORDERED adjacent pairs of d(u,v) x_u x_v
* A       = W - 2T
* m(b)    = W - int_{N(b)} g dmu, the value of the cut S = N(b)
* mono(S) = mass of unordered adjacent pairs with both endpoints on the same side of S
* ARCBOUND= min of mono(S) over all arcs S (cyclic intervals of the support, incl. empty/full)
* psi     = min of mono(S) over ALL subsets S
"""
from fractions import Fraction as F
from itertools import combinations

THIRD = F(1, 3)
TARGET = F(1, 25)


# --------------------------------------------------------------------------- geometry
def circdist(a, b):
    """exact circular distance on R/Z"""
    t = (a - b) % 1
    return min(t, 1 - t)


def far(a, b):
    """the adjacency of the circle graph: STRICT d > 1/3"""
    return circdist(a, b) > THIRD


# --------------------------------------------------------------------------- measures
def normalise(pos, wt):
    q = sum(wt)
    assert q > 0
    return list(pos), [F(w, 1) / q for w in wt]


def from_gamma(m, weights):
    """the measure supported on the vertices of Gamma_m with the given integer weights"""
    pos = [F(i, m) for i in range(m)]
    pos = [p for p, w in zip(pos, weights) if w != 0]
    wt = [F(w) for w in weights if w != 0]
    return normalise(pos, wt)


def adjacency(pos):
    n = len(pos)
    return [[(u != v and far(pos[u], pos[v])) for v in range(n)] for u in range(n)]


def sort_cyclic(pos, wt):
    z = sorted(zip(pos, wt))
    return [p for p, _ in z], [w for _, w in z]


# --------------------------------------------------------------------------- functionals
def W_of(pos, wt, adj=None):
    adj = adj or adjacency(pos)
    n = len(pos)
    return sum(wt[u] * wt[v] for u, v in combinations(range(n), 2) if adj[u][v])


def T_of(pos, wt, adj=None):
    adj = adj or adjacency(pos)
    n = len(pos)
    return sum(circdist(pos[u], pos[v]) * wt[u] * wt[v]
               for u, v in combinations(range(n), 2) if adj[u][v])


def A_of(pos, wt, adj=None):
    adj = adj or adjacency(pos)
    return W_of(pos, wt, adj) - 2 * T_of(pos, wt, adj)


def g_of(pos, wt, adj=None):
    """g(u) for every atom u (mass of the OPEN far arc of u)"""
    adj = adj or adjacency(pos)
    n = len(pos)
    return [sum(wt[v] for v in range(n) if adj[u][v]) for u in range(n)]


def g_at(pos, wt, b):
    """g(b) for an arbitrary point b of the circle, not necessarily an atom"""
    return sum(w for p, w in zip(pos, wt) if far(b, p))


def mono(pos, wt, inS, adj=None):
    adj = adj or adjacency(pos)
    n = len(pos)
    return sum(wt[u] * wt[v] for u, v in combinations(range(n), 2)
               if adj[u][v] and inS[u] == inS[v])


def m_at(pos, wt, b, adj=None):
    """value of the cut S = N(b) = {y : d(y,b) > 1/3}, for an arbitrary point b."""
    adj = adj or adjacency(pos)
    inS = [far(b, p) for p in pos]
    return mono(pos, wt, inS, adj)


def m_values(pos, wt, adj=None):
    """m(b) for b ranging over the atoms"""
    return [m_at(pos, wt, b, adj) for b in pos]


def bound_k(pos, wt, k, adj=None):
    """(sum_b x_b g(b)^k m(b)) / (sum_b x_b g(b)^k);  returns None if the denominator vanishes"""
    adj = adj or adjacency(pos)
    g = g_of(pos, wt, adj)
    mv = m_values(pos, wt, adj)
    num = den = F(0)
    for b in range(len(pos)):
        c = wt[b] * (g[b] ** k if k > 0 else F(1))
        num += c * mv[b]
        den += c
    if den == 0:
        return None
    return num / den


def arcs(n):
    """all cyclic intervals of {0..n-1} in cyclic position order, as boolean masks"""
    out = [[False] * n]
    for i in range(n):
        for L in range(1, n + 1):
            msk = [False] * n
            for t in range(L):
                msk[(i + t) % n] = True
            out.append(msk)
    return out


def arcbound(pos, wt, adj=None):
    """min over ARC cuts.  pos must already be in cyclic (sorted) order."""
    adj = adj or adjacency(pos)
    n = len(pos)
    return min(mono(pos, wt, msk, adj) for msk in arcs(n))


def psi(pos, wt, adj=None):
    """min over ALL cuts (exponential; only for n <= ~20)"""
    adj = adj or adjacency(pos)
    n = len(pos)
    best = None
    for msk_int in range(1 << (n - 1)):
        inS = [(msk_int >> i) & 1 for i in range(n - 1)] + [0]
        v = mono(pos, wt, inS, adj)
        if best is None or v < best:
            best = v
    return best


# --------------------------------------------------------------------------- graphs
def gamma_graph(m):
    """Gamma_m as an adjacency matrix: i ~ j iff 3*circular index distance > m"""
    return [[(i != j and 3 * min((i - j) % m, (j - i) % m) > m) for j in range(m)] for i in range(m)]


def has_triangle(adjm):
    n = len(adjm)
    for a, b, c in combinations(range(n), 3):
        if adjm[a][b] and adjm[b][c] and adjm[a][c]:
            return True
    return False


def blowup(adjm, sizes):
    """the blow-up H[sizes]: vertex v -> independent set of size sizes[v]"""
    idx = []
    for v, s in enumerate(sizes):
        idx += [v] * s
    N = len(idx)
    return [[adjm[idx[a]][idx[b]] for b in range(N)] for a in range(N)], idx


def bip_bruteforce(adjm):
    """|E| - maxcut, by brute force over all cuts (N <= ~22)"""
    N = len(adjm)
    E = [(u, v) for u, v in combinations(range(N), 2) if adjm[u][v]]
    best = None
    for msk in range(1 << (N - 1)):
        side = [(msk >> i) & 1 for i in range(N - 1)] + [0]
        c = sum(1 for u, v in E if side[u] == side[v])
        if best is None or c < best:
            best = c
    return best


def psi_graph(adjm, x):
    """psi(H, x) = min over cuts S of H of sum_{uv monochromatic} x_u x_v"""
    n = len(adjm)
    E = [(u, v) for u, v in combinations(range(n), 2) if adjm[u][v]]
    best = None
    for msk in range(1 << (n - 1)):
        side = [(msk >> i) & 1 for i in range(n - 1)] + [0]
        c = sum(x[u] * x[v] for u, v in E if side[u] == side[v])
        if best is None or c < best:
            best = c
    return best
