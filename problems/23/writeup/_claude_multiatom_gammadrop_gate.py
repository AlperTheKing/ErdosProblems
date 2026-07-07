"""EXACT gate for MAIN's MultiAtomCoreRecutGammaDrop (gap #1 aggregation assembly lemma, 2026-07-07).

For every deficient-cap switch (sigma=0 == boundary_delta=0 zero-slack, positive-debt psi>0, deficient
terminal cage) on a B-connected maximum cut, MAIN claims the completed cage switch strictly decreases Gamma
and quantitatively:
    Gamma(B^U) - Gamma(B)  <=  - sum_{alpha in Active(C)} (L_alpha + 2)^2 ,   Active(C) nonempty.
Here Gamma(cut) = sum over bad edges f of ell(f)^2 (shortest-odd-cycle length squared); B^U = flip the side of
every vertex in the switch set U; Active(C) = the K2-support components carrying >=2 bad edges (the type-B L/(L+2)
cores), each contributing (L_alpha+2)^2 with L_alpha = the short odd length of that core.

This gate reuses the EXACT deficient-cap enumeration of _defcap_component_mine.py (same filters), then for each
such switch computes Gamma(B) and Gamma(B^U) via struct_for_side on the flipped side, identifies the active cores,
and checks BOTH: (E) strict decrease Gamma(B^U) < Gamma(B) [the essential Gamma-minimality contradiction] and
(Q) the quantitative bound Gamma(B^U)-Gamma(B) <= -sum(L_alpha+2)^2 [MAIN's exact claim]. EXACT Fraction only.
Battery: census N<=10 (+ optional glue). Any (E) violation would falsify the reduction (surface it).
Run from problems/23/writeup."""
import sys, subprocess
from collections import Counter
from fractions import Fraction as F
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _pl_gate import witness_structure
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset
from _bdef_construct import is_triangle_free
from _defcap_component_mine import k2_components


def gamma_of(st):
    M, ell = st[0], st[1]
    return sum(F(ell[f]) ** 2 for f in M)


def active_core_Ls(n, st, crossM):
    """Active(C) = K2-support components carrying >=2 bad edges (type-B L/(L+2) cores); L_alpha = short length."""
    M, ell, T, _mu, cyc = st
    K2 = build_K2(n, M, cyc)
    comps = k2_components(n, K2)
    Ls = []
    for comp in comps:
        V = set(comp)
        cin = [f for f in crossM if f[0] in V or f[1] in V]
        if len(cin) >= 2:
            Ls.append(min(ell[f] for f in cin))
    return Ls


