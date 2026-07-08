r"""hpair RIGIDITY gate (2026-07-08). EXACT-verify the TWO graph facts the Lean |S|<=5 base case (Ell5CSReduction.
hall_le_five) depends on, BEFORE investing in the (delicate) graph-level Lean rigidity proof. Falsifier-first.

For a reduced triangle-free Gamma-min MAX-cut, an ell=5 atom is a same-side bad edge e=(u,v) with blue-dist(u,v)=4.
Its shortest-geodesic cut-edge support is
    P_e = union over all shortest blue geodesics u..v of the geodesic's 4 cut edges.
The Lean base case assumes:
  (h4)    for every ell=5 atom e:                4 <= |P_e|
  (hpair) for every two DISTINCT ell=5 atoms e,f: 5 <= |P_e u P_f|
The only tight instance of (hpair) is |P_e|=|P_f|=4 (unique geodesic each); there hpair <=> P_e != P_f, i.e. RIGIDITY
(a 4-edge geodesic determines its endpoint pair, so distinct atoms have distinct 4-edge supports).

This gate checks (h4) and (hpair) EXACTLY over: census triangle-free Gamma-min cages N<=11, and even-cycle+chord
N in {18,22,26,30} (the C_18 coverage lesson -- long odd rows). ell=5 atoms only (the Ell5SupportExpansion scope).
A single failure of (h4) or (hpair) is a decisive falsifier on the base case. EXACT set arithmetic (no float).
Run from problems/23/writeup.
"""
import subprocess
from _h import dec, maxcut_all, Bconn, GENG, gmin
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import geos_paths, residuals, k2_components, even_cycle_chord


def support_edges(adj, side, e):
    """P_e = union of cut edges over all shortest blue geodesics of bad edge e. Returns a frozenset of (min,max)."""
    edges = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            edges.add((min(a, b), max(a, b)))
    return frozenset(edges)


def check_cage(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    acc['cages'] += 1
    ell = cd['ell']
    # ell=5 atoms and their supports
    atoms5 = [e for e in cd['M'] if ell[e] == 5]
    Pe = {e: support_edges(adj, side, e) for e in atoms5}
    for e in atoms5:
        acc['atoms5'] += 1
        c = len(Pe[e])
        if c < 4:                                  # (h4) breach
            acc['h4_fail'] += 1
            if acc['h4_ex'] is None:
                acc['h4_ex'] = (name, n, e, c)
        acc['minPe'] = c if acc['minPe'] is None else min(acc['minPe'], c)
    for i in range(len(atoms5)):
        for j in range(i + 1, len(atoms5)):
            e, f = atoms5[i], atoms5[j]
            u = len(Pe[e] | Pe[f])
            acc['pairs'] += 1
            if u < 5:                              # (hpair) breach
                acc['hpair_fail'] += 1
                if acc['hpair_ex'] is None:
                    acc['hpair_ex'] = (name, n, e, f, len(Pe[e]), len(Pe[f]), u)
            acc['minUnion'] = u if acc['minUnion'] is None else min(acc['minUnion'], u)
            # rigidity self-check: both size-4 supports must be DISTINCT
            if len(Pe[e]) == 4 and len(Pe[f]) == 4:
                acc['tightpairs'] += 1
                if Pe[e] == Pe[f]:                 # RIGIDITY breach (would sink the base case)
                    acc['rigid_fail'] += 1
                    if acc['rigid_ex'] is None:
                        acc['rigid_ex'] = (name, n, e, f)


def main():
    acc = dict(cages=0, atoms5=0, pairs=0, tightpairs=0,
               h4_fail=0, hpair_fail=0, rigid_fail=0,
               h4_ex=None, hpair_ex=None, rigid_ex=None,
               minPe=None, minUnion=None)
    print("hpair RIGIDITY gate: EXACT-verify (h4) |P_e|>=4 and (hpair) |P_e u P_f|>=5 for ell=5 atoms")
    print("=" * 96)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            check_cage('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, ell5-atoms %d, pairs %d (tight %d) | h4_fail %d hpair_fail %d rigid_fail %d"
              % (nn, acc['cages'], acc['atoms5'], acc['pairs'], acc['tightpairs'],
                 acc['h4_fail'], acc['hpair_fail'], acc['rigid_fail']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            check_cage('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print("=" * 96)
    print("TOTALS: cages %d | ell5-atoms %d (min |P_e|=%s) | ell5-pairs %d (min |union|=%s) | tight(both|P|=4) pairs %d"
          % (acc['cages'], acc['atoms5'], acc['minPe'], acc['pairs'], acc['minUnion'], acc['tightpairs']))
    print("  (h4) |P_e|>=4 failures: %d %s" % (acc['h4_fail'], acc['h4_ex'] or ''))
    print("  (hpair) |P_e u P_f|>=5 failures: %d %s" % (acc['hpair_fail'], acc['hpair_ex'] or ''))
    print("  RIGIDITY (both size-4 => distinct) failures: %d %s" % (acc['rigid_fail'], acc['rigid_ex'] or ''))
    ok = acc['h4_fail'] == 0 and acc['hpair_fail'] == 0 and acc['rigid_fail'] == 0
    print("VERDICT: %s" % (
        "BOTH graph facts (h4, hpair) hold on ALL %d cages / %d ell5-atoms / %d pairs (min |P_e|=%s, min |union|=%s); "
        "graph-level rigidity CONFIRMED => the Lean base-case hypotheses h4+hpair are a JUSTIFIED formalization target."
        % (acc['cages'], acc['atoms5'], acc['pairs'], acc['minPe'], acc['minUnion'])
        if ok else
        "FALSIFIER on the base case: h4_fail=%d hpair_fail=%d rigid_fail=%d -- the |S|<=5 base case is FALSE as stated; "
        "investigate before any Lean instantiation." % (acc['h4_fail'], acc['hpair_fail'], acc['rigid_fail'])))


if __name__ == '__main__':
    main()
