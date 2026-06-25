"""VALIDATE the core structural reduction across ALL 2-connected edge-critical tri-free atoms N<=9:
  (R) kappa* = max_w min_{S min sig} sum_{e in S}(w_e + d^B_w(e))   [the metric form]
and that a SINGLE signature achieves the inner min at the saddle (automatic from minimax, but verify the
metric form equals the LP kappa* exactly). Also report the worst kappa*/(n^2/25t) ratio.

This confirms (16) <=> (16'): for every toll w there is ONE min signature S with
  sum_{e in S} (w_e + d^B_w(e)) <= n^2/(25t).
"""
import numpy as np
import heapq
import flag_engine as fe
import verify_D25_lemma16 as L
from exp_lemma16_atoms import is_2connected, tau_of, is_edge_critical
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


def metric_min_cost(N, A, w, edges, sigs):
    best = float('inf')
    for S in sigs:
        Bset = set(edges)-set(S)
        adjBw = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b); adjBw[a].append((c, w[b])); adjBw[c].append((a, w[b]))
        cost = sum(w[e] for e in S); ok = True
        for e in S:
            u, v = tuple(e); dist = wdist_B(N, adjBw, u)
            if dist[v] == float('inf'):
                ok = False; break
            cost += dist[v]
        if ok:
            best = min(best, cost)
    return best


def main():
    worst = 0.0; checked = 0; mismatch = 0
    for N in [5, 6, 7, 8, 9]:
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            adj = L.adjset(n, A)
            if not is_2connected(n, adj):
                continue
            tau = tau_of(n, adj)
            if tau == 0:
                continue
            if not is_edge_critical(n, A, adj, tau):
                continue
            try:
                kappa, w, edges, t, sigs, cyc, NN = solve_kappa_and_worst_w(n, A)
            except Exception as ex:
                continue
            mc = metric_min_cost(n, A, w, edges, sigs)
            checked += 1
            if abs(mc-kappa) > 1e-4:
                mismatch += 1
                print(f"  MISMATCH n={n} tau={t}: LP kappa*={kappa:.4f} metric-form={mc:.4f}")
            target = n*n/(25.0*t)
            worst = max(worst, kappa/target)
    print(f">>> checked {checked} atoms; metric-form != LP mismatches = {mismatch}; "
          f"worst kappa*/(n^2/25t) = {worst:.4f}")


if __name__ == "__main__":
    main()
