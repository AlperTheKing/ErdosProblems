"""Is the worst toll w* ALWAYS uniform on its support, across all 2-connected edge-critical tri-free atoms?
If yes, (16) reduces to the INTEGER statement: for every edge subset E0,
   min_{S min sig} ( |S cap E0| + sum_{e in S} d^{B,E0}(u_e,v_e) )  <=  n^2 |E0| / (25 t),
where d^{B,E0} = shortest-path distance in B=K-S counting only E0-edges (0-1 edge weights). Equivalently
   min_S  (private-cycle selector's total E0-edge count)  <=  n^2 |E0| / (25 t).
We TEST the integer statement directly over ALL subsets E0 (small graphs) -> this is the real lemma.
"""
import numpy as np
import heapq
from itertools import combinations
import flag_engine as fe
import verify_D25_lemma16 as L
from exp_lemma16_atoms import is_2connected, tau_of, is_edge_critical


def wdist_B_int(N, adjBw, s):
    dist = [float('inf')]*N; dist[s] = 0.0; pq = [(0.0, s)]
    while pq:
        d0, x = heapq.heappop(pq)
        if d0 > dist[x]+1e-12:
            continue
        for (y, wt) in adjBw[x]:
            if dist[x]+wt < dist[y]-1e-12:
                dist[y] = dist[x]+wt; heapq.heappush(pq, (dist[y], y))
    return dist


def int_cost(N, E0set, edges, sigs):
    """min over signatures of |S cap E0| + sum_e d^{B,E0}(e), where B-edges cost 1 if in E0 else 0."""
    best = float('inf')
    for S in sigs:
        Bset = set(edges)-set(S)
        adjBw = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b)
            wt = 1.0 if b in E0set else 0.0
            adjBw[a].append((c, wt)); adjBw[c].append((a, wt))
        cost = sum(1 for e in S if e in E0set); ok = True
        for e in S:
            u, v = tuple(e); dist = wdist_B_int(N, adjBw, u)
            if dist[v] == float('inf'):
                ok = False; break
            cost += dist[v]
        if ok:
            best = min(best, cost)
    return best


def test_atom(n, A):
    adj = L.adjset(n, A)
    edges = [frozenset((u, v)) for u in range(n) for v in adj[u] if v > u]
    mc, side = L.maxcut(n, adj); tau = len(edges)-mc
    sigs = L.min_signatures(n, adj, edges, tau)
    worst_ratio = 0.0; worst_E0 = None
    m = len(edges)
    # iterate over all nonempty subsets if small, else sample
    if m <= 18:
        subsets = (frozenset(c) for k in range(1, m+1) for c in combinations(edges, k))
        for E0 in subsets:
            ic = int_cost(n, E0, edges, sigs)
            bound = n*n*len(E0)/(25.0*tau)
            r = ic/bound if bound > 0 else 0
            if r > worst_ratio:
                worst_ratio = r; worst_E0 = E0
    return tau, worst_ratio, (len(worst_E0) if worst_E0 else 0), m


def main():
    overall = 0.0; viol = 0; natoms = 0
    for N in [5, 6, 7, 8]:
        for (n, A) in fe.enumerate_graphs(N, triangle_free=True):
            adj = L.adjset(n, A)
            if not is_2connected(n, adj):
                continue
            tau = tau_of(n, adj)
            if tau == 0:
                continue
            if not is_edge_critical(n, A, adj, tau):
                continue
            t, wr, e0sz, m = test_atom(n, A)
            natoms += 1
            if wr > 1.0+1e-7:
                viol += 1
                print(f"  VIOLATION n={n} tau={t} worst-ratio={wr:.4f} E0size={e0sz}/{m}")
            overall = max(overall, wr)
            print(f"  n={n} tau={t} m={m} worst integer-cost/bound ratio={wr:.4f} (E0 size {e0sz})", flush=True)
    print(f">>> {natoms} atoms; integer-lemma VIOLATIONS over ALL subsets E0 = {viol}; worst ratio={overall:.4f}")


if __name__ == "__main__":
    main()
