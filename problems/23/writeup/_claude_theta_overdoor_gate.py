r"""DECISIVE theta over-door gate (2026-07-08): probe whether OVER-DOOR full-support shells (Gamma_shell > 25*b_shell,
i.e. Demand>Door) arise in Gamma-MIN cuts, and whether the Gamma-decreasing switch (GPT-Pro option 1) exists otherwise.

Theta graphs (two hubs joined by 3 internally-disjoint paths) are the smallest IRREDUCIBLE multi-atom full-support
candidates (two odd cycles sharing a path -> not fig8-reducible). N<=16 so maxcut_all is feasible.

For each theta:
  (a) Gamma-MIN B-conn max cut: does any K2-component have Demand>Door (over-door) AND full support (|V_X|=N)?
      -- if YES at a Gamma-min cut, that is a DECISIVE OBSTRUCTION candidate to the lemma.
  (b) ALL max cuts: for each max cut with an over-door full-support shell (necessarily NON-Gamma-min), verify a
      zero-slack Gamma-DECREASING switch exists (search_switch, |W|<=3) -- confirming option 1 (Gamma-min excludes it).
EXACT (Fraction). Run from problems/23/writeup.
"""
from fractions import Fraction as F
from itertools import combinations
from _claude_residual_hall_gate import residuals, k2_components
from _claude_gamma_switch_verifier import gamma_of, cutval, search_switch
from _codex_k2t_switch_probe import adj_from_edges
from _h import maxcut_all, gmin, Bconn


def theta(p, a, b):
    """Hubs 0,1 joined by 3 paths of edge-lengths p,a,b (each >=2). Returns (n, adj) or None if degenerate."""
    if min(p, a, b) < 2:
        return None
    nxt = 2
    E = []
    for L in (p, a, b):
        prev = 0
        for _ in range(L - 1):
            E.append((prev, nxt)); prev = nxt; nxt += 1
        E.append((prev, 1))
    n = nxt
    return n, adj_from_edges(n, E)


def is_trianglefree(n, adj):
    return not any(b in adj[a] and c in adj[a] and c in adj[b]
                   for a in range(n) for b in adj[a] for c in adj[b] if a < b < c)


def overdoor_fullsupport_shells(n, adj, side):
    """Return list of (Demand, Door, |V_X|, ells) for K2-components that are over-door (Demand>Door). Full-support flagged."""
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    ell = cd['ell']
    cut_edges = sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])
    m = len(cd['M'])
    door = 25 * (cut_edges - m)
    out = []
    for X in k2_components(n, cd):
        atomsX = X['atoms']
        demand = sum(ell[e] ** 2 - 25 for e in atomsX)
        if demand > door:
            out.append(dict(demand=demand, door=door, nV=len(X['VX']), full=(len(X['VX']) == n),
                            m_comp=len(atomsX), ells=sorted(ell[e] for e in atomsX)))
    return out


def main():
    print("=" * 92)
    print("THETA OVER-DOOR GATE -- do over-door full-support shells arise in Gamma-min; else does the switch exist?")
    print("=" * 92)
    gmin_overdoor = 0; nonmin_overdoor = 0; nonmin_switch_found = 0; nonmin_noswitch = 0
    gmin_ex = None; noswitch_ex = None; thetas = 0
    for p in range(2, 10):
        for a in range(2, 8):
            for b in range(a, 8):
                t = theta(p, a, b)
                if t is None:
                    continue
                n, adj = t
                if n > 16 or not is_trianglefree(n, adj):
                    continue
                mc = maxcut_all(n, adj)
                best = gmin(n, adj, mc)
                if best is None:
                    continue
                thetas += 1
                # (a) Gamma-min cut over-door full-support?
                od = overdoor_fullsupport_shells(n, adj, best[0])
                if od:
                    for s in od:
                        if s['full']:
                            gmin_overdoor += 1
                            if gmin_ex is None:
                                gmin_ex = dict(theta=(p, a, b), n=n, **s)
                # (b) all max cuts: over-door full-support in a NON-Gamma-min cut => switch must exist
                gmin_gamma = gamma_of(n, adj, best[0])
                for side in mc:
                    if not Bconn(n, adj, side):
                        continue
                    g = gamma_of(n, adj, side)
                    if g is None or g <= gmin_gamma:
                        continue  # only strictly-higher-Gamma (non-min) cuts
                    od2 = overdoor_fullsupport_shells(n, adj, side)
                    if od2 and any(s['full'] for s in od2):
                        nonmin_overdoor += 1
                        sw = search_switch(n, adj, side, max_flip=3)
                        if sw is not None:
                            nonmin_switch_found += 1
                        else:
                            nonmin_noswitch += 1
                            if noswitch_ex is None:
                                noswitch_ex = dict(theta=(p, a, b), n=n, gamma=g, gmin_gamma=gmin_gamma)
    print("  thetas scanned (N<=16, tri-free, Gamma-min cage): %d" % thetas)
    print("  (a) Gamma-MIN cuts with an OVER-DOOR FULL-SUPPORT shell: %d  %s"
          % (gmin_overdoor, ("*** OBSTRUCTION CANDIDATE: %s ***" % gmin_ex) if gmin_ex else ""))
    print("  (b) NON-Gamma-min cuts with over-door full-support shell: %d | of those a |W|<=3 Gamma-decreasing switch EXISTS: %d | NO switch: %d"
          % (nonmin_overdoor, nonmin_switch_found, nonmin_noswitch))
    if noswitch_ex:
        print("     *** NON-min over-door shell with NO |W|<=3 switch (widen search or obstruction): %s ***" % noswitch_ex)
    print("VERDICT: %s" % (
        "NO Gamma-min over-door full-support shell in the theta family (Gamma-minimality excludes them, as the lemma predicts)."
        + (" All %d non-min over-door cuts admit a |W|<=3 Gamma-decreasing switch (option 1 confirmed on thetas)." % nonmin_overdoor
           if nonmin_overdoor and nonmin_noswitch == 0 else
           (" %d non-min over-door cuts have NO small switch (widen W or examine)." % nonmin_noswitch if nonmin_noswitch else
            " (no non-min over-door full-support cut arose in this family.)"))
        if gmin_overdoor == 0 else
        "*** %d Gamma-MIN over-door full-support shells FOUND -- DECISIVE OBSTRUCTION to NoReducedOverdoorFullSupportMultiShell ***" % gmin_overdoor))


if __name__ == '__main__':
    main()
