"""Extended adversarial hunt for (CX) violations, focusing on regimes the standing battery may underweight:
  (a) extreme-aspect non-uniform C5/C7/C9 blow-ups (hub-superposition, high |cyc| multiplicity),
  (b) two odd cycles sharing a long path (overlapping geodesics in ONE K-component -> cross terms),
  (c) Petersen, Kneser-ish, dodecahedron, Mobius-Kantor (girth-5+ vertex-transitive),
  (d) bridges between blow-ups (load on the bridge endpoint shared by two bundles).
Uses the SAME independent struct (mystruct) + (CX) check from _wf_cvver_crossterm. Exact Fraction.
Reports min (CX) margin, binding edge, any violation, plus min (CV) margin per component."""
import itertools
from fractions import Fraction as F
from _wf_cvver_crossterm import (mystruct, my_kcomp, adj_of, chk, blowup, bridge)
from _stark1 import gmins
from _bdef_construct import Cn

def nonuniform_blowup_cut(parts):
    """C_m blow-up with given part sizes; standard 'almost-bipartite' cut: side[part i]=i%2 (odd m -> one bad pair)."""
    m = len(parts); n = sum(parts)
    start = [0] * (m + 1)
    for i in range(m):
        start[i + 1] = start[i] + parts[i]
    adj = [set() for _ in range(n)]
    for i in range(m):
        j = (i + 1) % m
        for a in range(start[i], start[i + 1]):
            for b in range(start[j], start[j + 1]):
                adj[a].add(b); adj[b].add(a)
    side = [0] * n
    for i in range(m):
        for v in range(start[i], start[i + 1]):
            side[v] = i % 2
    return n, adj, side

def run(name, n, adj, side, acc):
    chk(name, n, adj, side, acc, do_crosscheck=True)

