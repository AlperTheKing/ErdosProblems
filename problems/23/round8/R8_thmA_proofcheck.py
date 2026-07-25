"""R8_thmA_proofcheck.py -- machine check of the proof of Theorem A.

PROOF (all quantities exact rationals).  Let G be triangle-free, x >= 0,
sum_v x_v = 1, w_uv = x_u x_v, d(v) = sum_{u ~ v} x_u.
WLOG x_v > 0 for all v and G has no isolated vertex (see the audit note), so
d(v) > 0.  Put g(v) = 1/d(v) and

        gamma := min over odd cycles C of  sum_{v in C} g(v),
        y_e   := (g(u) + g(v)) / (2*gamma)   for e = uv.

(1) y is a FEASIBLE fractional odd-cycle cover:
        sum_{e in C} y_e = (1/(2 gamma)) * 2 * sum_{v in C} g(v) >= 1.
(2) cost(y) = (1/(2 gamma)) * sum_v g(v) x_v d(v) = (1/(2 gamma)) * sum_v x_v
            = 1/(2 gamma).
(3) For every odd cycle C of length L in a triangle-free graph,
    sum_{v in C} d(v) = sum_u x_u |N(u) cap V(C)| <= (L-1)/2,
    because N(u) is independent, so N(u) cap V(C) is an independent set of the
    cycle C_L, of size at most floor(L/2) = (L-1)/2.
(4) Cauchy-Schwarz: sum_{v in C} 1/d(v) >= L^2 / sum_{v in C} d(v) >= 2L^2/(L-1),
    which is increasing in L, so for L >= 5 (triangle-free) gamma >= 25/2.
(5) Hence Lambda <= cost(y) = 1/(2 gamma) <= 1/25.

This script checks (1),(2),(3),(4),(5) numerically-exactly, and checks
Lambda_exact <= 1/(2 gamma) <= 1/25 on every test instance.
"""

from fractions import Fraction
import random
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *      # noqa
from R8_thmA_search import (clebsch, mcgee, named_graphs, five_cycles)  # noqa

FAIL = []


def proof_bound(g, x):
    """Return (gamma, bound, y, ok_flags) for the reduced (support) instance."""
    keep = [v for v in range(g.n) if x[v] > 0]
    h, idx = g.subgraph(keep)
    xs = [x[v] for v in keep]
    d = [sum(xs[u] for u in h.adj[v]) for v in range(h.n)]
    keep2 = [v for v in range(h.n) if d[v] > 0]
    h2, idx2 = h.subgraph(keep2)
    xs2 = [xs[v] for v in keep2]
    d2 = [sum(xs2[u] for u in h2.adj[v]) for v in range(h2.n)]
    assert all(t > 0 for t in d2)
    gg = [Fraction(1, 1) / t for t in d2]
    yhat = [(gg[u] + gg[v]) / 2 for (u, v) in h2.edges]   # cycle length = sum g(v)
    gamma, C = shortest_odd_cycle(h2, yhat)
    if gamma is None:
        return None, Fraction(0), None, {"bipartite": True}
    y = [t / gamma for t in yhat]
    cost = sum(xs2[u] * xs2[v] * y[i] for i, (u, v) in enumerate(h2.edges))
    # (1) feasibility, checked by the exact separation oracle over ALL odd cycles
    L, _ = shortest_odd_cycle(h2, y)
    flags = {
        "feasible": (L is not None and L >= 1),
        "cost_equals_1_over_2gamma": (cost == Fraction(1, 2) / gamma),
        "gamma_ge_25_over_2": (gamma >= Fraction(25, 2)),
        "bound_le_1_25": (Fraction(1, 2) / gamma <= Fraction(1, 25)),
    }
    return gamma, cost, y, flags


def check_instance(tag, g, x, do_exact=True):
    gamma, cost, y, flags = proof_bound(g, x)
    if flags.get("bipartite"):
        return None
    bad = [k for k, v in flags.items() if not v]
    lam = None
    if do_exact:
        r = exact_lambda(g, x)
        v = r.verify()
        assert v["primal_feasible"] and v["dual_feasible"] and v["match"], v
        lam = r.value
        if lam > cost:
            bad.append("LAMBDA_EXCEEDS_PROOF_BOUND")
        if lam > Fraction(1, 25):
            bad.append("LAMBDA_EXCEEDS_1_25")
    if bad:
        FAIL.append((tag, bad, str(gamma), str(cost), str(lam)))
        print("  FAIL %-28s gamma=%s cost=%s lambda=%s  %s" % (tag, gamma, cost, lam, bad))
    return gamma, cost, lam


