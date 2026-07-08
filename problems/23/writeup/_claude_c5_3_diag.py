r"""Focused C5[3] diagnostic (2026-07-08): resolve the workflow-vs-gate discrepancy on the ShortRowCutEdgeHall
counterexample. Compute the TRUE Gamma-min max cut of C5[3] and report, EXACTLY: bad edges, ell, canonical P_e,
all-shortest-geodesic P_e, |union| for each, the sum-form (sum ell^2 vs 25*|union|), and max-flow feasibility for both
incidences. Cross-check the workflow claim (225 > 200 canonical sum-form fail; all-geodesics feasible 225=225).
"""
from fractions import Fraction as F
from _claude_residual_hall_gate import residuals
from _claude_shortrow_hall_v2_gate import (all_shortest_geodesic_cut_edges, canonical_geodesic_cut_edges,
                                           hall_feasible, c5_blowup)
from _codex_k2t_switch_probe import adj_from_edges
from _h import maxcut_all, gmin, Bconn


def main():
    n, adj, side_bl = c5_blowup(3)
    print("C5[3]: N=%d, edges=%d" % (n, sum(len(adj[v]) for v in range(n)) // 2))
    # TRUE max cut + Gamma-min
    mc = maxcut_all(n, adj)
    print("  # maximum cuts: %d" % len(mc))
    best = gmin(n, adj, mc)
    side = best[0] if best else side_bl
    print("  using Gamma-min B-conn max cut; my c5_blowup side is max-cut: %s"
          % (sum(1 for a in range(n) for b in adj[a] if a < b and side_bl[a] != side_bl[b])
             == max(sum(1 for a in range(n) for b in adj[a] if a < b and s[a] != s[b]) for s in mc)))
    cd = residuals(n, adj, side)
    M, ell = cd['M'], cd['ell']
    print("  bad edges m=%d, ells=%s, Gamma=sum ell^2=%d, cutedges=%d"
          % (len(M), sorted(ell.values()),
             sum(v ** 2 for v in ell.values()),
             sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])))
    # canonical
    canon = {}; allg = {}
    for e in M:
        canon[e] = canonical_geodesic_cut_edges(adj, side, e[0], e[1], n) or set()
        allg[e] = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1]) or set()
    u_canon = set().union(*canon.values()) if canon else set()
    u_all = set().union(*allg.values()) if allg else set()
    demand = sum(ell[e] ** 2 for e in M)
    print("  |P_e| canonical: %s (each ell-1=%s)" % ([len(canon[e]) for e in M], [ell[e] - 1 for e in M]))
    print("  |union canonical P_e| = %d -> sum-form 25*|union| = %d vs demand %d -> canonical sum-form %s"
          % (len(u_canon), 25 * len(u_canon), demand, "FAILS" if demand > 25 * len(u_canon) else "holds"))
    print("  |union ALL-geodesic P_e| = %d -> sum-form 25*|union| = %d vs demand %d -> all-geodesic sum-form %s"
          % (len(u_all), 25 * len(u_all), demand, "FAILS" if demand > 25 * len(u_all) else "holds"))
    fc = hall_feasible(n, adj, side, cd, 'canonical')
    fa = hall_feasible(n, adj, side, cd, 'all')
    print("  MAX-FLOW canonical feasible=%s (demand=%s cap=%s)" % fc)
    print("  MAX-FLOW all-geodesics feasible=%s (demand=%s cap=%s)" % fa)
    print("VERDICT: workflow claim (canonical fails, all-geodesics feasible, tight 225) is %s"
          % ("CONFIRMED" if (demand > 25 * len(u_canon) and demand <= 25 * len(u_all)) else "NOT matching my exact computation -- investigate"))


if __name__ == '__main__':
    main()
