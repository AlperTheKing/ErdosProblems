"""R8_thmA_search.py -- search for a triangle-free (G,x) with Lambda(G,x) > 1/25.

Floats are used only to STEER the search.  Every reported number is recomputed
with exact rational arithmetic (exact_lambda + LambdaResult.verify).
"""

from fractions import Fraction
import itertools
import json
import random
import sys
import time

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from R8_thmA_lib import *   # noqa

TARGET = 1.0 / 25.0


class Evaluator:
    """Lambda(G,x) by cutting planes over a persistent cycle pool (float)."""

    def __init__(self, g):
        self.g = g
        self.rows = []
        self.keys = set()
        self.cycles = []
        L, C = shortest_odd_cycle(g, [0.0] * g.m)
        self.bipartite = (C is None)
        if C is not None:
            self.add(C)

    def add(self, C):
        k = frozenset(cycle_edges(C))
        if k in self.keys:
            return False
        self.keys.add(k)
        self.cycles.append(C)
        r = np.zeros(self.g.m)
        for e in cycle_edges(C):
            r[self.g.eidx[e]] = 1.0
        self.rows.append(r)
        return True

    def __call__(self, x):
        g = self.g
        if self.bipartite:
            return 0.0, np.zeros(g.m)
        w = np.array([x[u] * x[v] for (u, v) in g.edges], dtype=float)
        for _ in range(6000):
            A = -np.vstack(self.rows)
            b = -np.ones(len(self.rows))
            res = linprog(w, A_ub=A, b_ub=b, bounds=[(0, None)] * g.m, method="highs")
            if not res.success:
                raise RuntimeError(res.message)
            y = np.maximum(res.x, 0.0)
            L, C = shortest_odd_cycle(g, list(y))
            if L is None or L >= 1 - 1e-7 or not self.add(C):
                return float(res.fun), y
        raise RuntimeError("no convergence")


def replicator(g, y, x, steps=40):
    """Increase f(x)=sum_e y_e x_u x_v on the simplex (monotone for y>=0)."""
    n = g.n
    A = np.zeros((n, n))
    for i, (u, v) in enumerate(g.edges):
        A[u, v] = A[v, u] = y[i]
    x = np.array(x, dtype=float)
    for _ in range(steps):
        gr = A.dot(x)
        d = float(x.dot(gr))
        if d <= 0:
            break
        nx = x * gr / d
        s = nx.sum()
        if s <= 0:
            break
        nx = nx / s
        if np.max(np.abs(nx - x)) < 1e-13:
            x = nx
            break
        x = nx
    return x


def maximize(g, restarts=40, iters=60, seed=0, x0list=None, ev=None):
    rng = np.random.default_rng(seed)
    ev = ev or Evaluator(g)
    if ev.bipartite:
        return 0.0, np.ones(g.n) / g.n, ev
    best = -1.0
    bestx = None
    starts = []
    if x0list:
        starts += [np.array(x, dtype=float) for x in x0list]
    starts.append(np.ones(g.n) / g.n)
    for _ in range(restarts):
        a = rng.choice([0.3, 1.0, 3.0])
        v = rng.dirichlet(np.full(g.n, a))
        starts.append(v)
    for x in starts:
        cur, y = ev(x)
        if cur > best:
            best, bestx = cur, x.copy()
        for it in range(iters):
            xn = replicator(g, y, x, steps=25)
            for alpha in (1.0, 0.5, 0.25, 0.1, 0.03):
                cand = (1 - alpha) * x + alpha * xn
                cand = np.maximum(cand, 0.0)
                cand = cand / cand.sum()
                val, yy = ev(cand)
                if val > cur + 1e-15:
                    x, cur, y = cand, val, yy
                    break
            else:
                break
            if cur > best:
                best, bestx = cur, x.copy()
    return best, bestx, ev


