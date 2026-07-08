r"""STUBBORN-19 cut-family probe (2026-07-08). Cut-metric balls (+laminar) fail on 19/24349 multi-atom components.
N=11 is small enough to enumerate ALL 2^n vertex cuts. For each stubborn component, determine the MINIMAL structured
cut family that makes the fractional cut-cover feasible:
  (A) ALL cuts with delta_B(U) subset E(S)         -- must be feasible iff Hall holds (sanity; = LP-dual of Hall)
  (B) CONNECTED cuts (both U and complement connected in the CUT graph) with delta_B subset E(S)
  (C) cut-metric balls only (the failing family, for contrast)
Reports, per stubborn component, feasibility under A/B/C. If (B) connected-cuts feasible on ALL stubborn => the canonical
family is CONNECTED cuts (structured, laminar-uncrossable), a viable universal-construction candidate. If only (A) full
works => no small structured family; ShortestRowCutCover_exists is genuinely LP-dual-equivalent to Hall (certification-
grade, NOT a construction). Decisive for whether the cut-cover reframing is a real reduction. Run from writeup.
"""
import subprocess
from itertools import combinations
from collections import deque
import numpy as np
from scipy.optimize import linprog
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges
from _claude_cutmetric_ballcut_gate import cut_bfs_dist, cut_edges_all, deltaB, cut_components
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def cut_cover_feasible_over(cuts, atoms, ell, ES, cutedges):
    if not cuts:
        return False
    nU = len(cuts)
    A_ub = []; b_ub = []
    for e in atoms:
        A_ub.append([-1.0 if ((e[0] in U) != (e[1] in U)) else 0.0 for U in cuts]); b_ub.append(-float(ell[e] ** 2) / 25.0)
    dB = [set(deltaB(U, cutedges)) for U in cuts]
    for c in sorted(ES):
        A_ub.append([1.0 if c in dB[k] else 0.0 for k in range(nU)]); b_ub.append(1.0)
    res = linprog(c=np.zeros(nU), A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(0, None)] * nU, method='highs')
    return bool(res.success)


def both_connected(n, adj, side, U):
    Us = set(U); comp = set(range(n)) - Us
    if not comp:
        return False
    return len(cut_components(adj, side, list(U))) == 1 and len(cut_components(adj, side, list(comp))) == 1


def families(n, adj, side, ESset):
    cutedges = cut_edges_all(n, adj, side)
    allcuts = []; conn = []; balls = []
    # all subsets with deltaB subset E(S) (N<=11 => <=2048)
    verts = list(range(n))
    for r in range(1, n):
        for combo in combinations(verts, r):
            U = frozenset(combo)
            dB = deltaB(U, cutedges)
            if dB and all(c in ESset for c in dB):
                allcuts.append(U)
                if both_connected(n, adj, side, U):
                    conn.append(U)
    for v in range(n):
        dist = cut_bfs_dist(adj, side, v, n)
        reach = [u for u in range(n) if dist[u] >= 0]
        for rr in range(0, max((dist[u] for u in reach), default=0)):
            U = frozenset(u for u in reach if dist[u] <= rr)
            dB = deltaB(U, cutedges)
            if U and len(U) < n and dB and all(c in ESset for c in dB):
                balls.append(U)
    return allcuts, conn, balls, cutedges


def main():
    print("STUBBORN-19 cut-family probe: which structured cut family covers the components where cut-metric balls fail?")
    print("=" * 100)
    found = 0
    results = dict(A=0, B=0, C=0, total=0)
    for nn in [10, 11]:
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
                atoms = X['atoms']
                if len(atoms) < 2 or any(c2['ell'][e] > 23 for e in atoms):
                    continue
                ES = set()
                ok = True
                for e in atoms:
                    pe = all_shortest_geodesic_cut_edges(n, a2, s2, e[0], e[1])
                    if not pe:
                        ok = False; break
                    ES |= pe
                if not ok or not ES:
                    continue
                allcuts, conn, balls, cutedges = families(n, a2, s2, set(ES))
                ell = c2['ell']
                fC = cut_cover_feasible_over(balls, atoms, ell, ES, cutedges)
                if fC:
                    continue  # not stubborn
                # stubborn under balls: test connected + all
                fB = cut_cover_feasible_over(conn, atoms, ell, ES, cutedges)
                fA = cut_cover_feasible_over(allcuts, atoms, ell, ES, cutedges)
                found += 1; results['total'] += 1
                results['A'] += int(fA); results['B'] += int(fB); results['C'] += int(fC)
                if found <= 12:
                    print("  STUBBORN g6=%s N=%d ells=%s |ES|=%d #ballcuts=%d #conn=%d #all=%d : ballC=%s connB=%s allA=%s"
                          % (g6, n, sorted(ell[e] for e in atoms), len(ES), len(balls), len(conn), len(allcuts), fC, fB, fA), flush=True)
    print("=" * 100)
    print("stubborn components (cut-metric balls fail): %d | connected-cuts feasible: %d | ALL-cuts feasible: %d"
          % (results['total'], results['B'], results['A']))
    print("VERDICT: %s" % (
        "ALL %d stubborn components are covered by CONNECTED cuts => the canonical family is CONNECTED (both-sides-"
        "connected) cuts, a structured laminar-uncrossable family => universal-construction candidate for "
        "ShortestRowCutCover_exists." % results['total'] if results['B'] == results['total'] and results['total'] > 0 else
        "%d of %d stubborn covered by connected cuts; %d need the FULL cut family (all 2^n) => no small structured "
        "family suffices, ShortestRowCutCover_exists is LP-dual-equivalent to Hall (certification-grade, not a canonical "
        "construction). The cut-cover reframing does NOT reduce the universal difficulty." % (results['B'], results['total'], results['total'] - results['B'])))


if __name__ == '__main__':
    main()
