"""H4 verifier #1 (primary).  Erdos #23, conditional theorem for delta > N/3.

Checks, in EXACT integer / Fraction arithmetic, every plumbing step of the theorem

    G triangle-free, delta(G) > N/3
      -> G' maximal triangle-free completion            (bip up, delta up)
      -> H = G'/twins with multiplicities a             (G' = H[a])
      -> H is Gamma_i (Andrasfai) or a Vega graph       (Chen-Jin-Koh + Brandt-Thomasse)
      -> bip(G) <= bip(G') = N^2 psi(H, a/N) <= N^2 max psi(H).

Sections
  A  constructions: Gamma_i, the four Vega families, Grotzsch
  B  structural audit of the census: all triangle-free G on N<=16 with delta(G) > N/3
  C  homomorphism chain Gamma_j -> Gamma_k, Vega_j -> Upsilon_k (Brandt-Thomasse Cor 4.3(3))
  D  psi at the induced-C5 point on every family member (campaign fact 3: hypothesis = equality)

Usage:  python H4_verify.py [--nmax 16]
"""
import sys, subprocess, itertools
from fractions import Fraction
import numpy as np
import networkx as nx

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"

# ----------------------------------------------------------------------------- A
def gamma(i):
    """Brandt-Thomasse Gamma_i = Andrasfai graph And_i, on {1,...,3i-1},
    vertex j adjacent to j+i,...,j+2i-1 mod 3i-1."""
    m = 3 * i - 1
    lab = lambda t: (t - 1) % m + 1          # representatives 1..m, with m == 0
    G = nx.Graph()
    G.add_nodes_from(lab(j) for j in range(1, m + 1))
    for j in range(1, m + 1):
        for t in range(i, 2 * i):
            G.add_edge(lab(j), lab(j + t))
    return G


def upsilon(i):
    """Vega graph Upsilon_i (3i+7 vertices), Brandt-Thomasse section 1, verbatim:
    start with Gamma_i on {1,...,3i-1}, add edge xy and induced 6-cycle (a,v,c,u,b,w);
    x joined to a,b,c; y joined to u,v,w; N_Gamma(a)=N_Gamma(u)={1..i},
    N_Gamma(b)=N_Gamma(v)={i+1..2i}, N_Gamma(c)=N_Gamma(w)={2i+1..3i-1}."""
    G = gamma(i)
    G.add_nodes_from(['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w'])
    G.add_edge('x', 'y')
    for e in [('a', 'v'), ('v', 'c'), ('c', 'u'), ('u', 'b'), ('b', 'w'), ('w', 'a')]:
        G.add_edge(*e)                        # the induced 6-cycle (a,v,c,u,b,w)
    for t in ('a', 'b', 'c'):
        G.add_edge('x', t)
    for t in ('u', 'v', 'w'):
        G.add_edge('y', t)
    A = list(range(1, i + 1))
    B = list(range(i + 1, 2 * i + 1))
    C = list(range(2 * i + 1, 3 * i))
    for s, blk in (('a', A), ('u', A), ('b', B), ('v', B), ('c', C), ('w', C)):
        for j in blk:
            G.add_edge(s, j)
    return G


def vega_family(i):
    """The four Vega graphs built on Gamma_i (i >= 2)."""
    U = upsilon(i)
    out = {}
    out['Ups_%d' % i] = U
    H = U.copy(); H.remove_node('y'); out['Ups_%d-y' % i] = H
    H = U.copy(); H.remove_node(2 * i); out['Ups_%d-2i' % i] = H
    H = U.copy(); H.remove_node('y'); H.remove_node(2 * i); out['Ups_%d-y-2i' % i] = H
    return out


def grotzsch():
    """Mycielskian of C5, built independently of the Vega construction."""
    G = nx.Graph()
    for j in range(5):
        G.add_edge(('c', j), ('c', (j + 1) % 5))
    for j in range(5):
        for k in (j - 1, j + 1):
            G.add_edge(('m', j), ('c', k % 5))
        G.add_edge(('m', j), 'z')
    return G


# ----------------------------------------------------------------------------- basics
def is_triangle_free(G):
    return all(not set(G[u]) & set(G[v]) for u, v in G.edges())


def is_maximal_tf(G):
    if not is_triangle_free(G):
        return False
    for u, v in itertools.combinations(G.nodes(), 2):
        if not G.has_edge(u, v) and not (set(G[u]) & set(G[v])):
            return False
    return True


def delta(G):
    return min(dict(G.degree()).values())


