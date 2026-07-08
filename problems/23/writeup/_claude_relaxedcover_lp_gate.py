r"""RELAXED CUT-COVER LP gate (2026-07-08, Fable-5). Exact-gate GPT-Pro's relaxed-cover mechanism
(GAP1_SSE_RELAXEDCUTCOVER_GPTPRO.md; Lean soundness compiled in RelaxedCutCover.lean).

For each real config (census tri-free Gamma-min max cuts N<=9, C18+chord family, C5[t] t=1..3, the 11-vtx
escaping-atom max-cut counterpattern): S = ell=5 atoms, F = E_short(S) (multi-geodesic supports), X = other cut
edges. Relaxed-cover LP over the FULL cut family (subsets U not containing v0, N<=15):
    min externalLoad = sum_{c in X} load(c)   s.t.  coverage(e) >= 1 (e in S),  congestion(c) <= 1 (c in F).
Float LP (scipy highs) = annotation; then EXACT certificates:
  (a) rationalized LP solution, Fraction-checked (coverage/congestion/load) -- exact cert when it verifies;
  (b) the SINGLETON HALF-COVER (lambda_v = 1/2 for all v): ALWAYS exact-valid (coverage=1, congestion=1),
      exact load = |X|; Door-fit <=> |X| <= sigma <=> m_all <= |F|.
Key diagnostics per config: L*_float, exact cert load, sigma = |deltaB| - m_all (Door capacity in edge units),
DOORFIT (L* <= sigma?), and the list of configs needing beyond-Door bank. If DOORFIT holds everywhere real,
the existence-theorem bank plausibly reduces to Door-only (construction hint for GPT-Pro); failures pinpoint
which configs consume vertexSlack/base/prune. Counterfactual caveat: real graphs never have Hall defect, so this
is consistency annotation + construction-shape data, NEVER proof. Run from problems/23/writeup.
"""
import subprocess, json, sys
from itertools import product, combinations
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
from _h import dec, maxcut_all, Bconn, GENG, gmin
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import geos_paths, residuals, even_cycle_chord


def support_edges(adj, side, e):
    edges = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            edges.add((min(a, b), max(a, b)))
    return frozenset(edges)


def cut_edges(n, adj, side):
    return sorted((a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b])


def sep(U, e):
    return (e[0] in U) != (e[1] in U)


def in_dB(U, c):
    return (c[0] in U) != (c[1] in U)


def solve_config(name, n, adj, side, acc, maxfull=15):
    cd = residuals(n, adj, side)
    if cd is None:
        return
    ell = cd['ell']
    S = [e for e in cd['M'] if ell[e] == 5]
    if not S:
        acc['noS'] += 1
        return
    Pe = {e: support_edges(adj, side, e) for e in S}
    F = sorted(set().union(*Pe.values()))
    dB_all = cut_edges(n, adj, side)
    Fset = set(F)
    X = [c for c in dB_all if c not in Fset]
    m_all = len(cd['M'])
    sigma = len(dB_all) - m_all
    # cut family: all subsets avoiding vertex 0 (canonical) -- 2^(n-1)-1 columns
    if n - 1 > maxfull - 1:
        return
    cuts = []
    verts = list(range(1, n))
    for r in range(1, n):
        for combo in combinations(verts, r):
            cuts.append(frozenset(combo))
    nU = len(cuts)
    # LP data
    cost = np.array([sum(1.0 for c in X if in_dB(U, c)) for U in cuts])
    A_ub, b_ub = [], []
    for e in S:
        A_ub.append([-1.0 if sep(U, e) else 0.0 for U in cuts]); b_ub.append(-1.0)
    for c in F:
        A_ub.append([1.0 if in_dB(U, c) else 0.0 for U in cuts]); b_ub.append(1.0)
    res = linprog(c=cost, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)] * nU, method='highs')
    acc['cfgs'] += 1
    if not res.success:
        # relaxed cover is ALWAYS feasible (singleton half-cover) => a solver failure is numeric, flag it
        acc['lpfail'].append(name)
        return
    Lstar = float(res.fun)
    # exact certificate from the LP solution (rationalize + Fraction check; scale-up if coverage dips)
    lam = {}
    for k, v in enumerate(res.x):
        if v > 1e-9:
            lam[cuts[k]] = Fraction(v).limit_denominator(10 ** 4)
    exact_ok, exact_load = exact_check(lam, S, F, X)
    # singleton half-cover: exact load = |X| always
    half = Fraction(1, 2)
    singleton_load = Fraction(len(X))
    doorfit_lp = (exact_ok and exact_load <= sigma)
    doorfit_single = (singleton_load <= sigma)
    rec = dict(name=name, n=n, S=len(S), F=len(F), X=len(X), m_all=m_all, sigma=sigma,
               Lfloat=round(Lstar, 6), exact_ok=exact_ok,
               exact_load=str(exact_load) if exact_ok else None,
               doorfit_lp=bool(doorfit_lp), doorfit_single=bool(doorfit_single),
               strict=bool(Lstar < 1e-9))
    acc['rows'].append(rec)
    if Lstar < 1e-9:
        acc['strict0'] += 1
    if exact_ok:
        acc['exact'] += 1
        if not doorfit_lp:
            acc['beyond_door'].append(rec)
    else:
        acc['inexact'].append(name)
    if not doorfit_single:
        acc['single_overflow'].append(rec)


