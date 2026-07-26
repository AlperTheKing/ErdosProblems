"""R9 Theorem D audit -- exact core library.

psi(H,x) = min over bipartitions S of V(H) of  sum_{monochromatic uv in E} x_u x_v.
Everything integer/Fraction exact.  Floating point is used only to guide search.

Conventions
-----------
A graph is (n, adj) with adj a tuple of frozensets.
Weights are given as an integer vector a with sum q; then x = a/q and
psi(H,x) = M(a)/q^2 with M(a) an integer, computed by exhaustive minimisation
over all 2^(n-1) bipartitions (vertex 0 pinned to side 0).
"""
from fractions import Fraction
from itertools import combinations, permutations
import numpy as np

# ---------------------------------------------------------------- graphs ----

def mkgraph(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        assert u != v
        adj[u].add(v)
        adj[v].add(u)
    return (n, tuple(frozenset(s) for s in adj))


def edges_of(G):
    n, adj = G
    return [(u, v) for u in range(n) for v in adj[u] if u < v]


def is_triangle_free(G):
    n, adj = G
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True


def parse_graph6(s):
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    data = [ord(c) - 63 for c in s]
    if data[0] <= 62:
        n = data[0]
        rest = data[1:]
    else:
        n = (data[1] << 12) + (data[2] << 6) + data[3]
        rest = data[4:]
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
    return mkgraph(n, edges)


def to_graph6(G):
    n, adj = G
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        val = 0
        for b in bits[k:k + 6]:
            val = (val << 1) | b
        out += chr(val + 63)
    return out


def disjoint_union(G, H):
    n1, a1 = G
    n2, a2 = H
    e = edges_of(G) + [(u + n1, v + n1) for u, v in edges_of(H)]
    return mkgraph(n1 + n2, e)

# ------------------------------------------------------------- psi exact ----

_CACHE = {}


def _mono_matrix(G):
    """rows = 2^(n-1) bipartitions, cols = edges;  entry 1 iff edge monochromatic."""
    key = to_graph6(G)
    if key in _CACHE:
        return _CACHE[key]
    n, adj = G
    E = edges_of(G)
    masks = np.arange(1 << (n - 1), dtype=np.int64)

    def side(v):
        if v == 0:
            return np.zeros(masks.shape, dtype=np.int64)
        return (masks >> (v - 1)) & 1
    cols = []
    for (u, v) in E:
        cols.append((side(u) == side(v)).astype(np.int64))
    M = np.array(cols).T if cols else np.zeros((len(masks), 0), dtype=np.int64)
    _CACHE[key] = (M, E)
    return M, E


def psi_int(G, a):
    """a integer weight vector; returns integer M(a) = min_S sum_mono a_u a_v."""
    M, E = _mono_matrix(G)
    if not E:
        return 0
    w = np.array([a[u] * a[v] for (u, v) in E], dtype=np.int64)
    return int((M @ w).min())


def psi_argmin(G, a):
    M, E = _mono_matrix(G)
    if not E:
        return 0, 0
    w = np.array([a[u] * a[v] for (u, v) in E], dtype=np.int64)
    vals = M @ w
    k = int(vals.argmin())
    return int(vals[k]), k


def psi_frac(G, x):
    """x list of Fractions summing to 1 -> psi as Fraction (exact)."""
    den = 1
    for t in x:
        den = den * Fraction(t).denominator // np.gcd(den, Fraction(t).denominator)
    a = [int(Fraction(t) * den) for t in x]
    return Fraction(psi_int(G, a), den * den)

# ------------------------------------------------- pentagons / classes ------

def induced_C5s(G):
    """all induced 5-cycles, each returned once as a tuple (c0..c4) in cyclic order
    (canonical rotation/reflection representative)."""
    n, adj = G
    out = set()
    for S in combinations(range(n), 5):
        sub = {v: adj[v] & set(S) for v in S}
        if any(len(sub[v]) != 2 for v in S):
            continue
        # walk the cycle
        start = S[0]
        prev, cur = start, min(sub[start])
        order = [start, cur]
        ok = True
        for _ in range(3):
            nxt = [w for w in sub[cur] if w != prev]
            if len(nxt) != 1:
                ok = False
                break
            prev, cur = cur, nxt[0]
            order.append(cur)
        if not ok or len(set(order)) != 5 or start not in sub[order[-1]]:
            continue
        reps = []
        for k in range(5):
            reps.append(tuple(order[k:] + order[:k]))
            rr = list(reversed(order))
            reps.append(tuple(rr[k:] + rr[:k]))
        out.add(min(reps))
    return sorted(out)


def classify(G, C):
    """returns (T, R, Rj, Rnone) for the induced C5 C=(c0..c4).
    T[i] = full twins of class i, R = rest outside C,
    Rj[j] = R-vertices whose unique C-neighbour is c_j, Rnone = R-vertices with none."""
    n, adj = G
    Cs = set(C)
    T = [[] for _ in range(5)]
    R, Rj, Rnone = [], [[] for _ in range(5)], []
    for v in range(n):
        if v in Cs:
            continue
        nb = adj[v] & Cs
        placed = False
        for i in range(5):
            if nb == {C[(i - 1) % 5], C[(i + 1) % 5]}:
                T[i].append(v)
                placed = True
                break
        if placed:
            continue
        R.append(v)
        if len(nb) == 0:
            Rnone.append(v)
        elif len(nb) == 1:
            j = C.index(next(iter(nb)))
            Rj[j].append(v)
        else:
            # |N(v) cap C| = 2 and not a twin pair  ->  impossible if triangle-free
            Rj = None
            return T, R, Rj, Rnone
    return T, R, Rj, Rnone


def thmD_bound(G, C, x):
    """(1-rho)^2/25 + rho*eta as an exact Fraction, plus (rho, eta)."""
    T, R, Rj, Rnone = classify(G, C)
    rho = sum(x[v] for v in R)
    eta = 1 - sum(x[c] for c in C)
    return Fraction(1 - rho, 1) ** 2 / 25 + rho * eta, rho, eta

# ------------------------------------------------------- named graphs -------

def cycle(n):
    return mkgraph(n, [(i, (i + 1) % n) for i in range(n)])


def blowup(sizes):
    """complete C5 blow-up with the given 5 class sizes (zeros allowed)."""
    assert len(sizes) == 5
    start, cls = [], []
    s = 0
    for k in sizes:
        cls.append(list(range(s, s + k)))
        s += k
    e = []
    for i in range(5):
        for u in cls[i]:
            for v in cls[(i + 1) % 5]:
                e.append((u, v))
    return mkgraph(s, e), cls


def circulant(n, conn):
    e = set()
    for i in range(n):
        for d in conn:
            j = (i + d) % n
            if i != j:
                e.add((min(i, j), max(i, j)))
    return mkgraph(n, sorted(e))


def petersen():
    e = [(i, (i + 1) % 5) for i in range(5)]
    e += [(i, i + 5) for i in range(5)]
    e += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return mkgraph(10, e)


def mycielski(G):
    n, adj = G
    e = edges_of(G)
    for u in range(n):
        for v in adj[u]:
            e.append((u, n + v))
    e = list({(min(a, b), max(a, b)) for a, b in e})
    e += [(n + i, 2 * n) for i in range(n)]
    return mkgraph(2 * n + 1, e)


def wagner():
    """circle graph on 8 vertices, u~v iff 3*circdist > 8  <=> dist in {3,4}."""
    e = []
    for i in range(8):
        for j in range(i + 1, 8):
            d = min((j - i) % 8, (i - j) % 8)
            if 3 * d > 8:
                e.append((i, j))
    return mkgraph(8, e)


def andrasfai(k):
    """And(k) on 3k-1 vertices: i~j iff (i-j) = 1 mod 3."""
    n = 3 * k - 1
    conn = [d for d in range(1, n) if d % 3 == 1]
    return circulant(n, conn)


NAMED = {}


def named_graphs():
    if NAMED:
        return NAMED
    G = NAMED
    G['C5'] = cycle(5)
    G['C7'] = cycle(7)
    G['C9'] = cycle(9)
    G['K33'] = mkgraph(6, [(i, 3 + j) for i in range(3) for j in range(3)])
    G['C5[2]'] = blowup([2, 2, 2, 2, 2])[0]
    G['C5[3,1,2,2,1]'] = blowup([3, 1, 2, 2, 1])[0]
    G['C5[3,3,3,3,2]'] = blowup([3, 3, 3, 3, 2])[0]
    G['C5[2,2,0,2,2]'] = blowup([2, 2, 0, 2, 2])[0]
    G['C5[3,1,0,2,1]'] = blowup([3, 1, 0, 2, 1])[0]
    G['C5[2,2,1,1,1]'] = blowup([2, 2, 1, 1, 1])[0]
    G['Petersen'] = petersen()
    G['Grotzsch'] = mycielski(cycle(5))
    G['Wagner=And(3)'] = wagner()
    G['And(4)=G11'] = andrasfai(4)
    G['And(5)=G14'] = andrasfai(5)
    G['MTF14'] = parse_graph6('M?AE@bH{AYN_LgBs?')
    G['C5+K1'] = disjoint_union(cycle(5), mkgraph(1, []))
    G['C5+C5'] = disjoint_union(cycle(5), cycle(5))
    G['C5+C7'] = disjoint_union(cycle(5), cycle(7))
    G['Petersen+K1'] = disjoint_union(petersen(), mkgraph(1, []))
    return NAMED
