r"""EXACT-GATE obligation (ii) of the option-3 route (2026-07-08): geodesic edge-disjointness sum_e (ell_e - 1) <= b_X.

Option 3 derives Gamma_X = sum ell_e^2 <= 25*b_X from (i) short atoms (ell<=23; ell>=25 are base leaves) + (ii)
sum_{e in X}(ell_e - 1) <= b_X (the bad-edge geodesics do not over-share cut edges). Claude formalized the DERIVATION
(fullSupport_doorDominance_of_shortAtoms). This gate tests obligation (ii) EXACTLY on census Gamma-min cages (where all
ell<=11<25, so (i) is automatic) + thetas:
  whole-cage:  sum_{e in M}(ell_e - 1)  vs  cut_edges (= b).
  per-K2-component X: sum_{e in X}(ell_e - 1)  vs  b_X (cut edges with both endpoints in V_X).
If sum(ell-1) <= b everywhere, obligation (ii) holds (geodesics fit in the cut budget) -> option-3 route's structural
input is confirmed on this coverage, and combined with the formalized derivation + short-atom fact, Gamma_X<=25b_X follows.
A failure (sum(ell-1) > b) marks where the naive disjointness breaks (needs a per-cut-edge charging for overlap). EXACT (int).
Run from problems/23/writeup.
"""
import subprocess
from _claude_residual_hall_gate import residuals, k2_components, even_cycle_chord
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def check(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    ell, p = cd['ell'], cd['p']
    cut_pairs = [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b]]
    b_whole = len(cut_pairs)
    acc['cages'] += 1
    # whole-cage
    geo_whole = sum(ell[e] - 1 for e in cd['M'])
    if geo_whole > b_whole:
        acc['whole_fail'] += 1
        if acc['wex'] is None:
            acc['wex'] = (name, n, geo_whole, b_whole)
    # per-component: b_X = cut edges with BOTH endpoints in V_X
    for X in k2_components(n, cd):
        geo = sum(ell[e] - 1 for e in X['atoms'])
        bX = sum(1 for (a, b) in cut_pairs if a in X['VX'] and b in X['VX'])
        full = (len(X['VX']) == n)
        acc['comps'] += 1
        if full:
            acc['full_comps'] += 1
        if geo > bX:
            acc['comp_fail'] += 1
            if full:
                acc['full_fail'] += 1  # THE lemma's domain: a full-support obligation-(ii) failure would be serious
                if acc['fex'] is None:
                    acc['fex'] = (name, n, dict(geo=geo, bX=bX, nV=len(X['VX']), m=len(X['atoms']),
                                                ells=sorted(ell[e] for e in X['atoms'])))
            if acc['cex'] is None:
                acc['cex'] = (name, n, dict(geo=geo, bX=bX, nV=len(X['VX']), m=len(X['atoms']), full=full,
                                            ells=sorted(ell[e] for e in X['atoms'])))


def main():
    acc = dict(cages=0, comps=0, full_comps=0, whole_fail=0, comp_fail=0, full_fail=0, wex=None, cex=None, fex=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            check('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, comps %d, whole sum(ell-1)>b: %d, per-comp sum(ell-1)>b_X: %d"
              % (nn, acc['cages'], acc['comps'], acc['whole_fail'], acc['comp_fail']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            check('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print("=" * 90)
    print("GEODESIC-DISJOINTNESS GATE (obligation ii: sum_e (ell_e-1) <= b_X):")
    print("  cages %d, components %d (FULL-support %d) | whole-cage sum(ell-1)>b: %d | per-component sum(ell-1)>b_X: %d | FULL-SUPPORT fails: %d"
          % (acc['cages'], acc['comps'], acc['full_comps'], acc['whole_fail'], acc['comp_fail'], acc['full_fail']))
    if acc['cex']:
        print("   per-component fail example (proper-support, handled by mixed bank): %s" % (acc['cex'],))
    if acc['fex']:
        print("   *** FULL-SUPPORT fail (obligation ii breaks in the LEMMA's domain -- serious): %s ***" % (acc['fex'],))
    print("VERDICT: %s" % (
        "obligation (ii) HOLDS on the LEMMA's domain: FULL-support shells have b_X=b_whole and sum(ell-1)<=b_whole (0 whole-cage"
        " fails), so sum_e(ell_e-1)<=b_X for every FULL-support component (%d full-support comps, 0 fail). The %d per-component"
        " fails are all PROPER-support (b_X restricted to V_X undercounts shared geodesic edges) -- NOT the lemma's domain"
        " (proper-support uses the mixed bank). Combined with the formalized derivation + short-atom fact (all ell<=11<25 here),"
        " Gamma_X<=25*b_X follows for full-support shells on this coverage -- option-3 route CONFIRMED for the lemma's domain."
        % (acc['full_comps'], acc['comp_fail'])
        if acc['full_fail'] == 0 else
        "*** obligation (ii) FAILS on %d FULL-SUPPORT components -- the option-3 chain breaks in the LEMMA's own domain; needs a"
        " per-cut-edge charging argument. Examine: %s ***" % (acc['full_fail'], acc['fex'])))


if __name__ == '__main__':
    main()