if __name__ == "__main__":
    acc = {'ne': 0, 'viol': 0, 'first': None,
           'minm': (F(10 ** 18), '', '', '', '', '', '', '', ''),
           'xc': 0, 'cv_viol': 0, 'cv_minm': (F(10 ** 18), '', '', '', '', ''),
           'xc_bad_identity': [], 'xc_bad_gamma': [], 'xc_bad_cvform': [],
           'T_mismatch': []}
    print("=== EXTENDED (CX) hunt ===", flush=True)

    # (a) extreme-aspect non-uniform C5 blow-ups -- USE TRUE gamma-min MAX cuts (gmins), NOT naive parity.
    # (The naive parity 2-coloring is NOT a maximum cut for unbalanced parts -> outside the (CV) hypothesis.)
    cnt = 0; skipped_notmax = 0
    for parts in itertools.product([1, 2, 3, 4], repeat=5):
        if sum(parts) > 18:   # keep n<=18 so gmins' brute maxcut_all is fast
            continue
        n, E = blowup(list(parts))
        adj, cuts = gmins(n, E)
        if not cuts:
            continue
        for s in cuts[:2]:
            run("C5gm%s" % (parts,), n, adj, s, acc); cnt += 1
    print("  (a) C5 gamma-min MAX cuts: tested %d, CXviol=%d minCXm=%s" % (cnt, acc['viol'], float(acc['minm'][0])), flush=True)

    # (a2) extreme-aspect C7 / C9 via gmins (true gamma-min cuts), a few asymmetric shapes
    for parts in [[1, 1, 1, 1, 1, 1, 6], [6, 1, 1, 1, 1, 1, 1], [1, 4, 1, 4, 1, 1, 1],
                  [2, 3, 2, 3, 2, 1, 1], [1, 5, 1, 5, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2]]:
        n, E = blowup(parts)
        if n > 18: continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:2] if cuts else []):
            run("C7nu%s" % parts, n, adj, s, acc)
    for parts in [[1, 1, 1, 1, 1, 1, 1, 1, 2], [1, 2, 1, 2, 1, 2, 1, 2, 1]]:
        n, E = blowup(parts)
        if n > 18: continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:2] if cuts else []):
            run("C9nu%s" % parts, n, adj, s, acc)
    print("  (a2) C7/C9 asymmetric: CXviol=%d minCXm=%s" % (acc['viol'], float(acc['minm'][0])), flush=True)

    # (b) two C5 blow-ups bridged (geodesic bundles share the bridge endpoint)
    def blow5(t):
        return blowup([t] * 5)
    for (t1, t2) in [(1, 1), (1, 2), (1, 3)]:   # n<=20: keep brute maxcut feasible
        n1, E1 = blow5(t1); n2, E2 = blow5(t2)
        if n1 + n2 > 20: continue
        nn = n1 + n2
        E = list(E1) + [(a + n1, b + n1) for (a, b) in E2] + [(0, n1)]
        adj, cuts = gmins(nn, E)
        for s in (cuts[:2] if cuts else []):
            run("C5[%d]|C5[%d]" % (t1, t2), nn, adj, s, acc)
    print("  (b) bridged C5 blow-ups: CXviol=%d minCXm=%s" % (acc['viol'], float(acc['minm'][0])), flush=True)

    # (c) named girth>=5 vertex-transitive graphs
    def petersen():
        out = [(i, (i + 1) % 5) for i in range(5)]           # outer C5
        out += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]  # inner pentagram
        out += [(i, 5 + i) for i in range(5)]                # spokes
        return 10, out
    def desargues():
        # generalized Petersen GP(10,3): outer C10 + inner skip-3 + spokes
        out = [(i, (i + 1) % 10) for i in range(10)]
        out += [(10 + i, 10 + (i + 3) % 10) for i in range(10)]
        out += [(i, 10 + i) for i in range(10)]
        return 20, out
    def mobius_kantor():
        # GP(8,3)
        out = [(i, (i + 1) % 8) for i in range(8)]
        out += [(8 + i, 8 + (i + 3) % 8) for i in range(8)]
        out += [(i, 8 + i) for i in range(8)]
        return 16, out
    def dodecahedron():
        # 20 vertices, girth 5, 3-regular
        E = [(0,1),(1,2),(2,3),(3,4),(4,0),
             (0,5),(1,6),(2,7),(3,8),(4,9),
             (5,10),(6,11),(7,12),(8,13),(9,14),
             (10,11),(11,12),(12,13),(13,14),(14,10),
             (5,11),(6,12),(7,13),(8,14),(9,10)]  # corrected pentagonal prism-ish wiring below
        return None  # avoid wrong wiring; skip
    for nm, gg in [("Petersen", petersen()), ("MobiusKantor", mobius_kantor())]:  # Desargues n=20 too slow for brute maxcut
        nn, E = gg
        adj, cuts = gmins(nn, E)
        for s in (cuts[:3] if cuts else []):
            run(nm, nn, adj, s, acc)
    print("  (c) named girth>=5: CXviol=%d minCXm=%s" % (acc['viol'], float(acc['minm'][0])), flush=True)

    # (d) C5[t] blown-up cross with a longer odd cycle inside one component via shared blow-up class:
    #     non-uniform C5 with a giant hub class to maximize hub load superposition
    # hub-superposition via gmins is limited by brute maxcut (n<=18). Use balanced-ish hubs at n<=18.
    for parts in [[1, 6, 1, 1, 6], [1, 1, 6, 6, 1], [6, 1, 6, 1, 1], [1, 7, 1, 7, 1], [2, 6, 2, 6, 2]]:
        n, E = blowup(parts)
        if n > 18: continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:2] if cuts else []):
            run("C5hub%s" % parts, n, adj, s, acc)
    print("  (d) hub-superposition C5: CXviol=%d minCXm=%s" % (acc['viol'], float(acc['minm'][0])), flush=True)

    print("\n  ===== EXTENDED HUNT RESULTS =====", flush=True)
    print("  edges (CX) tested = %d" % acc['ne'], flush=True)
    print("  (CX) violations   = %d" % acc['viol'], flush=True)
    mm = acc['minm']
    print("  MIN (CX) margin   = %s (=%s) at name=%s N=%s beta=%s edge=%s ell=%s ncyc=%s R_f=%s rhs=%s"
          % (mm[0], float(mm[0]), mm[1], mm[2], mm[3], mm[4], mm[5], mm[6], mm[7], mm[8]), flush=True)
    if acc['first']:
        print("  FIRST (CX) violation: %s" % (acc['first'],), flush=True)
    print("  components cross-checked = %d ; (CV) viol=%d min(CV)margin=%s"
          % (acc['xc'], acc['cv_viol'], float(acc['cv_minm'][0])), flush=True)
    print("  identity/gamma/cvform breaks = %d/%d/%d  Tmismatch=%d"
          % (len(acc['xc_bad_identity']), len(acc['xc_bad_gamma']),
             len(acc['xc_bad_cvform']), len(acc['T_mismatch'])), flush=True)
    print("  === (CX) %s ===" % ("HOLDS (0 viol)" if not acc['viol'] else "FAILS"), flush=True)
