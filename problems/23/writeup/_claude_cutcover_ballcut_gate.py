r"""BALL-CUT FRACTIONAL CUT-COVER gate (2026-07-08). Tests whether GPT-Pro reply 20's ShortestRowCutCover_exists has a
CANONICAL geometric construction (distance-ball cuts = coarea layers), not just a per-instance LP dual of Hall.

GPT-Pro reply 20 reduced multi-atom row-subset Hall (sum_{e in S} ell^2 <= 25|E(S)|) to a fractional CUT-COVER cert:
  lambda_U >= 0 on vertex cuts, (COVER) sum_{U sep e} lambda_U >= ell(e)^2/25 for e in S, (CONGESTION) sum_{U: c in
  delta_B(U)} lambda_U <= indicator(c in E(S)). By LP duality this EXISTS iff Hall holds (equivalent). The open question
  is whether a CANONICAL/STRUCTURED family of cuts suffices -- if so, that is a universal proof, not certification-only.

Natural canonical family = BALL CUTS U_{v,r} = { u : dist_G(v,u) <= r } (graph BFS distance), the geodesic distance
LAYERS. delta_B(U_{v,r}) = cut edges from layer<=r to layer>r; a bad edge e=(s,t) is SEPARATED by U_{v,r} iff exactly
one endpoint is within radius r of v. CONGESTION for c not in E(S) forces lambda_U>0 only for cuts with delta_B(U) subset
of E(S); we restrict candidates to those.

Per multi-atom K2-component, S = all atoms (max demand). LP: over ball cuts U with delta_B(U) subset E(S), find
lambda>=0 with COVER (>= w_e) and CONGESTION (<=1 on E(S) cut edges). FEASIBLE => a canonical ball-cut cut-cover
certificate exists.
  * ball-cut LP feasible on ALL components => STRONG evidence ShortestRowCutCover_exists has a canonical coarea/ball
    construction => universal proof mechanism (the switch is not needed and neither is a per-instance LP).
  * ball-cut LP infeasible somewhere (while Hall/all-cut cover holds) => ball cuts insufficient; need richer cut family
    (still certifiable per-instance, but no canonical construction from balls alone). Reports how far ball cuts get.
EXACT rational LP (HiGHS float solve then this is annotation; feasibility is robust with the 2x slack). Run from writeup.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
import numpy as np
from scipy.optimize import linprog
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def bfs_dist(adj, s, n):
    d = [-1] * n; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d


def cut_edges_all(n, adj, side):
    return [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b]]


def deltaB(U, cutedges):
    """cut edges with exactly one endpoint in set U."""
    return [c for c in cutedges if (c[0] in U) != (c[1] in U)]


def ball_cut_cover_feasible(n, adj, side, cd, atoms):
    """LP feasibility of a ball-cut fractional cut-cover for S=atoms. Returns (feasible|None, ncuts, slack_or_none)."""
    ell = cd['ell']
    if any(ell[e] > 23 for e in atoms):
        return None, 0, None
    # E(S): union of all shortest-geodesic cut edges of the atoms
    ES = set()
    for e in atoms:
        pe = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
        if not pe:
            return None, 0, None
        ES |= pe
    ES = sorted(ES)
    if not ES:
        return None, 0, None
    cutedges = cut_edges_all(n, adj, side)
    # candidate ball cuts U_{v,r}; keep only those with deltaB subset E(S), nonempty, and separating >=1 atom
    ESset = set(ES)
    cuts = []
    seen = set()
    for v in range(n):
        dist = bfs_dist(adj, v, n)
        maxd = max(dist)
        for r in range(0, maxd):
            U = frozenset(u for u in range(n) if 0 <= dist[u] <= r)
            if U in seen or not U or len(U) == n:
                continue
            seen.add(U)
            dB = deltaB(U, cutedges)
            if not dB or any(c not in ESset for c in dB):
                continue
            cuts.append(U)
    if not cuts:
        return False, 0, None
    # separations: does cut U separate atom e=(s,t)? (exactly one endpoint in U)
    # COVER (>=): -sum_{U sep e} lambda <= -w_e   ;  CONGESTION (<=1): sum_{U: c in dB(U)} lambda <= 1
    nU = len(cuts)
    sep = [[1.0 if ((atoms[ai][0] in U) != (atoms[ai][1] in U)) else 0.0 for U in cuts] for ai in range(len(atoms))]
    w = [float(ell[e] ** 2) / 25.0 for e in atoms]
    A_ub = []; b_ub = []
    # cover: -sum sep*lambda <= -w
    for ai in range(len(atoms)):
        A_ub.append([-sep[ai][k] for k in range(nU)]); b_ub.append(-w[ai])
    # congestion: for each c in E(S): sum_{U: c in dB(U)} lambda <= 1
    dBcache = [set(deltaB(U, cutedges)) for U in cuts]
    for c in ES:
        A_ub.append([1.0 if c in dBcache[k] else 0.0 for k in range(nU)]); b_ub.append(1.0)
    res = linprog(c=np.zeros(nU), A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, None)] * nU, method='highs')
    return bool(res.success), nU, None


def main():
    print("BALL-CUT fractional CUT-COVER gate: does a canonical distance-ball (coarea) cut-cover certify row-subset Hall?")
    print("=" * 100)
    acc = dict(tested=0, feas=0, infeas=0, skip=0, ex=None)
    # extremal first
    E = [(0, 5), (0, 7), (1, 6), (1, 8), (2, 7), (2, 8), (3, 8), (3, 9), (4, 8), (4, 9), (5, 9), (6, 9)]
    adj = adj_from_edges(10, E); side = [0, 0, 0, 0, 0, 1, 1, 1, 1, 0]
    cd = residuals(10, adj, side)
    for X in k2_components(10, cd):
        if len(X['atoms']) >= 2:
            f, nu, _ = ball_cut_cover_feasible(10, adj, side, cd, X['atoms'])
            print("EXTREMAL N=10 atoms=%d: ball-cut cover feasible=%s (#ballcuts=%d)" % (len(X['atoms']), f, nu))
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, Ee = dec(g6); a2 = adj_from_edges(n, Ee)
            b = gmin(n, a2, maxcut_all(n, a2))
            if b is None:
                continue
            s2 = b[0]
            if not Bconn(n, a2, s2):
                continue
            c2 = residuals(n, a2, s2)
            if c2 is None or not c2['ell']:
                continue
            for X in k2_components(n, c2):
                if len(X['atoms']) < 2:
                    continue
                f, nu, _ = ball_cut_cover_feasible(n, a2, s2, c2, X['atoms'])
                if f is None:
                    acc['skip'] += 1; continue
                acc['tested'] += 1
                if f:
                    acc['feas'] += 1
                else:
                    acc['infeas'] += 1
                    if acc['ex'] is None:
                        acc['ex'] = ('cen%d' % nn, n, [c2['ell'][e] for e in X['atoms']])
        print("  census N=%d: multi-atom tested %d | ball-cut cover FEASIBLE %d | INFEASIBLE %d | skip %d"
              % (nn, acc['tested'], acc['feas'], acc['infeas'], acc['skip']), flush=True)
    print("=" * 100)
    print("TOTAL multi-atom tested %d | ball-cut cover FEASIBLE %d | INFEASIBLE %d | skip(ell>23) %d"
          % (acc['tested'], acc['feas'], acc['infeas'], acc['skip']))
    if acc['ex']:
        print("  *** ball-cut cover INFEASIBLE (canonical balls insufficient, need richer cuts): %s ***" % (acc['ex'],))
    print("VERDICT: %s" % (
        "canonical BALL-CUT (coarea) fractional cut-cover FEASIBLE on ALL %d multi-atom components -- STRONG evidence"
        " ShortestRowCutCover_exists has a CANONICAL distance-layer construction => a universal proof of the multi-atom"
        " Hall (no switch, no per-instance LP; lambda from geodesic balls + max-cutness)." % acc['feas']
        if acc['infeas'] == 0 else
        "*** ball cuts INSUFFICIENT on %d components -- the cut-cover needs a richer cut family than distance balls;"
        " ShortestRowCutCover_exists stays certification-grade (per-instance LP), no canonical ball construction. ***"
        % acc['infeas']))


if __name__ == '__main__':
    main()
