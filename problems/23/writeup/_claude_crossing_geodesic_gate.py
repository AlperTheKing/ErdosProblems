r"""EMPIRICAL arm of the born-edge-recut attack (2026-07-08): detect CROSSING shortest cut-geodesics of bad-edge pairs
in Gamma-minimal cuts, and check whether a Gamma-decreasing switch exists there.

GPT-Pro's monolithic switch = the born-edge recut of two CROSSING y-tight geodesics: P_e (a..x..y..b) and P_f
(c..y..x..d) sharing two vertices x,y in OPPOSITE order. Spreading feasibility <=> no such crossing arises in a Gamma-min
cut. This gate detects crossing bad-edge-pair geodesics in census Gamma-min cages + families, and for each crossing checks
search_switch (small-W Gamma-decreasing zero-slack switch). Findings:
  - if NO crossing pairs arise in Gamma-min cuts => consistent with spreading feasibility (the theory);
  - if crossings arise, does a Gamma-decreasing switch exist (as the lemma predicts)?
EXACT (int geodesics). Run from problems/23/writeup.
"""
import subprocess
from collections import deque
from _claude_residual_hall_gate import residuals, even_cycle_chord
from _claude_gamma_switch_verifier import search_switch, gamma_of
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def one_geo_vertices(adj, side, s, t, n):
    """Vertices of ONE shortest s-t cut-geodesic, in order s..t. None if unreachable."""
    dist = {s: 0}; pred = {s: None}; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[u] != side[w] and w not in dist:
                dist[w] = dist[u] + 1; pred[w] = u; q.append(w)
    if t not in dist:
        return None
    path = []; v = t
    while v is not None:
        path.append(v); v = pred[v]
    return path[::-1]


def crosses(pe, pf):
    """Do ordered vertex-paths pe, pf share >=2 vertices in OPPOSITE order? Return (x,y) or None."""
    common = [v for v in pe if v in pf]
    if len(common) < 2:
        return None
    pose = {v: i for i, v in enumerate(pe)}
    posf = {v: i for i, v in enumerate(pf)}
    # find two common vertices whose order flips between pe and pf
    for i in range(len(common)):
        for j in range(i + 1, len(common)):
            a, b = common[i], common[j]
            if (pose[a] < pose[b]) != (posf[a] < posf[b]):
                return (a, b)
    return None


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    M = cd['M']
    acc['cages'] += 1
    geo = {}
    for e in M:
        g = one_geo_vertices(adj, side, e[0], e[1], n)
        if g:
            geo[e] = g
    found_any = False
    for i in range(len(M)):
        for j in range(i + 1, len(M)):
            e, f = M[i], M[j]
            if e not in geo or f not in geo:
                continue
            xy = crosses(geo[e], geo[f])
            if xy:
                found_any = True
                acc['crossing_pairs'] += 1
                if acc['ex'] is None:
                    acc['ex'] = dict(name=name, n=n, e=e, f=f, ell_e=cd['ell'][e], ell_f=cd['ell'][f], xy=xy)
    if found_any:
        acc['crossing_cages'] += 1
        sw = search_switch(n, adj, side, max_flip=2)
        if sw is not None:
            acc['crossing_with_switch'] += 1  # a Gamma-decreasing switch exists (lemma-consistent)
        else:
            acc['crossing_no_small_switch'] += 1  # crossing but no |W|<=2 switch -- but this is a Gamma-MIN cut (rigid)


def main():
    acc = dict(cages=0, crossing_cages=0, crossing_pairs=0, crossing_with_switch=0, crossing_no_small_switch=0, ex=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            analyze('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, cages-with-crossing %d, crossing-pairs %d"
              % (nn, acc['cages'], acc['crossing_cages'], acc['crossing_pairs']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            analyze('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print("=" * 90)
    print("CROSSING-GEODESIC GATE (Gamma-min cuts):")
    print("  cages %d | cages with a crossing bad-edge-pair %d | total crossing pairs %d"
          % (acc['cages'], acc['crossing_cages'], acc['crossing_pairs']))
    print("  of crossing cages: with a |W|<=2 Gamma-decreasing switch %d | with NO small switch %d"
          % (acc['crossing_with_switch'], acc['crossing_no_small_switch']))
    if acc['ex']:
        print("  crossing example: %s" % (acc['ex'],))
    print("VERDICT: %s" % (
        "NO crossing bad-edge-pair geodesics arise in any Gamma-min cut -- CONSISTENT with spreading feasibility (the "
        "born-edge-recut switch is never NEEDED in a Gamma-min cut; the theory holds vacuously on this coverage)."
        if acc['crossing_cages'] == 0 else
        "%d Gamma-min cages have crossing geodesics; %d admit a small Gamma-decreasing switch, %d do NOT (a Gamma-min cage "
        "with a crossing but no switch would need the born-edge recut / is a candidate obstruction -- examine)."
        % (acc['crossing_cages'], acc['crossing_with_switch'], acc['crossing_no_small_switch'])))


if __name__ == '__main__':
    main()
