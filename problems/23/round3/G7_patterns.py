"""
G7_patterns.py -- explicit constructions of the Brandt-Thomasse pattern list.

Builds, from the *verbatim* definitions in
  S. Brandt, S. Thomasse, "Dense triangle-free graphs are four-colorable:
  A solution to the Erdos-Simonovits problem", p.3 (Gamma_i) and p.4 (Vega),
and from
  P. Heinig, arXiv:0907.3928, Definition 1 (Andrasfai graphs And_k),
the graphs

  Gamma_i = And(i)          3i-1 vertices, i-regular          (i >= 1)
  Upsilon_i                 3i+7 vertices                     (i >= 2)
  Upsilon_i - {y}           3i+6 vertices
  Upsilon_i - {2i}          3i+6 vertices
  Upsilon_i - {y,2i}        3i+5 vertices   (i=2 -> Grotzsch)

and verifies EXACTLY (integer arithmetic only):
  * the two published definitions of the Andrasfai graph agree up to isomorphism,
  * every graph is triangle-free,
  * every graph is maximal triangle-free (diameter <= 2),
  * every graph is twin-free,
  * the Brandt-Thomasse Theorem 3 integer weight function is REGULAR with the
    stated degree and stated total weight (this pins the adjacency down),
  * Brandt's Lemma 2 (max weight of a stable set <= delta),
  * chromatic number (3 for Gamma_i, 4 for Vega),
  * Upsilon_2 - {y,4} is isomorphic to the Grotzsch graph,
  * Upsilon_2 - {y} is isomorphic to Upsilon_2 - {4}  (flagged in BT p.4).

Outputs G7_patterns.g6 and G7_patterns_names.txt.
"""
import itertools, sys, os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------- graph type
class G:
    def __init__(self, verts):
        self.V = list(verts)
        self.idx = {v: i for i, v in enumerate(self.V)}
        self.adj = {v: set() for v in self.V}

    def add(self, u, v):
        assert u != v, (u, v)
        assert u in self.adj and v in self.adj, (u, v)
        self.adj[u].add(v)
        self.adj[v].add(u)

    def n(self):
        return len(self.V)

    def edges(self):
        return [(u, v) for i, u in enumerate(self.V) for v in self.V[i + 1:]
                if v in self.adj[u]]

    def m(self):
        return len(self.edges())

    def deg(self, v):
        return len(self.adj[v])

    def induced(self, S):
        S = list(S)
        h = G(S)
        for i, u in enumerate(S):
            for v in S[i + 1:]:
                if v in self.adj[u]:
                    h.add(u, v)
        return h

    def matrix(self):
        n = self.n()
        A = [[0] * n for _ in range(n)]
        for u, v in self.edges():
            A[self.idx[u]][self.idx[v]] = 1
            A[self.idx[v]][self.idx[u]] = 1
        return A


# ------------------------------------------------------------- constructions
def gamma(i):
    """Brandt-Thomasse p.3: vertex set {1,...,3i-1}, vertex j has neighbours
       j+i, ..., j+2i-1, taken modulo 3i-1."""
    m = 3 * i - 1
    lab = lambda t: ((t - 1) % m) + 1          # residues -> {1,...,m}
    g = G(range(1, m + 1))
    for j in range(1, m + 1):
        for d in range(i, 2 * i):
            k = lab(j + d)
            if k != j and k not in g.adj[j]:
                g.add(j, k)
    return g


def andrasfai_heinig(k):
    """Heinig arXiv:0907.3928 Definition 1: V = {v_0,...,v_{3k-2}},
       v_i ~ v_j iff |i-j| = 1 (mod 3)."""
    g = G(range(0, 3 * k - 1))
    for a in range(3 * k - 1):
        for b in range(a + 1, 3 * k - 1):
            if (b - a) % 3 == 1:
                g.add(a, b)
    return g


