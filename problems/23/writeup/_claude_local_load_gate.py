r"""ANGLE c5t-extremal-stability: test the LOCAL per-cut-edge sufficient condition for ShortRowCutEdgeHall.

Uniform-spread relaxation: each bad row e spreads its demand ell^2 uniformly over its |P_e|=ell-1 canonical
geodesic cut edges => ell^2/(ell-1) per edge. If for EVERY cut edge c the total load
      LOAD(c) := sum_{e: c in P_e} ell(e)^2/(ell(e)-1)   <=   25,
then uniform spread is a feasible flow => Hall holds for A=M and (by restriction) for EVERY subset A.
So (L): "LOAD(c)<=25 for all c" is SUFFICIENT for the full subset-Hall Claim, and it is TIGHT at C5[t]
(all ell=5, ell^2/(ell-1)=25/4, exactly 4 rows per cut edge => LOAD=25).

DECISIVE QUESTION: is (L) actually TRUE on Gamma-min cages, or is it strictly stronger than Hall (i.e. does
LOAD(c)>25 occur somewhere while the max-flow Claim still holds)? If (L) holds everywhere, this angle is a
valid proof route (reduce Claim to the local geometric bound LOAD<=25). If (L) fails while Claim holds, the
angle's uniform-spread reduction is too strong and must be abandoned.

We use the SAME canonical geodesic as _claude_shortrow_hall_gate (BFS predecessor tree, one shortest cut path),
include ALL short rows ell in {5,7,...,23} with full demand ell^2. EXACT rational arithmetic. Run from problems/23/writeup.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals, even_cycle_chord
from _claude_shortrow_hall_gate import one_shortest_geodesic_edges, shortrow_hall
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def local_load(n, adj, side, cd):
    """Return (max_load, argmax_cutedge, per_edge_loads_dict, rows_info). Uses canonical BFS geodesic, all ell<=23 rows."""
    M, ell = cd['M'], cd['ell']
    rows = [e for e in M if 5 <= ell[e] <= 23]
    if not rows:
        return None
    if any(ell[e] > 23 for e in M):
        return 'LONG', None, None, None
    load = {}
    lam = {}
    for e in rows:
        ed = one_shortest_geodesic_edges(adj, side, e[0], e[1])
        if ed is None:
            return None
        w = F(ell[e] ** 2, ell[e] - 1)
        for c in ed:
            load[c] = load.get(c, F(0)) + w
            lam[c] = lam.get(c, 0) + 1
    if not load:
        return F(0), None, {}, {}
    cmax = max(load, key=lambda c: load[c])
    return load[cmax], cmax, load, lam


def check(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None:
        return
    res = local_load(n, adj, side, cd)
    if res is None:
        return
    if res == ('LONG', None, None, None):
        acc['long'] += 1
        return
    mx, cmax, load, lam = res
    acc['cages'] += 1
    if mx > 25:
        acc['local_fail'] += 1
        # cross-check: does the TRUE max-flow Claim still hold here?
        feas, detail = shortrow_hall(n, adj, side, cd)
        rec = (name, n, str(mx), lam.get(cmax), 'flow_feasible=%s' % feas)
        if acc['ex'] is None or (feas is not False):
            # prioritise: a local-fail where flow is still feasible => (L) strictly stronger
            if feas is not False and acc['ex_strong'] is None:
                acc['ex_strong'] = rec
        if feas is False and acc['ex_true'] is None:
            acc['ex_true'] = rec  # genuine Hall counterexample!
        if acc['ex'] is None:
            acc['ex'] = rec
    if mx == 25:
        acc['tight'] += 1


def main():
    acc = dict(cages=0, local_fail=0, tight=0, long=0, ex=None, ex_strong=None, ex_true=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            check('cen%d' % nn, n, adj, best[0], acc)
        print("  census N=%d: cages %d | LOCAL(L) fail(load>25) %d | tight(load==25) %d | long-skip %d"
              % (nn, acc['cages'], acc['local_fail'], acc['tight'], acc['long']), flush=True)
    for n in [18, 22, 26, 30]:
        for gap in range(4, n // 2 + 1):
            nn, adj, side = even_cycle_chord(n, (0, gap))
            check('C%d+chord(0,%d)' % (n, gap), nn, adj, side, acc)
    print("=" * 90)
    print("LOCAL LOAD GATE (angle c5t-extremal-stability): sufficient condition LOAD(c)=sum ell^2/(ell-1) <= 25")
    print("  cages %d | (L) fails (some LOAD>25): %d | tight cages (max LOAD==25): %d | long-atom skipped: %d"
          % (acc['cages'], acc['local_fail'], acc['tight'], acc['long']))
    if acc['ex_true']:
        print("   *** GENUINE HALL COUNTEREXAMPLE (flow infeasible): %s ***" % (acc['ex_true'],))
    if acc['ex_strong']:
        print("   NOTE: (L) is STRICTLY STRONGER than Hall here (LOAD>25 but flow feasible): %s" % (acc['ex_strong'],))
    if acc['ex']:
        print("   first local-fail: %s" % (acc['ex'],))
    if acc['local_fail'] == 0:
        print("VERDICT: (L) HOLDS on ALL %d cages -> uniform-spread is always feasible -> angle is a VALID proof route:"
              " Claim reduces to the local geometric bound 'at most 25 weighted load per cut edge', tight at C5[t]." % acc['cages'])
    else:
        print("VERDICT: (L) FAILS on %d cages. If ex_true is None, (L) is merely too-strong (angle needs the full flow, not"
              " uniform spread). If ex_true is set, that is a real counterexample to the Claim." % acc['local_fail'])


if __name__ == '__main__':
    main()
