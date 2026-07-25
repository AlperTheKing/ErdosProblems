"""P3_vega.py -- construct the Brandt-Thomasse Vega graphs and verify every claimed property.

Definition (Brandt-Thomasse, "Dense triangle-free graphs are four-colorable", p.4, verbatim):

  For some integer i >= 2, start with a graph Gamma_i on vertex set {1,...,3i-1} and add an edge
  xy and an induced 6-cycle (a,v,c,u,b,w) such that x is joined to a,b,c and y is joined to u,v,w.
  The set of neighbors of a,u on the Gamma_i graph is {1,...,i}.
  The set of neighbors of b,v on the Gamma_i graph is {i+1,...,2i}.
  The set of neighbors of c,w on the Gamma_i graph is {2i+1,...,3i-1}.
  This is the sole Vega graph on 3i+7 vertices.  We denote it by Upsilon_i.
  There are two Vega graphs on 3i+6 vertices, obtained from Upsilon_i by a simple vertex deletion.
  The first one is Upsilon_i - {y}, the second Upsilon_i - {2i}.
  Finally, the last Vega graph, on 3i+5 vertices, is Upsilon_i - {y,2i}.

  Gamma_i = vertex set {1,...,3i-1}, vertex j has neighbours j+i,...,j+2i-1 mod 3i-1
          = the Andrasfai graph And(i).

Weights (Theorem 3 of the same paper, verbatim, integer form):
  Upsilon_i          : 1 to x,y,1,2i;  3i-3 to c,w;  3i-2 to u,v,a,b;  3 to all others.
                       degree 9i-6, total 27i-19.
  Upsilon_i-{y}      : 1 to 1 and 2i;  2 to x;  3i-4 to w;  3i-3 to u,v,c;  3i-2 to a,b;  3 others.
                       degree 9i-7, total 27i-22.
  Upsilon_i-{2i}     : 1 to x,y;  2 to 1,i;  3i-3 to b,v,c,w;  3i-2 to u,a;  3 to all others.
                       degree 9i-7, total 27i-22.
  Upsilon_i-{y,2i}   : 2 to x,1,i;  3i-4 to v,w;  3i-3 to u,b,c;  3i-2 to a;  3 to all others.
                       degree 9i-8, total 27i-25.
"""
import sys, itertools
from fractions import Fraction
import networkx as nx

SPECIAL = ['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w']


def gamma(i):
    """Andrasfai graph And(i) = Gamma_i on {1,...,3i-1}."""
    n = 3 * i - 1
    G = nx.Graph()
    G.add_nodes_from(range(1, n + 1))
    for j in range(1, n + 1):
        for d in range(i, 2 * i):
            k = (j + d - 1) % n + 1
            G.add_edge(j, k)
    return G


def upsilon(i):
    """Upsilon_i, the Vega graph on 3i+7 vertices."""
    n = 3 * i - 1
    G = gamma(i)
    G.add_nodes_from(SPECIAL)
    G.add_edge('x', 'y')
    for t in ('a', 'b', 'c'):
        G.add_edge('x', t)
    for t in ('u', 'v', 'w'):
        G.add_edge('y', t)
    # induced 6-cycle (a,v,c,u,b,w)
    cyc = ['a', 'v', 'c', 'u', 'b', 'w']
    for k in range(6):
        G.add_edge(cyc[k], cyc[(k + 1) % 6])
    X = list(range(1, i + 1))                 # = N_{Gamma_i}(2i)
    Y = list(range(i + 1, 2 * i + 1))         # = N_{Gamma_i}(1)
    Z = list(range(2 * i + 1, n + 1))         # short class, size i-1
    for t in ('a', 'u'):
        for j in X:
            G.add_edge(t, j)
    for t in ('b', 'v'):
        for j in Y:
            G.add_edge(t, j)
    for t in ('c', 'w'):
        for j in Z:
            G.add_edge(t, j)
    return G, (X, Y, Z)


