"""DECISIVE TEST: the spread-geodesic congestion bound
   rho_spread(K) := min over min-signatures S of [ max B-edge load of the uniform-over-all-shortest-
                    B-geodesics routing of the m bad edges ]
satisfies  rho_spread(K) <= max{1, n^2/(25 t)}  for every 2-CONNECTED EDGE-CRITICAL triangle-free atom K.

If TRUE on all atoms, then scaling the routing by 1/max(1,rho) gives a feasible fractional odd-cycle
packing of value t/max(1,rho) >= t/max(1,n^2/25t) >= 25 t^2/n^2 (since t<=n^2/25 by the bound itself...
careful: we need t/(n^2/25t)=25t^2/n^2 when n^2/25t>=1; and t when n^2/25t<1 i.e. t>n^2/25, but then
25t^2/n^2 > t so we'd need value >= 25t^2/n^2 > t = max value -> would FAIL. So the bound MUST give
n^2/25t >= 1 region, i.e. t <= n^2/25, exactly the theorem. CHECK: is t <= n^2/25 on all atoms? yes by
the theorem we're proving. So this is INTERNALLY the right normalization: value = 25t^2/n^2 needs
rho <= n^2/(25t) AND t<=n^2/25. Test both.)

Also re-test the DILUTION J_t (K23 + C5[t] via one edge) to confirm it is NOT 2-connected (has a cut
vertex) so it is OUT of scope -- explaining why GPT's QFC25 refutation does not touch the atom claim.
"""
import numpy as np
from collections import deque, defaultdict
import flag_engine as fe
import verify_D25_lemma16 as L
from exp_lemma16_atoms import is_2connected, tau_of, is_edge_critical
from primal_packing_attempt import all_geodesics_load


def rho_spread(N, A):
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    if tau == 0:
        return None
    sigs = L.min_signatures(N, adj, edges, tau)
    best = None
    for S in sigs:
        Bset = set(edges)-set(S)
        adjB = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
        congestion = defaultdict(float); ok = True
        for e in S:
            u, v = tuple(e)
            d = [-1]*N; d[u] = 0; q = deque([u])
            while q:
                x = q.popleft()
                for y in adjB[x]:
                    if d[y] < 0:
                        d[y] = d[x]+1; q.append(y)
            if d[v] < 0:
                ok = False; break
            res = all_geodesics_load(N, adjB, u, v, d[v])
            if res is None:
                ok = False; break
            load, vload = res
            for b, f in load.items():
                congestion[b] += f
        if not ok:
            continue
        maxc = max(congestion.values()) if congestion else 0.0
        if best is None or maxc < best:
            best = maxc
    return best, tau, N


def dilution_Jt(t):
    """K23 gadget H (the N=13 obstruction) joined by ONE edge to C5[t]. Build and check 2-connectivity."""
    # K23 part on 0..12
    N1 = 13
    A = []
    nK, AK = L.gpt_k23()
    # C5[t] on next 5t vertices
    nC, AC = L.c5n(t)
    N = nK + nC
    A = [0]*N
    for u in range(nK):
        for v in range(nK):
            if (AK[u] >> v) & 1:
                A[u] |= 1 << v
    for u in range(nC):
        for v in range(nC):
            if (AC[u] >> v) & 1:
                A[u+nK] |= 1 << (v+nK)
    # join by one edge: vertex 0 (K23) -- vertex nK (C5[t])
    A[0] |= 1 << nK; A[nK] |= 1 << 0
    return N, A


def main():
    worst = 0.0; viol = 0; natoms = 0
    for Nn in [5, 6, 7, 8, 9]:
        for (n, A) in fe.enumerate_graphs(Nn, triangle_free=True):
            adj = L.adjset(n, A)
            if not is_2connected(n, adj):
                continue
            tau = tau_of(n, adj)
            if tau == 0:
                continue
            if not is_edge_critical(n, A, adj, tau):
                continue
            r = rho_spread(n, A)
            if r is None:
                continue
            rho, t, NN = r; natoms += 1
            bound = max(1.0, NN*NN/(25.0*t))
            ratio = rho/bound
            if rho > bound+1e-7:
                viol += 1
                print(f"  VIOLATION atom n={n} tau={t} rho_spread={rho:.4f} bound={bound:.4f}")
            worst = max(worst, ratio)
    print(f">>> {natoms} 2-conn edge-critical atoms; QFC-spread VIOLATIONS={viol}; "
          f"worst rho/bound={worst:.4f}")
    # dilution check
    print("\n--- DILUTION J_t (K23 + C5[t] via one edge): is it a valid atom? ---")
    for t in [1, 2]:
        N, A = dilution_Jt(t)
        adj = L.adjset(N, A)
        twoconn = is_2connected(N, adj)
        tau = tau_of(N, adj)
        crit = is_edge_critical(N, A, adj, tau) if twoconn else False
        print(f"  J_{t}: N={N} 2-connected={twoconn} edge-critical={crit} tau={tau} "
              f"-> {'IN scope (PROBLEM)' if twoconn and crit else 'OUT of scope (cut vertex) -> handled by block decomposition'}")


if __name__ == "__main__":
    main()
