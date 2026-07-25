"""Q5: probe the integrality of the odd-cycle covering polyhedron Q(G) of the
extremal family C5[n].

By Lehman, Q(G) is integral for all w >= 0 iff it is integral for all
w in {0,1,infinity}^E (i.e. on every minor with unit weights).  We sample such
weight vectors exactly and compare tau_w (min weight odd-cycle transversal,
by exhaustive cut enumeration) with tau*_w (LP, exact row generation).

A single gap would prove, via Guenin's theorem, that C5[n] has an odd-K5 minor
and therefore that the LP/transport certificate is not available on the
extremal family.
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *

BIG = Fraction(10 ** 6)


def probe(n, adj, trials, seed, name):
    rnd = random.Random(seed)
    E = edges_of(n, adj)
    found = 0
    for t in range(trials):
        w = {}
        for e in E:
            r = rnd.random()
            w[e] = Fraction(0) if r < 0.25 else (BIG if r > 0.85 else Fraction(1))
        # tau_w exact (min over cuts)
        tau, S = bip_exact(n, adj, weights=w)
        if tau >= BIG:
            continue                      # degenerate: forced infinite cover
        ts = tau_star(n, adj, w=w)["value"]
        if ts < tau:
            print(f"  {name} GAP at trial {t}: tau*={ts} < tau={tau}")
            print(f"    w = { {str(k): str(v) for k, v in w.items()} }")
            found += 1
            if found >= 3:
                return True
    print(f"  {name}: no gap in {trials} random 0/1/inf weightings"
          f" ({'evidence for' if not found else 'AGAINST'} weak bipartiteness)")
    return found > 0


if __name__ == "__main__":
    for k in (2, 3):
        n, adj = blowup_C5(k)
        probe(n, adj, 400 if k == 2 else 120, 11 * k, f"C5[{k}]")
    # control: the N=14 extremal graph must show gaps
    n, adj = g6_decode("M?AE@bH{AYN_LgBs?")
    probe(n, adj, 60, 5, "N14(control)")
