"""Sweep every MAXIMAL triangle-free template H on n <= NMAX vertices and maximise, over
integer weightings w with sum w = D, the exact quantity  25 * bip(H[w]) / D^2.

Any value > 1 is an explicit counterexample to Erdos #23 (blow-ups of triangle-free graphs
are triangle-free). Monotonicity beta(H) <= beta(H') for H subset H' means maximal templates
suffice.

Usage: python sweep.py 12
"""
import sys, os, time
import numpy as np
from beta import Template, g6_decode, maximize

HERE = os.path.dirname(os.path.abspath(__file__))
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 12
DS = [25, 50, 100]

best_overall = (0.0, None, None)
viol = []
t0 = time.time()
for n in range(4, NMAX + 1):
    path = os.path.join(HERE, "maxtf_%d.g6" % n)
    if not os.path.exists(path):
        continue
    lines = [L for L in open(path).read().split() if L]
    nbest = (0.0, None, None)
    for gi, L in enumerate(lines):
        nn, E = g6_decode(L, n)
        t = Template(nn, E)
        prev = None
        for D in DS:
            extra = []
            if prev is not None:
                s = np.round(np.array(prev, dtype=float) * D / sum(prev))
                s[0] += D - s.sum()
                if s.min() >= 0:
                    extra.append(s)
            b, w = maximize(t, D, restarts=18 if D < 100 else 8, seed=1234 + D, starts_extra=extra)
            r = 25.0 * b / D ** 2
            prev = w
            if r > 1.0 + 1e-12:
                viol.append((n, L, D, w, b))
                print("!!! VIOLATION n=%d g6=%s D=%d w=%s bip=%d ratio=%.9f" % (n, L, D, w, b, r), flush=True)
            if r > nbest[0]:
                nbest = (r, L, (D, w, b))
    print("n=%2d  templates=%4d  max 25*bip/D^2 = %.9f   at %s %s   [%.1fs]"
          % (n, len(lines), nbest[0], nbest[1], nbest[2], time.time() - t0), flush=True)
    if nbest[0] > best_overall[0]:
        best_overall = nbest

print("\nOVERALL max 25*bip/D^2 = %.9f  template %s  %s" % best_overall)
print("violations:", len(viol))
