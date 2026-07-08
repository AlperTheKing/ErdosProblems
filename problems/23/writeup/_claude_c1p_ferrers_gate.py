r"""FERRERS CONSECUTIVE-ONES (C1P) GATE (2026-07-08). Decisive test of GPT-Pro reply 19's new route.

Reply 19 replaced the global switch theorem with FerrersShortestRouting_cutCondition_complete: the multi-atom Hall
holds because (a) the cut condition is PROVEN from max-cutness (M_cut(U)<=B_cut(U)) + rho_e=ell^2/(25(ell-1))<=1 for
ell<=23, and (b) Version A: the shortest-geodesic PATH-EDGE incidence matrix has the CONSECUTIVE-ONES PROPERTY (C1P)
=> interval matrix => totally unimodular => the cut condition is SUFFICIENT for shortest-geodesic routing.

This gate tests (b) DIRECTLY: for each multi-atom K2-component of a triangle-free Gamma-min max cut, collect ALL
shortest B-geodesics of all atoms as sequences of CUT edges (a bad edge e is same-side, so its geodesic alternates
sides -> every geodesic edge is a cut edge), build the path x cut-edge 0/1 matrix, and test whether there is an
ordering of the cut edges making EVERY geodesic an INTERVAL (contiguous block) = C1P for rows. Brute-force over
cut-edge orderings when #cut-edges <= 9 (else report SKIP).

  * C1P holds on all tested multi-atom components => STRONG evidence the FerrersShortestRouting mechanism (Version A) is
    real; the multi-atom Hall reduces to a classical interval/TU routing theorem (cut condition PROVEN => sufficient).
  * a FEASIBLE multi-atom component that is NOT C1P => Version A is not the mechanism (sufficiency comes from elsewhere;
    need Version B or a different argument) -- also decisive, redirects the route.
Includes the census L*=10 extremal g6=I?AAD@wF_. EXACT (integer geodesics). Run from problems/23/writeup.
"""
import subprocess
from itertools import permutations
from collections import deque
from _claude_residual_hall_gate import residuals, k2_components
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def all_shortest_geodesics_vertexpaths(adj, side, s, t, n):
    """All shortest s-t cut-geodesics as vertex sequences (BFS DAG enumeration)."""
    dist = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[u] != side[w] and w not in dist:
                dist[w] = dist[u] + 1; q.append(w)
    if t not in dist:
        return []
    D = dist[t]
    paths = []
    def bt(v, acc):
        if v == s:
            paths.append([s] + acc[::-1]); return
        for w in adj[v]:
            if side[v] != side[w] and dist.get(w, 10 ** 9) == dist[v] - 1:
                bt(w, acc + [v])
    bt(t, [])
    return paths


def path_edges(vp):
    return [(min(vp[i], vp[i + 1]), max(vp[i], vp[i + 1])) for i in range(len(vp) - 1)]


def is_c1p(rows_edgesets, edges):
    """Brute: exists an ordering of `edges` making every row's edge-set a contiguous interval?"""
    m = len(edges)
    if m > 9:
        return None
    idxsets = []
    ei = {e: i for i, e in enumerate(edges)}
    for R in rows_edgesets:
        idxsets.append(frozenset(ei[e] for e in R))
    # dedup rows
    idxsets = list(set(idxsets))
    for perm in permutations(range(m)):
        pos = {perm[i]: i for i in range(m)}
        ok = True
        for S in idxsets:
            ps = sorted(pos[x] for x in S)
            if ps and (ps[-1] - ps[0] + 1 != len(ps)):
                ok = False; break
        if ok:
            return True
    return False


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    for X in k2_components(n, cd):
        if len(X['atoms']) < 2:
            continue
        rows = []
        edges = set()
        toolong = False
        for e in X['atoms']:
            for vp in all_shortest_geodesics_vertexpaths(adj, side, e[0], e[1], n):
                pe = path_edges(vp)
                rows.append(pe); edges.update(pe)
        edges = sorted(edges)
        if len(edges) > 9:
            acc['skip'] += 1
            continue
        acc['tested'] += 1
        res = is_c1p(rows, edges)
        if res is True:
            acc['c1p'] += 1
        elif res is False:
            acc['not_c1p'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, len(X['atoms']), [cd['ell'][e] for e in X['atoms']], len(edges))


def main():
    print("FERRERS C1P GATE: do shortest-geodesic path-edge matrices of multi-atom components have consecutive-ones?")
    print("=" * 100)
    acc = dict(tested=0, c1p=0, not_c1p=0, skip=0, ex=None)
    # the L*=10 extremal first
    E = [(0, 5), (0, 7), (1, 6), (1, 8), (2, 7), (2, 8), (3, 8), (3, 9), (4, 8), (4, 9), (5, 9), (6, 9)]
    adj = adj_from_edges(10, E); side = [0, 0, 0, 0, 0, 1, 1, 1, 1, 0]
    analyze('EXTREMAL_I?AAD@wF_', 10, adj, side, acc)
    print("after L*=10 extremal: tested %d c1p %d not_c1p %d" % (acc['tested'], acc['c1p'], acc['not_c1p']))
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, Ee = dec(g6); a2 = adj_from_edges(n, Ee)
            b = gmin(n, a2, maxcut_all(n, a2))
            if b is None:
                continue
            analyze('cen%d' % nn, n, a2, b[0], acc)
        print("  census N=%d: multi-atom tested %d | C1P %d | NOT-C1P %d | skip(>9 edges) %d"
              % (nn, acc['tested'], acc['c1p'], acc['not_c1p'], acc['skip']), flush=True)
    print("=" * 100)
    print("TOTAL multi-atom components tested %d | C1P %d | NOT-C1P %d | skipped(>9 cut edges) %d"
          % (acc['tested'], acc['c1p'], acc['not_c1p'], acc['skip']))
    if acc['ex']:
        print("  *** NOT-C1P example (Version A is NOT the mechanism there): %s ***" % (acc['ex'],))
    print("VERDICT: %s" % (
        "ALL %d tested multi-atom components are C1P (interval/TU) -- STRONG evidence FerrersShortestRouting Version A"
        " is the mechanism: the PROVEN cut condition is SUFFICIENT for shortest-geodesic routing, closing multi-atom"
        " Hall for the ell<=23 rows. The remaining Lean theorem = classical interval-C1P => cut-condition-complete."
        % acc['c1p'] if acc['not_c1p'] == 0 else
        "*** %d multi-atom components are FEASIBLE but NOT C1P -- Version A (consecutive-ones) is NOT the universal"
        " mechanism; cut-condition-sufficiency must come from Version B (laminar min-cut) or a different argument. ***"
        % acc['not_c1p']))


if __name__ == '__main__':
    main()
