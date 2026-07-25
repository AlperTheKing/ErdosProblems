"""G4 stability round-2 library.

Exact integer arithmetic only.  No floating point on any acceptance path.

Contents
--------
 - graph6 decoding
 - exact bip(G) = |E| - maxcut(G) by exhaustive enumeration of all 2^(N-1) cuts
 - exact 5-cycle count
 - C5-colourability (homomorphism to C5) by backtracking
 - C5 blow-up construction
"""

from itertools import combinations


# ---------------------------------------------------------------- graph6
def g6_decode(s):
    """graph6 string -> (n, set of frozenset edges).  Handles n < 63 only."""
    if isinstance(s, str):
        b = s.encode()
    else:
        b = s
    assert b[0] != 126, "n >= 63 not supported"
    n = b[0] - 63
    bits = []
    for c in b[1:]:
        v = c - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    edges = set()
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.add((i, j))
            idx += 1
    return n, edges


def adj_from_edges(n, edges):
    a = [0] * n
    for (i, j) in edges:
        a[i] |= 1 << j
        a[j] |= 1 << i
    return a


# ---------------------------------------------------------------- exact bip
def exact_bip(n, adj):
    """Minimum over all bipartitions of the number of monochromatic edges.

    Exhaustive over the 2^(n-1) cuts containing vertex 0 on side 0.
    Exact integers.  n <= 22 or so.
    """
    best = None
    full = (1 << n) - 1
    for S in range(1 << (n - 1)):          # vertex 0 always on side 0
        S <<= 1
        T = full ^ S
        mono = 0
        m = S
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            mono += bin(adj[v] & S).count("1")
        m = T
        while m:
            v = (m & -m).bit_length() - 1
            m &= m - 1
            mono += bin(adj[v] & T).count("1")
        mono >>= 1
        if best is None or mono < best:
            best = mono
            if best == 0:
                return 0
    return best


def n_edges(adj):
    return sum(bin(a).count("1") for a in adj) // 2


# ---------------------------------------------------------------- 5-cycles
def count_c5(n, adj):
    """Exact number of 5-cycles (as subgraphs)."""
    total = 0
    for a in range(n):
        for b in range(a + 1, n):
            if not (adj[a] >> b) & 1:
                continue
            # count paths a - x - y - z - b with x,y,z > a, all distinct, != a,b
            for x in range(a + 1, n):
                if x == b or not (adj[a] >> x) & 1:
                    continue
                for y in range(a + 1, n):
                    if y in (b, x) or not (adj[x] >> y) & 1:
                        continue
                    for z in range(a + 1, n):
                        if z in (b, x, y) or not (adj[y] >> z) & 1:
                            continue
                        if (adj[z] >> b) & 1:
                            total += 1
    # each 5-cycle counted: min vertex a fixed, its two neighbours in the cycle
    # play the roles of b and x, and the traversal has 2 directions => 2 times.
    assert total % 2 == 0
    return total // 2


def has_triangle(n, adj):
    for i in range(n):
        m = adj[i]
        while m:
            j = (m & -m).bit_length() - 1
            m &= m - 1
            if j > i and (adj[i] & adj[j]):
                return True
    return False


# ---------------------------------------------------------------- hom to C5
def hom_to_c5(n, adj):
    """True iff there is phi: V -> Z_5 with |phi(u)-phi(v)| = 1 mod 5 on edges."""
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))
    pos = {v: i for i, v in enumerate(order)}
    phi = [None] * n

    def bt(k):
        if k == n:
            return True
        v = order[k]
        cands = range(5) if k else [0]
        for c in cands:
            ok = True
            m = adj[v]
            while m:
                u = (m & -m).bit_length() - 1
                m &= m - 1
                if phi[u] is not None and (c - phi[u]) % 5 not in (1, 4):
                    ok = False
                    break
            if ok:
                phi[v] = c
                if bt(k + 1):
                    return True
                phi[v] = None
        return False

    return bt(0)


# ---------------------------------------------------------------- blow-ups
def c5_blowup(parts):
    """parts = (n0,...,n4).  Returns (N, adj, part_of) with parts laid out in order."""
    N = sum(parts)
    off = [0] * 5
    s = 0
    for i in range(5):
        off[i] = s
        s += parts[i]
    adj = [0] * N
    part_of = [0] * N
    for i in range(5):
        for j in range(parts[i]):
            part_of[off[i] + j] = i
    for i in range(5):
        k = (i + 1) % 5
        for a in range(parts[i]):
            for b in range(parts[k]):
                u, v = off[i] + a, off[k] + b
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return N, adj, part_of


def blowup_graph(n, adj, t):
    """balanced blow-up H[t]."""
    N = n * t
    A = [0] * N
    for u in range(n):
        for v in range(n):
            if (adj[u] >> v) & 1:
                for a in range(t):
                    for b in range(t):
                        A[u * t + a] |= 1 << (v * t + b)
    return N, A
