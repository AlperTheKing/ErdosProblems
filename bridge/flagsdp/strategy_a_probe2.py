"""Follow-up: at the saddle, a single signature S achieves kappa*. So (16) reduces to:

  (16')  for EVERY toll w>=0 (sum w=1), there EXISTS a min signature S with
            sum_{e in S} min_{C odd, C cap S = {e}} w(C)  <=  n^2/(25 t).

Strengthen: choose S to be a min signature, B=K-S bipartite. The private cycle for e=uv is e + a B-path
from u to v. Cheapest private toll = w_e + min_{B-path P: u->v} w(P) = w_e + d^B_w(u,v) where d^B_w is the
w-shortest-path distance in B. So:

  cost(S,w) = sum_{e in S} ( w_e + d^B_w(endpoints of e) ).

We want min_S cost(S,w) <= n^2/(25t). Note sum_e w_e <= sum_a w_a = 1 (signatures are edge sets, disjoint
from B). So the real content is sum_{e in S} d^B_w(u_e, v_e) <= n^2/(25t) - (mass of w on S).

THIS is the GPT 'metric inequality' MT-style object but with ONE signature and the w-metric on B.
Test: (a) confirm cost(S,w) = sum_e (w_e + d^B_w) exactly; (b) see the structure of the minimizing S;
(c) at the worst w, what is sum_e d^B_w?  Relate to Cauchy/cycle-degree.
"""
import numpy as np
import heapq
from collections import deque
import verify_D25_lemma16 as L
from strategy_a_probe import solve_kappa_and_worst_w


def wdist_B(N, adjB_w, s):
    dist = [float('inf')]*N; dist[s] = 0.0; pq = [(0.0, s)]
    while pq:
        d0, x = heapq.heappop(pq)
        if d0 > dist[x]+1e-12:
            continue
        for (y, wt) in adjB_w[x]:
            if dist[x]+wt < dist[y]-1e-12:
                dist[y] = dist[x]+wt; heapq.heappush(pq, (dist[y], y))
    return dist


def analyze(builder, lab):
    kappa, w, edges, tau, sigs, cyc, N = solve_kappa_and_worst_w(*builder)
    target = N*N/(25.0*tau)
    print(f"\n=== {lab}: kappa*={kappa:.4f} target={target:.4f} tau={tau} N={N} ===")
    best = None
    for S in sigs:
        Bset = set(edges)-set(S)
        adjBw = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b); adjBw[a].append((c, w[b])); adjBw[c].append((a, w[b]))
        wmass_S = sum(w[e] for e in S)
        dsum = 0.0; ok = True
        for e in S:
            u, v = tuple(e); dist = wdist_B(N, adjBw, u)
            if dist[v] == float('inf'):
                ok = False; break
            dsum += dist[v]
        if not ok:
            continue
        cost = wmass_S + dsum
        if best is None or cost < best[0]:
            best = (cost, wmass_S, dsum, S)
    cost, wmass_S, dsum, S = best
    print(f"  min cost over sigs = {cost:.4f} (= kappa* {kappa:.4f}? {abs(cost-kappa)<1e-4})")
    print(f"  decomposition: w-mass on S = {wmass_S:.4f}, sum_e d^B_w(endpoints) = {dsum:.4f}")
    print(f"  so 'metric part' sum_e d^B_w = {dsum:.4f}  <= target-wmass = {target-wmass_S:.4f}")


for b, lab in [(L.gpt_k23(), 'K23-N13'), (L.petersen(), 'Petersen'), (L.c5n(2), 'C5[2]'), (L.c5n(3), 'C5[3]')]:
    analyze(b, lab)
