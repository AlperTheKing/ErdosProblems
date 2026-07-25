"""R8 entropy/counting lane -- core exact machinery for Erdos #23.

Everything on an acceptance path is exact integer arithmetic (Python ints /
fractions.Fraction).  Floats appear only in diagnostic printouts.

Objects
-------
Graph: (n, edges) with edges a sorted list of (u,v), u<v.
bip(H, a):  exact min over all 2^(n-1) cuts of sum_{uv mono} a_u a_v   (= psi * (sum a)^2)
PRGM:       the x-adapted Z5-rotation geometric-mean certificate, see R8_entropy.md.

Rotation cuts.  For phi: V -> Z5 and r in Z5 the bipartition is
    B_r = phi^{-1}({r, r+2, r+4}),   S_r = phi^{-1}({r+1, r+3}).
An edge uv with (phi_u, phi_v) = (a, a+1) is monochromatic iff r = a+1.
An edge with phi_u = phi_v = a is monochromatic for every r.
An edge with (phi_u, phi_v) = (a, a+2) is monochromatic iff r in {a, a-1, a-2}.
Hence, with
    E1[p] = weight of edges joining class p to class p+1,
    E2[p] = weight of edges joining class p to class p+2,
    Z     = weight of edges inside classes,
    m_r = E1[r-1] + Z + E2[r] + E2[r+1] + E2[r+2].
"""

from fractions import Fraction
from itertools import product as iproduct

# ----------------------------------------------------------------- graphs


def cycle(n):
    return (n, [(i, (i + 1) % n) if i + 1 < n else (0, n - 1) for i in range(n)])


def blowup(g, a):
    """Blow up graph g by the integer vector a (zero classes allowed)."""
    n, edges = g
    assert len(a) == n
    start, idx = [], 0
    for i in range(n):
        start.append(idx)
        idx += a[i]
    E = []
    for (u, v) in edges:
        for p in range(a[u]):
            for q in range(a[v]):
                x, y = start[u] + p, start[v] + q
                E.append((min(x, y), max(x, y)))
    return (idx, sorted(set(E)))


def petersen():
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))          # outer C5
        E.append((i, 5 + i))                 # spokes
        E.append((5 + i, 5 + (i + 2) % 5))   # inner pentagram
    return (10, sorted(set((min(u, v), max(u, v)) for u, v in E)))


def grotzsch():
    """Mycielskian of C5.  0..4 = C5, 5..9 = shadows (i+5 copies i), 10 = apex."""
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((5 + i, 10))
    return (11, sorted(set((min(u, v), max(u, v)) for u, v in E)))


def andrasfai(k):
    """And(k): circulant on Z_{3k-1} with connection set {i = 1 mod 3}.
    And(2) = C5, And(3) = Wagner graph V8 = C8(1,4), And(4) has 11 vertices."""
    p = 3 * k - 1
    S = [i for i in range(1, p) if i % 3 == 1]
    E = set()
    for v in range(p):
        for s in S:
            u = (v + s) % p
            E.add((min(u, v), max(u, v)))
    return (p, sorted(E))


def wagner():
    """Wagner / Moebius-Kantor V8: u~v iff 3*circdist(u,v) > 8 on Z8."""
    E = set()
    for u in range(8):
        for v in range(u + 1, 8):
            d = min((u - v) % 8, (v - u) % 8)
            if 3 * d > 8:
                E.add((u, v))
    return (8, sorted(E))


def complete_bipartite(p, q):
    return (p + q, sorted((i, p + j) for i in range(p) for j in range(q)))


def kneser_clebsch():
    """Clebsch graph (folded 5-cube), triangle-free, 16 vertices, 5-regular."""
    E = set()
    for u in range(16):
        for v in range(u + 1, 16):
            x = u ^ v
            if bin(x).count("1") in (1, 4):
                E.add((u, v))
    return (16, sorted(E))


def is_triangle_free(g):
    n, edges = g
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True


# ------------------------------------------------------- exact bip / psi


def bip_weighted(g, a):
    """Exact min over all cuts of sum_{uv monochromatic} a_u a_v (integers)."""
    n, edges = g
    best = None
    for mask in range(1 << (n - 1)):
        tot = 0
        for (u, v) in edges:
            bu = (mask >> u) & 1 if u < n - 1 else 0
            bv = (mask >> v) & 1 if v < n - 1 else 0
            if bu == bv:
                tot += a[u] * a[v]
        if best is None or tot < best:
            best = tot
            bestmask = mask
    return best, bestmask


def bip(g):
    n, _ = g
    return bip_weighted(g, [1] * n)[0]


# ------------------------------------------------------------- PRGM


def rotation_values(g, a, phi):
    """The five monochromatic weights m_0..m_4 of the rotation cuts of phi."""
    n, edges = g
    E1 = [0] * 5
    E2 = [0] * 5
    Z = 0
    for (u, v) in edges:
        w = a[u] * a[v]
        d = (phi[u] - phi[v]) % 5
        if d == 0:
            Z += w
        elif d == 1:            # phi_u = phi_v + 1 : pair (phi_v, phi_v+1)
            E1[phi[v]] += w
        elif d == 4:            # phi_v = phi_u + 1
            E1[phi[u]] += w
        elif d == 2:            # pair (phi_v, phi_v+2)
            E2[phi[v]] += w
        else:                   # d == 3, pair (phi_u, phi_u+2)
            E2[phi[u]] += w
    m = []
    for r in range(5):
        m.append(E1[(r - 1) % 5] + Z + E2[r % 5] + E2[(r + 1) % 5] + E2[(r + 2) % 5])
    return m


def rotation_cut_check(g, a, phi, r):
    """Independent re-derivation of m_r straight from the bipartition."""
    n, edges = g
    big = {(r + 0) % 5, (r + 2) % 5, (r + 4) % 5}
    side = [1 if phi[v] in big else 0 for v in range(n)]
    return sum(a[u] * a[v] for (u, v) in edges if side[u] == side[v])


def prgm_bruteforce(g, a):
    """min over all phi: V -> Z5 of prod_r m_r, by exhaustive search
    (phi[0] fixed to 0 by rotation invariance).  Returns (value, phi)."""
    n, _ = g
    best, bestphi = None, None
    for tail in iproduct(range(5), repeat=n - 1):
        phi = (0,) + tail
        m = rotation_values(g, a, phi)
        p = 1
        for t in m:
            p *= t
        if best is None or p < best:
            best, bestphi = p, phi
    return best, bestphi


def prgm_target(q):
    """prod_r m_r <= q^10 / 5^10 is the certificate; return (5^10, q^10)."""
    return 5 ** 10, q ** 10
