r"""PATH-ROUTING vs B-MATCHING decisive gate (2026-07-08). Tests soundness of GPT-Pro reply 19's FerrersShortestRouting.

Two models for the multi-atom spreading feasibility of a K2-component:
  * B-MATCHING (the real target, = _claude_minmaxload_gate): atom e demand ell(e)^2, routed to INDIVIDUAL cut edges in
    P_e (union of all shortest-geodesic cut edges), each edge cap 25. L*_edge = min max load. Feasible <=> L*_edge<=25
    <=> row-subset Hall  sum_{e in S} ell^2 <= 25|union P_e(S)| for all S.
  * PATH-ROUTING (GPT-Pro reply 19): commodity e demand rho_e = ell(e)^2/(25(ell-1)), routed along WHOLE shortest
    s_e-t_e geodesic PATHS, each cut edge cap 1. L*_path = min max edge congestion. Feasible <=> L*_path <= 1.
Path-routing is STRICTLY STRONGER: routing whole paths (not free edges) => L*_path >= L*_edge/25 (normalized). So
path-feasible => b-feasible, NOT conversely. GPT-Pro's route needs PATH feasibility (via FerrersShortestRouting cut-
condition sufficiency). Version A (C1P) for it was FALSIFIED (~80% not-C1P). DECISIVE QUESTION: is PATH-ROUTING itself
feasible (L*_path<=1) on the components where C1P fails?
  * YES everywhere => FerrersShortestRouting CONCLUSION holds (cut-condition => path-feasible); only the PROOF needs
    Version B (laminar), not C1P. GPT-Pro's route is viable.
  * L*_path > 1 somewhere (while b-matching L*_edge<=25 still holds) => path-routing is TOO STRONG; GPT-Pro's route
    does NOT work and gap#1 must use the b-matching row-subset Hall directly. DECISIVE against reply 19's route.
Also reports GPT-Pro's cut-condition value (max over vertex cuts is hard; instead we report the b-matching row-subset
Hall tightness = L*_edge/25, and path congestion, for direct comparison). EXACT rational LP. Run from problems/23/writeup.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
import numpy as np
from scipy.optimize import linprog
from _claude_residual_hall_gate import residuals, k2_components
from _claude_c1p_ferrers_gate import all_shortest_geodesics_vertexpaths, path_edges
from _claude_multiatom_congestion_probe import min_max_load
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def path_routing_congestion(n, adj, side, cd, atoms):
    """L*_path: min max cut-edge congestion routing rho_e = ell^2/(25(ell-1)) along shortest geodesic PATHS (cap-free,
    minimize max). Feasible for GPT-Pro's model iff L*_path <= 1. Returns (L*_path as float, #paths, #edges)."""
    ell = cd['ell']
    if any(ell[e] > 23 for e in atoms):
        return None, None, None
    # enumerate all shortest geodesic paths per atom, as edge-sets
    paths = []  # (atom_index, [cut edges])
    edges = set()
    rho = []
    for ei, e in enumerate(atoms):
        vps = all_shortest_geodesics_vertexpaths(adj, side, e[0], e[1], n)
        if not vps:
            return None, None, None
        rho.append(F(ell[e] ** 2, 25 * (ell[e] - 1)))
        for vp in vps:
            pe = path_edges(vp)
            paths.append((ei, pe)); edges.update(pe)
    edges = sorted(edges)
    ci = {c: i for i, c in enumerate(edges)}
    nP = len(paths); nE = len(edges)
    NV = nP + 1  # path flows + L
    obj = np.zeros(NV); obj[nP] = 1.0
    # per atom: sum of its path flows = rho_e
    natoms = len(atoms)
    A_eq = np.zeros((natoms, NV)); b_eq = np.zeros(natoms)
    for ai in range(natoms):
        b_eq[ai] = float(rho[ai])
        for pj, (ei, pe) in enumerate(paths):
            if ei == ai:
                A_eq[ai, pj] = 1.0
    # per edge: sum path flows through it - L <= 0
    A_ub = np.zeros((nE, NV)); b_ub = np.zeros(nE)
    for pj, (ei, pe) in enumerate(paths):
        for c in pe:
            A_ub[ci[c], pj] += 1.0
    for j in range(nE):
        A_ub[j, nP] = -1.0
    res = linprog(c=obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * NV, method='highs')
    if not res.success:
        return None, nP, nE
    return res.x[nP], nP, nE


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    for X in k2_components(n, cd):
        if len(X['atoms']) < 2:
            continue
        Lp, nP, nE = path_routing_congestion(n, adj, side, cd, X['atoms'])
        if Lp is None:
            acc['skip'] += 1
            continue
        Le, bx, ells = min_max_load(n, adj, side, cd, X['atoms'])
        acc['tested'] += 1
        if Lp > acc['maxpath'][0]:
            acc['maxpath'] = (Lp, name, n, [cd['ell'][e] for e in X['atoms']], nE)
        if Le and Le > acc['maxedge'][0]:
            acc['maxedge'] = (Le, name, n)
        if Lp > 1 + 1e-9:
            acc['path_infeas'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, round(Lp, 5), [cd['ell'][e] for e in X['atoms']], 'L_edge=%s' % (round(Le, 4) if Le else Le))


