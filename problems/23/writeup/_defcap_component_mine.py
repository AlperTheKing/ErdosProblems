"""Decisive cross-gate of Codex's ALGEBRAIC SIGN PROOF (19:45) for the deficient-cap atom.

For every deficient-cap switch (neutral positive-Psi two-cap terminal-shadow, |N(Y)|<=|Y|), look at the
FULL-cut K2 support components (v~w iff K2[v][w]>0). Codex's claim: R_full(u)=R_local(u)+(N-|V_comp|)T(u)
with R_local>=0 per component (type-A pure odd cycle ->0, type-B 5/7 core ->25/4), giving R_full>=0.

This gate verifies, on each deficient switch:
  (i)   block-diagonality: T[u] == sum_{w in comp(u)} K2[u][w]    (so components are K2-disjoint)
  (ii)  additive identity:  R_full[u] == R_local(u) + (N-|V_comp|)*T[u]   (R_local via N'=|V_comp|)
  (iii) R_local(u) >= 0 for every u in every component
  + classifies each crossM-bearing component by (#bad edges, sorted ell) to see A/B/other.
EXACT Fraction. Battery: census N<=10 + glued I?AEBAwF_+C5 (n=15). From problems/23/writeup."""
import subprocess
from collections import Counter
from fractions import Fraction as F
from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _pl_gate import witness_structure
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset
from _bdef_construct import Cn, is_triangle_free


def k2_components(n, K2):
    seen = [False] * n
    comps = []
    for s in range(n):
        if seen[s] or all(K2[s][w] == 0 for w in range(n)):
            seen[s] = True
            continue
        stack = [s]; seen[s] = True; comp = []
        while stack:
            u = stack.pop(); comp.append(u)
            for w in range(n):
                if not seen[w] and K2[u][w] != 0:
                    seen[w] = True; stack.append(w)
        comps.append(sorted(comp))
    return comps


def analyze_switch(n, side, st, crossM, acc, name):
    M, ell, T, _mu, cyc = st
    K2 = build_K2(n, M, cyc)
    Tfull = [sum(K2[v][w] for w in range(n)) for v in range(n)]
    N = F(n)
    Rfull = [N * Tfull[v] - sum(K2[v][w] * Tfull[w] for w in range(n)) for v in range(n)]
    comps = k2_components(n, K2)
    for comp in comps:
        V = set(comp); sz = len(comp)
        # (i) block-diagonality
        for u in comp:
            if Tfull[u] != sum(K2[u][w] for w in V):
                acc['blockdiag_fail'] += 1
                if acc['ex_bd'] is None:
                    acc['ex_bd'] = (name, n, comp, u)
                break
        # R_local with N' = sz
        Rloc = {u: F(sz) * Tfull[u] - sum(K2[u][w] * Tfull[w] for w in V) for u in comp}
        for u in comp:
            # (ii) additive identity
            if Rfull[u] != Rloc[u] + (N - sz) * Tfull[u]:
                acc['identity_fail'] += 1
                if acc['ex_id'] is None:
                    acc['ex_id'] = (name, n, comp, u, str(Rfull[u]), str(Rloc[u]))
            # (iii) R_local >= 0
            if Rloc[u] < 0:
                acc['rlocal_neg'] += 1
                if acc['ex_rl'] is None:
                    acc['ex_rl'] = (name, n, comp, u, str(Rloc[u]))
        # classify component by crossM bad edges it carries
        cross_in = [f for f in crossM if f[0] in V or f[1] in V]
        if cross_in:
            sig = (len(cross_in), tuple(sorted(ell[f] for f in cross_in)))
            acc['comp_sig'][sig] += 1
            acc['comp_minRloc'][sig] = min(acc['comp_minRloc'].get(sig, Rloc[comp[0]]), min(Rloc.values()))


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
            analyze_switch(n, side, st, list(crossM), acc, name)


def new_acc():
    return dict(defcap=0, blockdiag_fail=0, identity_fail=0, rlocal_neg=0,
                comp_sig=Counter(), comp_minRloc={}, ex_bd=None, ex_id=None, ex_rl=None)


def report(label, acc):
    print('=' * 64)
    print('BATTERY:', label, '| deficient switches:', acc['defcap'])
    print('block-diagonality fails:', acc['blockdiag_fail'], acc['ex_bd'] or '')
    print('additive-identity fails:', acc['identity_fail'], acc['ex_id'] or '')
    print('R_local < 0 occurrences:', acc['rlocal_neg'], acc['ex_rl'] or '')
    print('component signatures (#bad, ell) -> min R_local:')
    for sig in sorted(acc['comp_sig']):
        print('   ', sig, 'x', acc['comp_sig'][sig], ' minRloc=', str(acc['comp_minRloc'].get(sig)))
    ok = acc['blockdiag_fail'] == 0 and acc['identity_fail'] == 0 and acc['rlocal_neg'] == 0 and acc['defcap'] > 0
    print('VERDICT:', 'ALGEBRAIC SIGN PROOF VERIFIED (block-diag + additive identity + R_local>=0)'
          if ok else 'FAIL')


def glue_single(k):
    """core + a single C_k baggage, all cut-bridges."""
    cn, cE = dec('I?AEBAwF_')
    cyc = [(cn + i, cn + (i + 1) % k) for i in range(k)]
    acc = new_acc()
    for a in range(cn):
        for b in range(cn, cn + k):
            E = list(cE) + cyc + [(a, b)]
            if is_triangle_free(cn + k, E):
                scan_graph('g%d-%d' % (a, b), cn + k, E, acc)
    report('GLUE core + C%d (all bridges)' % k, acc)


def glue_multi(sizes):
    """core + several odd-cycle baggage cycles, representative bridges (cycle j -> core vertex j)."""
    cn, cE = dec('I?AEBAwF_')
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
        print('GLUE %s: not triangle-free with representative bridges' % sizes)


def census(maxn):
    acc = new_acc()
    for nn in range(5, maxn + 1):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); scan_graph('cen%d' % nn, n, E, acc)
        print('  census N=%d done: defcap=%d rlocal_neg=%d' % (nn, acc['defcap'], acc['rlocal_neg']), flush=True)
    report('CENSUS N<=%d' % maxn, acc)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'glue':
        spec = sys.argv[2]
        sizes = [int(x) for x in spec.split(',')]
        if len(sizes) == 1:
            glue_single(sizes[0])
        else:
            glue_multi(sizes)
    elif len(sys.argv) > 1 and sys.argv[1] == 'census':
        census(int(sys.argv[2]))
    else:
        census(10)
        glue_single(5)


if __name__ == '__main__':
    import sys
    main()
