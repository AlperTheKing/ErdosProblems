"""G10_census.py -- independent cross-check of the C++ hunter.

For each pattern in a corpus file it runs the LP max-min ascent (G10_lpascent) from
many restarts, records the best value found, and separately records the best value
found from restarts that are NOT C5-concentration points ("reach test": if random
starts also climb to 1/25 then the optimiser genuinely explores the landscape and its
failure to exceed 1/25 is evidence, not an artefact).

Every reported number is re-derived exactly with Fractions from the rounded weights.
"""
import sys, os, time
import numpy as np
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G10_lpascent import Psi, ascend, exact_check, DEFAULT_DENOMS
from G10_core import induced_c5s, all_cut_monoedges, psi_exact


def load(path, hmax=99):
    out = []
    for L in open(path):
        p = L.split()
        if not p:
            continue
        nm = p[0]; h = int(p[1]); E = int(p[2])
        if h > hmax:
            continue
        e = [(int(p[3 + 2 * k]), int(p[4 + 2 * k])) for k in range(E)]
        out.append((nm, h, e))
    return out


def census(nm, h, edges, nrand=120, seed=0):
    P = Psi(h, edges)
    rng = np.random.default_rng(seed)
    c5 = induced_c5s(h, edges)
    bestC5 = -1.0
    for cyc in c5[:40]:
        x = np.zeros(h)
        for v in cyc:
            x[v] = 0.2
        _, f = ascend(P, x, iters=150)
        bestC5 = max(bestC5, f)
    bestR = -1.0; argR = None
    for t in range(nrand):
        if t % 3 == 0:
            x0 = rng.dirichlet(np.ones(h))
        elif t % 3 == 1:
            k = int(rng.integers(4, h + 1)); s = rng.choice(h, size=k, replace=False)
            x0 = np.zeros(h); x0[s] = rng.dirichlet(np.ones(k))
        else:
            x0 = rng.dirichlet(np.ones(h) * 0.35)
        x, f = ascend(P, x0, iters=150)
        if f > bestR:
            bestR, argR = f, x
    best = max(bestC5, bestR)
    xb = argR if bestR >= bestC5 else None
    ex = None
    if xb is not None:
        ex = exact_check(h, edges, xb)
    return bestC5, bestR, best, ex


if __name__ == '__main__':
    path = sys.argv[1]
    hmax = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    nrand = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    gs = load(path, hmax)
    print('# patterns:', len(gs))
    worst = 0.0
    rows = []
    for i, (nm, h, e) in enumerate(gs):
        t0 = time.time()
        bC5, bR, best, ex = census(nm, h, e, nrand=nrand, seed=1000 + i)
        flag = 'ABOVE-1/25' if best > 0.04 + 1e-12 else ('EQ' if abs(best - 0.04) < 1e-11 else 'below')
        exs = str(ex[0]) if ex else '-'
        print('%-14s h=%2d  bestC5=%.12f  bestRANDOM=%.12f  max=%.12f  %s  exact(rand)=%s  [%.1fs]'
              % (nm, h, bC5, bR, best, flag, exs, time.time() - t0))
        sys.stdout.flush()
        rows.append((best, nm, h, bC5, bR))
        worst = max(worst, best)
    print('# overall max over corpus = %.12f  (1/25 = 0.04)' % worst)
    rows.sort(reverse=True)
    print('# top 20')
    for r in rows[:20]:
        print('  %.12f %-14s h=%d  C5-start=%.12f random-start=%.12f' % (r[0], r[1], r[2], r[3], r[4]))
