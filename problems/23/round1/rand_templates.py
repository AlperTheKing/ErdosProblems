"""Counterexample hunt beyond the exhaustive range: random MAXIMAL triangle-free templates on
n = 14..17 vertices (the geng enumeration is only feasible to n = 13).

A random maximal triangle-free graph is grown by repeatedly adding a uniformly random non-edge
whose addition keeps the graph triangle-free, until none remains. beta is then maximised with the
same calibrated optimiser (structured 5-cycle starts + hill climbing + SLSQP + exact integer
re-check). Any ratio > 1 refutes Erdos #23.

Usage: python rand_templates.py <n> <count> <seed>
"""
import sys, random, time
import numpy as np
from beta import Template
from opt import climb, starts_for
from refine import refine, exact_check

n, cnt, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
t0 = time.time()
mx = (0.0, None, None)
viol = 0
for it in range(cnt):
    adj = [0] * n
    cand = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(cand)
    for (u, v) in cand:
        if adj[u] & adj[v]:
            continue                      # would create a triangle
        adj[u] |= 1 << v; adj[v] |= 1 << u
    E = [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]
    t = Template(n, E)
    pool = []
    for w0 in starts_for(t, 25, seed=seed + it, nrand=6, cap_cycles=12):
        val, w = climb(t, w0)
        pool.append((val, list(w)))
    pool.sort(key=lambda z: -z[0])
    best = (25.0 * pool[0][0] / 625.0, 25, pool[0][1], pool[0][0])
    for val, w in pool[:2]:
        x, _ = refine(t, np.array(w, float) + 1e-9)
        e = exact_check(t, x)
        if e[0] > best[0]:
            best = e
    if best[0] > 1.0 + 1e-9:
        viol += 1
        print("!!! VIOLATION n=%d |E|=%d %s" % (n, len(E), best), flush=True)
    if best[0] > mx[0]:
        mx = (best[0], len(E), best[1:])
print("n=%d  %d random maximal triangle-free templates  max ratio = %.9f  (|E|=%s)  violations=%d  [%.0fs]"
      % (n, cnt, mx[0], mx[1], viol, time.time() - t0), flush=True)
