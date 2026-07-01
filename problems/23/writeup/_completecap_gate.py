"""Independent cross-gate (Claude machinery) of Codex's COMPLETE-CAP classification (18:31Z).

On the SELECTED + MINIMALIZED neutral terminal-shadow Gamma-decreasing switch S (from R[v]<0),
using my from-scratch witness_structure: for each side-cap K (laminar leaf of the miss-sets
{E \\ exits(f)}), let touch(K) = {f in crossM : exits(f) cap K != empty}. Check:
  (Complete cap)  every f in touch(K) witnesses EVERY exit in K   (K subset exits(f)),
  (Surplus touch) |touch(K)| > |K|,
  (N=touch)       for every nonempty Y subset K, N(Y) = touch(K)   [brute over all Y, exhaustive].
(Complete)+(Surplus) => strict cap expansion |N(Y)|=|touch(K)|>|K|>=|Y|, immediately.
Battery: census R<0 (N<=10) + H?AFBo]x2 (N=18, 148-cap source). EXACT counts. From problems/23/writeup."""
import subprocess, itertools
from collections import Counter
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _codex_minimalized_sidecap_gate import minimalize
from _codex_selected_minimality_gate import mask_of, vertices_of
from _codex_selected_interval_hall_gate import laminar_leaves


def gate_switch(name, n, adj, side, st, smask, acc):
    Sset = set(vertices_of(smask, n))
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        acc['no_wit'] += 1
        return
    crossM, bdyB, wit = res
    E = set(bdyB)
    if not crossM or not E:
        return
    exits = {f: set() for f in crossM}
    for (f, e) in wit:
        exits[f].add(e)
    miss_sets = [E - exits[f] for f in crossM]
    leaves = laminar_leaves(miss_sets) or []
    if not leaves:
        acc['no_cap_switch'] += 1
        return
    acc['switches'] += 1
    for cap in leaves:
        K = set(cap)
        touch = set(f for f in crossM if exits[f] & K)
        acc['caps'] += 1
        complete = all(K <= exits[f] for f in touch)
        surplus = len(touch) > len(K)
        # exhaustive N(Y)=touch over all nonempty Y subset K
        nY_ok = True
        for r in range(1, len(K) + 1):
            for Y in itertools.combinations(sorted(K), r):
                Ys = set(Y)
                NY = set(f for f in crossM if exits[f] & Ys)
                if NY != touch:
                    nY_ok = False
                    break
            if not nY_ok:
                break
        acc['sig_hist'][(len(K), len(touch), len(touch) - len(K))] += 1
        if not complete:
            acc['noncomplete'] += 1
            if acc['ex_nc'] is None:
                acc['ex_nc'] = (name, n, ''.join(map(str, side)), sorted(K), sorted(touch),
                                {f: sorted(exits[f]) for f in touch})
        if not surplus:
            acc['nonsurplus'] += 1
            if acc['ex_ns'] is None:
                acc['ex_ns'] = (name, n, ''.join(map(str, side)), sorted(K), sorted(touch))
        if not nY_ok:
            acc['nY_fail'] += 1
            if acc['ex_ny'] is None:
                acc['ex_ny'] = (name, n, ''.join(map(str, side)), sorted(K), sorted(touch))


def process(name, n, edges, acc, max_add=1):
    adj = [set() for _ in range(n)]
    for x, y in edges:
        adj[x].add(y); adj[y].add(x)
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
            smask0 = mask_of(set(seed) | set(moat))
            smask = minimalize(n, adj, side, st, gamma0, smask0, v)
            gate_switch(name, n, adj, side, st, smask, acc)


def main():
    acc = dict(switches=0, caps=0, no_wit=0, no_cap_switch=0, noncomplete=0, nonsurplus=0,
               nY_fail=0, sig_hist=Counter(), ex_nc=None, ex_ns=None, ex_ny=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process('cen%d' % nn, n, E, acc)
        print('census N=%d: switches=%d caps=%d noncomplete=%d nonsurplus=%d nY_fail=%d' %
              (nn, acc['switches'], acc['caps'], acc['noncomplete'], acc['nonsurplus'], acc['nY_fail']), flush=True)
    n, E = vertex_blowup(*dec('H?AFBo]'), 2)
    process('H2x', n, E, acc)
    print('=' * 64)
    print('switches:', acc['switches'], 'caps:', acc['caps'], 'no_wit:', acc['no_wit'], 'no_cap_switch:', acc['no_cap_switch'])
    print('signature (|K|,|touch|,surplus) histogram:', sorted(acc['sig_hist'].items()))
    print('NONCOMPLETE caps:', acc['noncomplete'], acc['ex_nc'] or '')
    print('NONSURPLUS caps :', acc['nonsurplus'], acc['ex_ns'] or '')
    print('N(Y)!=touch     :', acc['nY_fail'], acc['ex_ny'] or '')
    ok = acc['noncomplete'] == 0 and acc['nonsurplus'] == 0 and acc['nY_fail'] == 0 and acc['caps'] > 0
    print('VERDICT:', 'COMPLETE-CAP + SURPLUS-TOUCH HOLD (my machinery) -- strict expansion immediate'
          if ok else 'FAILS -- see example')


if __name__ == '__main__':
    main()