def check_cycle_lemma(g, x, tag):
    """(3): for every odd cycle C, sum_{v in C} d(v) <= (|C|-1)/2. Brute force."""
    d = [sum(x[u] for u in g.adj[v]) for v in range(g.n)]
    worst = None
    for C in all_odd_cycles(g):
        s = sum(d[v] for v in C)
        lim = Fraction(len(C) - 1, 2)
        if s > lim:
            FAIL.append((tag, "CYCLE_DEGREE_LEMMA", str(C), str(s), str(lim)))
            print("  FAIL cycle-degree lemma", tag, C, s, lim)
        r = float(s / lim) if lim else 0
        worst = max(worst, r) if worst is not None else r
    return worst


if __name__ == "__main__":
    rng = random.Random(4242)
    print("=" * 96)
    print("1. cycle-degree lemma  sum_{v in C} d(v) <= (|C|-1)/2  (brute force over ALL odd cycles)")
    print("=" * 96)
    for nm, g in [("C5", cycle_graph(5)), ("C7", cycle_graph(7)), ("Petersen", petersen()),
                  ("Grotzsch", grotzsch()), ("Wagner", wagner()),
                  ("Gamma_11", circle_graph(11, 11)), ("Clebsch", clebsch())]:
        xs = [[Fraction(1, g.n)] * g.n]
        for _ in range(4):
            v = [Fraction(rng.randint(1, 30)) for _ in range(g.n)]
            s = sum(v)
            xs.append([t / s for t in v])
        w = max(check_cycle_lemma(g, x, nm) for x in xs)
        print("  %-12s max ratio sum_C d / ((L-1)/2) = %.6f" % (nm, w))
    for t in range(200):
        n = rng.randint(5, 10)
        gg = random_maximal_triangle_free(n, rng)
        v = [Fraction(rng.randint(0, 20)) for _ in range(n)]
        s = sum(v)
        if s == 0:
            continue
        check_cycle_lemma(gg, [t2 / s for t2 in v], "rand%d" % t)
    print("  200 random maximal triangle-free graphs: %s" %
          ("all OK" if not FAIL else "FAILURES %s" % FAIL))

    print()
    print("=" * 96)
    print("2. full proof chain vs exact Lambda")
    print("=" * 96)
    tests = []
    for nm, g in named_graphs():
        if g.has_triangle() or g.n > 20:
            continue
        tests.append((nm, g, [Fraction(1, g.n)] * g.n))
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(3,2,2,2,2),(2,1,2,1,2),(3,3,3,3,3)]:
        gb, _ = blowup_C5(sizes)
        tests.append(("C5%s" % (sizes,), gb, [Fraction(1, gb.n)] * gb.n))
    for nm, g, x in tests:
        gamma, cost, lam = check_instance(nm, g, x)
        print("  %-24s n=%2d  gamma=%-10s  proof bound=%-12s=%.8f  exact Lambda=%-10s=%.8f"
              % (nm, g.n, gamma, cost, float(cost), lam, float(lam)))

    print()
    print("  random instances (graph, weights):")
    worstratio = 0.0
    for t in range(400):
        n = rng.randint(5, 11)
        g = random_maximal_triangle_free(n, rng)
        if g.is_bipartite():
            continue
        v = [Fraction(rng.randint(0, 12)) for _ in range(n)]
        s = sum(v)
        if s == 0:
            continue
        x = [t2 / s for t2 in v]
        if all(sum(x[u] for u in g.adj[w]) == 0 for w in range(n)):
            continue
        out = check_instance("rand%d" % t, g, x)
        if out and out[2] is not None and out[1] > 0:
            worstratio = max(worstratio, float(out[2] / out[1]))
    print("  400 random weighted instances: worst ratio Lambda/proof-bound = %.6f" % worstratio)

    print()
    print("FAILURES:", FAIL if FAIL else "none")