def exact_check(g, xf, denom=None, ev=None):
    """Rationalise xf and compute the exact Lambda; try several denominators."""
    outs = []
    for D in ([denom] if denom else [5, 10, 20, 25, 50, 100, 200, 1000, 10000]):
        xr = [Fraction(int(round(t * D)), D) for t in xf]
        s = sum(xr)
        if s == 0:
            continue
        xr = [t / s for t in xr]
        r = exact_lambda(g, xr)
        v = r.verify()
        assert v["primal_feasible"] and v["dual_feasible"] and v["match"], v
        outs.append((r.value, xr, r))
    outs.sort(key=lambda t: -t[0])
    return outs[0]


def report(name, g, best, bestx, exact_val, exact_x, extra=""):
    print("%-34s n=%2d m=%3d og=%s  maxLambda~%.10f  exact=%s=%.10f  %s%s"
          % (name, g.n, g.m, g.odd_girth(), best, exact_val, float(exact_val),
             "OVER 1/25 !!!" if exact_val > Fraction(1, 25) else "", extra))
    sys.stdout.flush()


def run(name, g, restarts=40, iters=60, seed=0, x0list=None):
    assert not g.has_triangle(), name + " has a triangle"
    t0 = time.time()
    best, bestx, ev = maximize(g, restarts=restarts, iters=iters, seed=seed, x0list=x0list)
    val, xr, r = exact_check(g, bestx)
    report(name, g, best, bestx, val, xr, extra="  [%.1fs, %d cycles pooled]" % (time.time() - t0, len(ev.cycles)))
    return {"name": name, "n": g.n, "m": g.m, "g6": g.graph6(),
            "odd_girth": g.odd_girth(), "float_max": best,
            "exact": str(val), "exact_float": float(val),
            "x": [str(t) for t in xr], "over": val > Fraction(1, 25)}


def five_cycles(g, k=40):
    """all 5-cycles, direct (never calls the full cycle enumerator)."""
    out = []
    adj = g.adj
    for a in range(g.n):
        for b in adj[a]:
            if b < a:
                continue
            for c in adj[b]:
                if c <= a or c == b:
                    continue
                for d in adj[c]:
                    if d <= a or d in (b, c):
                        continue
                    for e in adj[d]:
                        if e <= a or e in (b, c, d) or e <= b:
                            continue
                        if a in adj[e]:
                            out.append([a, b, c, d, e])
                            if len(out) >= k:
                                return out
    return out


def c5_starts(g, k=12, eps=(0.0, 0.02, 0.08, 0.25)):
    """x on a 5-cycle of G (Lambda = 1/25 exactly), plus leaked versions.

    The leak matters: replicator dynamics preserve zero coordinates, so a pure
    C5-supported start can never explore off its own face.
    """
    outs = []
    rng = np.random.default_rng(11)
    for C in five_cycles(g, k):
        for e in eps:
            v = np.zeros(g.n)
            for u in C:
                v[u] = 0.2 * (1 - e)
            rest = [u for u in range(g.n) if u not in C]
            if rest:
                sp = rng.dirichlet(np.ones(len(rest)))
                for i, u in enumerate(rest):
                    v[u] = e * sp[i]
            elif e > 0:
                continue
            outs.append(v / v.sum())
    return outs


def perturb_scan(g, tag=""):
    """Exactly evaluate Lambda at C5-concentration leaked onto outside vertices.

    Returns the exact maximum found (a rigorous lower bound on max_x Lambda).
    """
    best = Fraction(0)
    bestx = None
    C5s = five_cycles(g, 60)
    for C in C5s:
        rest = [u for u in range(g.n) if u not in C]
        for t in [Fraction(0), Fraction(1, 100), Fraction(1, 50), Fraction(1, 25),
                  Fraction(1, 10), Fraction(1, 5)]:
            for target in ([None] + [[u] for u in rest] + ([rest] if rest else [])):
                if t > 0 and target is None:
                    continue
                if t == 0 and target is not None:
                    continue
                x = [Fraction(0)] * g.n
                for u in C:
                    x[u] = (1 - t) / 5
                if target:
                    for u in target:
                        x[u] += t / len(target)
                s = sum(x)
                x = [xi / s for xi in x]
                val = exact_lambda(g, x).value
                if val > best:
                    best, bestx = val, x
    return best, bestx