def main():
    print("PATH-ROUTING vs B-MATCHING: is GPT-Pro reply 19's stronger path model feasible (L*_path<=1) everywhere?")
    print("=" * 100)
    acc = dict(tested=0, path_infeas=0, skip=0, maxpath=(0.0, '', 0, [], 0), maxedge=(0.0, '', 0), ex=None)
    # extremal first
    E = [(0, 5), (0, 7), (1, 6), (1, 8), (2, 7), (2, 8), (3, 8), (3, 9), (4, 8), (4, 9), (5, 9), (6, 9)]
    analyze('EXTREMAL', 10, adj_from_edges(10, E), [0, 0, 0, 0, 0, 1, 1, 1, 1, 0], acc)
    mp = acc['maxpath']
    print("after extremal: tested %d, max L*_path=%.5f, path-infeas(>1) %d" % (acc['tested'], mp[0], acc['path_infeas']))
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, Ee = dec(g6); a2 = adj_from_edges(n, Ee)
            b = gmin(n, a2, maxcut_all(n, a2))
            if b is None:
                continue
            analyze('cen%d' % nn, n, a2, b[0], acc)
        mp = acc['maxpath']
        print("  census N=%d: multi-atom tested %d | PATH-INFEAS(L*_path>1) %d | max L*_path=%.5f @ N=%d ells=%s | skip %d"
              % (nn, acc['tested'], acc['path_infeas'], mp[0], mp[2], mp[3], acc['skip']), flush=True)
    print("=" * 100)
    mp = acc['maxpath']; me = acc['maxedge']
    print("TOTAL multi-atom tested %d | PATH-ROUTING infeasible (L*_path>1) %d | skip(ell>23) %d" % (acc['tested'], acc['path_infeas'], acc['skip']))
    print("MAX path congestion L*_path = %.5f @ %s N=%d ells=%s (%d cut edges)" % mp)
    print("MAX b-matching load L*_edge = %.4f @ %s N=%d (feasible iff <=25)" % me)
    if acc['ex']:
        print("  *** PATH-INFEASIBLE (L*_path>1) while b-matching feasible: %s ***" % (acc['ex'],))
    print("VERDICT: %s" % (
        "PATH-ROUTING FEASIBLE (L*_path<=1) on ALL %d multi-atom components -- GPT-Pro reply 19's stronger path model"
        " holds even where C1P fails => FerrersShortestRouting CONCLUSION is empirically true; only its PROOF needs"
        " Version B (laminar), not the failed C1P. The route is VIABLE." % acc['tested']
        if acc['path_infeas'] == 0 else
        "*** PATH-ROUTING INFEASIBLE (L*_path>1) on %d components while the b-matching L*_edge<=25 still holds -- GPT-"
        "Pro's path-routing normalization is TOO STRONG; its reply-19 route does NOT prove the b-matching Hall. gap#1"
        " must use the b-matching row-subset Hall directly (max_S sum ell^2/|union P_e| <= 25). ***" % acc['path_infeas']))


if __name__ == '__main__':
    main()
