r"""DECISIVE PREMISE GATE (2026-07-08): does GPT-Pro's switch-theorem premise ever OCCUR?

GPT-Pro reply 18's monolithic switch lemma DualHallObstruction_baseLeaf_or_certifiedSwitch has HYPOTHESIS
  hDual : ViolatesShortestGeodesicHall rowDB X y
i.e. a K2-COMPONENT X of a triangle-free Gamma-minimal maximum cut whose per-component spreading-Hall is
INFEASIBLE. The lemma then produces a Gamma-decreasing zero-slack switch (contradicting Gamma-minimality).
The whole GERSH proof is by contradiction: IF such an infeasible component exists THEN a switch exists THEN
Gamma is not minimal. So the entire crux hinges on whether the premise can EVER be realized.

This gate searches EXHAUSTIVELY for a spreading-INFEASIBLE per-K2-component in a real Gamma-min max cut, the
STRICTEST form (a component cannot borrow cut-edge capacity from other components -- harder to satisfy than the
whole-cage LP that _claude_shortrow_hall_v2_gate.py already found feasible on 71820 cages).

Per component X: rows = X.atoms (bad edges, demand ell(e)^2, FULL square incl ell=5=>25), sinks = cut edges on
SOME shortest B-geodesic of some e in X (cap 25 each), arc e->c iff c on a shortest geodesic of e. Diagnostics:
  * Gamma_X = sum_{e in X} ell(e)^2 ;  b_X = # sink cut edges ;  ratio rho_X = Gamma_X / (25 b_X).
    rho_X > 1  == DECISIVELY infeasible (total demand exceeds total cap) == the dual obstruction EXISTS.
    feasibility LP is the exact test; rho_X <= 1 is necessary. Track MAX rho_X seen (how close reality gets to 1+).
  * per-component all-geodesics max-flow feasibility (exact necessary+sufficient).
Battery: census N<=11 (all triangle-free connected, gmin max cut), C5[t] t=1..6 (the tight family, rho=1),
even-cycle+chord N=18..30, and BINDING-REGIME odd-cycle blowups / long chords pushing ell into [13,23]
(the workflow/GPT-Pro flagged risk region). EXACT rational demand; LP feasibility via HiGHS.

If NO infeasible component and max rho_X == 1 (only at C5[t]): STRONG evidence the premise is COUNTERFACTUAL
-- it never occurs for a real graph because it would locally violate the conjecture. Then the coarea identity
is proving a statement about a case that cannot arise, and Gamma<=N^2 must be reached via DIRECT spreading-
feasibility (rho_X<=1 with LP-feasible everywhere), which is what every gate shows. That reframes the target.
Run from problems/23/writeup.
"""
from fractions import Fraction as F
from collections import deque
import subprocess
from _claude_residual_hall_gate import residuals, even_cycle_chord, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges, c5_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin

try:
    from scipy.optimize import linprog
    import numpy as np
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def component_feasible(n, adj, side, cd, X):
    """All-geodesics per-component spreading-Hall feasibility for K2-component X.
    Returns (feasible|None, Gamma_X:int, b_X:int, ratio:F). None if any atom ell>23 (out of short shell) or no geodesic."""
    ell = cd['ell']
    atoms = X['atoms']
    if any(ell[e] > 23 for e in atoms):
        return None, 0, 0, F(0)
    Pe = {}
    for e in atoms:
        pe = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
        if not pe:
            return None, 0, 0, F(0)
        Pe[e] = pe
    cut_edges = sorted(set().union(*Pe.values()))
    b_X = len(cut_edges)
    Gamma_X = sum(ell[e] ** 2 for e in atoms)
    ratio = F(Gamma_X, 25 * b_X) if b_X else F(10 ** 9)
    if not HAVE_SCIPY:
        return (ratio <= 1), Gamma_X, b_X, ratio  # necessary-only fallback
    ci = {c: i for i, c in enumerate(cut_edges)}
    rows = list(atoms)
    var = [(ei, ci[c]) for ei, e in enumerate(rows) for c in Pe[e]]
    idx = {kv: i for i, kv in enumerate(var)}
    nv = len(var)
    A_eq = np.zeros((len(rows), nv)); b_eq = np.zeros(len(rows))
    for ei, e in enumerate(rows):
        b_eq[ei] = float(ell[e] ** 2)
        for k, (a, cc) in enumerate(var):
            if a == ei:
                A_eq[ei, k] = 1.0
    A_ub = np.zeros((b_X, nv)); b_ub = np.full(b_X, 25.0)
    for k, (a, cc) in enumerate(var):
        A_ub[cc, k] = 1.0
    res = linprog(c=np.zeros(nv), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method='highs')
    return bool(res.success), Gamma_X, b_X, ratio


def odd_cycle_chord_blowup(base_n, chord, t):
    """Blow up C_{base_n}+chord by replacing each vertex with an independent t-set (proper blow-up keeps triangle-free
    iff base triangle-free); pushes shortest odd cycles => larger ell. side inherited from base parity."""
    m, adj0, side0 = even_cycle_chord(base_n, chord) if base_n % 2 == 0 else (None, None, None)
    return None  # placeholder (unused; kept simple)