def check_switch(n, adj, side, st, Sset, crossM, acc, name):
    side_U = [side[i] ^ (1 if i in Sset else 0) for i in range(n)]
    st_U = struct_for_side(n, adj, side_U)
    if st_U is None:
        acc['no_struct_U'] += 1
        return
    gB = gamma_of(st)
    gBU = gamma_of(st_U)
    dG = gBU - gB
    Ls = active_core_Ls(n, st, crossM)
    acc['switches'] += 1
    # --- TS-CTI structural check (MAIN's TerminalShadowCrossTermIsolation) ---
    # killed = old bad edges no longer bad (should be the length-7 old7, one per active core);
    # born = new bad edges (should be length-5 born5, one per active core);
    # stable = bad in both cuts (clause c: ell must be UNCHANGED = ell-locality).
    M_set = set(st[0]); ellB = st[1]; MU_set = set(st_U[0]); ellU = st_U[1]
    killed = [e for e in M_set if e not in MU_set]
    born = [e for e in MU_set if e not in M_set]
    stable = [e for e in M_set if e in MU_set]
    k = len(Ls)  # activeB57Count
    tscti_ok = True
    if len(killed) != k or len(born) != k:
        acc['tscti_count_fail'] += 1; tscti_ok = False
        if acc['ex_tscti'] is None:
            acc['ex_tscti'] = (name, n, 'k=%d killed=%d born=%d' % (k, len(killed), len(born)))
    if any(ellB[e] != 7 for e in killed):
        acc['tscti_killed_not7'] += 1; tscti_ok = False
        if acc['ex_tscti'] is None:
            acc['ex_tscti'] = (name, n, 'killed ell=%s' % sorted(ellB[e] for e in killed))
    if any(ellU[e] != 5 for e in born):
        acc['tscti_born_not5'] += 1; tscti_ok = False
        if acc['ex_tscti'] is None:
            acc['ex_tscti'] = (name, n, 'born ellU=%s' % sorted(ellU[e] for e in born))
    if any(ellB[e] != ellU[e] for e in stable):
        acc['tscti_stable_ell_changed'] += 1; tscti_ok = False  # clause (c) ell-locality FAIL
        if acc['ex_tscti'] is None:
            acc['ex_tscti'] = (name, n, 'stable ell changed: %s' % [(ellB[e], ellU[e]) for e in stable if ellB[e] != ellU[e]][:3])
    if tscti_ok:
        acc['tscti_pass'] += 1
    acc['dG_dist'][str(dG)] += 1
    acc['nactive_dist'][len(Ls)] += 1
    acc['dG_by_nactive'].setdefault(len(Ls), Counter())[str(dG)] += 1
    # (E) essential: strict Gamma decrease (Gamma-minimality contradiction)
    if dG < 0:
        acc['E_pass'] += 1
    elif dG == 0:
        acc['E_zero'] += 1
        if acc['ex_E'] is None:
            acc['ex_E'] = (name, n, 'dG=0', Ls)
    else:
        acc['E_fail'] += 1
        if acc['ex_E'] is None:
            acc['ex_E'] = (name, n, 'dG=%s>0' % dG, Ls)
    # (Q) MAIN's quantitative bound
    if not Ls:
        acc['active_empty'] += 1
        return
    # CORRECTED identity (MAIN 2026-07-07, gate-driven): per type-B L/(L+2) core the drop is
    # (L^2+(L+2)^2) - (L^2+L^2) = (L+2)^2 - L^2 = 4L+4 (= 24 for L=5). EXACT identity dG == -sum(4L+4).
    rhs = -sum(4 * F(L) + 4 for L in Ls)
    acc['Q_tested'] += 1
    if dG == rhs:
        acc['Q_pass'] += 1
    else:
        acc['Q_fail'] += 1
        if acc['ex_Q'] is None:
            acc['ex_Q'] = (name, n, 'dG=%s' % dG, 'rhs=%s' % rhs, 'Ls=%s' % Ls)


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            Sset = set(i for i in range(n) if (mask >> i) & 1)
            res = witness_structure(n, adj, side, st, Sset)
            if res is None:
                continue
            crossM, bdyB, wit = res
            if not crossM or not bdyB:
                continue
            witnesses = {e: set() for e in bdyB}
            for (f, e) in wit:
                witnesses[e].add(f)
            if any(not witnesses[e] for e in bdyB):
                continue
            psi = sum(ell[f] ** 2 for f in crossM) - sum(min(ell[f] for f in witnesses[e]) ** 2 for e in bdyB)
            if psi <= 0:
                continue
            det = {'cross_m': tuple(sorted(crossM)), 'bdy_b': tuple(sorted(bdyB)),
                   'witnesses': {e: tuple(sorted(witnesses[e])) for e in bdyB}}
            data = two_cap_data(det)
            if data is None:
                continue
            fset, _eset, exits_of_f, leaves = data
            if deficient_cap_subset(leaves, exits_of_f, fset) is None:
                continue
            acc['defcap'] += 1
            check_switch(n, adj, side, st, Sset, list(crossM), acc, name)


def new_acc():
    return dict(defcap=0, switches=0, no_struct_U=0, E_pass=0, E_zero=0, E_fail=0,
                Q_tested=0, Q_pass=0, Q_fail=0, active_empty=0, ex_E=None, ex_Q=None,
                dG_dist=Counter(), nactive_dist=Counter(), dG_by_nactive={},
                tscti_pass=0, tscti_count_fail=0, tscti_killed_not7=0, tscti_born_not5=0,
                tscti_stable_ell_changed=0, ex_tscti=None)