def vega_family(i):
    """The (at most) four Vega graphs for a given i, as (name, graph, weightdict)."""
    U, (X, Y, Z) = upsilon(i)
    n = 3 * i - 1
    out = []

    def build(name, delete, wspec):
        G = U.copy()
        G.remove_nodes_from(delete)
        w = {}
        for vtx in G.nodes():
            w[vtx] = 3
        for val, verts in wspec:
            for vtx in verts:
                assert vtx in w, (name, vtx)
                w[vtx] = val
        out.append((name, G, w))

    build('Ups_%d' % i, [],
          [(1, ['x', 'y', 1, 2 * i]), (3 * i - 3, ['c', 'w']), (3 * i - 2, ['u', 'v', 'a', 'b'])])
    build('Ups_%d-y' % i, ['y'],
          [(1, [1, 2 * i]), (2, ['x']), (3 * i - 4, ['w']), (3 * i - 3, ['u', 'v', 'c']),
           (3 * i - 2, ['a', 'b'])])
    build('Ups_%d-2i' % i, [2 * i],
          [(1, ['x', 'y']), (2, [1, i]), (3 * i - 3, ['b', 'v', 'c', 'w']),
           (3 * i - 2, ['u', 'a'])])
    build('Ups_%d-y-2i' % i, ['y', 2 * i],
          [(2, ['x', 1, i]), (3 * i - 4, ['v', 'w']), (3 * i - 3, ['u', 'b', 'c']),
           (3 * i - 2, ['a'])])
    return out, (X, Y, Z)


# ---------------------------------------------------------------- verification helpers
def is_triangle_free(G):
    for u_, v_ in G.edges():
        if set(G[u_]) & set(G[v_]):
            return False, (u_, v_)
    return True, None


def is_maximal_triangle_free(G):
    """triangle-free and diameter <= 2 (== every non-edge has a common neighbour)."""
    tf, w = is_triangle_free(G)
    if not tf:
        return False, ('triangle', w)
    V = list(G.nodes())
    for a_, b_ in itertools.combinations(V, 2):
        if G.has_edge(a_, b_):
            continue
        if not (set(G[a_]) & set(G[b_])):
            return False, ('no common nbr', a_, b_)
    return True, None


def is_twin_free(G):
    seen = {}
    for vtx in G.nodes():
        key = frozenset(G[vtx])
        if key in seen:
            return False, (seen[key], vtx)
        seen[key] = vtx
    return True, None


def chromatic_number(G, cap=6):
    """exact chromatic number by exhaustive DSATUR-style backtracking (small graphs)."""
    V = sorted(G.nodes(), key=lambda t: -G.degree(t))
    n = len(V)
    idx = {vtx: k for k, vtx in enumerate(V)}
    adj = [set() for _ in range(n)]
    for a_, b_ in G.edges():
        adj[idx[a_]].add(idx[b_])
        adj[idx[b_]].add(idx[a_])

    def colorable(k):
        col = [-1] * n

        def rec(p, used):
            if p == n:
                return True
            forb = {col[q] for q in adj[p] if col[q] >= 0}
            for cc in range(min(used + 1, k)):
                if cc in forb:
                    continue
                col[p] = cc
                if rec(p + 1, max(used, cc + 1)):
                    return True
                col[p] = -1
            return False
        return rec(0, 0)

    for k in range(1, cap + 1):
        if colorable(k):
            return k
    return None


def odd_girth(G):
    """length of shortest odd cycle (BFS from every vertex)."""
    best = None
    for s in G.nodes():
        dist = {s: 0}
        order = [s]
        qi = 0
        while qi < len(order):
            cur = order[qi]; qi += 1
            for nb in G[cur]:
                if nb not in dist:
                    dist[nb] = dist[cur] + 1
                    order.append(nb)
        for a_, b_ in G.edges():
            if a_ in dist and b_ in dist and dist[a_] == dist[b_]:
                L = dist[a_] + dist[b_] + 1
                if best is None or L < best:
                    best = L
    return best


def weighted_min_degree(G, w):
    tot = sum(w.values())
    degs = {vtx: sum(w[t] for t in G[vtx]) for vtx in G.nodes()}
    return min(degs.values()), max(degs.values()), tot, degs


def to_g6(G, order=None):
    V = list(G.nodes()) if order is None else order
    n = len(V)
    idx = {vtx: k for k, vtx in enumerate(V)}
    bits = []
    for j in range(n):
        for k in range(j):
            bits.append(1 if G.has_edge(V[k], V[j]) else 0)
    out = []
    if n <= 62:
        out.append(chr(n + 63))
    else:
        raise ValueError('n>62 not implemented')
    while len(bits) % 6:
        bits.append(0)
    for k in range(0, len(bits), 6):
        val = 0
        for bb in bits[k:k + 6]:
            val = val * 2 + bb
        out.append(chr(val + 63))
    return ''.join(out)


def canon_order(G):
    """deterministic vertex order: Gamma_i vertices ascending, then x,y,a,b,c,u,v,w."""
    ints = sorted(t for t in G.nodes() if isinstance(t, int))
    sp = [t for t in SPECIAL if t in G.nodes()]
    return ints + sp


