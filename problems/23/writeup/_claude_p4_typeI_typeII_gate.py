r"""P4 Type-I (C5BookParallel) vs Type-II (S1Theta / order-inverted) classification gate (2026-07-08).

Decisive test of GPT-Pro reply 24's P4SharedSupportDichotomy route. For two distinct ell=5 atoms e,f and length-4 cut
geodesics P (of e), Q (of f) sharing a cut edge, GPT-Pro classifies the sharing as:
  Type I  C5BookParallel: POSITION-COMPATIBLE -- exists an orientation of P and Q s.t. every shared VERTEX is at the same
          path index (0..4) and every shared EDGE at the same index; NO order inversion.
  Type II S1ThetaPattern: NO orientation is position-compatible (order inversion / edge shared at different indices) =>
          a reduced first-split theta = the HARD branch needing Gamma-min recut elimination.
(Type IV triangle/shorter-walk cannot occur for genuine geodesics in a triangle-free graph; Type III reducible needs the
cage machinery, not classified here.) QUESTION: over ALL ell=5 shared-geodesic witnesses in triangle-free Gamma-min MAX
cuts (census N<=11 + C5[t]), do any Type-II (order-inverted) witnesses occur?
  * (near-)NONE Type-II => classification collapses to Type-I C5-book => C5BookSupportExpansion (the "easiest" piece)
    carries the expansion; GPT-Pro's route essentially closes empirically (Type-II elimination is vacuous).
  * Type-II OCCUR => the hard S1ThetaPattern_eliminates branch is genuinely needed; report examples for study.
A P4 geodesic p0-p1-p2-p3-p4 has atom endpoints p0,p4 (same side), cut edges p0p1,p1p2,p2p3,p3p4. Orientation = choice of
which atom-endpoint is p0 (2 per path); we test all 4 (P,Q) orientation combos. EXACT. Run from problems/23/writeup.
"""
import subprocess
from itertools import combinations
from collections import deque
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import c5_blowup
from _claude_c1p_ferrers_gate import all_shortest_geodesics_vertexpaths
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def edges_of(vp):
    return {(min(vp[i], vp[i + 1]), max(vp[i], vp[i + 1])) for i in range(len(vp) - 1)}


def position_compatible(P, Q):
    """Exists orientation of P and Q s.t. all shared vertices are at equal index and no order inversion? P,Q vertex lists len 5."""
    for Pv in (P, P[::-1]):
        posP = {v: i for i, v in enumerate(Pv)}
        for Qv in (Q, Q[::-1]):
            posQ = {v: i for i, v in enumerate(Qv)}
            common = [v for v in Pv if v in posQ]
            if not common:
                continue
            ok = all(posP[v] == posQ[v] for v in common)  # same index for every shared vertex
            if ok:
                # also no order inversion is automatic if all equal-index; edges: shared edge at same index follows
                return True
    return False


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    ell = cd['ell']
    for X in k2_components(n, cd):
        five = [e for e in X['atoms'] if ell[e] == 5]
        if len(five) < 2:
            continue
        geo = {e: all_shortest_geodesics_vertexpaths(adj, side, e[0], e[1], n) for e in five}
        for e, f in combinations(five, 2):
            for P in geo[e]:
                Pe = edges_of(P)
                for Q in geo[f]:
                    if not (Pe & edges_of(Q)):
                        continue  # only witnesses that SHARE a cut edge
                    acc['witnesses'] += 1
                    if position_compatible(P, Q):
                        acc['typeI'] += 1
                    else:
                        acc['typeII'] += 1
                        if len(acc['typeII_ex']) < 5:
                            acc['typeII_ex'].append((name, n, e, f, tuple(P), tuple(Q)))


def main():
    print("P4 Type-I (C5-book) vs Type-II (order-inverted theta) classification over ell=5 shared-geodesic witnesses.")
    print("=" * 96)
    acc = dict(witnesses=0, typeI=0, typeII=0, typeII_ex=[])
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            analyze('cen%d' % nn, n, adj, b[0], acc)
        print("  census N=%d: witnesses %d | Type-I %d | Type-II %d" % (nn, acc['witnesses'], acc['typeI'], acc['typeII']), flush=True)
    for t in range(1, 8):
        n, adj, side = c5_blowup(t)
        analyze('C5[%d]' % t, n, adj, side, acc)
    print("=" * 96)
    print("TOTAL shared-geodesic witnesses %d | Type-I C5-book-parallel %d | Type-II order-inverted %d"
          % (acc['witnesses'], acc['typeI'], acc['typeII']))
    if acc['typeII_ex']:
        print("Type-II examples (name,n,e,f,P,Q):")
        for x in acc['typeII_ex']:
            print("  %s" % (x,))
    print("=" * 96)
    print("VERDICT: %s" % (
        "ALL %d ell=5 shared-geodesic witnesses are Type-I C5BookParallel (position-compatible); ZERO Type-II. => in real"
        " triangle-free Gamma-min MAX cuts the P4-sharing classification COLLAPSES to Type-I (+Type-IV vacuous); the hard"
        " S1ThetaPattern_eliminates branch is EMPIRICALLY VACUOUS, so GPT-Pro's route reduces to C5BookSupportExpansion"
        " (the 'easiest' layered-Hall piece). Strong support that the expansion follows without the theta recut."
        % acc['typeI'] if acc['typeII'] == 0 else
        "*** %d Type-II (order-inverted) witnesses occur in real Gamma-min max cuts -- the S1ThetaPattern_eliminates branch"
        " is GENUINELY NEEDED (not vacuous); these must be shown reducible/recut. Examples above for study. ***"
        % acc['typeII']))


if __name__ == '__main__':
    main()
