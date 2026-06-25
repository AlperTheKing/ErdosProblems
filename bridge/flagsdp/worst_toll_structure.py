"""Examine the structure of the WORST toll w* (dual maximizer of (16')) and whether the metric
inequality reduces to a CUT/coarea inequality.

The metric LP (16') dual: kappa* = max_w min_S sum_e (w_e + d^B_w(e)). For FIXED S, the inner sum_e d^B_w(e)
is a concave function of w (min of linear). The outer max over w of a min over S of concave... messy.

Alternative clean view (sparsest-cut style): introduce, for each min signature S, the value
  phi(S, w) = sum_{e in S} (w_e + d^B_w(e)).
We want min_S phi(S,w) <= n^2/(25t). The metric d^B_w is realized by shortest paths. By LP duality on the
shortest-path subproblem, d^B_w(u,v) = max over potentials... Instead, let's just CHARACTERIZE w*:
  - support size, whether uniform, whether it's the indicator of an odd cycle / a cut / the K23 core.
  - relationship to the EXTREMAL packing (the y_C that the bound produces).

Also test the DIRECT sufficient inequality candidate:
  (CAND)  min_S sum_e d^B_w(e)  <=  (n^2/(25t)) - sum_{e in S} w_e,
  via:  sum_e d^B_w(e) <= sqrt( |S| * sum_e d^B_w(e)^2 )  and a cycle-degree bound on d^B_w(e)^2... test numerically.
"""
import numpy as np
import heapq
import verify_D25_lemma16 as L
from strategy_a_probe import solve_kappa_and_worst_w


def wdist_B(N, adjBw, s):
    dist = [float('inf')]*N; dist[s] = 0.0; pq = [(0.0, s)]
    while pq:
        d0, x = heapq.heappop(pq)
        if d0 > dist[x]+1e-12:
            continue
        for (y, wt) in adjBw[x]:
            if dist[x]+wt < dist[y]-1e-12:
                dist[y] = dist[x]+wt; heapq.heappush(pq, (dist[y], y))
    return dist


def best_sig(N, w, edges, sigs):
    best = None
    for S in sigs:
        Bset = set(edges)-set(S)
        adjBw = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b); adjBw[a].append((c, w[b])); adjBw[c].append((a, w[b]))
        cost = sum(w[e] for e in S); ds = []; ok = True
        for e in S:
            u, v = tuple(e); dist = wdist_B(N, adjBw, u)
            if dist[v] == float('inf'):
                ok = False; break
            ds.append(dist[v]); cost += dist[v]
        if ok and (best is None or cost < best[0]):
            best = (cost, S, ds)
    return best


def analyze(builder, lab):
    kappa, w, edges, tau, sigs, cyc, N = solve_kappa_and_worst_w(*builder)
    target = N*N/(25.0*tau)
    nz = [(tuple(sorted(a)), round(v, 4)) for a, v in w.items() if v > 1e-6]
    vals = sorted(set(round(v, 4) for a, v in w.items() if v > 1e-6))
    cost, S, ds = best_sig(N, w, edges, sigs)
    print(f"\n=== {lab}: kappa*={kappa:.4f} target={target:.4f} N={N} tau={tau} ===")
    print(f"  w* support={len(nz)} edges, distinct values={vals}, uniform={len(vals)==1}")
    print(f"  best S bad-edge w-distances d^B_w(e) = {[round(x,4) for x in ds]}, sum={sum(ds):.4f}")
    print(f"  Cauchy: sqrt(tau * sum d^2)={np.sqrt(tau*sum(x*x for x in ds)):.4f} vs sum d={sum(ds):.4f}")
    # is w* the indicator (scaled) of an odd cycle's edges, or a cut?
    # check: do the support edges form a connected odd subgraph?
    return nz


for b, lab in [(L.gpt_k23(), 'K23-N13'), (L.petersen(), 'Petersen'), (L.c5n(2), 'C5[2]'), (L.c5(), 'C5')]:
    analyze(b, lab)
