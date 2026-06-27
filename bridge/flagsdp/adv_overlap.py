"""CRUX TEST: the strategy relies on E(w) and I(w) not both being large on the same
vertex. Measure, census-wide over ALL max cuts, the worst single vertex where BOTH
E(w)>0 and I(w)>0, and the ratio (E(w)+I(w))/K there. If some non-extremal graph has
a vertex carrying substantial endpoint AND interior load, that is the over-concentration
the strategy fears. Also report the max of (E+I) overlap product."""
import numpy as np
from flag_engine import enumerate_graphs
from mycielskian_check import all_shortest_geos, Bconnected, edges_of, maxcut_value, gamma_of

def adjset(n, A):
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if (A[i] >> j) & 1:
                adj[i].add(j)
    return adj

def split(N, adj, side, M):
    E = np.zeros(N); I = np.zeros(N)
    for (u, v) in M:
        geos = all_shortest_geos(N, adj, side, u, v); g = len(geos); h = len(geos[0])
        cnt = np.zeros(N)
        for P in geos:
            for x in P:
                cnt[x] += 1
        for x in range(N):
            if cnt[x] == 0:
                continue
            frac = cnt[x] / g
            if x == u or x == v:
                E[x] += h * frac
            else:
                I[x] += h * frac
    return E, I

worst_both = -1.0; wb_case = None      # max over vertices with E>0 AND I>0 of (E+I)/K
worst_min = -1.0; wm_case = None       # max of min(E,I)/K  (true overlap strength)
worst_sumratio = -1.0; ws_case = None  # max (E+I).max / K
cnt = 0
for N in range(5, 11):
    for (n, A) in enumerate_graphs(N, triangle_free=True):
        adj = adjset(n, A); Ee = edges_of(adj); mc = maxcut_value(n, Ee)
        for mask in range(1 << (n - 1)):
            c = sum(1 for (u, v) in Ee if ((mask >> u) & 1) != ((mask >> v) & 1))
            if c != mc:
                continue
            side = [(mask >> u) & 1 for u in range(n)]
            if not Bconnected(n, adj, side):
                continue
            G, M = gamma_of(n, adj, side)
            if G is None or not M:
                continue
            E, I = split(n, adj, side, M); K = n + (n * n - G); cnt += 1
            T = E + I
            if T.max() / K > worst_sumratio:
                worst_sumratio = T.max() / K; ws_case = (n, G, K, T.max())
            both = np.where((E > 1e-9) & (I > 1e-9))[0]
            for w in both:
                if T[w] / K > worst_both:
                    worst_both = T[w] / K; wb_case = (n, G, K, E[w], I[w])
                mn = min(E[w], I[w])
                if mn / K > worst_min:
                    worst_min = mn / K; wm_case = (n, G, K, E[w], I[w])
print("checked %d (graph,maxcut) pairs" % cnt)
print("worst (E+I).max/K = %.4f at %s" % (worst_sumratio, ws_case))
print("among vertices with BOTH E>0 and I>0:")
print("  worst (E+I)/K = %.4f at (n,G,K,E,I)=%s" % (worst_both, wb_case))
print("  worst min(E,I)/K = %.4f at (n,G,K,E,I)=%s" % (worst_min, wm_case))
