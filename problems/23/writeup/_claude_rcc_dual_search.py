r"""RCC DUAL-LP falsifier search + margin map (2026-07-08, Fable-5). GPT-Pro reply 3 Section 8: a decisive
falsifier = rational dual cert (alpha,beta,gamma,delta) with (D1) over the FULL cut family, (D2), strict (D3),
on a cage-legal config. Search method: solve the DUAL LP directly per config,

    val = max  Sum(alpha) - Sum_F(beta) - sigma*delta_door        [Door-only bank v1: kappa=sigma, I=all]
    s.t. (D1) for every cut U (full family, canonical v0 notin U),
         (D2) gamma_c <= delta_door  for all c in O,
         0 <= alpha_e <= 1 (normalization; dual cert scale-invariant),
         beta, gamma, delta >= 0.

val > 0  => dual certificate candidate => rationalize + EXACT-verify (D1/D2/D3, Fractions) => if verified and the
config is cage-legal (tri-free + genuine max cut), that is THE decisive falsifier (primal infeasible by compiled
weak duality). val <= 0 on real configs is FORCED if the cover+bank primal is feasible (my LP gate: 736/736).
THE INFORMATIVE OUTPUT on real configs: the MARGIN |val| -- how far the config is from carrying a dual cert.
Tight anchors (C5[t]; odd cycles are base-leaf not ell5-multi) should sit at margin ~0 via Sum(alpha)=Sum(beta);
the NEAR-TIGHT NON-extremal census configs expose the binding pattern that Lemma 3 (full_closure_bank_dominates_
dual) must exploit. Exact Fraction re-verify for any val > -1e-9. Run from problems/23/writeup.
"""
import subprocess, json
from itertools import combinations
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
from _h import dec, maxcut_all, Bconn, GENG, gmin
from _codex_k2t_switch_probe import adj_from_edges
from _claude_residual_hall_gate import geos_paths, residuals


def support_edges(adj, side, e):
    edges = set()
    for P in geos_paths(adj, side, e[0], e[1]):
        for i in range(len(P) - 1):
            a, b = P[i], P[i + 1]
            edges.add((min(a, b), max(a, b)))
    return frozenset(edges)


def sepf(U, e):
    return (e[0] in U) != (e[1] in U)


def dual_lp(name, n, adj, side, acc, maxn=12):
    if n > maxn:
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    ell = cd['ell']
    S = [e for e in cd['M'] if ell[e] == 5]
    if not S:
        return
    Pe = {e: support_edges(adj, side, e) for e in S}
    F = sorted(set().union(*Pe.values()))
    dB_all = sorted((a, b) for a in range(n) for b in adj[a] if a < b and side[a] != side[b])
    Fset = set(F)
    O = [c for c in dB_all if c not in Fset]
    m_all = len(cd['M'])
    sigma = len(dB_all) - m_all
    nS, nF, nO = len(S), len(F), len(O)
    # vars: alpha (nS), beta (nF), gamma (nO), delta_door (1)
    nv = nS + nF + nO + 1
    # objective: maximize sum(alpha) - sum(beta) - sigma*delta  -> minimize -(...)
    cvec = np.zeros(nv)
    cvec[:nS] = -1.0
    cvec[nS:nS + nF] = 1.0
    cvec[nS + nF + nO] = float(sigma)
    A_ub, b_ub = [], []
    # (D1) per cut U (canonical: 0 notin U)
    for r in range(1, n):
        for combo in combinations(range(1, n), r):
            U = frozenset(combo)
            row = np.zeros(nv)
            hit = False
            for i, e in enumerate(S):
                if sepf(U, e):
                    row[i] = 1.0; hit = True
            for i, c in enumerate(F):
                if sepf(U, c):
                    row[nS + i] = -1.0; hit = True
            for i, c in enumerate(O):
                if sepf(U, c):
                    row[nS + nF + i] = -1.0; hit = True
            if hit:
                A_ub.append(row); b_ub.append(0.0)
    # (D2) gamma_c - delta <= 0
    for i in range(nO):
        row = np.zeros(nv)
        row[nS + nF + i] = 1.0
        row[nS + nF + nO] = -1.0
        A_ub.append(row); b_ub.append(0.0)
    bounds = [(0, 1)] * nS + [(0, None)] * (nF + nO + 1)
    res = linprog(c=cvec, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method='highs')
    if not res.success:
        acc['lpfail'].append(name); return
    val = -float(res.fun)
    acc['n'] += 1
    rec = dict(name=name, n=n, S=nS, F=nF, O=nO, sigma=sigma, val=round(val, 9))
    acc['rows'].append(rec)
    if val > 1e-9:
        acc['positive'].append(rec)
        # exact re-verify candidate
        al = {S[i]: Fraction(res.x[i]).limit_denominator(10 ** 4) for i in range(nS)}
        be = {F[i]: Fraction(res.x[nS + i]).limit_denominator(10 ** 4) for i in range(nF)}
        ga = {O[i]: Fraction(res.x[nS + nF + i]).limit_denominator(10 ** 4) for i in range(nO)}
        de = Fraction(res.x[nS + nF + nO]).limit_denominator(10 ** 4)
        ok = exact_dual_check(n, S, F, O, sigma, al, be, ga, de)
        rec['exact_dual'] = ok
        if ok:
            acc['FALSIFIER'].append(rec)
            json.dump(dict(rec=rec, alpha={str(k): str(v) for k, v in al.items()},
                           beta={str(k): str(v) for k, v in be.items()},
                           gamma={str(k): str(v) for k, v in ga.items()}, delta=str(de)),
                      open('../../../tmp/claude_rcc_FALSIFIER_%s.json' % name.replace('/', '_'), 'w'), indent=1)
    if acc['tight'] is None or val < acc['tight'][1]:
        acc['tight'] = (name, val, nS, nF, nO, sigma)


