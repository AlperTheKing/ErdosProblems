"""Independent cross-gate of Codex's REX-THETA row-side claim (20:49):
For every selected R[v]<0 switch and every residual SINGLETON miss (f,e) (a row f in F1 that misses
exactly one exit e in its residual component), assert ell(f)=7 AND there exists g in F0 with ell(g)=5
(=L0) and geodesics Q in cyc[g], P in cyc[f] such that Q is a contiguous vertex-subpath of P (up to
reversal) -- i.e. the singleton miss is the nested 5/7 terminal theta (short side an F0 edge).

Uses MY witness_structure for cross_m/bdy_b/witnesses; Codex's min_cost_stage0 + components for the
residual structure. Battery: census N<=10 + H?AFBo]x2 (the 72-singleton-miss source). From problems/23/writeup."""
import subprocess
from collections import Counter
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _codex_balanced_stage0_gate import min_cost_stage0
from _codex_rare_exit_complement_gate import components
from _codex_k2t_switch_probe import adj_from_edges


def contiguous_subpath(Q, P):
    Q = list(Q)
    for PP in (list(P), list(P)[::-1]):
        L = len(Q)
        for i in range(len(PP) - L + 1):
            if PP[i:i + L] == Q:
                return True
    return False


def check_switch(name, n, adj, side, st, Sset, acc):
    M, ell, T, mu, cyc = st
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, bdyB, wit = res
    Fed = tuple(sorted(crossM)); Eed = tuple(sorted(bdyB))
    if not Fed or len(Fed) != len(Eed):
        return
    witnesses = {}
    for (f, e) in wit:
        witnesses.setdefault(e, set()).add(f)
    for e in Eed:
        witnesses.setdefault(e, set())
    if any(not witnesses[e] for e in Eed):
        return
    lamb = {e: min(ell[f] for f in witnesses[e]) for e in Eed}
    min_len = min(ell[f] for f in Fed)
    min_lam = min(lamb.values())
    F0 = tuple(f for f in Fed if ell[f] == min_len)
    F1 = tuple(f for f in Fed if ell[f] > min_len)
    if not F1:
        return
    E0 = tuple(e for e in Eed if lamb[e] == min_lam)
    deg_f1 = {e: sum(1 for f in F1 if f in witnesses[e]) for e in E0}
    m0 = min_cost_stage0(F0, E0, witnesses, deg_f1)
    if m0 is None:
        return
    rem = tuple(e for e in Eed if e not in set(m0.values()))
    adj1 = {f: {e for e in rem if f in witnesses[e]} for f in F1}
    acc['switches'] += 1
    acc['L0'][min_len] += 1
    for cl, cr in components(F1, rem, adj1):
        cr = tuple(cr)
        for f in cl:
            misses = [e for e in cr if e not in adj1[f]]
            if len(misses) != 1:
                continue
            e = misses[0]
            acc['singleton'] += 1
            acc['ellf'][ell[f]] += 1
            if ell[f] != 7:
                acc['ellf_not7'] += 1
                if acc['ex7'] is None:
                    acc['ex7'] = (name, n, ''.join(map(str, side)), f, ell[f])
            nested = False
            for g in F0:
                if ell[g] != min_len:
                    continue
                for Q in cyc[g]:
                    for P in cyc[f]:
                        if contiguous_subpath(Q, P):
                            nested = True
                            break
                    if nested:
                        break
                if nested:
                    break
            if nested:
                acc['nested_ok'] += 1
            else:
                acc['nested_fail'] += 1
                if acc['exn'] is None:
                    acc['exn'] = (name, n, ''.join(map(str, side)), f, e, sorted(ell[g] for g in F0), min_len)


def process_allmax(name, n, edges, acc, max_add=1):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v, rv in enumerate(R):
            if rv >= 0:
                continue
            got = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=max_add)
            if got is None:
                continue
            seed, moat, _drop = got
            check_switch(name, n, adj, side, st, set(seed) | set(moat), acc)


def main():
    acc = dict(switches=0, singleton=0, ellf_not7=0, nested_ok=0, nested_fail=0,
               L0=Counter(), ellf=Counter(), ex7=None, exn=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process_allmax('cen%d' % nn, n, E, acc)
        print('  census N=%d: switches=%d singleton=%d nested_fail=%d ellf_not7=%d' %
              (nn, acc['switches'], acc['singleton'], acc['nested_fail'], acc['ellf_not7']), flush=True)
    n, E = vertex_blowup(*dec('H?AFBo]'), 2)
    process_allmax('H2x', n, E, acc)
    print('=' * 60)
    print('switches:', acc['switches'], 'singleton misses:', acc['singleton'])
    print('L0 (min_len) histogram:', dict(acc['L0']))
    print('ell(f) of singleton misses:', dict(acc['ellf']))
    print('ell(f) != 7 :', acc['ellf_not7'], acc['ex7'] or '')
    print('REX-Theta nested (5 in 7) ok:', acc['nested_ok'], '| nested FAIL:', acc['nested_fail'], acc['exn'] or '')
    ok = acc['nested_fail'] == 0 and acc['ellf_not7'] == 0 and acc['singleton'] > 0
    print('VERDICT:', 'REX-THETA HOLDS: every singleton miss = nested 5/7 terminal theta'
          if ok else ('no singleton misses' if acc['singleton'] == 0 else 'FAIL'))


if __name__ == '__main__':
    main()