def grotzsch():
    """Mycielskian of C5."""
    G = nx.Graph()
    for k in range(5):
        G.add_edge(('o', k), ('o', (k + 1) % 5))
    for k in range(5):
        for nb in [(k - 1) % 5, (k + 1) % 5]:
            G.add_edge(('m', k), ('o', nb))
        G.add_edge(('m', k), 'z')
    return G


def main(imax=8):
    lines = []
    names = []
    rep = []
    for i in range(2, imax + 1):
        fam, (X, Y, Z) = vega_family(i)
        for (name, G, w) in fam:
            n = G.number_of_nodes()
            m = G.number_of_edges()
            tf, tw = is_triangle_free(G)
            mtf, mw = is_maximal_triangle_free(G)
            twf, tww = is_twin_free(G)
            chi = chromatic_number(G)
            og = odd_girth(G)
            dmin, dmax, tot, degs = weighted_min_degree(G, w)
            regular = (dmin == dmax)
            delta = Fraction(dmin, tot)
            ok = tf and mtf and twf and (chi == 4) and regular and delta > Fraction(1, 3)
            rep.append(dict(i=i, name=name, n=n, m=m, tf=tf, mtf=mtf, twinfree=twf, chi=chi,
                            oddgirth=og, wdeg=dmin, wtot=tot, regular=regular,
                            delta=delta, ok=ok, delta_float=float(delta)))
            order = canon_order(G)
            lines.append(to_g6(G, order))
            names.append('%s n=%d m=%d chi=%d oddgirth=%s delta=%s(%.6f) order=%s'
                         % (name, n, m, chi, og, delta, float(delta),
                            ','.join(str(t) for t in order)))
    with open('P3_vega.g6', 'w') as f:
        for L, nm in zip(lines, names):
            f.write('%s\t%s\n' % (L, nm))
    # closed-form checks of the paper's degree/total formulas
    print('%-14s %3s %3s %5s %4s %4s %4s %4s %3s %4s %9s %-10s %s'
          % ('name', 'n', 'm', 'tf', 'mtf', 'twf', 'chi', 'og', 'reg', 'wdeg', 'wtot',
             'delta', 'ok'))
    for r in rep:
        print('%-14s %3d %3d %5s %4s %4s %4d %4s %3s %4d %9d %-10s %s'
              % (r['name'], r['n'], r['m'], r['tf'], r['mtf'], r['twinfree'], r['chi'],
                 r['oddgirth'], r['regular'], r['wdeg'], r['wtot'], r['delta'], r['ok']))
    bad = [r for r in rep if not r['ok']]
    print('FAILURES:', len(bad))
    for r in bad:
        print('  ', r)
    # formula check
    for r in rep:
        i = r['i']
        exp = {'Ups_%d' % i: (9 * i - 6, 27 * i - 19, 3 * i + 7),
               'Ups_%d-y' % i: (9 * i - 7, 27 * i - 22, 3 * i + 6),
               'Ups_%d-2i' % i: (9 * i - 7, 27 * i - 22, 3 * i + 6),
               'Ups_%d-y-2i' % i: (9 * i - 8, 27 * i - 25, 3 * i + 5)}[r['name']]
        assert (r['wdeg'], r['wtot'], r['n']) == exp, (r['name'], (r['wdeg'], r['wtot'], r['n']), exp)
    print('paper degree/total/order formulas: VERIFIED for i=2..%d' % imax)
    # Grotzsch identification
    G2 = dict((nm, g) for nm, g, _ in vega_family(2)[0])
    gr = grotzsch()
    print('Ups_2-y-2i == Grotzsch :', nx.is_isomorphic(G2['Ups_2-y-2i'], gr))
    print('Ups_2-y == Ups_2-2i    :', nx.is_isomorphic(G2['Ups_2-y'], G2['Ups_2-2i']))
    for i in range(3, imax + 1):
        Gi = dict((nm, g) for nm, g, _ in vega_family(i)[0])
        print('i=%d: Ups-y == Ups-2i : %s' % (i, nx.is_isomorphic(Gi['Ups_%d-y' % i],
                                                                  Gi['Ups_%d-2i' % i])))
    # every Vega graph contains an induced C5 ?
    for r_i in range(2, imax + 1):
        fam, _ = vega_family(r_i)
        for name, G, _w in fam:
            print('%s induced C5: %s' % (name, has_induced_c5(G)))


def has_induced_c5(G):
    V = list(G.nodes())
    for S in itertools.combinations(V, 5):
        H = G.subgraph(S)
        if H.number_of_edges() == 5 and all(d == 2 for _, d in H.degree()):
            return True
    return False


if __name__ == '__main__':
    imax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(imax)