def andrasfai_circulant(k):
    """circulant on Z_{3k-1} with connection set {k, k+1, ..., 2k-1}"""
    m = 3 * k - 1
    g = G(range(m))
    for a in range(m):
        for d in range(k, 2 * k):
            b = (a + d) % m
            if b != a and b not in g.adj[a]:
                g.add(a, b)
    return g


def upsilon(i, drop_y=False, drop_2i=False):
    """Brandt-Thomasse p.4:  'start with a graph Gamma_i on vertex set
       {1,...,3i-1} and add an edge xy and an induced 6-cycle (a,v,c,u,b,w)
       such that x is joined to a,b,c and y is joined to u,v,w.  The set of
       neighbors of a,u on the Gamma_i graph is {1,...,i}.  The set of
       neighbors of b,v on the Gamma_i graph is {i+1,...,2i}.  The set of
       neighbors of c,w on the Gamma_i graph is {2i+1,...,3i-1}.' """
    assert i >= 2
    m = 3 * i - 1
    base = gamma(i)
    extra = ['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w']
    g = G(list(range(1, m + 1)) + extra)
    for p, q in base.edges():
        g.add(p, q)
    g.add('x', 'y')
    for t in ('a', 'b', 'c'):
        g.add('x', t)
    for t in ('u', 'v', 'w'):
        g.add('y', t)
    # induced 6-cycle (a,v,c,u,b,w)
    cyc = ['a', 'v', 'c', 'u', 'b', 'w']
    for t in range(6):
        g.add(cyc[t], cyc[(t + 1) % 6])
    X = list(range(1, i + 1))
    Y = list(range(i + 1, 2 * i + 1))
    Z = list(range(2 * i + 1, 3 * i))
    for j in X:
        g.add('a', j); g.add('u', j)
    for j in Y:
        g.add('b', j); g.add('v', j)
    for j in Z:
        g.add('c', j); g.add('w', j)
    dele = []
    if drop_y:
        dele.append('y')
    if drop_2i:
        dele.append(2 * i)
    keep = [t for t in g.V if t not in dele]
    return g.induced(keep), (X, Y, Z)


def bt_weights(i, drop_y, drop_2i):
    """Brandt-Thomasse Theorem 3 (p.4), verbatim integer weights.
       returns (weightdict, stated_degree, stated_total)."""
    m = 3 * i - 1
    w = {}
    if not drop_y and not drop_2i:                       # Upsilon_i
        for t in ('x', 'y', 1, 2 * i):
            w[t] = 1
        for t in ('c', 'w'):
            w[t] = 3 * i - 3
        for t in ('u', 'v', 'a', 'b'):
            w[t] = 3 * i - 2
        deg, tot = 9 * i - 6, 27 * i - 19
    elif drop_y and not drop_2i:                         # Upsilon_i - {y}
        w[1] = 1; w[2 * i] = 1; w['x'] = 2; w['w'] = 3 * i - 4
        for t in ('u', 'v', 'c'):
            w[t] = 3 * i - 3
        for t in ('a', 'b'):
            w[t] = 3 * i - 2
        deg, tot = 9 * i - 7, 27 * i - 22
    elif not drop_y and drop_2i:                         # Upsilon_i - {2i}
        w['x'] = 1; w['y'] = 1; w[1] = 2; w[i] = 2
        for t in ('b', 'v', 'c', 'w'):
            w[t] = 3 * i - 3
        for t in ('u', 'a'):
            w[t] = 3 * i - 2
        deg, tot = 9 * i - 7, 27 * i - 22
    else:                                                # Upsilon_i - {y,2i}
        for t in ('x', 1, i):
            w[t] = 2
        for t in ('v', 'w'):
            w[t] = 3 * i - 4
        for t in ('u', 'b', 'c'):
            w[t] = 3 * i - 3
        w['a'] = 3 * i - 2
        deg, tot = 9 * i - 8, 27 * i - 25
    return w, deg, tot


