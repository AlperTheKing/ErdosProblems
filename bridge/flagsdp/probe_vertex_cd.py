#!/usr/bin/env python3
"""Probe the |S|=1 GPI:  for each vertex w,  V1(w) := Sum_{e: w on EVERY shortest geo of e} h_e  <= K = N+(N^2-Gamma).
Question: is V1(w) bounded by a CUT quantity? Test candidate bounds:
  (a) V1(w) <= N always (tight at C5[q] hub vertex)?
  (b) relation to deg_M(w), deg_B(w), and the bad edges incident to w.
A bad edge e=(u,v) is FORCED through w only if w in {u,v} (endpoint) OR w is a cut vertex of all u-v B-geodesics.
Report max_w V1(w) vs N and vs K across census; flag any w with V1(w)>N (would refute (a))."""
from mycielskian_check import all_shortest_geos, edges_of, gamma_min_cut
from flag_engine import enumerate_graphs


def V1_all(N, adj, side, M):
    geos = []; he = []
    for (u, v) in M:
        gs = all_shortest_geos(N, adj, side, u, v); geos.append(gs); he.append(len(gs[0]))
    forced = [set.intersection(*[set(P) for P in gs]) if gs else set() for gs in geos]
    V1 = [0] * N
    for e in range(len(M)):
        for w in forced[e]:
            V1[w] += he[e]
    return V1, he, forced


maxoverN = 0.0; worst = None
for N in range(5, 10):
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = [set(v for v in range(n) if (A[u] >> v) & 1) for u in range(n)]
        res, mc = gamma_min_cut(n, adj, edges_of(adj))
        if not res:
            continue
        side, G, M = res
        if not M:
            continue
        V1, he, forced = V1_all(n, adj, side, M)
        K = n + n * n - G
        mw = max(V1)
        if mw / n > maxoverN:
            maxoverN = mw / n
            worst = (n, len(M), G, mw, K, [i for i in range(n) if V1[i] == mw])
        # flag V1>N
        if mw > n + 1e-9:
            print("  V1>N witness: N=%d beta=%d Gam=%d maxV1=%d  N=%d  (vertices %s)" % (
                n, len(M), G, mw, n, [i for i in range(n) if V1[i] == mw]))
print("max_w V1(w)/N over census N<=9 = %.4f" % maxoverN)
if worst:
    print("  attained at: N=%d beta=%d Gam=%d V1=%d N=%d K=%d vertices=%s" % (worst[0], worst[1], worst[2], worst[3], worst[0], worst[4], worst[5]))
