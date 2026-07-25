"""
g3_lib.py -- independent library for the G3 weighted-pattern optimisation.

Everything here is written from scratch (own graph6 codec, own cut enumeration,
own maxcut) so that it is an independent check on anything already in round1.

Conventions
-----------
A graph on n vertices is stored as a tuple of n int bitmasks `adj`, adj[v] has
bit u set iff uv is an edge.

psi(H,x) = min over cuts S of sum_{uv in E, u,v on the same side} x_u x_v.
For an integer weight vector a, N = sum a, we have bip(H[a]) = psi(H,a) and the
conjecture for the blow-up H[a] is exactly 25*psi(H,a) <= N^2.
"""

from fractions import Fraction
from itertools import combinations


# ---------------------------------------------------------------- graph6 codec
def g6_decode(s):
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[10:]
    d = [ord(c) - 63 for c in s]
    if d[0] == 63:                      # n >= 63 (not needed here, but correct)
        n = (d[1] << 12) + (d[2] << 6) + d[3]
        rest = d[4:]
    else:
        n = d[0]
        rest = d[1:]
    bits = []
    for v in rest:
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    adj = [0] * n
    i = 0
    for j in range(1, n):
        for i_ in range(j):
            if bits[i]:
                adj[i_] |= 1 << j
                adj[j] |= 1 << i_
            i += 1
    return n, tuple(adj)


