"""H2 family utilities: exact graph6 <-> adjacency, exact maxcut, exact bip.

Integer arithmetic only.  maxcut for N <= 30 by exhaustive Gray-code enumeration
of all 2^(N-1) bipartitions (vertex 0 fixed).  For larger N use h2_cpsat.py.
"""
import itertools


def g6_decode(s):
    """graph6 string -> (n, adjacency as list of int bitmasks). n <= 62 only."""
    s = s.strip()
    b = [ord(c) - 63 for c in s]
    n = b[0]
    assert 0 <= n <= 62, "only n<=62 supported"
    bits = []
    for x in b[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


def g6_encode(n, adj):
    """(n, adjacency bitmasks) -> graph6 string."""
    assert n <= 62
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (adj[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for t in range(6):
            v = (v << 1) | bits[k + t]
        out += chr(v + 63)
    return out


def edges_to_adj(n, edges):
    adj = [0] * n
    for u, v in edges:
        assert u != v
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def adj_to_edges(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def num_edges(n, adj):
    return sum(bin(adj[i]).count("1") for i in range(n)) // 2


def is_triangle_free(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                if adj[i] & adj[j]:
                    return False
    return True


def maxcut_exhaustive(n, adj):
    """Exact maxcut by Gray-code enumeration over 2^(n-1) bipartitions."""
    assert n <= 30, "too large for exhaustive"
    deg = [bin(adj[i]).count("1") for i in range(n)]
    S = 1
    cut = deg[0]
    best = cut
    steps = 1 << (n - 1)
    for k in range(1, steps):
        v = ((k & -k).bit_length() - 1) + 1
        bit = 1 << v
        a = bin(adj[v] & S).count("1")
        if S & bit:
            cut += 2 * a - deg[v]
            S &= ~bit
        else:
            cut += deg[v] - 2 * a
            S |= bit
        if cut > best:
            best = cut
    return best


def bip_exhaustive(n, adj):
    return num_edges(n, adj) - maxcut_exhaustive(n, adj)


# ---------- blow-up machinery ----------

def blowup(base_n, base_edges, parts):
    """Blow up base graph (base_n vertices, edge list) with part sizes `parts`.
    Returns (N, adj).  Parts are independent sets; base edges become complete
    bipartite.  Base must be triangle-free for the blow-up to be triangle-free."""
    assert len(parts) == base_n
    offs = [0] * (base_n + 1)
    for i in range(base_n):
        offs[i + 1] = offs[i] + parts[i]
    N = offs[base_n]
    adj = [0] * N
    for (u, v) in base_edges:
        for a in range(offs[u], offs[u + 1]):
            for b in range(offs[v], offs[v + 1]):
                adj[a] |= 1 << b
                adj[b] |= 1 << a
    return N, adj, offs


def compositions(total, k, lo=0):
    """All k-tuples of ints >= lo summing to total."""
    if k == 1:
        if total >= lo:
            yield (total,)
        return
    for x in range(lo, total - lo * (k - 1) + 1):
        for rest in compositions(total - x, k - 1, lo):
            yield (x,) + rest


C5_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
C7_EDGES = [(i, (i + 1) % 7) for i in range(7)]
PETERSEN_EDGES = ([(i, (i + 1) % 5) for i in range(5)] +
                  [(i, i + 5) for i in range(5)] +
                  [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
# Andrasfai graph And(k): circulant on Z_{3k-1} with connection set
# {i : i = 1 mod 3}.  And(2)=C5, And(3)=Mobius-Kantor? no: And(3) is on 8 vertices
def andrasfai(k):
    n = 3 * k - 1
    S = set()
    for d in range(1, n):
        if d % 3 == 1:
            S.add(d % n)
            S.add((-d) % n)
    edges = sorted({(min(i, (i + d) % n), max(i, (i + d) % n))
                    for i in range(n) for d in S})
    return n, edges


def circulant(n, S):
    edges = sorted({(min(i, (i + d) % n), max(i, (i + d) % n))
                    for i in range(n) for d in S if d % n != 0})
    return n, edges


def wagner():
    # Mobius-Kantor ladder V8 = Wagner graph = Mobius-Kantor graph on 8 vertices
    return circulant(8, [1, 4])


def mobius_kantor():
    # Mobius-Kantor graph: generalized Petersen GP(8,3), 16 vertices, girth 6
    edges = [(i, (i + 1) % 8) for i in range(8)]
    edges += [(i, 8 + i) for i in range(8)]
    edges += [(8 + i, 8 + (i + 3) % 8) for i in range(8)]
    edges = sorted({(min(a, b), max(a, b)) for a, b in edges})
    return 16, edges


def kneser52():
    # Petersen graph = K(5,2)
    return 10, PETERSEN_EDGES
