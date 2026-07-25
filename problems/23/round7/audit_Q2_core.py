"""audit_Q2_core.py -- INDEPENDENT re-implementation for the audit of round7/Q2.md.

Nothing is imported from Q2_*.py.  Own graph6 decoder, own max-cut, own switching
algebra.  Everything is Python int / Fraction -- no float anywhere on an
acceptance path.

Vertex-level representation only:  a graph is (n, adj) with adj a list of int
bitmasks.  Blow-ups are EXPANDED to vertices, so no "multilinearity" shortcut is
trusted; the pattern-level shortcuts of Q2.md are checked against it.
"""
from fractions import Fraction as F
from itertools import product, combinations

# ------------------------------------------------------------------ graph6 (own)


def g6_decode(s):
    """graph6 -> (n, adjacency bitmask list).  Written from the format spec:
    first byte(s) encode n (n<63: one byte n+63); then ceil(n(n-1)/2 / 6) bytes,
    each carrying 6 bits (value-63, big-endian within the byte), the bit stream
    listing the upper triangle column by column: (0,1),(0,2),(1,2),(0,3),...
    """
    s = s.strip()
    data = [ord(c) - 63 for c in s]
    if data[0] == 63:                     # 63 marker -> longer n encoding
        n = (data[1] << 12) | (data[2] << 6) | data[3]
        rest = data[4:]
    else:
        n = data[0]
        rest = data[1:]
    bits = []
    for d in rest:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


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


# ------------------------------------------------------------------ basic graph ops

def edges_of(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def is_triangle_free(n, adj):
    for i, j in edges_of(n, adj):
        if adj[i] & adj[j]:
            return False
    return True


def is_maximal_tf(n, adj):
    if not is_triangle_free(n, adj):
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if not ((adj[i] >> j) & 1):
                if adj[i] & adj[j] == 0:       # no common neighbour -> can add ij
                    return False
    return True


def popcount(x):
    return bin(x).count('1')


def mono_count(n, adj, X):
    """X = bitmask of side-1 vertices.  Returns number of monochromatic edges."""
    m = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                if (((X >> i) & 1) == ((X >> j) & 1)):
                    m += 1
    return m


def maxcut_bip(n, adj):
    """bip(G) = |E| - maxcut(G) = min over cuts of the monochromatic count.
    Own routine: exhaustive over 2^(n-1) cuts (vertex 0 pinned)."""
    best = None
    for X in range(1 << (n - 1)):
        m = mono_count(n, adj, X)
        if best is None or m < best:
            best = m
    return best


def all_min_cuts(n, adj):
    b = maxcut_bip(n, adj)
    return [X for X in range(1 << (n - 1)) if mono_count(n, adj, X) == b]


# ------------------------------------------------------------------ switching algebra

def sigma_vec(n, adj, X):
    sg = []
    for v in range(n):
        db = dm = 0
        for w in range(n):
            if (adj[v] >> w) & 1:
                if ((X >> v) & 1) == ((X >> w) & 1):
                    dm += 1
                else:
                    db += 1
        sg.append(db - dm)
    return sg


def delta_set(n, adj, X, S):
    """Direct definition: Delta(S) = mono(X) - mono(X xor S)  (gain in cut size).
    NO use of the sigma formula -- this is the honest definition used to CHECK
    Lemma 1 of Q2.md."""
    return mono_count(n, adj, X) - mono_count(n, adj, X ^ S)


def delta_formula(n, adj, X, S, sg=None):
    """Lemma 1 of Q2.md:  Delta(S) = -sum_S sigma - 2 e_M(S) + 2 e_B(S)."""
    if sg is None:
        sg = sigma_vec(n, adj, X)
    val = 0
    for v in range(n):
        if (S >> v) & 1:
            val -= sg[v]
    for i in range(n):
        if not ((S >> i) & 1):
            continue
        for j in range(i + 1, n):
            if not ((S >> j) & 1):
                continue
            if (adj[i] >> j) & 1:
                if ((X >> i) & 1) == ((X >> j) & 1):
                    val -= 2
                else:
                    val += 2
    return val


# ------------------------------------------------------------------ blow-up builder

def blowup(h, pat_edges, a):
    """Expand pattern (h, edges) with part sizes a into a vertex-level graph."""
    n = sum(a)
    start = []
    t = 0
    for i in range(h):
        start.append(t)
        t += a[i]
    adj = [0] * n
    for (i, j) in pat_edges:
        for u in range(start[i], start[i] + a[i]):
            for v in range(start[j], start[j] + a[j]):
                adj[u] |= 1 << v
                adj[v] |= 1 << u
    return n, adj, start


C5E = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
P4E = [(0, 1), (1, 2), (2, 3)]
