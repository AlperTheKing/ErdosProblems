"""R8 transport/flow mechanism: exact core library for Erdos #23.

Everything decisive is exact (Fraction / integers).  Floats only guide search.

Notation used throughout:
  G          graph on N vertices, adjacency as frozensets / bitmasks
  cut S      subset of V, encoded as an N-bit int mask
  mono(S)    edges with both ends on the same side of the cut S
  U(S)       set of vertices incident to at least one monochromatic edge
  bip(G)     min_S |mono(S)|            (= |E| - maxcut)
  psi(G,x)   min_S sum_{uv in mono(S)} x_u x_v        (x on the simplex)
"""
from fractions import Fraction
from itertools import combinations

# ---------------------------------------------------------------- graph6 I/O


def g6_decode(s):
    """graph6 string -> (n, list of edges).  Handles n < 63 only (enough here)."""
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for d in data[1:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


class Graph:
    def __init__(self, n, edges, name="G"):
        self.n = n
        self.name = name
        self.edges = sorted(tuple(sorted(e)) for e in set(tuple(sorted(e)) for e in edges))
        self.adj = [0] * n
        for u, v in self.edges:
            self.adj[u] |= 1 << v
            self.adj[v] |= 1 << u

    @property
    def m(self):
        return len(self.edges)

    def triangle_free(self):
        for u, v in self.edges:
            if self.adj[u] & self.adj[v]:
                return False
        return True

    def induced_edges(self, mask):
        return [(u, v) for (u, v) in self.edges if (mask >> u) & 1 and (mask >> v) & 1]

    def mono_edges(self, S):
        """edges monochromatic under the bipartition (S, V\\S)."""
        out = []
        for u, v in self.edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                out.append((u, v))
        return out

    def all_cuts(self):
        """one representative per bipartition (S and its complement identified)."""
        return range(1 << (self.n - 1))

    def bip(self):
        best = self.m
        for S in self.all_cuts():
            c = sum(1 for u, v in self.edges if ((S >> u) & 1) == ((S >> v) & 1))
            if c < best:
                best = c
        return best

    def __repr__(self):
        return "Graph(%s, n=%d, m=%d)" % (self.name, self.n, self.m)


# ---------------------------------------------------------------- constructions


def cycle(n, name=None):
    return Graph(n, [(i, (i + 1) % n) for i in range(n)], name or "C%d" % n)


def complete_bipartite(a, b):
    return Graph(a + b, [(i, a + j) for i in range(a) for j in range(b)], "K_{%d,%d}" % (a, b))


def blowup(H, parts, name=None):
    """H[parts]: replace vertex i of H by an independent set of size parts[i]."""
    off, idx = [], 0
    for p in parts:
        off.append(idx)
        idx += p
    edges = []
    for u, v in H.edges:
        for a in range(parts[u]):
            for b in range(parts[v]):
                edges.append((off[u] + a, off[v] + b))
    return Graph(idx, edges, name or "%s[%s]" % (H.name, ",".join(map(str, parts))))


def circulant(n, dists, name=None):
    edges = []
    for i in range(n):
        for d in dists:
            edges.append((i, (i + d) % n))
    return Graph(n, edges, name or "Circ(%d;%s)" % (n, dists))


def andrasfai(k):
    """And(k) = circulant on Z_{3k-1} with connection set {k,...,2k-1}."""
    n = 3 * k - 1
    return circulant(n, list(range(k, (n // 2) + 1)), "And(%d)" % k)


def wagner():
    """Wagner / Moebius-Kantor V8 = And(3): u~v iff 3*circdist > 8."""
    n = 8
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            d = min(j - i, n - (j - i))
            if 3 * d > n:
                edges.append((i, j))
    return Graph(n, edges, "Wagner")


def petersen():
    edges = [(i, (i + 1) % 5) for i in range(5)]
    edges += [(i, 5 + i) for i in range(5)]
    edges += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return Graph(10, edges, "Petersen")


def mycielski(H, name=None):
    n = H.n
    edges = list(H.edges)
    for u, v in H.edges:
        edges.append((u, n + v))
        edges.append((v, n + u))
    for i in range(n):
        edges.append((n + i, 2 * n))
    return Graph(2 * n + 1, edges, name or "M(%s)" % H.name)


def grotzsch():
    return mycielski(cycle(5), "Grotzsch")


def from_g6(s, name=None):
    n, e = g6_decode(s)
    return Graph(n, e, name or s)


# ---------------------------------------------------------------- exact psi


def psi_exact(G, x):
    """psi(G,x) = min over cuts of the monochromatic weight.  x: list of Fractions."""
    best = None
    for S in G.all_cuts():
        s = Fraction(0)
        for u, v in G.edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                s += x[u] * x[v]
        if best is None or s < best:
            best = s
    return best


def mono_profile(G):
    """For every cut S return (mask of U(S), |mono|, mono edge list, bipartite? parts)."""
    out = []
    for S in G.all_cuts():
        mono = G.mono_edges(S)
        U = 0
        for u, v in mono:
            U |= (1 << u) | (1 << v)
        out.append((S, U, mono))
    return out


def two_colour(mono, n):
    """proper 2-colouring of the mono graph, or None if it has an odd cycle.

    returns (A, B) as bitmasks over the vertices touched by mono."""
    adj = {}
    for u, v in mono:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    colour = {}
    for s in adj:
        if s in colour:
            continue
        colour[s] = 0
        stack = [s]
        while stack:
            a = stack.pop()
            for b in adj[a]:
                if b not in colour:
                    colour[b] = 1 - colour[a]
                    stack.append(b)
                elif colour[b] == colour[a]:
                    return None
    A = B = 0
    for v, c in colour.items():
        if c == 0:
            A |= 1 << v
        else:
            B |= 1 << v
    return (A, B)


def popcount(x):
    return bin(x).count("1")


TESTBED = None


def testbed():
    """the mandated regression list."""
    global TESTBED
    if TESTBED is None:
        C5 = cycle(5)
        TESTBED = [
            C5,
            blowup(C5, [2, 2, 2, 2, 2]),
            blowup(C5, [3, 1, 2, 2, 1]),
            blowup(C5, [2, 3, 1, 1, 0]),
            petersen(),
            grotzsch(),
            wagner(),
            cycle(7),
            complete_bipartite(3, 3),
            from_g6("M?AE@bH{AYN_LgBs?", "N14extremal"),
        ]
    return TESTBED
