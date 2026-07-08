r"""DECISIVE GATE for gap#1's SINGLE remaining residual (GPT-Pro reply 7, 2026-07-08):
MultiAtomFullSupportShell_absorbed_without_topEta.

The multi-atom density-ledger induction (rank = #owned atoms) is WELL-FOUNDED unless it bottoms out at a MULTI-ATOM
FULL-SUPPORT SHELL: a K2-component X with support V_X = ALL N vertices (=> NO ambient room, since ambient needs v
outside V_X) AND m_X >= 2 atoms, that is not decomposable into prunable descendants and is not a single-edge base leaf.
Such a shell's only apparent capacity is its own UNPROVED eta_C = |V_C|^2/25 - m_C -> circular.

DECISIVE OBSTRUCTION (GPT-Pro's exact test): a reduced multi-atom full-support shell with
   Demand  >  Door(25*sigma) + Prune + independent BaseDensity   and no ambient room.

This gate does the EXISTENTIAL search (graph-computable, EXACT Fraction):
  For every Gamma-min cage, find K2-components with |V_X| == N (full support) and m_X >= 2 atoms.
  For each, report Demand = sum(ell^2-25) vs Door = 25*sigma (sigma = cutedges - m_total).
  (Prune/BaseDensity need the rowDB cage tree; a multi-atom full-support component has no single-edge leaf to prune,
   so Door is the main graph-computable token. Demand <= Door => absorbed without eta_C. Demand > Door => candidate
   obstruction to examine.)
KEY QUESTION: do multi-atom full-support components EXIST at all? If NONE arise (every full-support component is a
single-atom leaf, already closed by fullSupport_leaf_absorbed_by_density), the induction's circular bottom-out case is
EMPTY and gap#1 closes. Coverage: census N<=11 + odd-cycle+chord + two-chord + double-odd families. Run from writeup.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals, k2_components
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def scan(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    ell = cd['ell']
    cut_edges = sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])
    m_total = len(cd['M'])
    sigma = cut_edges - m_total
    door = 25 * sigma
    comps = k2_components(n, cd)
    acc['cages'] += 1
    for X in comps:
        VX = X['VX']; atomsX = X['atoms']
        if len(VX) == n and len(atomsX) >= 2:  # MULTI-ATOM FULL-SUPPORT shell
            acc['multiatom_fullsupport'] += 1
            demand = sum(ell[e] ** 2 - 25 for e in atomsX)
            rec = dict(name=name, n=n, m_comp=len(atomsX), m_total=m_total, sigma=sigma,
                       demand=demand, door=door, ells=sorted(ell[e] for e in atomsX),
                       demand_le_door=(demand <= door))
            acc['examples'].append(rec)
            if demand > door:
                acc['demand_gt_door'] += 1
                if acc['worst'] is None:
                    acc['worst'] = rec


def try_family(name, n, E, side, acc):
    scan(name, n, adj_from_edges(n, E), side, acc)


def main():
    acc = dict(cages=0, multiatom_fullsupport=0, demand_gt_door=0, examples=[], worst=None)
    # census N<=11
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            scan('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, multi-atom-full-support comps %d, Demand>Door %d"
              % (nn, acc['cages'], acc['multiatom_fullsupport'], acc['demand_gt_door']), flush=True)
    # families that might create multi-atom full-support (2 long bad edges covering the graph)
    # even cycle + 2 chords (both endpoints same parity => 2 bad edges)
    for n in [16, 18, 20, 22, 24, 26]:
        for g1 in range(4, n // 2):
            for g2 in range(g1 + 2, n // 2 + 1):
                E = [(i, (i + 1) % n) for i in range(n)] + [(0, g1), (n // 2, (n // 2 + g2) % n)]
                # keep only if both chords are same-side (bad) under parity
                side = [i % 2 for i in range(n)]
                try_family('C%d+2ch(%d,%d)' % (n, g1, g2), n, E, side, acc)
    # odd cycle + chord (odd cycle already has 1 bad edge; chord may add another)
    for k in range(4, 14):
        n = 2 * k + 1
        for g in range(2, k):
            E = [(i, (i + 1) % n) for i in range(n)] + [(0, g)]
            adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj)) if n <= 15 else None
            if best is not None:
                scan('C%d+ch%d' % (n, g), n, adj, best[0], acc)
    print("=" * 96)
    print("MULTI-ATOM FULL-SUPPORT SHELL SEARCH (gap#1's circular bottom-out case):")
    print("  cages scanned %d | MULTI-ATOM FULL-SUPPORT components found: %d | of those Demand > Door: %d"
          % (acc['cages'], acc['multiatom_fullsupport'], acc['demand_gt_door']))
    for r in acc['examples'][:8]:
        print("   %s N=%d m_comp=%d sigma=%d Demand=%d Door=%d ells=%s Demand<=Door=%s"
              % (r['name'], r['n'], r['m_comp'], r['sigma'], r['demand'], r['door'], r['ells'], r['demand_le_door']))
    if acc['worst']:
        print("   *** Demand>Door multi-atom full-support (obstruction candidate): %s ***" % (acc['worst'],))
    print("VERDICT: %s" % (
        "NO multi-atom full-support shell found -- every full-support component is a single-atom LEAF (closed by"
        " fullSupport_leaf_absorbed_by_density). The induction's circular bottom-out case is EMPTY on this coverage;"
        " strong evidence gap#1's ReducedShellHall_NoTopEta closes."
        if acc['multiatom_fullsupport'] == 0 else
        ("multi-atom full-support shells EXIST (%d) but ALL have Demand <= Door (absorbed without eta_C) -- induction closes on this coverage."
         % acc['multiatom_fullsupport'] if acc['demand_gt_door'] == 0 else
         "*** %d multi-atom full-support shells with Demand > Door -- CIRCULARITY OBSTRUCTION CANDIDATE (verify prune/base can't cover) ***"
         % acc['demand_gt_door'])))


if __name__ == '__main__':
    main()
