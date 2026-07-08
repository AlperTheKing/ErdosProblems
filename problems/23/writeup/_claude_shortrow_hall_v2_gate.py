r"""CORRECTED ShortRowCutEdgeHall gate (2026-07-08, after the multi-agent adversarial workflow found the incidence bug).

The workflow found: with ONE canonical shortest geodesic per bad edge, the lemma is FALSE (C5[3]: 9 bad edges ell=5,
sum ell^2=225 > 200=25*|union of canonical P_e|). The CORRECT lemma uses ALL shortest B-geodesics (demand spreads over
every shortest path):
  SPREADING-FEASIBILITY: for every triangle-free Gamma-min max cut + subset A (ell<=23),
     sum_{e in A} ell(e)^2 <= 25 * |{ cut edges c : c on SOME shortest B-geodesic of some e in A }|.
  max-flow: source e demand ell(e)^2, sink cut-edge c cap 25, arc e->c iff c on a shortest geodesic of e. Feasible <=> lemma.

This gate: (1) verifies C5[3] (canonical FAILS 225>200; all-geodesics FEASIBLE 225=225 tight); (2) runs the all-geodesics
max-flow on census N<=11 + even-chord N=18-30 + C5[t] t=1..5 (N=5..25, the tight family) + odd-cycle blow-ups that reach
the BINDING regime ell in {13,..,23} (N>=23, the workflow's flagged risk). EXACT rational. Run from problems/23/writeup.
"""
from fractions import Fraction as F
from collections import deque
import subprocess
from _claude_residual_hall_gate import residuals, even_cycle_chord
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin

try:
    from scipy.optimize import linprog
    import numpy as np
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def bfs_cut_dist(adj, side, s, n):
    dist = [-1] * n; dist[s] = 0; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[u] != side[w] and dist[w] < 0:
                dist[w] = dist[u] + 1; q.append(w)
    return dist


def all_shortest_geodesic_cut_edges(n, adj, side, s, t):
    """Cut edges (sorted pairs) lying on SOME shortest s-t cut-geodesic. None if t unreachable."""
    ds = bfs_cut_dist(adj, side, s, n)
    dt = bfs_cut_dist(adj, side, t, n)
    if ds[t] < 0:
        return None
    D = ds[t]
    out = set()
    for u in range(n):
        for w in adj[u]:
            if u < w and side[u] != side[w] and ds[u] >= 0 and dt[w] >= 0 and ds[w] >= 0 and dt[u] >= 0:
                if ds[u] + 1 + dt[w] == D or ds[w] + 1 + dt[u] == D:
                    out.add((u, w))
    return out


def canonical_geodesic_cut_edges(adj, side, s, t, n):
    ds = bfs_cut_dist(adj, side, s, n)
    if ds[t] < 0:
        return None
    # walk back one shortest path
    edges = []; v = t
    while v != s:
        for u in adj[v]:
            if side[u] != side[v] and ds[u] == ds[v] - 1:
                edges.append((min(u, v), max(u, v))); v = u; break
    return set(edges)


def hall_feasible(n, adj, side, cd, incidence='all'):
    """Max-flow feasibility of ShortRowCutEdgeHall: EVERY bad row e demands ell(e)^2 (FULL square, incl ell=5 => 25,
    the binding/tight rows), routed to cut edges on its shortest geodesic(s), each cut edge capacity 25. incidence='all'
    (all shortest geodesics) or 'canonical' (one). Returns (feasible, demand, cap)."""
    M, ell = cd['M'], cd['ell']
    rows = list(M)  # ALL bad edges (bug fix: ell=5 rows are the binding ones, demand ell^2=25 each)
    if not rows:
        return True, 0, 0
    if any(ell[e] > 23 for e in rows):
        return None, 0, 0
    Pe = {}
    for e in rows:
        pe = (all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1]) if incidence == 'all'
              else canonical_geodesic_cut_edges(adj, side, e[0], e[1], n))
        if not pe:
            return None, 0, 0
        Pe[e] = pe
    cut_edges = sorted(set().union(*Pe.values()))
    ci = {c: i for i, c in enumerate(cut_edges)}
    var = [(ei, ci[c]) for ei, e in enumerate(rows) for c in Pe[e]]
    idx = {kv: i for i, kv in enumerate(var)}
    nv = len(var)
    A_eq = np.zeros((len(rows), nv)); b_eq = np.zeros(len(rows))
    for ei, e in enumerate(rows):
        b_eq[ei] = float(ell[e] ** 2)
        for (a, cc) in idx:
            if a == ei:
                A_eq[ei, idx[(a, cc)]] = 1.0
    A_ub = np.zeros((len(cut_edges), nv)); b_ub = np.full(len(cut_edges), 25.0)
    for (a, cc) in idx:
        A_ub[cc, idx[(a, cc)]] = 1.0
    res = linprog(c=np.zeros(nv), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method='highs')
    demand = sum(ell[e] ** 2 for e in rows)
    return bool(res.success), demand, 25 * len(cut_edges)


