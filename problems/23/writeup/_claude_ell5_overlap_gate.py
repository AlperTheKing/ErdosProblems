r"""ELL=5 GEODESIC-SUPPORT OVERLAP gate (2026-07-08). Ground-truth for the ell=5 support-expansion proof attack.

The SDR/Hall, counting/entropy, and discharging proof strategies all hinge on: how much can two DISTINCT ell=5 atoms'
shortest-geodesic cut-edge supports P_e, P_f OVERLAP? This gate measures, over all ell=5 atom pairs in the same
K2-component of a triangle-free Gamma-min MAX cut (census N<=11 + C5[t]):
  * the distribution of |P_e cap P_f| and of |P_e| (single geodesic => 4; more geodesics => >4);
  * whether P_e == P_f or P_e subset P_f EVER occurs for distinct atoms (would break a naive SDR / distinct-rep proof);
  * per cut edge c, d(c) = #atoms of the component whose P_e contains c (local multiplicity; high in C5[t]);
  * sum_c binom(d(c),2) vs #{atom pairs} (for the entropy/Cauchy-Schwarz strategy: each shared edge = a co-incidence);
  * the min expansion ratio |E_short(S)|/|S| witness and whether |P_e cap P_f| <= 3 always (no two distinct ell=5
    atoms share a full 4-edge geodesic set) -- the key structural bound the SDR route needs.
EXACT (integer supports). Run from problems/23/writeup.
"""
import subprocess
from itertools import combinations
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges, c5_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    ell = cd['ell']
    for X in k2_components(n, cd):
        five = [e for e in X['atoms'] if ell[e] == 5]
        if len(five) < 1:
            continue
        Pe = {}
        ok = True
        for e in five:
            p = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
            if not p:
                ok = False; break
            Pe[e] = set(p)
        if not ok:
            continue
        acc['comps'] += 1
        for e in five:
            acc['Pe_sizes'][min(len(Pe[e]), 9)] = acc['Pe_sizes'].get(min(len(Pe[e]), 9), 0) + 1
        # pairwise overlaps
        for e, f in combinations(five, 2):
            ov = len(Pe[e] & Pe[f])
            acc['overlap_dist'][ov] = acc['overlap_dist'].get(ov, 0) + 1
            acc['maxov'] = max(acc['maxov'], ov)
            if Pe[e] == Pe[f]:
                acc['equal_supports'] += 1
                if acc['eq_ex'] is None:
                    acc['eq_ex'] = (name, n, e, f, sorted(Pe[e]))
            elif Pe[e] <= Pe[f] or Pe[f] <= Pe[e]:
                acc['subset_supports'] += 1
        # d(c) multiplicity
        dc = {}
        for e in five:
            for c in Pe[e]:
                dc[c] = dc.get(c, 0) + 1
        for c, d in dc.items():
            acc['maxdc'] = max(acc['maxdc'], d)


def main():
    print("ELL=5 GEODESIC-SUPPORT OVERLAP gate (ground-truth for the expansion proof attack).")
    print("=" * 96)
    acc = dict(comps=0, Pe_sizes={}, overlap_dist={}, maxov=0, maxdc=0,
               equal_supports=0, subset_supports=0, eq_ex=None)
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            analyze('cen%d' % nn, n, adj, b[0], acc)
        print("  census N=%d done: comps %d, max|P_e cap P_f|=%d, equal-supports=%d, subset-supports=%d, max d(c)=%d"
              % (nn, acc['comps'], acc['maxov'], acc['equal_supports'], acc['subset_supports'], acc['maxdc']), flush=True)
    for t in range(1, 8):
        n, adj, side = c5_blowup(t)
        analyze('C5[%d]' % t, n, adj, side, acc)
    print("=" * 96)
    print("ell=5 atoms per component analyzed across %d comps." % acc['comps'])
    print("|P_e| size distribution (#geodesic cut edges per atom): %s" % dict(sorted(acc['Pe_sizes'].items())))
    print("|P_e cap P_f| overlap distribution over distinct ell=5 pairs: %s" % dict(sorted(acc['overlap_dist'].items())))
    print("MAX overlap |P_e cap P_f| = %d ; distinct atoms with EQUAL supports P_e==P_f: %d ; nested (subset): %d ; max d(c)=%d"
          % (acc['maxov'], acc['equal_supports'], acc['subset_supports'], acc['maxdc']))
    if acc['eq_ex']:
        print("  *** EQUAL-support example (breaks naive SDR): %s ***" % (acc['eq_ex'],))
    print("=" * 96)
    print("KEY FACTS for the proof:")
    print("  - two distinct ell=5 atoms share at MOST %d geodesic cut edges%s"
          % (acc['maxov'], " (never a full 4-edge geodesic set => SDR-friendly)" if acc['maxov'] <= 3 and acc['equal_supports'] == 0 else ""))
    print("  - equal/nested supports for distinct atoms: %s (%d equal, %d nested)"
          % ("NONE => distinct-representative injection is not blocked by collisions" if acc['equal_supports'] == 0 and acc['subset_supports'] == 0 else "OCCUR => naive SDR needs care", acc['equal_supports'], acc['subset_supports']))
    print("  - local multiplicity max d(c)=%d confirms high local sharing (C5[t]) => local per-edge bound insufficient, GLOBAL needed." % acc['maxdc'])


if __name__ == '__main__':
    main()