def grotzsch():
    """Standard Mycielskian of C5: outer C5 u0..u4, mirrors v0..v4, apex z;
       v_j ~ u_{j-1}, u_{j+1}; z ~ all v_j."""
    g = G(['u%d' % j for j in range(5)] + ['v%d' % j for j in range(5)] + ['z'])
    for j in range(5):
        g.add('u%d' % j, 'u%d' % ((j + 1) % 5))
        g.add('v%d' % j, 'u%d' % ((j + 1) % 5))
        g.add('v%d' % j, 'u%d' % ((j - 1) % 5))
        g.add('z', 'v%d' % j)
    return g


# ------------------------------------------------------------------- checks
def triangle_free(g):
    for u, v in g.edges():
        if g.adj[u] & g.adj[v]:
            return False
    return True


def maximal_triangle_free(g):
    """triangle-free and every non-adjacent pair has a common neighbour"""
    if not triangle_free(g):
        return False
    for a in range(g.n()):
        for b in range(a + 1, g.n()):
            u, v = g.V[a], g.V[b]
            if v not in g.adj[u] and not (g.adj[u] & g.adj[v]):
                return False
    return True


def twin_free(g):
    for a in range(g.n()):
        for b in range(a + 1, g.n()):
            u, v = g.V[a], g.V[b]
            if g.adj[u] == g.adj[v]:
                return False
    return True


def independence_number(g, weights=None):
    """exact max-weight independent set by branch and bound (small graphs)."""
    n = g.n()
    A = [0] * n
    for u, v in g.edges():
        A[g.idx[u]] |= 1 << g.idx[v]
        A[g.idx[v]] |= 1 << g.idx[u]
    if weights is None:
        w = [1] * n
    else:
        w = [weights[v] for v in g.V]
    best = [0]

    def rec(cand, cur):
        if cur + sum(w[t] for t in range(n) if cand >> t & 1) <= best[0]:
            return
        if cand == 0:
            if cur > best[0]:
                best[0] = cur
            return
        # pick vertex of max degree inside cand
        t = max((t for t in range(n) if cand >> t & 1),
                key=lambda t: bin(cand & A[t]).count('1'))
        rec(cand & ~(1 << t) & ~A[t], cur + w[t])       # take t
        rec(cand & ~(1 << t), cur)                      # drop t
    rec((1 << n) - 1, 0)
    return best[0]


def chromatic_number(g, cap=6):
    n = g.n()
    A = [0] * n
    for u, v in g.edges():
        A[g.idx[u]] |= 1 << g.idx[v]
        A[g.idx[v]] |= 1 << g.idx[u]
    order = sorted(range(n), key=lambda t: -bin(A[t]).count('1'))

    def try_k(k):
        col = [-1] * n

        def rec(p):
            if p == n:
                return True
            t = order[p]
            used = set()
            for c in range(k):
                if any(col[s] == c for s in range(n) if A[t] >> s & 1):
                    continue
                if c in used:
                    continue
                col[t] = c
                if rec(p + 1):
                    return True
                col[t] = -1
                if c > max([col[order[j]] for j in range(p)] + [-1]):
                    break      # symmetry break: only one new colour
            return False
        return rec(0)
    for k in range(1, cap + 1):
        if try_k(k):
            return k
    return None


import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher


def to_nx(g):
    h = nx.Graph()
    h.add_nodes_from(range(g.n()))
    for u, v in g.edges():
        h.add_edge(g.idx[u], g.idx[v])
    return h


def isomorphic(g1, g2):
    if g1.n() != g2.n() or g1.m() != g2.m():
        return False
    return nx.is_isomorphic(to_nx(g1), to_nx(g2))


def induced_subgraph_iso(big, small):
    """is `small` isomorphic to an INDUCED subgraph of `big`?"""
    gm = GraphMatcher(to_nx(big), to_nx(small))
    return gm.subgraph_is_isomorphic()


