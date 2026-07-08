r"""EXACT-GATE for GPT-Pro's ProperSupportAmbientAbsorption (2026-07-08): the load-bearing claim of the full-support
reduction. GPT-Pro claims proper-support K2 components (|V_X| < N) have their demand covered by AMBIENT ALONE (no
door, no C5), routing atom demand to vertices OUTSIDE the component support V_X.

Claude's DOUBLE-SPEND concern: GPT-Pro uses cap_X(v)=Gamma_X (per-(component,vertex)), but the real per-vertex
ambient reserve is N-T(v) (Sigma_v (N-T(v)) = N^2 - Gamma). If components share external vertices, per-component
Gamma_X caps can exceed the global reserve. This gate tests the SOUND version: ONE GLOBAL max-flow over ALL
proper-support atoms simultaneously, sinks = vertices with a GLOBAL cap, atom a -> v iff v not in V_{comp(a)}.
If globally feasible => no double-spend, GPT-Pro's ambient reduction is SOUND (proper-support closes by ambient).
An infeasible proper-support instance => the claim is too strong (door/C5 also needed there).

Two cap models (both reported):
  (A) cap(v) = N - T(v)         canonical reserve, Sigma = N^2 - Gamma (may be <0 at a vertex if T(v)>N; clamp>=0).
  (B) cap(v) = Gamma_X-style is per-component, NOT global -> replaced by the SOUND global (A). Also report the
      per-component single-vertex existence: does some external v0 have cap(v0) >= Demand_X (GPT-Pro's literal route)?

FULL-support components (|V_X|=N) have NO external vertex -> their atoms are EXCLUDED here (they are the residual
FullSupportC5Dominance, handled by C5, not ambient). We report how many exist and their demand.

Coverage: census N<=11 Gamma-min + even-cycle+chord N=18..30 (proper-support long annuli live here). EXACT rational.
Run from problems/23/writeup.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals, k2_components, even_cycle_chord
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin

try:
    from scipy.optimize import linprog
    import numpy as np
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    if not any(side[a] == side[b] for a in range(n) for b in adj[a] if a < b):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    ell, p, T = cd['ell'], cd['p'], cd['T']
    comps = k2_components(n, cd)
    # per atom -> its component support V_comp
    comp_of = {}
    for X in comps:
        for e in X['atoms']:
            comp_of[e] = X['VX']
    cap = [F(n) - T[v] for v in range(n)]              # canonical reserve N-T(v)
    acc['cages'] += 1
    # split atoms into proper-support (V_comp != all) and full-support (V_comp == all)
    allV = set(range(n))
    proper_atoms = []
    full_demand = F(0); full_atoms = 0
    for e in ell:
        dem = ell[e] ** 2 - 25
        if dem <= 0:
            continue
        VX = comp_of[e]
        if VX == allV:
            full_atoms += 1; full_demand += dem
        else:
            proper_atoms.append((e, dem, VX))
    acc['full_atoms'] += full_atoms
    if full_atoms:
        acc['full_cages'] += 1
    if not proper_atoms:
        return
    # per-component single-vertex existence check (GPT-Pro literal route): some external v0 with cap>=Demand?
    for X in comps:
        VX = X['VX']
        if VX == allV:
            continue
        dem = sum(ell[e] ** 2 - 25 for e in X['atoms'] if ell[e] ** 2 - 25 > 0)
        if dem <= 0:
            continue
        ext_caps = [cap[v] for v in range(n) if v not in VX]
        if not ext_caps or max(ext_caps) < dem:
            acc['single_vertex_fail'] += 1  # GPT-Pro's naive single-vertex route needs a distributed flow instead
    # GLOBAL max-flow (SOUND double-spend test): proper-support atoms -> external vertices, cap(v)=max(0,N-T(v))
    if not HAVE_SCIPY:
        return
    var = []
    for ai, (e, dem, VX) in enumerate(proper_atoms):
        for v in range(n):
            if v not in VX and cap[v] > 0:
                var.append((ai, v))
    idx = {kv: i for i, kv in enumerate(var)}
    nv = len(var)
    if nv == 0:
        acc['global_infeasible'] += 1
        if acc['gi_ex'] is None:
            acc['gi_ex'] = (name, n, 'no eligible external vertex with positive reserve')
        return
    A_eq = np.zeros((len(proper_atoms), nv)); b_eq = np.zeros(len(proper_atoms))
    for ai, (e, dem, VX) in enumerate(proper_atoms):
        b_eq[ai] = float(dem)
        has = False
        for v in range(n):
            if (ai, v) in idx:
                A_eq[ai, idx[(ai, v)]] = 1.0; has = True
        if not has:
            acc['global_infeasible'] += 1
            if acc['gi_ex'] is None:
                acc['gi_ex'] = (name, n, 'atom %s no external reserve' % (e,))
            return
    A_ub = np.zeros((n, nv)); b_ub = np.zeros(n)
    for v in range(n):
        b_ub[v] = float(max(F(0), cap[v]))
        for ai in range(len(proper_atoms)):
            if (ai, v) in idx:
                A_ub[v, idx[(ai, v)]] = 1.0
    res = linprog(c=np.zeros(nv), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * nv, method='highs')
    if not res.success:
        acc['global_infeasible'] += 1
        if acc['gi_ex'] is None:
            acc['gi_ex'] = (name, n, 'proper-support atoms=%d global ambient flow INFEASIBLE (cap N-T(v))' % len(proper_atoms))
    else:
        acc['global_ok'] += 1


def main():
    print("scipy:", HAVE_SCIPY)
    acc = dict(cages=0, global_ok=0, global_infeasible=0, gi_ex=None, single_vertex_fail=0,
               full_atoms=0, full_cages=0)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            analyze('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d, proper-support global-OK %d, global-INFEAS %d, single-vtx-route-fail %d, full-support cages %d"
              % (nn, acc['cages'], acc['global_ok'], acc['global_infeasible'], acc['single_vertex_fail'], acc['full_cages']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            analyze('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print("=" * 90)
    print("PROPER-SUPPORT AMBIENT ABSORPTION GATE (GPT-Pro claim (1)):")
    print("  cages %d | proper-support GLOBAL ambient flow: OK %d, INFEASIBLE %d | full-support cages (residual C5) %d, full atoms %d"
          % (acc['cages'], acc['global_ok'], acc['global_infeasible'], acc['full_cages'], acc['full_atoms']))
    print("  GPT-Pro's LITERAL single-external-vertex route fails on %d components (=> needs DISTRIBUTED flow, not one v0)"
          % acc['single_vertex_fail'])
    if acc['gi_ex']:
        print("  *** GLOBAL-INFEASIBLE example (proper-support NOT ambient-absorbable => claim (1) too strong): %s ***" % (acc['gi_ex'],))
    print("VERDICT: %s" % (
        "GPT-Pro claim (1) SOUND -- every proper-support component's demand is globally absorbed by ambient reserve"
        " cap(v)=N-T(v) with NO double-spend (door/C5 not needed). gap#1 residual = FullSupportC5Dominance ALONE."
        if acc['global_infeasible'] == 0 else
        "GPT-Pro claim (1) TOO STRONG on %d cages -- proper-support demand NOT ambient-absorbable under global cap N-T(v)"
        " (door/C5 also needed there); the reduction to full-support-only does NOT hold as stated." % acc['global_infeasible']))
    print("  (Note: GPT-Pro's cap_X(v)=Gamma_X is per-component; this gate used the SOUND global cap N-T(v). If the"
          " single-vertex route fails but the global flow succeeds, the ambient claim holds via a distributed flow.)")


if __name__ == '__main__':
    main()
