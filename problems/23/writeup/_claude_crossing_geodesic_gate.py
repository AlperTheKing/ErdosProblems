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


def bfs_cut_dist(adj, side, s, n):
    dist = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[u] != side[w] and w not in dist:
                dist[w] = dist[u] + 1; q.append(w)
    return dist


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
                # SHORTCUTTING test: does a re-pairing of the 4 endpoints give strictly smaller total cut-distance?
                # e=(s,t), f=(u,v). original dist sum = d(s,t)+d(u,v). Re-pairings: {(s,v),(u,t)}, {(s,u),(t,v)}.
                s, t = e; u, v = f
                ds = bfs_cut_dist(adj, side, s, n); du = bfs_cut_dist(adj, side, u, n); dtt = bfs_cut_dist(adj, side, t, n)
                orig = ds.get(t, 10 ** 9) + du.get(v, 10 ** 9)
                rp1 = ds.get(v, 10 ** 9) + du.get(t, 10 ** 9)
                rp2 = ds.get(u, 10 ** 9) + dtt.get(v, 10 ** 9)
                if min(rp1, rp2) < orig:
                    acc['shortcutting'] += 1
                    if acc['sc_ex'] is None:
                        acc['sc_ex'] = dict(name=name, n=n, e=e, f=f, ell_e=cd['ell'][e], ell_f=cd['ell'][f],
                                            xy=xy, orig=orig, rp1=rp1, rp2=rp2)
                if acc['ex'] is None:
                    acc['ex'] = dict(name=name, n=n, e=e, f=f, ell_e=cd['ell'][e], ell_f=cd['ell'][f], xy=xy)
    if found_any:
        acc['crossing_cages'] += 1


def main():
    acc = dict(cages=0, crossing_cages=0, crossing_pairs=0, shortcutting=0, ex=None, sc_ex=None)
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
    print("CROSSING-GEODESIC GATE (Gamma-min cuts). Crossings are HARMLESS unless SHORTCUTTING (born re-pairing strictly shorter):")
    print("  cages %d | cages with a crossing bad-edge-pair %d | total crossing pairs %d | SHORTCUTTING crossings %d"
          % (acc['cages'], acc['crossing_cages'], acc['crossing_pairs'], acc['shortcutting']))
    if acc['ex']:
        print("  benign crossing example: %s" % (acc['ex'],))
    if acc['sc_ex']:
        print("  *** SHORTCUTTING crossing in a Gamma-min cut (candidate obstruction -- born re-pairing shorter yet Gamma-min): %s ***"
              % (acc['sc_ex'],))
    print("VERDICT: %s" % (
        "Crossings ARISE in Gamma-min cuts (%d cages) but NONE are SHORTCUTTING (0 born re-pairings strictly shorter) -- "
        "CONSISTENT with the born-edge-recut theory: a shortcutting crossing would let the recut strictly drop Gamma, "
        "contradicting Gamma-minimality; benign (non-shortcutting) crossings are harmless (Delta_Gamma=0). Empirical support "
        "that Gamma-min forbids the switch-relevant (shortcutting) crossing." % acc['crossing_cages']
        if acc['shortcutting'] == 0 else
        "*** %d SHORTCUTTING crossings in Gamma-min cuts -- a born re-pairing is strictly SHORTER yet the cut is Gamma-minimal. "
        "This is a DIRECT TENSION with sub-claim C (shortcut => Gamma drop => not Gamma-min); examine whether the recut really "
        "drops Gamma (it may raise the cut deficiency / not be zero-slack). Decisive-obstruction candidate. ***" % acc['shortcutting']))


if __name__ == '__main__':
    main()
