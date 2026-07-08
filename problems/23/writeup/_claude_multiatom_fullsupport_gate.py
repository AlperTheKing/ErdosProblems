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
            if demand > 0:  # the DANGEROUS regime: a long atom present (some ell>=7)
                acc['demand_pos'] += 1
                acc['examples_pos'].append(rec)
            if demand > door:
                acc['demand_gt_door'] += 1
                if acc['worst'] is None:
                    acc['worst'] = rec


def try_family(name, n, E, side, acc):
    scan(name, n, adj_from_edges(n, E), side, acc)


def main():
    acc = dict(cages=0, multiatom_fullsupport=0, demand_pos=0, demand_gt_door=0,
               examples_pos=[], worst=None)
    # census N<=11
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            scan('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, multi-atom-full-support %d, DEMAND>0 %d, Demand>Door %d"
              % (nn, acc['cages'], acc['multiatom_fullsupport'], acc['demand_pos'], acc['demand_gt_door']), flush=True)
    # ---- CONSTRUCTIONS forcing multi-atom full-support with a LONG atom (Demand>0), N>=14 (the C_18-lesson regime) ----
    # (a) two odd cycles C_{2a+1}, C_{2b+1} sharing exactly ONE common vertex (figure-8): 2 bad edges, supports cover all.
    def fig8(a, b):
        # cycle A: 0..2a  (vertex 0 shared); cycle B: 0, 2a+1..2a+2b
        n = 2 * a + 2 * b + 1
        EA = [(i, i + 1) for i in range(2 * a)] + [(2 * a, 0)]
        off = 2 * a + 1
        EB = [(0, off)] + [(off + i, off + i + 1) for i in range(2 * b - 1)] + [(off + 2 * b - 1, 0)]
        E = EA + EB
        # parity cut on each cycle independently from shared vertex 0
        side = [0] * n
        for i in range(2 * a + 1):
            side[i] = i % 2
        for i in range(2 * b):
            side[off + i] = (i + 1) % 2  # continue parity from 0's neighbor
        return n, adj_from_edges(n, E), side
    for a in range(2, 9):
        for b in range(2, 9):
            n, adj, side = fig8(a, b)
            scan('fig8(%d,%d)' % (2 * a + 1, 2 * b + 1), n, adj, side, acc)
    # (b) two odd cycles sharing a common PATH of length p (theta-like), long bad edges
    def shared_path(a, b, p):
        # path 0..p shared; arc A of length a returns p->0; arc B of length b returns p->0
        n = (p + 1) + (a - 1) + (b - 1)
        E = [(i, i + 1) for i in range(p)]
        nxt = p + 1
        prev = p
        for _ in range(a - 1):
            E.append((prev, nxt)); prev = nxt; nxt += 1
        E.append((prev, 0))
        prev = p
        for _ in range(b - 1):
            E.append((prev, nxt)); prev = nxt; nxt += 1
        E.append((prev, 0))
        adj = adj_from_edges(n, E)
        best = gmin(n, adj, maxcut_all(n, adj)) if n <= 20 else None
        return n, adj, (best[0] if best else None)
    for p in range(1, 5):
        for a in range(3, 8):
            for b in range(3, 8):
                n, adj, side = shared_path(a, b, p)
                if side is not None:
                    scan('theta(p%d,%d,%d)' % (p, a, b), n, adj, side, acc)
    print("=" * 96)
    print("MULTI-ATOM FULL-SUPPORT SHELL SEARCH (gap#1's circular bottom-out case):")
    print("  cages scanned %d | multi-atom full-support comps %d | with DEMAND>0 (long atom, the dangerous case): %d | Demand>Door: %d"
          % (acc['cages'], acc['multiatom_fullsupport'], acc['demand_pos'], acc['demand_gt_door']))
    print("  DEMAND>0 multi-atom full-support examples (the regime that could bottom out circularly):")
    for r in acc['examples_pos'][:12]:
        print("   %s N=%d m_comp=%d sigma=%d Demand=%d Door=%d ells=%s Demand<=Door=%s"
              % (r['name'], r['n'], r['m_comp'], r['sigma'], r['demand'], r['door'], r['ells'], r['demand_le_door']))
    if not acc['examples_pos']:
        print("   (none found -- no multi-atom full-support shell with a long atom arose on this coverage)")
    if acc['worst']:
        print("   *** Demand>Door multi-atom full-support (CIRCULARITY OBSTRUCTION candidate): %s ***" % (acc['worst'],))
    print("VERDICT: %s" % (
        ("NO multi-atom full-support shell with DEMAND>0 arose (all such shells are all-ell=5, Demand=0, trivially absorbed;"
         " the %d found are harmless). The induction's circular bottom-out case (a long-atom multi-atom full-support shell)"
         " is EMPTY on this coverage incl N>=14 constructions -- strong evidence ReducedShellHall_NoTopEta closes."
         % acc['multiatom_fullsupport'] if acc['demand_pos'] == 0 else
         ("multi-atom full-support shells WITH a long atom EXIST (%d) but ALL have Demand <= Door (absorbed by the door"
          " WITHOUT eta_C) -- induction closes on this coverage." % acc['demand_pos'] if acc['demand_gt_door'] == 0 else
          "*** %d long-atom multi-atom full-support shells with Demand > Door -- CIRCULARITY OBSTRUCTION CANDIDATE ***"
          % acc['demand_gt_door']))))


if __name__ == '__main__':
    main()
