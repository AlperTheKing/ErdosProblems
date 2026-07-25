"""G10_avgblock.py -- EXACT proof-check that NO averaging certificate, however finely
localised, can certify max_x psi <= 1/25 near a C5-concentration point.

Claim (G10-4).  Let H be triangle-free with an induced C5, x* the concentration point
(1/5 on the C5).  Let lambda be ANY probability distribution over the cuts of H and
put f(x) = sum_c lambda_c Q_c(x)  (an upper bound for psi, since psi = min_c Q_c).
Then for every neighbourhood U of x*,   sup_{x in U} f(x) > 1/25.

Proof.  f(x*) = (1/25) * sum_c lambda_c k_c with k_c = #monochromatic C5-edges >= 1,
so f(x*) >= 1/25 with equality only if lambda is supported on the ACTIVE cuts (k_c=1).
Assume that.  Restrict to directions d inside the C5 face (d = 0 off the C5, sum d = 0).
There grad f . d = (1/5) sum_i mu_i (d_i + d_{i+1}),  mu_i = lambda-mass of the cuts whose
mono C5-edge is (i,i+1).  This vanishes for all such d iff mu_{i-1}+mu_i is constant,
i.e. (odd cycle) mu_i = 1/5 for every i.  Then the second-order term is
   sum_c lambda_c Q_c(d) = (1/5) sum_i d_i d_{i+1},
and the 5-cycle form has eigenvalue 2cos(2 pi/5) > 0 on {sum d = 0}: the explicit
integer direction d = (309, -809, -809, 309, 1000) has sum 0 and sum_i d_i d_{i+1} =
772519 > 0.  So f strictly increases along d from x*, giving sup_U f > 1/25.  QED

Consequence: every branch-and-bound / region-decomposition scheme whose per-region
certificate is "some convex combination of cut-values is <= 1/25" FAILS on every region
containing a C5-concentration point, no matter how small the region.  This strictly
generalises the recorded dead end "fixed averaging certificates give >= 1/20 on C5"
(that is the special case of one global lambda).
"""
import sys, os
from fractions import Fraction
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G10_core import cycle, all_cut_monoedges, psi_exact, grotzsch, petersen, adjacency


def active_cuts(n, edges, cyc):
    """Cuts of H with exactly one monochromatic C5-edge (the active set at x*)."""
    cs = set(cyc)
    out = []
    for mask in range(1 << (n - 1)):
        m = mask << 1
        mono = [(u, v) for (u, v) in edges if ((m >> u) & 1) == ((m >> v) & 1)]
        k = sum(1 for (u, v) in mono if u in cs and v in cs)
        if k == 1:
            out.append((mask, mono))
    return out


def check(n, edges, cyc, dvec):
    """Exact check: for EVERY lambda supported on active cuts with mu_i = 1/5,
    f(x*+t d) > 1/25 for small t>0, witnessed by the exact second-order term."""
    x = [Fraction(0)] * n
    for v in cyc:
        x[v] = Fraction(1, 5)
    d = [Fraction(0)] * n
    for k, v in enumerate(cyc):
        d[v] = Fraction(dvec[k])
    assert sum(d) == 0
    acts = active_cuts(n, edges, cyc)
    # group active cuts by which C5-edge is mono
    cs = set(cyc)
    epos = {}
    for i in range(5):
        e = (min(cyc[i], cyc[(i + 1) % 5]), max(cyc[i], cyc[(i + 1) % 5]))
        epos[e] = i
    groups = [[] for _ in range(5)]
    for (mask, mono) in acts:
        mu, mv = [(u, v) for (u, v) in mono if u in cs and v in cs][0]
        groups[epos[(min(mu, mv), max(mu, mv))]].append((mask, mono))
    # lambda = uniform 1/5 over the five groups, uniform inside each group
    lam = {}
    for i in range(5):
        for (mask, mono) in groups[i]:
            lam[mask] = Fraction(1, 5 * len(groups[i]))
    assert sum(lam.values()) == 1

    def f(y):
        s = Fraction(0)
        for (mask, mono) in acts:
            if mask not in lam:
                continue
            q = sum(y[u] * y[v] for (u, v) in mono)
            s += lam[mask] * q
        return s
    f0 = f(x)
    # second-order coefficient  sum_c lambda_c Q_c(d)  computed exactly
    quad = Fraction(0)
    for (mask, mono) in acts:
        if mask not in lam:
            continue
        quad += lam[mask] * sum(d[u] * d[v] for (u, v) in mono)
    rows = []
    for num in (1, 2, 5, 10):
        t = Fraction(1, num * 100000)
        y = [x[v] + t * d[v] for v in range(n)]
        rows.append((t, f(y), f(y) > Fraction(1, 25)))
    return f0, quad, rows


if __name__ == '__main__':
    dvec = (309, -809, -809, 309, 1000)
    s = sum(dvec[i] * dvec[(i + 1) % 5] for i in range(5))
    print('direction', dvec, ' sum =', sum(dvec), ' sum_i d_i d_{i+1} =', s, '(>0)' if s > 0 else '(<=0)')
    for nm, (n, e), cyc in [('C5', cycle(5), (0, 1, 2, 3, 4)),
                            ('Petersen', petersen(), (0, 1, 2, 3, 4)),
                            ('Grotzsch', grotzsch(), (0, 1, 2, 3, 4))]:
        f0, quad, rows = check(n, e, cyc, dvec)
        print('%-9s f(x*) = %s (= 1/25 ? %s)   second-order coeff = %s  sign %s'
              % (nm, f0, f0 == Fraction(1, 25), quad, '+' if quad > 0 else '-'))
        for (t, val, gt) in rows:
            print('          t=%-14s  f = %-24s  f > 1/25 : %s' % (t, val, gt))
    # and the true psi at those points, to show psi itself does NOT exceed 1/25
    n, e = cycle(5)
    ml = all_cut_monoedges(n, e)
    x = [Fraction(1, 5)] * 5
    for num in (1, 2, 5, 10):
        t = Fraction(1, num * 100000)
        y = [x[i] + t * Fraction(dvec[i]) for i in range(5)]
        print('psi(C5, x*+t d) at t=%s : %s   (<= 1/25 : %s)' % (t, psi_exact(ml, y), psi_exact(ml, y) <= Fraction(1, 25)))
