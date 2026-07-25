"""Full counterexample sweep: every MAXIMAL triangle-free template H on 5..13 vertices,
maximise 25*bip(H[w])/D^2 over integer weightings (structured C5/C7/C9-supported starts +
random starts + hill climbing with multi-unit moves + continuous SLSQP refinement, then an
EXACT integer re-check of the refined point).

ratio > 1 anywhere  ==>  explicit counterexample to Erdos #23 (bip <= N^2/25).
Calibration: every template containing a 5-cycle must return exactly 1.000000.
"""
import sys, os, time
import numpy as np
from beta import Template, g6_decode
from opt import climb, starts_for
from refine import refine, exact_check

HERE = os.path.dirname(os.path.abspath(__file__))
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 13


def best_for(t, seed=3, cap=40, nrand=25):
    pool = []
    for w0 in starts_for(t, 25, seed=seed, nrand=nrand, cap_cycles=cap):
        v, w = climb(t, w0)
        pool.append((v, list(w)))
    pool.sort(key=lambda z: -z[0])
    best = (25.0 * pool[0][0] / 625.0, 25, pool[0][1], pool[0][0])
    for v, w in pool[:5]:
        x, _ = refine(t, np.array(w, float) + 1e-9)
        e = exact_check(t, x)
        if e[0] > best[0]:
            best = e
    # ladder from the winner
    cur = best[2]
    for D in (50, 100, 200):
        s = np.floor(np.array(cur, float) * D / sum(cur))
        s[int(np.argmax(s))] += D - s.sum()
        if s.min() < 0:
            break
        v, w = climb(t, s)
        r = 25.0 * v / D ** 2
        if r > best[0]:
            best = (r, D, [int(z) for z in w], v)
        cur = [int(z) for z in w]
    return best


t0 = time.time()
worst = (0.0, None)
viol = 0
for n in range(5, NMAX + 1):
    path = os.path.join(HERE, "maxtf_%d.g6" % n)
    if not os.path.exists(path):
        continue
    lines = [L for L in open(path).read().split() if L]
    mx = (0.0, None, None)
    for L in lines:
        nn, E = g6_decode(L, n)
        t = Template(nn, E)
        r, D, w, b = best_for(t)
        if r > 1.0 + 1e-9:
            viol += 1
            print("!!! VIOLATION n=%d g6=%s D=%d w=%s bip=%d ratio=%.9f" % (n, L, D, w, b, r), flush=True)
        if r > mx[0]:
            mx = (r, L, (D, w, b))
    print("n=%2d templates=%4d  max ratio = %.9f  at %s %s   [%.0fs]"
          % (n, len(lines), mx[0], mx[1], mx[2], time.time() - t0), flush=True)
    if mx[0] > worst[0]:
        worst = (mx[0], (n, mx[1]))
print("\nOVERALL max 25*bip/D^2 = %.9f at %s ; violations=%d" % (worst[0], worst[1], viol))