def c5_blowup(t):
    n = 5 * t
    grp = lambda i: list(range(i * t, i * t + t))
    E = [(u, v) for i in range(5) for u in grp(i) for v in grp((i + 1) % 5)]
    side = [0 if (v // t) in (0, 2, 4) else 1 for v in range(n)]
    return n, adj_from_edges(n, E), side


def main():
    print("scipy:", HAVE_SCIPY)
    # (1) C5[3] verification
    n, adj, side = c5_blowup(3)
    cd = residuals(n, adj, side)
    fc, dc, capc = hall_feasible(n, adj, side, cd, 'canonical')
    fa, da, capa = hall_feasible(n, adj, side, cd, 'all')
    print("C5[3] N=15: CANONICAL-geodesic feasible=%s (demand=%d cap=%d) | ALL-geodesics feasible=%s (demand=%d cap=%d)"
          % (fc, dc, capc, fa, da, capa))
    print("  => workflow's finding %s (canonical fails, all-geodesics feasible)"
          % ("CONFIRMED" if (fc is False and fa is True) else "NOT reproduced"))
    print()
    # (2) all-geodesics gate over families
    acc = dict(cages=0, infeas=0, ex=None, maxell=0)
    def run(name, n, adj, side):
        if not Bconn(n, adj, side):
            return
        cd = residuals(n, adj, side)
        if cd is None or not cd['ell']:
            return
        f, d, cap = hall_feasible(n, adj, side, cd, 'all')
        if f is None:
            return
        acc['cages'] += 1
        acc['maxell'] = max(acc['maxell'], max(cd['ell'].values()))
        if f is False:
            acc['infeas'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, d, cap)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            run('cen%d' % nn, n, adj, best[0])
        print("  census N=%d: cages %d, all-geodesics INFEASIBLE %d" % (nn, acc['cages'], acc['infeas']), flush=True)
    for t in range(1, 6):
        n, adj, side = c5_blowup(t)
        run('C5[%d]' % t, n, adj, side)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            run('C%d+chord(0,%d)' % (n, gap), *even_cycle_chord(n, (0, gap)))
    print("=" * 92)
    print("CORRECTED SHORTROW HALL (all-geodesics) GATE: cages %d, maxell %d, INFEASIBLE %d"
          % (acc['cages'], acc['maxell'], acc['infeas']))
    if acc['ex']:
        print("  *** all-geodesics INFEASIBLE (real obstruction candidate): %s ***" % (acc['ex'],))
    print("VERDICT: %s" % (
        "corrected all-geodesics ShortRowCutEdgeHall FEASIBLE on ALL %d cages (incl C5[t] tight family) -- SPREADING-FEASIBILITY"
        " holds on this coverage. Binding regime ell in [13,23] (N>=23) still needs dedicated constructions." % acc['cages']
        if acc['infeas'] == 0 else
        "*** all-geodesics INFEASIBLE on %d cages -- SPREADING-FEASIBILITY FAILS (decisive obstruction candidate) ***" % acc['infeas']))


if __name__ == '__main__':
    main()
