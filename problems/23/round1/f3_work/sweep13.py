"""n=13 slice of the template sweep, chunked so each job fits in the runner's time budget.
Usage: python sweep13.py <chunk_index> <num_chunks>
"""
import sys, os, time
import numpy as np
from beta import Template, g6_decode
from opt import climb, starts_for
from refine import refine, exact_check

HERE = os.path.dirname(os.path.abspath(__file__))
ci, nc = int(sys.argv[1]), int(sys.argv[2])
n = 13
lines = [L for L in open(os.path.join(HERE, "maxtf_%d.g6" % n)).read().split() if L]
mine = lines[ci::nc]
t0 = time.time()
mx = (0.0, None, None)
viol = 0
for L in mine:
    nn, E = g6_decode(L, n)
    t = Template(nn, E)
    pool = []
    for w0 in starts_for(t, 25, seed=7, nrand=5, cap_cycles=10):
        v, w = climb(t, w0)
        pool.append((v, list(w)))
    pool.sort(key=lambda z: -z[0])
    best = (25.0 * pool[0][0] / 625.0, 25, pool[0][1], pool[0][0])
    for v, w in pool[:2]:
        x, _ = refine(t, np.array(w, float) + 1e-9)
        e = exact_check(t, x)
        if e[0] > best[0]:
            best = e
    cur = best[2]
    for D in (50, 100):
        s = np.floor(np.array(cur, float) * D / sum(cur))
        s[int(np.argmax(s))] += D - s.sum()
        if s.min() < 0:
            break
        v, w = climb(t, s)
        r = 25.0 * v / D ** 2
        if r > best[0]:
            best = (r, D, [int(z) for z in w], v)
        cur = [int(z) for z in w]
    if best[0] > 1.0 + 1e-9:
        viol += 1
        print("!!! VIOLATION g6=%s %s" % (L, best), flush=True)
    if best[0] > mx[0]:
        mx = (best[0], L, best[1:])
print("chunk %d/%d: %d templates  max ratio = %.9f at %s %s  violations=%d  [%.0fs]"
      % (ci, nc, len(mine), mx[0], mx[1], mx[2], viol, time.time() - t0), flush=True)