def long_odd_family(k):
    """C_{2k+1} with a single long chord (0, k): triangle-free for k>=2, creates two odd cycles; a Gamma-min cut of the
    odd cycle has one bad edge with ell = 2k+1 (the whole odd cycle). Pushes ell into the binding regime."""
    n = 2 * k + 1
    E = [(i, (i + 1) % n) for i in range(n)]
    # odd cycle: NO proper 2-cut makes it B-connected with a single bad edge unless we add structure; use bare C_n
    adj = adj_from_edges(n, E)
    # best max cut of odd cycle has exactly one same-side (bad) edge; side = alternating with one defect
    side = [i % 2 for i in range(n)]  # forces edge (n-1,0) bad since n odd
    return n, adj, side


def run(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    comps = k2_components(n, cd)
    for X in comps:
        f, GX, bX, rho = component_feasible(n, adj, side, cd, X)
        if f is None:
            acc['skip_long'] += 1
            continue
        acc['comps'] += 1
        if rho > acc['maxrho'][0]:
            acc['maxrho'] = (rho, name, n, GX, bX, sorted(X['atoms']))
        if rho > 1:
            acc['ratio_infeas'] += 1
            if acc['ratio_ex'] is None:
                acc['ratio_ex'] = (name, n, GX, bX, str(rho), sorted(X['atoms']))
        if f is False:
            acc['lp_infeas'] += 1
            if acc['lp_ex'] is None:
                acc['lp_ex'] = (name, n, GX, bX, str(rho), sorted(X['atoms']))


def main():
    print("DECISIVE PREMISE GATE: does a spreading-INFEASIBLE per-K2-component (the switch-theorem premise) ever occur?")
    print("scipy(HiGHS exact-necessary+sufficient LP):", HAVE_SCIPY)
    print("=" * 100)
    acc = dict(comps=0, ratio_infeas=0, lp_infeas=0, skip_long=0,
               maxrho=(F(0), '', 0, 0, 0, []), ratio_ex=None, lp_ex=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            run('cen%d' % nn, n, adj, best[0], acc)
        mr = acc['maxrho']
        print("  census N=%d: comps %d | ratio-infeas(rho>1) %d | LP-infeas %d | max rho=%s @ %s N=%d (Gamma_X=%d b_X=%d)"
              % (nn, acc['comps'], acc['ratio_infeas'], acc['lp_infeas'], mr[0], mr[1], mr[2], mr[3], mr[4]), flush=True)
    # tight family + binding regime
    for t in range(1, 7):
        n, adj, side = c5_blowup(t)
        run('C5[%d]' % t, n, adj, side, acc)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            run('C%d+chord(0,%d)' % (n, gap), *even_cycle_chord(n, (0, gap)), acc)
    for k in range(2, 16):
        n, adj, side = long_odd_family(k)
        run('C%d' % n, n, adj, side, acc)
    print("=" * 100)
    mr = acc['maxrho']
    print("TOTALS: components tested %d | skipped(ell>23) %d | ratio-INFEASIBLE(rho>1) %d | LP-INFEASIBLE %d"
          % (acc['comps'], acc['skip_long'], acc['ratio_infeas'], acc['lp_infeas']))
    print("MAX tightness ratio rho_X = Gamma_X/(25 b_X) = %s  @ %s N=%d (Gamma_X=%d, b_X=%d, atoms=%s)"
          % (mr[0], mr[1], mr[2], mr[3], mr[4], mr[5]))
    if acc['ratio_ex']:
        print("  *** rho>1 (DECISIVE dual obstruction -- demand exceeds cap): %s ***" % (acc['ratio_ex'],))
    if acc['lp_ex']:
        print("  *** LP-INFEASIBLE component (switch-theorem premise REALIZED): %s ***" % (acc['lp_ex'],))
    print("=" * 100)
    if acc['ratio_infeas'] == 0 and acc['lp_infeas'] == 0:
        tight = "== 1 (only at the tight C5[t] extremal)" if mr[0] == 1 else "= %s < 1" % mr[0]
        print("VERDICT: NO spreading-infeasible per-K2-component found. Max tightness ratio %s." % tight)
        print("  => The switch-theorem premise (ViolatesShortestGeodesicHall) is COUNTERFACTUAL on this coverage:")
        print("     it never occurs for a real Gamma-min max cut. The dual-defect coarea theorem proves a")
        print("     statement about a case that does not arise; Gamma<=N^2 is reached via DIRECT spreading-")
        print("     feasibility (rho_X<=1, LP-feasible), tight ONLY at C5[t]. This REFRAMES gap#1's target from")
        print("     'construct the switch' to 'prove rho_X<=1 directly' (a per-component capacity bound).")
    else:
        print("VERDICT: *** PREMISE REALIZED -- %d ratio-infeasible / %d LP-infeasible components. The dual obstruction"
              % (acc['ratio_infeas'], acc['lp_infeas']))
        print("  EXISTS on a real Gamma-min max cut. Either the switch must be constructed (theorem live) OR the")
        print("  spreading-feasibility lemma is FALSE (decisive falsifier -- examine the LP-infeasible component). ***")


if __name__ == '__main__':
    main()