def g6_encode(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (adj[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out


# ---------------------------------------------------------------- basic checks
def edges(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def is_triangle_free(n, adj):
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1 and (adj[u] & adj[v]):
                return False
    return True


def is_maximal_tf(n, adj):
    """maximal triangle-free  <=>  triangle-free and every non-adjacent pair has
    a common neighbour."""
    if not is_triangle_free(n, adj):
        return False
    for u in range(n):
        for v in range(u + 1, n):
            if not ((adj[u] >> v) & 1) and not (adj[u] & adj[v]):
                return False
    return True


def is_twin_free(n, adj):
    seen = set()
    for v in range(n):
        # adjacent twins in a triangle-free graph would be a K2 component
        key = adj[v]
        if key in seen:
            return False
        seen.add(key)
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1:
                if (adj[u] & ~(1 << v)) == (adj[v] & ~(1 << u)):
                    return False
    return True


def is_connected(n, adj):
    if n == 0:
        return True
    seen, stack = 1, [0]
    while stack:
        v = stack.pop()
        m = adj[v] & ~seen
        while m:
            b = m & -m
            u = b.bit_length() - 1
            seen |= b
            stack.append(u)
            m ^= b
    return seen == (1 << n) - 1


def mindeg(n, adj):
    return min(bin(adj[v]).count('1') for v in range(n))


def odd_girth(n, adj):
    """length of a shortest odd cycle, or None if bipartite (BFS from each vertex)."""
    best = None
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = [s]
        while q:
            nq = []
            for v in q:
                m = adj[v]
                while m:
                    b = m & -m
                    u = b.bit_length() - 1
                    m ^= b
                    if dist[u] == -1:
                        dist[u] = dist[v] + 1
                        nq.append(u)
                    elif dist[u] == dist[v]:
                        c = dist[u] + dist[v] + 1
                        if best is None or c < best:
                            best = c
            q = nq
    return best


def has_c5(n, adj):
    """induced 5-cycle; in a triangle-free graph any C5 subgraph is induced."""
    for a, b, c, d, e in combinations(range(n), 5):
        for perm in ((a, b, c, d, e), (a, b, c, e, d), (a, b, d, c, e),
                     (a, b, d, e, c), (a, b, e, c, d), (a, b, e, d, c),
                     (a, c, b, d, e), (a, c, b, e, d), (a, c, d, b, e),
                     (a, c, e, b, d), (a, d, b, c, e), (a, d, c, b, e)):
            p, q, r, s, t = perm
            if ((adj[p] >> q) & 1 and (adj[q] >> r) & 1 and (adj[r] >> s) & 1
                    and (adj[s] >> t) & 1 and (adj[t] >> p) & 1):
                return True
    return False


# ------------------------------------------------------- cuts / bip / psi core
def all_cut_masks(n):
    """one representative per bipartition (fix vertex 0 on side 0)."""
    return range(1 << (n - 1))


def mono_edges_of_cut(n, adj, S):
    """S is a bitmask of the side containing vertex 0 is not enforced here."""
    return [(u, v) for u in range(n) for v in range(u + 1, n)
            if (adj[u] >> v) & 1 and (((S >> u) & 1) == ((S >> v) & 1))]


def psi(n, adj, a):
    """exact min over cuts of sum_{mono uv} a_u a_v.  a: list of numbers
    (ints or Fractions).  Straight O(2^(n-1) * m) enumeration -- reference
    implementation, deliberately dumb so that it is obviously correct."""
    E = edges(n, adj)
    best = None
    for S in range(1 << (n - 1)):
        tot = 0
        for (u, v) in E:
            su = (S >> u) & 1 if u else 0
            sv = (S >> v) & 1 if v else 0
            # vertex 0 pinned to side 0: bit index shifted
            if su == sv:
                tot += a[u] * a[v]
        if best is None or tot < best:
            best = tot
    return best


def psi_fast(n, adj, a):
    """same value, computed with a Gray-code sweep over sign vectors.
    psi = (P + min_y y^T A y / 2) / 2  with y_u = +- a_u, P = sum_{uv in E} a_u a_v.
    Exact for integer or Fraction input."""
    E = edges(n, adj)
    P = sum(a[u] * a[v] for (u, v) in E)
    y = list(a)                      # all +1 signs
    h = [sum(y[u] for u in range(n) if (adj[v] >> u) & 1) for v in range(n)]
    cur = sum(y[u] * y[v] for (u, v) in E)      # = (1/2) y^T A y
    best = cur
    sign = [1] * n
    # Gray code over vertices 1..n-1 (vertex 0 sign fixed)
    g = 0
    for i in range(1, 1 << (n - 1)):
        j = (i & -i).bit_length() - 1          # bit that flips
        v = j + 1
        cur -= 2 * y[v] * h[v]                 # removing v's contribution twice
        y[v] = -y[v]
        sign[v] = -sign[v]
        d = 2 * y[v]                           # change of y[v] is 2*new value
        m = adj[v]
        while m:
            b = m & -m
            u = b.bit_length() - 1
            m ^= b
            h[u] += d
        h[v] = sum(y[u] for u in range(n) if (adj[v] >> u) & 1)
        if cur < best:
            best = cur
    return (P + best) // 2 if all(isinstance(t, int) for t in a) else (P + best) / 2


def bip(n, adj):
    return psi_fast(n, adj, [1] * n)


# ------------------------------------------------------------- C5 homomorphism
C5ADJ = tuple(((1 << ((i + 1) % 5)) | (1 << ((i + 4) % 5))) for i in range(5))


def hom_to_C5(n, adj):
    """backtracking search for a homomorphism V(H) -> Z_5 with |phi(u)-phi(v)|=1
    mod 5 on every edge.  Returns the colouring or None."""
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count('1'))
    col = [-1] * n

    def bt(i):
        if i == n:
            return True
        v = order[i]
        allowed = 31
        for u in range(n):
            if (adj[v] >> u) & 1 and col[u] >= 0:
                allowed &= C5ADJ[col[u]]
        lo = 5 if i > 0 else 1        # symmetry: fix colour of first vertex
        for c in range(min(lo, 5)):
            if (allowed >> c) & 1:
                col[v] = c
                if bt(i + 1):
                    return True
                col[v] = -1
        return False

    return col if bt(0) else None


# ------------------------------------------------------------------- reduction
def reduce_pattern(n, adj):
    """merge non-adjacent twins (this preserves max_x psi exactly, see report),
    then re-maximalise is NOT done here -- returns the twin-free graph."""
    while True:
        n_, adj_ = n, list(adj)
        found = None
        for u in range(n):
            for v in range(u + 1, n):
                if not ((adj[u] >> v) & 1) and adj[u] == adj[v]:
                    found = (u, v)
                    break
            if found:
                break
        if not found:
            return n, tuple(adj)
        u, v = found
        keep = [w for w in range(n) if w != v]
        idx = {w: i for i, w in enumerate(keep)}
        m = len(keep)
        na = [0] * m
        for w in keep:
            for z in keep:
                if (adj[w] >> z) & 1:
                    na[idx[w]] |= 1 << idx[z]
        n, adj = m, tuple(na)


# --------------------------------------------------------------- named graphs
def cayleyZ(m, S):
    adj = [0] * m
    for i in range(m):
        for s in S:
            adj[i] |= 1 << ((i + s) % m)
            adj[i] |= 1 << ((i - s) % m)
    for i in range(m):
        adj[i] &= ~(1 << i)
    return m, tuple(adj)


def cycle(m):
    return cayleyZ(m, [1])


def complete_bipartite(p, q):
    n = p + q
    adj = [0] * n
    for i in range(p):
        for j in range(p, n):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    return n, tuple(adj)


def petersen():
    verts = list(combinations(range(5), 2))
    n = 10
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if not (set(verts[i]) & set(verts[j])):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return n, tuple(adj)


def grotzsch():
    # Mycielskian of C5: u0..u4 (C5), v0..v4 (copies), w
    n = 11
    adj = [0] * n

    def add(a, b):
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    for i in range(5):
        add(i, (i + 1) % 5)
    for i in range(5):
        for j in ((i + 1) % 5, (i + 4) % 5):
            add(5 + i, j)
        add(5 + i, 10)
    return n, tuple(adj)


def andrasfai(k):
    """And(k): circulant on Z_{3k-1} with connection set {1,4,7,...,3k-2}
    (the residues = 1 mod 3).  And(2)=C5, And(3)=Moebius-Kantor-like 8-vertex."""
    m = 3 * k - 1
    S = [i for i in range(1, m) if i % 3 == 1 and i <= m // 2]
    S2 = [i for i in range(1, m // 2 + 1) if i % 3 == 1 or (m - i) % 3 == 1]
    return cayleyZ(m, S2)


def clebsch():
    """the 16-vertex Clebsch graph (folded 5-cube): triangle-free, 5-regular."""
    n = 16
    adj = [0] * n
    for i in range(n):
        for k in range(4):
            adj[i] |= 1 << (i ^ (1 << k))
        adj[i] |= 1 << (i ^ 15)
    return n, tuple(adj)


def kneser52():
    return petersen()