def bip_bruteforce(G):
    """bip(G) = |E| - maxcut(G), exact, by enumerating all cuts (numpy bitmask)."""
    nodes = list(G.nodes())
    idx = {v: k for k, v in enumerate(nodes)}
    n = len(nodes)
    E = [(idx[u], idx[v]) for u, v in G.edges()]
    if not E:
        return 0
    masks = np.arange(1 << (n - 1), dtype=np.int64)   # vertex 0 fixed on side 0
    side = lambda t: ((masks >> (t - 1)) & 1) if t > 0 else np.zeros_like(masks)
    mono = np.zeros(masks.shape, dtype=np.int64)
    for (a, b) in E:
        mono += (side(a) == side(b))
    return int(mono.min())


def blowup_bip(H, mult):
    """min over cuts S of H of sum_{uv monochromatic} a_u a_v  (campaign fact 1)."""
    nodes = list(H.nodes())
    idx = {v: k for k, v in enumerate(nodes)}
    n = len(nodes)
    E = [(idx[u], idx[v], mult[u] * mult[v]) for u, v in H.edges()]
    if not E:
        return 0
    masks = np.arange(1 << (n - 1), dtype=np.int64)
    side = lambda t: ((masks >> (t - 1)) & 1) if t > 0 else np.zeros_like(masks)
    tot = np.zeros(masks.shape, dtype=np.int64)
    for (a, b, w) in E:
        tot += w * (side(a) == side(b))
    return int(tot.min())


def maximal_completion(G, order=None):
    """Greedily add non-edges that create no triangle."""
    H = G.copy()
    pairs = list(itertools.combinations(list(H.nodes()), 2))
    if order is not None:
        pairs = [pairs[k] for k in order]
    changed = True
    while changed:
        changed = False
        for u, v in pairs:
            if not H.has_edge(u, v) and not (set(H[u]) & set(H[v])):
                H.add_edge(u, v)
                changed = True
    return H


def twin_quotient(G):
    """Collapse classes of vertices with equal neighbourhood.  Returns (H, mult)."""
    classes = {}
    for v in G.nodes():
        classes.setdefault(frozenset(G[v]), []).append(v)
    reps = {}
    for key, vs in classes.items():
        reps[key] = vs[0]
    H = nx.Graph()
    mult = {}
    for key, vs in classes.items():
        H.add_node(reps[key])
        mult[reps[key]] = len(vs)
    for k1, k2 in itertools.combinations(classes.keys(), 2):
        u, v = reps[k1], reps[k2]
        if G.has_edge(u, v):
            H.add_edge(u, v)
    return H, mult, classes


def chrom_le(G, k):
    """exact k-colourability test (backtracking)."""
    nodes = sorted(G.nodes(), key=lambda v: -G.degree(v))
    col = {}

    def bt(t):
        if t == len(nodes):
            return True
        v = nodes[t]
        used = {col[w] for w in G[v] if w in col}
        for c in range(min(k, t + 1)):
            if c not in used:
                col[v] = c
                if bt(t + 1):
                    return True
                del col[v]
        return False
    return bt(0)


def hom_exists(G, H):
    """Is there a homomorphism G -> H?  Simple backtracking CSP."""
    gn = sorted(G.nodes(), key=lambda v: -G.degree(v))
    hn = list(H.nodes())
    Hadj = {v: set(H[v]) for v in hn}
    asg = {}

    def bt(t):
        if t == len(gn):
            return True
        v = gn[t]
        nb = [w for w in G[v] if w in asg]
        for img in hn:
            if all(asg[w] in Hadj[img] for w in nb):
                asg[v] = img
                if bt(t + 1):
                    return True
                del asg[v]
        return False
    return bt(0)


def psi_at(H, x):
    """psi(H,x) = min over cuts of sum_{uv monochromatic} x_u x_v.  x: dict of Fractions."""
    nodes = list(H.nodes())
    n = len(nodes)
    best = None
    for bits in range(1 << (n - 1)):
        side = {nodes[0]: 0}
        for k in range(1, n):
            side[nodes[k]] = (bits >> (k - 1)) & 1
        s = Fraction(0)
        for u, v in H.edges():
            if side[u] == side[v]:
                s += x[u] * x[v]
        if best is None or s < best:
            best = s
    return best


def induced_C5(H):
    """Return an induced 5-cycle of H as a list, or None."""
    nodes = list(H.nodes())
    for comb in itertools.combinations(nodes, 5):
        S = H.subgraph(comb)
        if S.number_of_edges() == 5 and all(d == 2 for _, d in S.degree()):
            if nx.is_connected(S):
                return list(comb)
    return None


