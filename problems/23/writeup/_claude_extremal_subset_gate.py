r"""EXTREMAL-SUBSET (exchange-lemma) gate (2026-07-08). Validates the audit workflow's recommended attack on the OPEN
residual L* = max_S [ sum_{e in S} ell(e)^2 / |E(S)| ] <= 25 (E(S) = all-shortest-geodesic cut-edge union).

Workflow's exchange lemma: the density-maximizing subset S* is a union of SHORT (ell=5-dominated) atoms; a long/high-
charge atom can be swapped out without decreasing density. Since single long atoms are separately Lean-proven
(ell^2 <= 25(ell-1) <= 25(single-atom L*)), the content is about MULTI-atom (|S|>=2) subsets. This gate enumerates
ALL subsets S of each K2-component and reports:
  * the GLOBAL argmax density and its ell-composition (should be a single long atom OR short-atom multi);
  * the MULTI-atom (|S|>=2) argmax density and its ell-composition (workflow claim: ell=5-dominated);
  * whether any MULTI-atom subset containing a LONG atom (ell>=7) beats the best all-short multi-subset (would REFUTE
    the exchange lemma) and whether any multi-atom density exceeds 12 / approaches 25.
Focus on MIXED-length components (a long atom co-resident with short atoms). EXACT rational density. Run from writeup.
"""
import subprocess
from fractions import Fraction as F
from itertools import combinations
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges
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
        atoms = X['atoms']
        if len(atoms) < 2:
            continue
        # precompute P_e
        Pe = {}
        ok = True
        for e in atoms:
            p = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
            if not p:
                ok = False; break
            Pe[e] = p
        if not ok:
            continue
        lens = sorted(ell[e] for e in atoms)
        mixed = lens[0] != lens[-1] or lens[-1] >= 7
        best_all = (F(0), None)      # global argmax over |S|>=1
        best_multi = (F(0), None)    # argmax over |S|>=2
        best_multi_short = (F(0), None)  # argmax over |S|>=2 all ell=5
        best_multi_long = (F(0), None)   # argmax over |S|>=2 containing an ell>=7 atom
        idx = list(range(len(atoms)))
        for r in range(1, len(atoms) + 1):
            for combo in combinations(idx, r):
                S = [atoms[i] for i in combo]
                ES = set()
                for e in S:
                    ES |= Pe[e]
                dens = F(sum(ell[e] ** 2 for e in S), len(ES))
                comp = sorted(ell[e] for e in S)
                if dens > best_all[0]:
                    best_all = (dens, comp)
                if r >= 2:
                    if dens > best_multi[0]:
                        best_multi = (dens, comp)
                    if all(ell[e] == 5 for e in S) and dens > best_multi_short[0]:
                        best_multi_short = (dens, comp)
                    if any(ell[e] >= 7 for e in S) and dens > best_multi_long[0]:
                        best_multi_long = (dens, comp)
        acc['comps'] += 1
        if mixed:
            acc['mixed'] += 1
        # exchange-lemma check: does a long-containing multi-subset beat the best all-short multi-subset?
        if best_multi_long[1] is not None and best_multi_long[0] > best_multi_short[0]:
            acc['long_beats_short'] += 1
            if acc['lb_ex'] is None:
                acc['lb_ex'] = (name, n, best_multi_long, best_multi_short)
        if best_multi[0] > acc['max_multi'][0]:
            acc['max_multi'] = (best_multi[0], name, n, best_multi[1])
        # is the global extremal a single atom or short-multi?
        if best_all[1] is not None and len(best_all[1]) >= 2 and any(x >= 7 for x in best_all[1]):
            acc['global_is_long_multi'] += 1
            if acc['glm_ex'] is None:
                acc['glm_ex'] = (name, n, best_all)


def main():
    print("EXTREMAL-SUBSET gate: is the density-max MULTI-atom S* short-atom (ell=5) dominated? (validates exchange lemma)")
    print("=" * 100)
    acc = dict(comps=0, mixed=0, long_beats_short=0, global_is_long_multi=0,
               max_multi=(F(0), '', 0, None), lb_ex=None, glm_ex=None)
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            analyze('cen%d' % nn, n, adj, b[0], acc)
        mm = acc['max_multi']
        print("  census N=%d: multi-atom comps %d (mixed-len %d) | long-multi beats short-multi: %d | max multi-density=%s @ %s N=%d ells=%s"
              % (nn, acc['comps'], acc['mixed'], acc['long_beats_short'], mm[0], mm[1], mm[2], mm[3]), flush=True)
    print("=" * 100)
    mm = acc['max_multi']
    print("TOTAL multi-atom comps %d (mixed-length %d)" % (acc['comps'], acc['mixed']))
    print("MAX multi-atom density (|S|>=2) = %s ~ %.4f @ %s N=%d ells=%s  (<=25? %s)"
          % (mm[0], float(mm[0]), mm[1], mm[2], mm[3], mm[0] <= 25))
    print("multi-atom subsets where a LONG-containing S beats the best all-short S: %d" % acc['long_beats_short'])
    if acc['lb_ex']:
        print("  long-beats-short example: %s" % (acc['lb_ex'],))
    print("global extremal is a multi-atom subset containing a long atom: %d" % acc['global_is_long_multi'])
    if acc['glm_ex']:
        print("  example: %s" % (acc['glm_ex'],))
    print("VERDICT: %s" % (
        "multi-atom density-max is short-atom (ell=5) dominated on ALL comps (0 long-containing multi-subset beats the "
        "best all-short multi-subset; 0 global extremal is a long-multi) => EXCHANGE LEMMA SUPPORTED: the extremal S* is "
        "either a single long atom (Lean-proven) or an ell=5 short-multi subset (<=%.2f). The workflow's attack direction "
        "is validated on census." % float(mm[0])
        if acc['long_beats_short'] == 0 and acc['global_is_long_multi'] == 0 else
        "*** exchange lemma CHALLENGED: %d comps where a long-containing multi-subset beats the best all-short subset, or "
        "%d where the global extremal is a long-multi -- the 'short-atom-dominated' claim needs refinement. ***"
        % (acc['long_beats_short'], acc['global_is_long_multi'])))


if __name__ == '__main__':
    main()
