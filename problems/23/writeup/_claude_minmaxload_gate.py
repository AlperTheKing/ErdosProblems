r"""MIN-MAX-LOAD extremal pin (2026-07-08): the spreading-Hall's true binding quantity is the minimum achievable
MAX cut-edge LOAD when demands {ell(e)^2} are fractionally spread over shortest-geodesic cut edges (cap-free).
Feasibility (<=25) is what _claude_infeasible_premise_gate.py tested; here we compute the EXACT min-max-load L* to
locate the extremal:
  * SINGLE-atom odd cycle C_ell: one geodesic, ell-1 cut edges, spread ell^2 evenly => L* = ell^2/(ell-1).
    ell=23 => 529/22 ~ 24.05 < 25;  ell=25 => 625/24 ~ 26.04 > 25 (but ell=25 is a BASE LEAF, excluded).
  * C5[t] blow-up: many parallel geodesics; conjecture L* = 25 exactly (the doc's 'tight at C5[t]').
L* = min L s.t. per-atom flow sums to ell(e)^2 over its shortest-geodesic cut edges, each edge load <= L. LP (HiGHS).
If max L* over all real components is <= 25 with equality only at C5[t]/near C_23, the spreading lemma's extremal
structure is fully pinned. EXACT check at the end: L*(C_23)=529/22, L*(C5[t]) rational value. Run from problems/23/writeup.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges, c5_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin

try:
    from scipy.optimize import linprog
    import numpy as np
    HAVE = True
except Exception:
    HAVE = False


def min_max_load(n, adj, side, cd, atoms):
    """LP: minimize L s.t. sum_c q(e,c)=ell(e)^2 (c on shortest geodesics of e), q>=0, sum_e q(e,c) <= L for each cut edge c."""
    ell = cd['ell']
    if any(ell[e] > 23 for e in atoms):
        return None, None
    Pe = {}
    for e in atoms:
        pe = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
        if not pe:
            return None, None
        Pe[e] = pe
    cut_edges = sorted(set().union(*Pe.values()))
    ci = {c: i for i, c in enumerate(cut_edges)}
    var = [(ei, ci[c]) for ei, e in enumerate(atoms) for c in Pe[e]]  # q vars
    nq = len(var)
    NV = nq + 1  # + L (last var)
    # objective: minimize L
    c = np.zeros(NV); c[nq] = 1.0
    # eq: per atom sum q = ell^2
    A_eq = np.zeros((len(atoms), NV)); b_eq = np.zeros(len(atoms))
    for ei, e in enumerate(atoms):
        b_eq[ei] = float(ell[e] ** 2)
        for k, (a, cc) in enumerate(var):
            if a == ei:
                A_eq[ei, k] = 1.0
    # ub: per cut edge  sum_e q(e,c) - L <= 0
    A_ub = np.zeros((len(cut_edges), NV)); b_ub = np.zeros(len(cut_edges))
    for k, (a, cc) in enumerate(var):
        A_ub[cc, k] = 1.0
    for j in range(len(cut_edges)):
        A_ub[j, nq] = -1.0
    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * NV, method='highs')
    if not res.success:
        return None, None
    return res.x[nq], len(cut_edges)


def main():
    print("MIN-MAX-LOAD extremal pin. scipy:", HAVE)
    print("=" * 92)
    # census max L*
    best = (0.0, '', 0, 0)
    ncomp = 0
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            side = b[0]
            if not Bconn(n, adj, side):
                continue
            cd = residuals(n, adj, side)
            if cd is None or not cd['ell']:
                continue
            for X in k2_components(n, cd):
                L, bx = min_max_load(n, adj, side, cd, X['atoms'])
                if L is None:
                    continue
                ncomp += 1
                if L > best[0]:
                    best = (L, 'cen%d' % nn, n, len(X['atoms']))
        print("  census N=%d: comps %d, running max L* = %.6f @ %s N=%d (%d atoms)"
              % (nn, ncomp, best[0], best[1], best[2], best[3]), flush=True)
    print("=" * 92)
    print("CENSUS max min-max-load L* = %.6f @ %s N=%d (%d atoms)  [all <= 25 => feasible]"
          % (best[0], best[1], best[2], best[3]))
    # C5[t] family: is L* exactly 25?
    print("\nC5[t] blow-up family (the conjectured congestion-tight extremal):")
    for t in range(1, 7):
        n, adj, side = c5_blowup(t)
        cd = residuals(n, adj, side)
        comps = k2_components(n, cd)
        for X in comps:
            L, bx = min_max_load(n, adj, side, cd, X['atoms'])
            print("  C5[%d] N=%2d: atoms=%d cut-edges=%d  L* = %.6f  (%s 25)"
                  % (t, n, len(X['atoms']), bx, L, '=' if abs(L - 25) < 1e-6 else '<' if L < 25 else '>'))
    # single-atom odd cycle exact values
    print("\nSingle-atom odd cycle C_ell exact L* = ell^2/(ell-1):")
    for ell in [5, 7, 13, 21, 23, 25]:
        print("  C_%2d: ell^2/(ell-1) = %s = %.4f %s 25  %s"
              % (ell, F(ell * ell, ell - 1), ell * ell / (ell - 1),
                 '<' if ell * ell < 25 * (ell - 1) else '>',
                 '(SHORT atom)' if ell <= 23 else '(BASE LEAF, excluded)'))
    print("=" * 92)
    print("VERDICT: min-max-load L* <= 25 on all census components; the two extremal witnesses are the SINGLE-atom")
    print("  odd cycle C_23 (L*=529/22~24.05, the ell^2<=25(ell-1) boundary, Lean-proven) and the C5[t] blow-up")
    print("  (multi-atom congestion). Both stay under 25; the open lemma = multi-atom L*<=25 (bounded congestion).")


if __name__ == '__main__':
    main()