# ----------------------------------------------------------------------------- census
def geng_graphs(n, d):
    out = subprocess.run([GENG, '-t', '-d%d' % d, str(n)],
                         capture_output=True, text=True)
    for line in out.stdout.split('\n'):
        line = line.strip()
        if line:
            yield nx.from_graph6_bytes(line.encode())


def main():
    nmax = 16
    for k, arg in enumerate(sys.argv):
        if arg == '--nmax':
            nmax = int(sys.argv[k + 1])

    print("=" * 78)
    print("SECTION A  constructions")
    print("=" * 78)
    ref = {}
    for i in range(2, 6):
        Gm = gamma(i)
        ok = is_triangle_free(Gm) and is_maximal_tf(Gm)
        tw = len({frozenset(Gm[v]) for v in Gm}) == Gm.number_of_nodes()
        print("Gamma_%d: n=%2d m=%3d  reg=%s  tri-free=%s maximal=%s twin-free=%s chi<=3=%s"
              % (i, Gm.number_of_nodes(), Gm.number_of_edges(),
                 len({d for _, d in Gm.degree()}) == 1, is_triangle_free(Gm),
                 is_maximal_tf(Gm), tw, chrom_le(Gm, 3)))
        assert ok and tw
        ref['Gamma_%d' % i] = Gm
    print("Gamma_2 == C5:", nx.is_isomorphic(gamma(2), nx.cycle_graph(5)))
    W = nx.Graph([(j, (j + 1) % 8) for j in range(8)] + [(j, j + 4) for j in range(4)])
    print("Gamma_3 == Moebius ladder / Wagner V8:", nx.is_isomorphic(gamma(3), W))

    for i in (2, 3, 4):
        for name, V in vega_family(i).items():
            tw = len({frozenset(V[v]) for v in V}) == V.number_of_nodes()
            print("%-12s n=%2d m=%3d tri-free=%s maximal=%s twin-free=%s chi<=3=%s"
                  % (name, V.number_of_nodes(), V.number_of_edges(),
                     is_triangle_free(V), is_maximal_tf(V), tw, chrom_le(V, 3)))
            assert is_triangle_free(V) and is_maximal_tf(V) and tw
            assert not chrom_le(V, 3), name
            ref[name] = V
    print("Ups_2-y-2i == Grotzsch:",
          nx.is_isomorphic(vega_family(2)['Ups_2-y-2i'], grotzsch()))

    # Brandt-Thomasse Theorem 3 weights, verbatim, exact rational check
    print("-- Theorem 3 (regular weights, delta > 1/3) --")
    for i in range(2, 7):
        U = upsilon(i)
        wt = {}
        for v in U.nodes():
            wt[v] = 3
        for v in ['x', 'y', 1, 2 * i]:
            wt[v] = 1
        for v in ['c', 'w']:
            wt[v] = 3 * i - 3
        for v in ['u', 'v', 'a', 'b']:
            wt[v] = 3 * i - 2
        tot = sum(wt.values())
        degs = {sum(wt[w] for w in U[v]) for v in U.nodes()}
        print("  Ups_%d: total=%d (claim %d) regular=%s degree=%s (claim %d) delta>1/3: %s"
              % (i, tot, 27 * i - 19, len(degs) == 1, degs, 9 * i - 6,
                 Fraction(9 * i - 6, 27 * i - 19) > Fraction(1, 3)))
        assert tot == 27 * i - 19 and degs == {9 * i - 6}
        assert Fraction(9 * i - 6, 27 * i - 19) > Fraction(1, 3)

    print()
    print("=" * 78)
    print("SECTION B  census audit: every triangle-free G, N<=%d, delta(G) > N/3" % nmax)
    print("=" * 78)
    catalogue = []                      # (name, graph) of all admissible quotients
    for i in range(1, 7):
        if 3 * i - 1 <= nmax:
            catalogue.append(('Gamma_%d' % i, gamma(i)))
    for i in range(2, 7):
        for name, V in vega_family(i).items():
            if V.number_of_nodes() <= nmax:
                catalogue.append((name, V))
    print("catalogue (order <= %d): %s" % (nmax, [c[0] for c in catalogue]))

    grand = dict(graphs=0, quot=dict())
    for N in range(2, nmax + 1):
        d = N // 3 + 1                       # smallest integer > N/3
        cnt = 0
        for G in geng_graphs(N, d):
            if delta(G) * 3 <= N:
                continue
            cnt += 1
            bG = bip_bruteforce(G)
            Gp = maximal_completion(G)
            assert is_maximal_tf(Gp)
            assert delta(Gp) >= delta(G)                          # (i) delta does not drop
            bGp = bip_bruteforce(Gp)
            assert bGp >= bG, (N, bG, bGp)                        # (i) bip does not drop
            H, mult, classes = twin_quotient(Gp)
            # twin classes independent and completely joined
            for key, vs in classes.items():
                for p, q in itertools.combinations(vs, 2):
                    assert not Gp.has_edge(p, q)
            for k1, k2 in itertools.combinations(classes.keys(), 2):
                r1, r2 = list(classes[k1]), list(classes[k2])
                if Gp.has_edge(r1[0], r2[0]):
                    assert all(Gp.has_edge(p, q) for p in r1 for q in r2)
            assert is_triangle_free(H) and is_maximal_tf(H)        # (ii) quotient m.t.f.
            assert len({frozenset(H[v]) for v in H}) == H.number_of_nodes()   # twin-free
            assert chrom_le(H, 3) == chrom_le(Gp, 3)               # chi preserved
            assert sum(mult.values()) == N
            assert min(sum(mult[w] for w in H[v]) for v in H) == delta(Gp)    # weighted delta
            assert Fraction(delta(Gp), N) > Fraction(1, 3)
            # campaign fact 1 on this instance
            assert blowup_bip(H, mult) == bGp, (N, blowup_bip(H, mult), bGp)
            # Brandt-Thomasse Corollary 4.1
            hit = [nm for nm, K in catalogue if nx.is_isomorphic(H, K)]
            assert len(hit) == 1, (N, sorted(dict(H.degree()).values()), hit)
            grand['quot'][hit[0]] = grand['quot'].get(hit[0], 0) + 1
            # end-to-end: the conjecture itself, exactly
            assert Fraction(bG) <= Fraction(N * N, 25)
            assert Fraction(bGp) <= Fraction(N * N, 25)
            grand['graphs'] += 1
        print("  N=%2d  delta>=%d : %4d graphs audited" % (N, d, cnt))
    print("TOTAL graphs audited:", grand['graphs'])
    print("quotients realised  :", grand['quot'])

    print()
    print("=" * 78)
    print("SECTION C  homomorphism chain (Brandt-Thomasse Cor 4.3(3) plumbing)")
    print("=" * 78)
    for j in range(2, 5):
        for k in range(j, 6):
            print("  Gamma_%d -> Gamma_%d : %s" % (j, k, hom_exists(gamma(j), gamma(k))))
            assert hom_exists(gamma(j), gamma(k))
    for k in (2, 3, 4):
        U = upsilon(k)
        print("  Gamma_%d subgraph of Ups_%d : %s"
              % (k, k, set(gamma(k).edges()) <= set(U.edges()) or
                 all(U.has_edge(*e) for e in gamma(k).edges())))
        assert all(U.has_edge(*e) for e in gamma(k).edges())
    for j in (2, 3):
        for k in range(j + 1, 5):
            for nm, V in vega_family(j).items():
                r = hom_exists(V, upsilon(k))
                print("  %-12s -> Ups_%d : %s" % (nm, k, r))
                assert r
    for j in (2, 3, 4):
        print("  Gamma_%d -> Ups_%d : %s" % (j, j, hom_exists(gamma(j), upsilon(j))))
        assert hom_exists(gamma(j), upsilon(j))
    print("  C5 -> Gamma_k for k=2..5 :",
          [hom_exists(nx.cycle_graph(5), gamma(k)) for k in range(2, 6)])
    print("  Ups_2 -> C5 (must be False, Ups_2 is 4-chromatic):",
          hom_exists(upsilon(2), nx.cycle_graph(5)))
    assert not hom_exists(upsilon(2), nx.cycle_graph(5))

    print()
    print("=" * 78)
    print("SECTION D  psi at the induced-C5 point (campaign fact 3)")
    print("=" * 78)
    fifth = Fraction(1, 5)
    for name, K in catalogue:
        C = induced_C5(K)
        assert C is not None, name
        x = {v: (fifth if v in C else Fraction(0)) for v in K.nodes()}
        val = psi_at(K, x)
        print("  %-12s n=%2d  psi(C5 point) = %s   (1/25 = %s) equal=%s"
              % (name, K.number_of_nodes(), val, Fraction(1, 25), val == Fraction(1, 25)))
        assert val == Fraction(1, 25)
    print("  => max_x psi >= 1/25 for every graph in the catalogue: the hypothesis of the")
    print("     conditional theorem is an EQUALITY statement, never a strict inequality.")


if __name__ == '__main__':
    main()
