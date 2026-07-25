"""
G7_chain.py

(1) EXACT refutation of the frequently-quoted form
        "Jin 1995: delta > 10n/29 implies G is homomorphic to C5".
    Witness: the balanced blow-up of And(4) = Gamma_4 (11 vertices, 4-regular).
    delta = 4n/11 > 10n/29, but And(4) has NO homomorphism to C5.
    Verified here by EXHAUSTIVE search over all 5^11 maps (with pruning) and,
    independently, by the fractional-chromatic bound n/alpha = 11/4 > 5/2.
    We also list every Gamma_i / Vega graph with delta > 10/29 and test each.

(2) Explicit vertex sets realising the induced-subgraph chain
        Upsilon_2 < Upsilon_3 < Upsilon_4 < ...
    (searched, then re-verified as an explicit deletion set).
"""
import sys, os, itertools
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from G7_patterns import (gamma, upsilon, independence_number, isomorphic,
                         to_nx, G)
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

C5 = gamma(2)   # the 5-cycle


def hom_exists(g, h):
    """exhaustive backtracking search for a homomorphism g -> h"""
    nv = g.n()
    gn = [[g.idx[u] for u in g.adj[v]] for v in g.V]
    hn = [set(h.idx[u] for u in h.adj[v]) for v in h.V]
    nh = h.n()
    order = sorted(range(nv), key=lambda t: -len(gn[t]))
    pos = {v: i for i, v in enumerate(order)}
    col = [-1] * nv

    def rec(p):
        if p == nv:
            return True
        v = order[p]
        for c in range(nh):
            ok = True
            for u in gn[v]:
                if col[u] >= 0 and col[u] not in hn[c]:
                    ok = False
                    break
            if ok:
                col[v] = c
                if rec(p + 1):
                    return True
                col[v] = -1
        return False
    return rec(0)


def report_hom():
    print('== (1) which BT patterns are homomorphic to C5? ==')
    print('   delta(Gamma_i)/n = i/(3i-1);  10/29 = %s' % Fraction(10, 29))
    rows = []
    for i in range(2, 11):
        g = gamma(i)
        d = Fraction(i, 3 * i - 1)
        al = independence_number(g)
        rows.append(('Gamma_%d' % i, g.n(), d, al, Fraction(g.n(), al),
                     hom_exists(g, C5)))
    for i in range(2, 5):
        for dy, d2, nm, dg, tt in [
                (False, False, 'Upsilon_%d', 9 * i - 6, 27 * i - 19),
                (True, False, 'Upsilon_%d-y', 9 * i - 7, 27 * i - 22),
                (False, True, 'Upsilon_%d-2i', 9 * i - 7, 27 * i - 22),
                (True, True, 'Upsilon_%d-y-2i', 9 * i - 8, 27 * i - 25)]:
            g, _ = upsilon(i, dy, d2)
            al = independence_number(g)
            rows.append((nm % i, g.n(), Fraction(dg, tt), al,
                         Fraction(g.n(), al), hom_exists(g, C5)))
    print('   %-16s %4s %-10s %5s %-8s %-10s %s'
          % ('graph', 'n', 'delta/n', 'alpha', 'n/alpha', '>10/29?', 'hom->C5?'))
    for nm, n, d, al, fa, h in rows:
        print('   %-16s %4d %-10s %5d %-8s %-10s %s'
              % (nm, n, d, al, fa, 'YES' if d > Fraction(10, 29) else 'no', h))
    print()
    g4 = gamma(4)
    print('   FALSIFIER for "delta>10n/29 => hom to C5":')
    print('     H = And(4) = Gamma_4, n=11, 4-regular, triangle-free=%s'
          % all(not (g4.adj[u] & g4.adj[v]) for u, v in g4.edges()))
    print('     balanced blow-up H[t]: N=11t, delta=4t = 4N/11 = %s N'
          % Fraction(4, 11))
    print('     4/11 = %s  >  10/29 = %s   (difference %s)'
          % (Fraction(4, 11), Fraction(10, 29), Fraction(4, 11) - Fraction(10, 29)))
    print('     hom(And(4) -> C5) exists : %s' % hom_exists(g4, C5))
    print('     alpha(And(4)) = %d, so chi_f >= 11/4 = %s > 5/2 = chi_f(C5)'
          % (independence_number(g4), Fraction(11, 4)))
    print('     a blow-up H[t] is hom to C5 iff H is, so the whole family works.')
    print()
    print('   Same test for And(3)=Wagner (Haggkvist sharpness example):')
    print('     delta/n = 3/8 = %s, hom->C5 = %s' % (Fraction(3, 8), hom_exists(gamma(3), C5)))


def report_chain():
    print()
    print('== (2) explicit induced chain Upsilon_i < Upsilon_{i+1} ==')
    for i in range(2, 6):
        A, _ = upsilon(i, False, False)
        B, _ = upsilon(i + 1, False, False)
        gm = GraphMatcher(to_nx(B), to_nx(A))
        found = None
        for mp in gm.subgraph_isomorphisms_iter():
            S = sorted(mp.keys())
            keep = set(B.V[t] for t in S)
            dele = [v for v in B.V if v not in keep]
            # prefer a deletion set inside the Gamma part
            if all(isinstance(v, int) for v in dele):
                found = sorted(dele)
                break
            if found is None:
                found = dele
        print('   Upsilon_%d = Upsilon_%d - %s   (verified induced: %s)'
              % (i, i + 1, found,
                 isomorphic(B.induced([v for v in B.V if v not in set(found)]), A)))


if __name__ == '__main__':
    report_hom()
    report_chain()
