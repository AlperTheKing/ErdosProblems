"""P3_special_points.py -- exact rational psi at the structurally distinguished weightings of
every Vega graph, and the exact witnesses that kill the neighbourhood-cut ("m(b)") family.

For each Vega graph and each named weighting a (integer, sum q) we report, exactly:
    bip(a)              = min over ALL cuts of the monochromatic mass         (n <= NEXACT only)
    arcplus(a)          = min over ARCPLUS = {arc of the circle} x {subset of the specials}
    nbhd(a)             = min over the neighbourhood cuts N(t), t a vertex
and the three ratios against q^2/25.  arcplus >= bip always, so 25*arcplus <= q^2 already
certifies Erdos 23 at that weighting without needing the exact bip.

Named weightings:
    REG    the paper's regular weight function (Brandt-Thomasse Theorem 3)
    UNIF   all weights 1
    C5     weight 1 on an induced C5, 0 elsewhere
"""
import sys, itertools
from fractions import Fraction as F
import networkx as nx
import P3_vega as V

NEXACT = 21          # do the 2^(n-1) exact computation only up to this order


def circle_arcs(G, order, i):
    L = 3 * i - 1
    seen = set()
    out = []
    for s in range(1, L + 1):
        for ln in range(L + 1):
            A = frozenset((s - 1 + t) % L + 1 for t in range(ln)) & frozenset(G.nodes())
            if A in seen:
                continue
            seen.add(A)
            out.append(set(A))
    return out


def arcplus_min(G, order, i, w):
    spec = [t for t in order if isinstance(t, str)]
    E = [(a, b) for a, b in G.edges()]
    best = None
    for A in circle_arcs(G, order, i):
        for mask in range(1 << len(spec)):
            S = set(A)
            for t, sv in enumerate(spec):
                if (mask >> t) & 1:
                    S.add(sv)
            val = sum(w[a] * w[b] for a, b in E if (a in S) == (b in S))
            if best is None or val < best:
                best = val
                if best == 0:
                    return best
    return best


def nbhd_min(G, order, w):
    E = [(a, b) for a, b in G.edges()]
    best = None
    for t in order:
        S = set(G[t])
        val = sum(w[a] * w[b] for a, b in E if (a in S) == (b in S))
        if best is None or val < best:
            best = val
    return best


def exact_bip(G, order, w):
    supp = [t for t in order if w[t] > 0]
    n = len(supp)
    if n > NEXACT:
        return None
    E = [(a, b) for a, b in G.edges() if w[a] > 0 and w[b] > 0]
    idx = {t: k for k, t in enumerate(supp)}
    ee = [(idx[a], idx[b], w[a] * w[b]) for a, b in E]
    best = None
    for mask in range(1 << max(0, n - 1)):
        s = 0
        for a, b, pr in ee:
            if ((mask >> a) & 1) == ((mask >> b) & 1):
                s += pr
        if best is None or s < best:
            best = s
    return best if best is not None else 0


def find_induced_c5(G, order):
    for S in itertools.combinations(order, 5):
        H = G.subgraph(S)
        if H.number_of_edges() == 5 and all(d == 2 for _, d in H.degree()):
            return set(S)
    return None


def report(imax=8):
    print('%-12s %-5s %4s %5s %-12s %-12s %-12s %s'
          % ('graph', 'wgt', 'q', 'n', 'bip (exact)', 'ARCPLUSmin', 'NBHDmin', 'ratios vs q^2/25'))
    rows = []
    for i in range(2, imax + 1):
        fam, _ = V.vega_family(i)
        for name, G, wreg in fam:
            order = V.canon_order(G)
            c5 = find_induced_c5(G, order)
            named = [('REG', {t: wreg[t] for t in order}),
                     ('UNIF', {t: 1 for t in order}),
                     ('C5', {t: (1 if t in c5 else 0) for t in order})]
            for tag, w in named:
                q = sum(w.values())
                bp = exact_bip(G, order, w)
                ap = arcplus_min(G, order, i, w)
                nb = nbhd_min(G, order, w)
                r = lambda z: 'n/a' if z is None else '%.6f' % (25.0 * z / (q * q))
                rows.append((name, tag, q, G.number_of_nodes(), bp, ap, nb,
                             F(bp, q * q) if bp is not None else None, F(ap, q * q), F(nb, q * q)))
                print('%-12s %-5s %4d %5d %-12s %-12s %-12s  25bip/q2=%-9s 25arc/q2=%-9s 25nbhd/q2=%s'
                      % (name, tag, q, G.number_of_nodes(), bp, ap, nb, r(bp), r(ap), r(nb)))
            sys.stdout.flush()
    return rows


def nbhd_killers():
    """the exact witnesses on which the neighbourhood-cut family (hence every bound_k of the
    g^k-weighted hierarchy) exceeds 1/25 on a Vega graph."""
    print()
    print('NEIGHBOURHOOD-CUT FAMILY: exact falsifying witnesses on Vega graphs')
    cases = [
        ('Ups_2', 2, [1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1]),
        ('Ups_2', 2, [0, 2, 2, 0, 1, 1, 1, 1, 2, 1, 1, 2, 1]),
        ('Ups_2-y-2i', 2, [0, 2, 1, 1, 1, 2, 2, 1, 2, 2, 1]),
        ('Ups_3-y-2i', 3, [1, 0, 2, 2, 0, 2, 0, 2, 2, 1, 1, 1, 1, 0]),
        ('Ups_3', 3, [1, 0, 2, 2, 0, 1, 1, 1, 0, 2, 1, 1, 0, 1, 1, 1]),
    ]
    for name, i, wl in cases:
        fam, _ = V.vega_family(i)
        G = dict((nm, g) for nm, g, _ in fam)[name]
        order = V.canon_order(G)
        w = {t: wl[k] for k, t in enumerate(order)}
        q = sum(wl)
        bp = exact_bip(G, order, w)
        ap = arcplus_min(G, order, i, w)
        nb = nbhd_min(G, order, w)
        print('  %-12s q=%d  a=%s' % (name, q, ''.join(str(t) for t in wl)))
        print('     roles      %s' % ' '.join(str(t) for t in order))
        print('     bip=%s -> psi=%s=%.6f   ARCPLUSmin=%s=%s   NBHDmin=%s -> %s = %.6f  %s'
              % (bp, F(bp, q * q), float(F(bp, q * q)), ap, F(ap, q * q), nb, F(nb, q * q),
                 float(F(nb, q * q)), 'NBHD EXCEEDS 1/25' if F(nb, q * q) > F(1, 25) else 'nbhd ok'))


if __name__ == '__main__':
    report(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
    nbhd_killers()