def report(label, acc):
    print('=' * 66)
    print('BATTERY:', label, '| deficient switches:', acc['defcap'], '| checked:', acc['switches'])
    print('  no_struct_U (flip not a valid struct):', acc['no_struct_U'])
    print('  (E) STRICT Gamma DECREASE: pass=%d  dG==0=%d  dG>0(FAIL)=%d  ex=%s'
          % (acc['E_pass'], acc['E_zero'], acc['E_fail'], acc['ex_E'] or ''))
    print('  (Q) MultiAtomCoreRecutGammaDrop bound: tested=%d pass=%d FAIL=%d  active_empty=%d  ex=%s'
          % (acc['Q_tested'], acc['Q_pass'], acc['Q_fail'], acc['active_empty'], acc['ex_Q'] or ''))
    print('  dG distribution (global Gamma drop):', dict(acc['dG_dist']))
    print('  |Active(C)| distribution:', dict(acc['nactive_dist']))
    print('  dG by |Active|:', {k: dict(v) for k, v in acc['dG_by_nactive'].items()})
    print('  (TS-CTI) structural isolation: pass=%d  count_fail=%d killed_not7=%d born_not5=%d stable_ell_CHANGED=%d  ex=%s'
          % (acc['tscti_pass'], acc['tscti_count_fail'], acc['tscti_killed_not7'], acc['tscti_born_not5'],
             acc['tscti_stable_ell_changed'], acc['ex_tscti'] or ''))
    E_ok = acc['E_fail'] == 0 and acc['E_zero'] == 0 and acc['switches'] > 0
    Q_ok = acc['Q_fail'] == 0 and acc['Q_tested'] > 0
    T_ok = (acc['tscti_count_fail'] == 0 and acc['tscti_killed_not7'] == 0 and acc['tscti_born_not5'] == 0
            and acc['tscti_stable_ell_changed'] == 0 and acc['tscti_pass'] > 0)
    print('VERDICT: (E) strict-decrease %s ; (Q) exact-identity %s ; (TS-CTI) structural %s'
          % ('PASS' if E_ok else 'CHECK', 'PASS' if Q_ok else 'CHECK', 'PASS' if T_ok else 'CHECK'))


def census(maxn):
    acc = new_acc()
    for nn in range(5, maxn + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            scan_graph('cen%d' % nn, n, E, acc)
        print('  census N=%d done: defcap=%d E_fail=%d E_zero=%d Q_fail=%d'
              % (nn, acc['defcap'], acc['E_fail'], acc['E_zero'], acc['Q_fail']), flush=True)
    report('CENSUS N<=%d' % maxn, acc)


def glue_single(k):
    """core (I?AEBAwF_) + a single C_k baggage cycle, all cut-bridges. Rich in deficient caps."""
    from _h import dec as _dec
    cn, cE = _dec('I?AEBAwF_')
    cyc = [(cn + i, cn + (i + 1) % k) for i in range(k)]
    acc = new_acc()
    for a in range(cn):
        for b in range(cn, cn + k):
            E = list(cE) + cyc + [(a, b)]
            if is_triangle_free(cn + k, E):
                scan_graph('g%d-%d' % (a, b), cn + k, E, acc)
    report('GLUE core + C%d (all bridges)' % k, acc)


def glue_multi(sizes):
    from _h import dec as _dec
    cn, cE = _dec('I?AEBAwF_')
    E = list(cE); n = cn; bridges = []
    for j, k in enumerate(sizes):
        E += [(n + i, n + (i + 1) % k) for i in range(k)]
        bridges.append((j % cn, n)); n += k
    E += bridges
    acc = new_acc()
    if is_triangle_free(n, E):
        scan_graph('multi', n, E, acc)
        report('GLUE core + %s' % ('+'.join('C%d' % s for s in sizes)), acc)
    else:
        print('GLUE %s: not triangle-free' % sizes)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'glue':
        spec = [int(x) for x in sys.argv[2].split(',')]
        if len(spec) == 1:
            glue_single(spec[0])
        else:
            glue_multi(spec)
    else:
        maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 9
        census(maxn)


if __name__ == '__main__':
    main()