def part_a():
    results = []
    print("=" * 100)
    print("A. C5 and C5 blow-ups (exact)")
    print("=" * 100)
    C5 = cycle_graph(5)
    r = exact_lambda(C5, [Fraction(1, 5)] * 5)
    print("C5 uniform: Lambda = %s  (verify %s)" % (r.value, r.verify()))
    # unbalanced weights on C5 itself
    worst = Fraction(0)
    rng = random.Random(7)
    for trial in range(4000):
        p = [Fraction(rng.randint(0, 40), 1) for _ in range(5)]
        s = sum(p)
        if s == 0:
            continue
        p = [t / s for t in p]
        val = exact_lambda(C5, p).value
        if val > worst:
            worst = val
            wp = p
    print("C5, 4000 random rational x: max Lambda = %s = %.10f at x=%s"
          % (worst, float(worst), wp))
    # blow-ups with unequal parts, uniform inside parts
    print("\nC5 blow-ups C5[a1..a5], x uniform on the whole vertex set:")
    for sizes in [(1,1,1,1,1),(2,1,1,1,1),(2,2,1,1,1),(2,1,2,1,1),(3,1,1,1,1),
                  (2,2,2,2,2),(3,2,2,2,2),(3,3,2,2,2),(2,2,2,1,1),(3,2,1,2,1),
                  (4,1,1,1,1),(1,1,1,1,0),(2,2,1,1,0),(3,3,3,3,3)]:
        gb, parts = blowup_C5(sizes)
        if gb.n == 0 or gb.m == 0:
            continue
        xu = [Fraction(1, gb.n)] * gb.n
        rb = exact_lambda(gb, xu)
        assert rb.verify()["match"]
        print("   sizes=%-16s n=%2d  Lambda(uniform x) = %-12s = %.10f %s"
              % (str(sizes), gb.n, rb.value, float(rb.value),
                 "OVER" if rb.value > Fraction(1, 25) else ""))
    print("\nC5 blow-ups, x optimised (part weights free):")
    for sizes in [(2,2,2,2,2),(3,2,2,1,1),(2,1,2,1,2),(3,3,1,1,1),(2,2,2,1,1)]:
        gb, parts = blowup_C5(sizes)
        results.append(run("C5%s" % (str(sizes),), gb, restarts=30, iters=50, seed=1))

    with open("R8_thmA_results_partA.json", "w") as f:
        json.dump(results, f, indent=1)
    print("\nwrote R8_thmA_results_partA.json")


def named_graphs():
    return [
        ("C5", cycle_graph(5)),
        ("C7", cycle_graph(7)),
        ("C9", cycle_graph(9)),
        ("C11", cycle_graph(11)),
        ("Petersen", petersen()),
        ("Grotzsch", grotzsch()),
        ("Wagner=circle(8,8)", wagner()),
        ("Gamma_11=circle(11,11)", circle_graph(11, 11)),
        ("Gamma_14=circle(14,14)", circle_graph(14, 14)),
        ("Gamma_17=circle(17,17)", circle_graph(17, 17)),
        ("And(3)", andrasfai(3)),
        ("And(4)", andrasfai(4)),
        ("And(5)", andrasfai(5)),
        ("And(6)", andrasfai(6)),
        ("Myc(C7)", mycielskian(cycle_graph(7))),
        ("Myc(Petersen)", mycielskian(petersen())),
        ("Clebsch", clebsch()),
        ("Kneser(7,3)=O4", kneser(7, 3)),
        ("McGee(girth7)", mcgee()),
    ]


def clebsch():
    """folded 5-cube = Clebsch graph srg(16,5,0,2): Cayley(F_2^4, {e1..e4,1111})."""
    S = [1, 2, 4, 8, 15]
    edges = []
    for a in range(16):
        for s in S:
            b = a ^ s
            if a < b:
                edges.append((a, b))
    return Graph(16, edges)


