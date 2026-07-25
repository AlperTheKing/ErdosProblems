"""R8_thmA_sweep.py -- lean broad falsification sweep over random maximal
triangle-free graphs, with an exact cross-check of the proof of Theorem A.

For each graph:
  * float multistart ascent for max_x Lambda,
  * exact rational re-evaluation at the best x (several denominators),
  * exact C5-leak scan (weight moved off a 5-cycle onto outside vertices),
  * for every x examined exactly: check Lambda_exact <= 1/(2 gamma) <= 1/25,
    where gamma = min over odd cycles of sum_{v in C} 1/d(v).

Maximality is WLOG: Lambda is monotone under adding edges, so on a fixed vertex
set the maximum over triangle-free graphs is attained at a maximal one.
"""

from fractions import Fraction
import random
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *            # noqa
from R8_thmA_search import maximize, exact_check, five_cycles, c5_starts   # noqa
from R8_thmA_proofcheck import proof_bound                                  # noqa

ONE25 = Fraction(1, 25)
VIOL = []


def exact_probe(g, x, tag):
    """exact Lambda at x + exact proof-bound cross-check. Returns Lambda."""
    r = exact_lambda(g, x)
    v = r.verify()
    if not (v["primal_feasible"] and v["dual_feasible"] and v["match"]):
        VIOL.append(("CERTIFICATE", tag, str(v)))
    gamma, cost, y, flags = proof_bound(g, x)
    if not flags.get("bipartite"):
        if r.value > cost:
            VIOL.append(("LAMBDA>PROOFBOUND", tag, g.graph6(), str(r.value), str(cost)))
        if not flags["gamma_ge_25_over_2"]:
            VIOL.append(("GAMMA<25/2", tag, g.graph6(), str(gamma)))
    if r.value > ONE25:
        VIOL.append(("OVER_1/25", tag, g.graph6(), str(r.value), [str(t) for t in x]))
        print("  *** OVER 1/25 ***", g.graph6(), r.value, [str(t) for t in x])
    return r.value


def leak_scan(g, ncyc=3):
    best = Fraction(0)
    for C in five_cycles(g, ncyc):
        rest = [u for u in range(g.n) if u not in C]
        for t in [Fraction(0), Fraction(1, 25), Fraction(1, 10), Fraction(1, 4)]:
            targets = [None] if t == 0 else ([[u] for u in rest[:6]] + ([rest] if rest else []))
            for tg in targets:
                x = [Fraction(0)] * g.n
                for u in C:
                    x[u] = (1 - t) / 5
                if tg:
                    for u in tg:
                        x[u] += t / len(tg)
                s = sum(x)
                if s == 0:
                    continue
                best = max(best, exact_probe(g, [q / s for q in x], "leak"))
    return best


if __name__ == "__main__":
    nmin, nmax, per_n = 6, 14, 60
    if len(sys.argv) > 3:
        nmin, nmax, per_n = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(202607261)
    overall = Fraction(0)
    for n in range(nmin, nmax + 1):
        t0 = time.time()
        seen = set()
        best_n = Fraction(0)
        wit = None
        cnt = 0
        tries = 0
        while cnt < per_n and tries < per_n * 12:
            tries += 1
            g = random_maximal_triangle_free(n, rng)
            k = canon_key(g)
            if k in seen or g.is_bipartite():
                continue
            seen.add(k)
            cnt += 1
            best, bestx, ev = maximize(g, restarts=6, iters=20, seed=tries,
                                       x0list=c5_starts(g, k=2, eps=(0.0, 0.05)))
            val, xr, _ = exact_check(g, bestx, denom=None)
            exact_probe(g, xr, "ascent")
            val = max(val, leak_scan(g))
            xu = [Fraction(1, n)] * n
            val = max(val, exact_probe(g, xu, "uniform"))
            if val > best_n:
                best_n, wit = val, g.graph6()
        overall = max(overall, best_n)
        print("n=%2d  %3d distinct non-bipartite maximal triangle-free graphs | "
              "max exact Lambda = %-10s = %.12f | %s | %.0fs"
              % (n, cnt, best_n, float(best_n),
                 "== 1/25" if best_n == ONE25 else ("OVER 1/25" if best_n > ONE25 else "< 1/25"),
                 time.time() - t0))
        sys.stdout.flush()
    print()
    print("OVERALL max exact Lambda = %s = %.12f   (1/25 = 0.04)" % (overall, float(overall)))
    print("VIOLATIONS:", VIOL if VIOL else "none")