def exact_check(lam, S, F, X):
    """Fraction-exact verify of a rationalized cover; auto-rescale if coverage dips below 1."""
    if not lam:
        return False, None
    covmin = None
    for e in S:
        cov = sum(w for U, w in lam.items() if sep(U, e))
        covmin = cov if covmin is None else min(covmin, cov)
    if covmin is None or covmin <= 0:
        return False, None
    scale = Fraction(1) if covmin >= 1 else Fraction(1) / covmin
    for c in F:
        cong = sum(w for U, w in lam.items() if in_dB(U, c)) * scale
        if cong > 1:
            return False, None
    load = sum(sum(w for U, w in lam.items() if in_dB(U, c)) for c in X) * scale
    return True, load


def c5t(t):
    """C5[t] blowup: classes K0..K4 of size t, complete bipartite between consecutive classes.
    Cut = class pattern A,B,A,B,A (classes 0,2,4 red; 1,3 blue) -- verify max + Gamma-min by brute force."""
    n = 5 * t
    cls = lambda v: v // t
    E = []
    for a in range(5):
        b = (a + 1) % 5
        for i in range(t):
            for j in range(t):
                u, w = a * t + i, b * t + j
                E.append((min(u, w), max(u, w)))
    adj = adj_from_edges(n, E)
    best = gmin(n, adj, maxcut_all(n, adj))
    return n, adj, best[0]


def counterpattern11():
    V = ['p', 'q', 'a', 'b', 'bb', 'c', 'y', 'w', 'r1', 'r2', 'r3']
    idx = {v: i for i, v in enumerate(V)}
    given = {v: 0 for v in ['p', 'q', 'b', 'bb', 'y', 'w', 'r2']}
    for v in ['a', 'c', 'r1', 'r3']:
        given[v] = 1
    B = [('p', 'a'), ('a', 'b'), ('b', 'c'), ('c', 'y'), ('q', 'c'), ('c', 'bb'), ('bb', 'a'),
         ('a', 'w'), ('p', 'r1'), ('r1', 'r2'), ('r2', 'r3'), ('r3', 'q')]
    M = [('p', 'y'), ('q', 'w'), ('p', 'q')]
    E = [(min(idx[u], idx[w]), max(idx[u], idx[w])) for u, w in B + M]
    n = 11
    adj = adj_from_edges(n, E)
    side = [given[v] for v in V]
    return n, adj, side


def main():
    acc = dict(cfgs=0, noS=0, strict0=0, exact=0, rows=[], lpfail=[], inexact=[],
               beyond_door=[], single_overflow=[])
    print("RELAXED CUT-COVER LP gate: min externalLoad + exact certs + Door-fit, per real config")
    print("=" * 100)
    # 1. census
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            if not Bconn(n, adj, best[0]):
                continue
            solve_config('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d done: cfgs %d, strict(L*=0) %d, exact-certs %d, beyond-Door %d"
              % (nn, acc['cfgs'], acc['strict0'], acc['exact'], len(acc['beyond_door'])), flush=True)
    # 2. C18 + chord family: needs a structured family (2^17 full columns too heavy) -- v2; skipped in v1.
    # 3. C5[t]
    for t in [1, 2, 3]:
        n, adj, side = c5t(t)
        solve_config('C5[%d]' % t, n, adj, side, acc)
        print("  C5[%d] done" % t, flush=True)
    # 4. the 11-vtx escaping-atom max-cut counterpattern (full closure realized)
    n, adj, side = counterpattern11()
    solve_config('CP11-escaping', n, adj, side, acc)
    print("=" * 100)
    print("TOTALS: configs %d (noS skipped %d) | strict L*=0: %d | exact certs %d (inexact %d) | LP fails %d"
          % (acc['cfgs'], acc['noS'], acc['strict0'], acc['exact'], len(acc['inexact']), len(acc['lpfail'])))
    print("SINGLETON half-cover overflow (|X| > sigma <=> m_all > |F|): %d" % len(acc['single_overflow']))
    for r in acc['single_overflow'][:10]:
        print("   ", r)
    print("BEYOND-DOOR (exact LP-cert load > sigma): %d" % len(acc['beyond_door']))
    for r in acc['beyond_door'][:10]:
        print("   ", r)
    named = [r for r in acc['rows'] if not r['name'].startswith('cen')]
    print("named configs:")
    for r in named:
        print("   %-18s n=%-3d |S|=%-3d |F|=%-3d |X|=%-3d m=%-3d sigma=%-3d L*=%-9s exact=%s doorfitLP=%s single-doorfit=%s strict=%s"
              % (r['name'], r['n'], r['S'], r['F'], r['X'], r['m_all'], r['sigma'], r['Lfloat'],
                 r['exact_load'], r['doorfit_lp'], r['doorfit_single'], r['strict']))
    with open('../../../tmp/claude_relaxedcover_lp_gate.json', 'w') as f:
        json.dump(acc, f, indent=1, default=str)
    doorfit_all = (len(acc['beyond_door']) == 0 and acc['exact'] == acc['cfgs'] - len(acc['lpfail']))
    print("VERDICT: %s" % (
        "min-load relaxed covers exist with EXACT certificates and fit the DOOR bank alone on ALL %d configs "
        "=> Door-only absorption is the construction target (annotation, counterfactual caveat)." % acc['cfgs']
        if doorfit_all and acc['cfgs'] else
        "beyond-Door configs exist (%d) or inexact certs (%d) -- vertexSlack/base/prune genuinely needed; "
        "list above feeds GPT-Pro's construction." % (len(acc['beyond_door']), len(acc['inexact']))))


if __name__ == '__main__':
    main()
