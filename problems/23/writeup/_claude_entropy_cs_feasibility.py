r"""CAUCHY-SCHWARZ FEASIBILITY probe for the ell=5 support-expansion claim |E_short(S)|>=|S|.

The assigned entropy strategy proves |E_short(S)| >= T^2/Q  (Cauchy-Schwarz), where
  T = sum_{e in S} |P_e|,  Q = sum_c d_S(c)^2,  d_S(c)=#{e in S: c in P_e}.
Cauchy-Schwarz CLOSES the claim for a subset S  iff  T^2/Q >= |S|, i.e.
  R(S) := T(S)^2 / ( Q(S) * |S| )  >= 1.
This gate measures, per K2-component (census N<=11 + C5[t]), the MINIMUM of R(S) over a
searched family of subsets S of ell=5 atoms (exhaustive for small #atoms, greedy descent for large),
alongside the ACTUAL min expansion ratio |E_short(S)|/|S|.  If min R(S) < 1 anywhere, the pure
Cauchy-Schwarz / second-moment route is INSUFFICIENT (cannot prove Hall) even though the claim holds.
EXACT integer arithmetic. Run from problems/23/writeup.
"""
import subprocess, random
from itertools import combinations
from fractions import Fraction
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges, c5_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def stats(subset, Pe):
    """Return (R = T^2/(Q*m), expansion = |E|/m) as Fractions, for subset (list of atoms)."""
    m = len(subset)
    dc = {}
    T = 0
    for e in subset:
        T += len(Pe[e])
        for c in Pe[e]:
            dc[c] = dc.get(c, 0) + 1
    Q = sum(d * d for d in dc.values())
    E = len(dc)
    R = Fraction(T * T, Q * m)
    return R, Fraction(E, m), E


def greedy_min_R(atoms, Pe, iters=4000, seed=0):
    """Local search to MINIMIZE R(S): start from full set, random add/drop moves keeping best."""
    rng = random.Random(seed)
    cur = list(atoms)
    bestR, _, _ = stats(cur, Pe)
    bestset = list(cur)
    inset = set(cur)
    for _ in range(iters):
        e = rng.choice(atoms)
        if e in inset:
            if len(inset) > 1:
                inset.discard(e)
        else:
            inset.add(e)
        if not inset:
            inset.add(e); continue
        R, _, _ = stats(list(inset), Pe)
        if R <= bestR:
            bestR = R; bestset = list(inset)
        else:
            # revert with prob to keep exploring: simple hill-climb, revert always
            if e in inset:
                inset.discard(e)
            else:
                inset.add(e)
    return bestR, bestset


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
        Pe = {}
        ok = True
        for e in five:
            p = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
            if not p:
                ok = False; break
            Pe[e] = set(p)
        if not ok:
            continue
        acc['comps'] += 1
        m = len(five)
        # TARGETED sunflower search: for each cut edge c, subset = atoms whose P_e contains c
        # (the theoretical Cauchy-Schwarz killer is a large star through one high-d(c) edge with small |P_e|)
        edge_atoms = {}
        for e in five:
            for c in Pe[e]:
                edge_atoms.setdefault(c, []).append(e)
        for c, sub in edge_atoms.items():
            if len(sub) >= 2:
                R, exp, E = stats(sub, Pe)
                if R < acc['global_minR'][0]:
                    acc['global_minR'] = (R, name + '/sunflower', len(sub), sorted(sub))
                if R < 1:
                    acc['CS_FAIL'].append((name + '/sunflower-edge', float(R), len(sub)))
                if E < len(sub):
                    acc['CLAIM_FAIL'].append((name + '/sunflower', sorted(sub)))
        # min R search
        if m <= 16:
            best = None; bestsub = None
            for r in range(1, m + 1):
                for sub in combinations(five, r):
                    R, exp, E = stats(list(sub), Pe)
                    if best is None or R < best:
                        best = R; bestsub = sub
                        if E < len(sub):
                            acc['CLAIM_FAIL'].append((name, sorted(sub)))
            minR = best
        else:
            minR, bestsub = greedy_min_R(five, Pe)
        # actual min expansion over same search (subset ratios)
        if minR < acc['global_minR'][0]:
            acc['global_minR'] = (minR, name, m, sorted(bestsub))
        if minR < 1:
            acc['CS_FAIL'].append((name, float(minR), m))
        # full-set R
        Rf, expf, Ef = stats(five, Pe)
        if Rf < acc['global_minRfull'][0]:
            acc['global_minRfull'] = (Rf, name, m)


def main():
    print("CAUCHY-SCHWARZ FEASIBILITY probe: does R(S)=T^2/(Q|S|) >= 1 hold (=> entropy route closes)?")
    print("=" * 100)
    acc = dict(comps=0, CS_FAIL=[], CLAIM_FAIL=[],
               global_minR=(Fraction(10**9), '', 0, None),
               global_minRfull=(Fraction(10**9), '', 0))
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            analyze('cen%d' % nn, n, adj, b[0], acc)
        gr, gn, gm, gs = acc['global_minR']
        print("  census N=%d done: comps=%d  min R(S) so far=%.4f (n atoms=%d)  #CS-fail subsets=%d  #CLAIM-fail=%d"
              % (nn, acc['comps'], float(gr), gm, len(acc['CS_FAIL']), len(acc['CLAIM_FAIL'])), flush=True)
    for t in range(1, 9):
        n, adj, side = c5_blowup(t)
        analyze('C5[%d]' % t, n, adj, side, acc)
        gr = acc['global_minR'][0]
        print("  C5[%d] done: comps=%d  min R(S) so far=%.4f  #CS-fail=%d" % (t, acc['comps'], float(gr), len(acc['CS_FAIL'])), flush=True)
    print("=" * 100)
    gr, gn, gm, gs = acc['global_minR']
    print("GLOBAL min R(S) over searched subsets = %s = %.5f   (component %s, %d atoms)" % (gr, float(gr), gn, gm))
    print("GLOBAL min R(full atom set) = %s = %.5f  (component %s, %d atoms)"
          % (acc['global_minRfull'][0], float(acc['global_minRfull'][0]), acc['global_minRfull'][1], acc['global_minRfull'][2]))
    print("VERDICT: Cauchy-Schwarz route %s" % ("CLOSES (R>=1 everywhere searched)" if gr >= 1 else "FAILS: found subset with R<1"))
    if acc['CS_FAIL']:
        print("  CS-fail witnesses (component, R, #atoms): %s" % acc['CS_FAIL'][:10])
    if acc['CLAIM_FAIL']:
        print("  *** CLAIM ITSELF FAILED (E<|S|): %s ***" % acc['CLAIM_FAIL'][:5])
    else:
        print("  (claim |E_short(S)|>=|S| held on every searched subset)")


if __name__ == '__main__':
    main()
