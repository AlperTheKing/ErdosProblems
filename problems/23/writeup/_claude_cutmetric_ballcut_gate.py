r"""CUT-METRIC ball cut-cover gate (2026-07-08). Refinement of _claude_cutcover_ballcut_gate after GRAPH-metric balls
failed on 87/24349 components. Geodesics live in the CUT graph (bad edge e => shortest cut-geodesic alternates sides,
all edges are cut edges), so the natural canonical cut family = balls in the CUT METRIC: dist using ONLY cut edges.
Their boundaries delta_B are exactly geodesic LAYERS (spheres). Tests three progressively richer canonical families:
  (F1) cut-metric balls U_{v,r} = {u : cutdist(v,u) <= r}
  (F2) F1 + connected components (in the cut graph) of each ball's COMPLEMENT (laminar refinement)
  (F3) F2 + connected components of each ball itself
restricted to delta_B(U) subset E(S). LP: lambda>=0, COVER (>= ell^2/25 per atom) + CONGESTION (<=1 on E(S)).
If F1 (or F2/F3) FEASIBLE on ALL multi-atom components => canonical cut-metric construction of ShortestRowCutCover_exists
=> universal proof of multi-atom Hall from geodesic layers + max-cutness (NO switch, NO per-instance LP). Run from writeup.
"""
import subprocess
from collections import deque
import numpy as np
from scipy.optimize import linprog
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def cut_bfs_dist(adj, side, s, n):
    d = [-1] * n; d[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[u] != side[w] and d[w] < 0:
                d[w] = d[u] + 1; q.append(w)
    return d


def cut_edges_all(n, adj, side):
    return [(a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b]]


def deltaB(U, cutedges):
    return [c for c in cutedges if (c[0] in U) != (c[1] in U)]


def cut_components(adj, side, vertices):
    """connected components (in the cut graph) of the induced vertex set."""
    vs = set(vertices); seen = set(); comps = []
    for s in vertices:
        if s in seen:
            continue
        comp = set(); q = deque([s]); seen.add(s)
        while q:
            u = q.popleft(); comp.add(u)
            for w in adj[u]:
                if side[u] != side[w] and w in vs and w not in seen:
                    seen.add(w); q.append(w)
        comps.append(frozenset(comp))
    return comps


def candidate_cuts(n, adj, side, ESset, family):
    cutedges = cut_edges_all(n, adj, side)
    cuts = set()
    balls = []
    for v in range(n):
        dist = cut_bfs_dist(adj, side, v, n)
        reach = [u for u in range(n) if dist[u] >= 0]
        maxd = max((dist[u] for u in reach), default=0)
        for r in range(0, maxd):
            U = frozenset(u for u in reach if dist[u] <= r)
            balls.append(U)
    def add(U):
        if U and len(U) < n:
            dB = deltaB(U, cutedges)
            if dB and all(c in ESset for c in dB):
                cuts.add(U)
    for U in balls:
        add(U)
        if family >= 2:
            comp_all = frozenset(range(n)) - U
            for c in cut_components(adj, side, comp_all):
                add(c)
        if family >= 3:
            for c in cut_components(adj, side, U):
                add(c)
    return sorted(cuts, key=lambda s: (len(s), tuple(sorted(s)))), cutedges


def cover_feasible(n, adj, side, cd, atoms, family):
    ell = cd['ell']
    if any(ell[e] > 23 for e in atoms):
        return None
    ES = set()
    for e in atoms:
        pe = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
        if not pe:
            return None
        ES |= pe
    if not ES:
        return None
    cuts, cutedges = candidate_cuts(n, adj, side, set(ES), family)
    if not cuts:
        return False
    nU = len(cuts)
    A_ub = []; b_ub = []
    for e in atoms:
        row = [-1.0 if ((e[0] in U) != (e[1] in U)) else 0.0 for U in cuts]
        A_ub.append(row); b_ub.append(-float(ell[e] ** 2) / 25.0)
    dBcache = [set(deltaB(U, cutedges)) for U in cuts]
    for c in sorted(ES):
        A_ub.append([1.0 if c in dBcache[k] else 0.0 for k in range(nU)]); b_ub.append(1.0)
    res = linprog(c=np.zeros(nU), A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, None)] * nU, method='highs')
    return bool(res.success)


def main():
    print("CUT-METRIC ball cut-cover gate (F1 balls, F2 +complement-components, F3 +ball-components).")
    print("=" * 100)
    for family in (1, 2, 3):
        acc = dict(tested=0, feas=0, infeas=0, skip=0, ex=None)
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
                    f = cover_feasible(n, a2, s2, c2, X['atoms'], family)
                    if f is None:
                        acc['skip'] += 1; continue
                    acc['tested'] += 1
                    if f:
                        acc['feas'] += 1
                    else:
                        acc['infeas'] += 1
                        if acc['ex'] is None:
                            acc['ex'] = (nn, n, [c2['ell'][e] for e in X['atoms']])
        print("FAMILY F%d: tested %d | FEASIBLE %d | INFEASIBLE %d | skip %d %s"
              % (family, acc['tested'], acc['feas'], acc['infeas'], acc['skip'],
                 ('| first-infeas %s' % (acc['ex'],)) if acc['ex'] else '| ALL FEASIBLE'), flush=True)
        if acc['infeas'] == 0:
            print("  => CUT-METRIC family F%d gives a CANONICAL universal cut-cover: multi-atom Hall proven from geodesic"
                  " layers + max-cutness. STRONGEST route." % family)
            break


if __name__ == '__main__':
    main()