def automorphism_group(g):
    """all automorphisms as tuples (image of index 0..n-1)."""
    h = to_nx(g)
    gm = GraphMatcher(h, h)
    out = []
    for mp in gm.isomorphisms_iter():
        out.append(tuple(mp[t] for t in range(g.n())))
    return out


def graph6(g):
    n = g.n()
    A = g.matrix()
    bits = []
    for j in range(n):
        for i in range(j):
            bits.append(A[i][j])
    out = []
    if n <= 62:
        out.append(chr(n + 63))
    else:
        raise ValueError('n too large for simple graph6')
    while len(bits) % 6:
        bits.append(0)
    for t in range(0, len(bits), 6):
        val = 0
        for b in bits[t:t + 6]:
            val = val * 2 + b
        out.append(chr(val + 63))
    return ''.join(out)


# --------------------------------------------------------------------- main
def main():
    log = []
    P = lambda s: (print(s), log.append(s))

    # --- (0) the three published descriptions of the Andrasfai graph agree
    P('== Andrasfai definition cross-check ==')
    for k in range(2, 8):
        g1 = gamma(k)
        g2 = andrasfai_heinig(k)
        g3 = andrasfai_circulant(k)
        ok12 = isomorphic(g1, g2)
        ok13 = isomorphic(g1, g3)
        regular = all(g1.deg(v) == k for v in g1.V)
        P('  k=%d  |V|=%d(exp %d)  k-regular=%s  BT~Heinig=%s  BT~circulant{k..2k-1}=%s  alpha=%d'
          % (k, g1.n(), 3 * k - 1, regular, ok12, ok13, independence_number(g1)))
        assert g1.n() == 3 * k - 1 and regular and ok12 and ok13

    entries = []          # (name, graph)

    P('')
    P('== Gamma_i = And(i) ==')
    for i in range(1, 9):
        g = gamma(i)
        tf = triangle_free(g)
        mtf = maximal_triangle_free(g)
        tw = twin_free(g)
        al = independence_number(g)
        ch = chromatic_number(g)
        P('  Gamma_%d: n=%d(exp %d) deg=%d(exp %d) tri-free=%s maxTF=%s twin-free=%s alpha=%d chi=%d  delta/n=%s'
          % (i, g.n(), 3 * i - 1, min(g.deg(v) for v in g.V), i, tf, mtf, tw, al, ch,
             Fraction(i, 3 * i - 1)))
        assert g.n() == 3 * i - 1 and tf and mtf
        assert all(g.deg(v) == i for v in g.V)
        if i >= 2:
            assert tw and al == i and ch == 3
        entries.append(('Gamma_%d' % i, g))

    P('')
    P('== Vega graphs (Brandt-Thomasse p.4 + Theorem 3 exact weight check) ==')
    fams = [(False, False, 'Upsilon_%d', lambda i: 3 * i + 7),
            (True, False, 'Upsilon_%d-y', lambda i: 3 * i + 6),
            (False, True, 'Upsilon_%d-2i', lambda i: 3 * i + 6),
            (True, True, 'Upsilon_%d-y-2i', lambda i: 3 * i + 5)]
    for i in range(2, 7):
        for dy, d2, nm, nf in fams:
            g, (X, Y, Z) = upsilon(i, dy, d2)
            name = nm % i
            w, sdeg, stot = bt_weights(i, dy, d2)
            wt = {v: w.get(v, 3) for v in g.V}
            tot = sum(wt.values())
            degs = set(sum(wt[u] for u in g.adj[v]) for v in g.V)
            reg = (len(degs) == 1)
            d = degs.pop() if reg else None
            tf = triangle_free(g)
            mtf = maximal_triangle_free(g)
            tw = twin_free(g)
            al = independence_number(g)
            alw = independence_number(g, wt)
            ch = chromatic_number(g)
            P('  %-16s n=%2d(exp %2d) triFree=%s maxTF=%s twinFree=%s chi=%d alpha=%d | '
              'weights: regular=%s deg=%s(exp %d) total=%d(exp %d) maxWtStable=%d(<=delta:%s)'
              % (name, g.n(), nf(i), tf, mtf, tw, ch, al, reg, d, sdeg, tot, stot,
                 alw, alw <= sdeg))
            assert g.n() == nf(i), name
            assert tf and mtf and tw, name
            assert ch == 4, name
            assert reg and d == sdeg and tot == stot, name
            assert alw <= sdeg, name          # Brandt Lemma 2
            entries.append((name, g))

    P('')
    P('== identifications flagged in the source ==')
    gro = grotzsch()
    v11, _ = upsilon(2, True, True)
    P('  Upsilon_2-{y,4} ~= Grotzsch : %s   (n=%d, m=%d)'
      % (isomorphic(v11, gro), v11.n(), v11.m()))
    assert isomorphic(v11, gro)
    a12, _ = upsilon(2, True, False)
    b12, _ = upsilon(2, False, True)
    P('  Upsilon_2-{y} ~= Upsilon_2-{4} : %s   (BT p.4 parenthetical)'
      % isomorphic(a12, b12))
    for i in range(3, 6):
        a, _ = upsilon(i, True, False)
        b, _ = upsilon(i, False, True)
        P('  Upsilon_%d-{y} ~= Upsilon_%d-{2i} : %s' % (i, i, isomorphic(a, b)))

    P('')
    P('== induced-subgraph containments that COLLAPSE the list ==')
    for i in range(2, 6):
        full, _ = upsilon(i, False, False)
        idx = {v: t for t, v in enumerate(full.V)}
        for dy, d2, nm, _ in fams[1:]:
            sub, _ = upsilon(i, dy, d2)
            keep = [v for v in full.V if v in set(sub.V)]
            ind = full.induced(keep)
            P('  %-16s is an INDUCED subgraph of Upsilon_%d : %s'
              % (nm % i, i, isomorphic(ind, sub)))
            assert isomorphic(ind, sub)
        gi = gamma(i)
        ind = full.induced([v for v in full.V if isinstance(v, int)])
        P('  Gamma_%d          is an INDUCED subgraph of Upsilon_%d : %s'
          % (i, i, isomorphic(ind, gi)))
        assert isomorphic(ind, gi)
    for i in range(2, 6):
        a, _ = upsilon(i, False, False)
        b, _ = upsilon(i + 1, False, False)
        P('  Upsilon_%d induced in Upsilon_%d : %s'
          % (i, i + 1, induced_subgraph_iso(b, a)))
        P('  Gamma_%d   induced in Gamma_%d   : %s'
          % (i, i + 1, induced_subgraph_iso(gamma(i + 1), gamma(i))))
        aa, _ = upsilon(i, True, True)
        P('  Upsilon_%d-y-2i induced in Upsilon_%d-y-2i : %s'
          % (i, i + 1, induced_subgraph_iso(upsilon(i + 1, True, True)[0], aa)))

    P('')
    P('== |Aut| of the small patterns ==')
    for name, g in entries:
        if g.n() <= 14:
            P('  %-16s |Aut| = %d' % (name, len(automorphism_group(g))))

    # ---- emit graph6
    g6 = os.path.join(HERE, 'G7_patterns.g6')
    nm = os.path.join(HERE, 'G7_patterns_names.txt')
    with open(g6, 'w') as f6, open(nm, 'w') as fn:
        for name, g in entries:
            f6.write(graph6(g) + '\n')
            fn.write('%s n=%d m=%d\n' % (name, g.n(), g.m()))
    P('')
    P('wrote %d graphs to %s' % (len(entries), g6))
    with open(os.path.join(HERE, 'G7_patterns_log.txt'), 'w') as f:
        f.write('\n'.join(log) + '\n')


if __name__ == '__main__':
    main()