def exact_dual_check(n, S, F, O, sigma, al, be, ga, de):
    for r in range(1, n):
        for combo in combinations(range(1, n), r):
            U = frozenset(combo)
            lhs = sum(al[e] for e in S if sepf(U, e))
            rhs = sum(be[c] for c in F if sepf(U, c)) + sum(ga[c] for c in O if sepf(U, c))
            if lhs > rhs:
                return False
    if any(g > de for g in ga.values()):
        return False
    return sum(al.values()) > sum(be.values()) + sigma * de


def c5t_build(t):
    n = 5 * t
    E = []
    for a in range(5):
        b = (a + 1) % 5
        for i in range(t):
            for j in range(t):
                u, w = a * t + i, b * t + j
                E.append((min(u, w), max(u, w)))
    adj = adj_from_edges(n, E)
    side = [0 if (v // t) in (0, 2, 4) else 1 for v in range(n)]
    return n, adj, side


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
    adj = adj_from_edges(11, E)
    side = [given[v] for v in V]
    return 11, adj, side


def main():
    acc = dict(n=0, rows=[], positive=[], FALSIFIER=[], lpfail=[], tight=None)
    print("RCC DUAL-LP search: val = max Sum(a)-Sum(b)-sigma*d | val>0 => falsifier candidate | margin map")
    print("=" * 100)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None or not Bconn(n, adj, best[0]):
                continue
            dual_lp('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cfgs %d, positives %d, FALSIFIERS %d, tightest %s"
              % (nn, acc['n'], len(acc['positive']), len(acc['FALSIFIER']),
                 ("%s val=%.6f" % (acc['tight'][0], acc['tight'][1])) if acc['tight'] else None), flush=True)
    for t in (1, 2):
        n, adj, side = c5t_build(t)
        dual_lp('C5[%d]' % t, n, adj, side, acc, maxn=12)
    n, adj, side = counterpattern11()
    dual_lp('CP11', n, adj, side, acc, maxn=12)
    print("=" * 100)
    named = [r for r in acc['rows'] if not r['name'].startswith('cen')]
    for r in named:
        print("   %-10s n=%-3d |S|=%-3d |F|=%-3d |O|=%-2d sigma=%-3d dual-val=%s" %
              (r['name'], r['n'], r['S'], r['F'], r['O'], r['sigma'], r['val']))
    vals = sorted(r['val'] for r in acc['rows'])
    print("TOTALS: %d configs | positives %d | EXACT FALSIFIERS %d | val range [%.6f, %.6f]"
          % (acc['n'], len(acc['positive']), len(acc['FALSIFIER']), vals[0], vals[-1]))
    print("TIGHTEST (closest to dual cert): %s val=%.9f (S=%d F=%d O=%d sigma=%d)" % acc['tight'])
    tight10 = sorted(acc['rows'], key=lambda r: r['val'])[:10]
    print("10 tightest configs (binding-pattern candidates for L3):")
    for r in tight10:
        print("   %-10s n=%-2d |S|=%-2d |F|=%-3d |O|=%-2d sigma=%-2d val=%.6f"
              % (r['name'], r['n'], r['S'], r['F'], r['O'], r['sigma'], r['val']))
    json.dump(acc, open('../../../tmp/claude_rcc_dual_search.json', 'w'), indent=1, default=str)
    print("VERDICT:", ("DUAL FALSIFIER FOUND -- exact-verified, decisive; see tmp/claude_rcc_FALSIFIER_*.json"
                       if acc['FALSIFIER'] else
                       "no dual certificate on any tested real config (margin map saved); consistent with "
                       "counterfactual-only binding; tightest configs above = L3 binding-pattern data"))


if __name__ == '__main__':
    main()