def mcgee():
    """(3,7)-cage, 24 vertices, girth 7."""
    lcf = [12, 7, -7] * 8
    n = 24
    edges = [(i, (i + 1) % n) for i in range(n)]
    for i, s in enumerate(lcf):
        j = (i + s) % n
        edges.append((min(i, j), max(i, j)))
    return Graph(n, edges)


def part_b():
    results = []
    print("=" * 100)
    print("B. named graphs")
    print("=" * 100)
    for nm, g in named_graphs():
        if g.has_triangle():
            print("SKIP %s: has a triangle" % nm)
            continue
        # uniform-x value, exactly
        xu = [Fraction(1, g.n)] * g.n
        ru = exact_lambda(g, xu)
        assert ru.verify()["match"]
        x0 = c5_starts(g, k=10)
        r = run(nm, g, restarts=25, iters=40, seed=2, x0list=x0)
        pb, pbx = perturb_scan(g)
        r["uniform_x"] = str(ru.value)
        r["uniform_x_float"] = float(ru.value)
        r["perturb_scan"] = str(pb)
        r["perturb_scan_float"] = float(pb)
        if pb > Fraction(1, 25):
            print("   *** perturb_scan EXCEEDS 1/25:", pb, pbx)
        print("      uniform-x Lambda = %-14s = %.10f ; C5-leak scan max = %s = %.10f"
              % (ru.value, float(ru.value), pb, float(pb)))
        results.append(r)
    with open("R8_thmA_results_partB.json", "w") as f:
        json.dump(results, f, indent=1)
    print("\nwrote R8_thmA_results_partB.json")


def part_c(nmin=6, nmax=14, per_n=120, seed=123):
    """random maximal triangle-free graphs (WLOG maximal: Lambda is monotone
    under adding edges, so the max over triangle-free graphs on n vertices is
    attained on a maximal one)."""
    results = []
    print("=" * 100)
    print("C. random maximal triangle-free graphs, n=%d..%d, %d each" % (nmin, nmax, per_n))
    print("=" * 100)
    rng = random.Random(seed)
    overall = Fraction(0)
    for n in range(nmin, nmax + 1):
        seen = set()
        best_n = Fraction(0)
        best_rec = None
        t0 = time.time()
        cnt = 0
        for t in range(per_n):
            g = random_maximal_triangle_free(n, rng)
            k = canon_key(g)
            if k in seen:
                continue
            seen.add(k)
            if g.is_bipartite():
                continue
            cnt += 1
            best, bestx, ev = maximize(g, restarts=8, iters=25, seed=t, x0list=c5_starts(g, k=4))
            val, xr, r = exact_check(g, bestx)
            pb, pbx = perturb_scan(g)
            val = max(val, pb)
            if val > Fraction(1, 25):
                print("!!! OVER 1/25:", g.graph6(), val, xr)
            if val > best_n:
                best_n, best_rec = val, (g.graph6(), [str(z) for z in xr], best)
        print("n=%2d: %3d distinct non-bipartite maximal graphs, max exact Lambda = %s = %.12f  (float max %.10f) [%.0fs]"
              % (n, cnt, best_n, float(best_n), best_rec[2] if best_rec else 0, time.time() - t0))
        results.append({"n": n, "count": cnt, "max_exact": str(best_n),
                        "max_float": float(best_n), "witness": best_rec})
        overall = max(overall, best_n)
    print("\nOVERALL max exact Lambda over part C: %s = %.12f  (1/25 = 0.04)" % (overall, float(overall)))
    with open("R8_thmA_results_partC.json", "w") as f:
        json.dump(results, f, indent=1)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "a"
    if which == "a":
        part_a()
    elif which == "b":
        part_b()
    elif which == "c":
        part_c(*[int(z) for z in sys.argv[2:]])
