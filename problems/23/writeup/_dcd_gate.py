"""EXACT gate for GPT-Pro's DIRTY CAP DEFECT inequality (DCD) -- the replacement for the dead
cap-pruning identities. Proof of strict cap expansion (C): |N(K)| >= |K|+1.

For a SELECTED + MINIMALIZED neutral terminal-shadow Gamma-decreasing switch S (from R[v]<0),
build my independent witness structure (crossM=C, bdyB=E, wit[(f,e)]=terminal-prefix vertset).
For a cap K (laminar leaf of the miss-sets {E \\ exits(f)}):
  F_K   = {f in C : exits(f) cap K = empty}   (= C \\ N(K), the rows that MISS the cap)
  U_K   = union over f in F_K, e in exits(f) of pref(f,e)   (terminal-prefix vertices, inside S)
  dB,dM = delta_B(U_K), delta_M(U_K)
  B_good = dB cap (E\\K)        B_leak = dB \\ (E\\K)
  M_good = F_K                  M_leak = dM \\ F_K
  missing_allowed = (E\\K) \\ B_good
DCD (claimed):    |missing_allowed| + |M_leak| - |B_leak| >= 1.
Max-cut optimality (must hold, S a max cut): |dB| >= |dM|.
These two => |N(K)| - |K| >= missing_allowed + M_leak - B_leak >= 1  (strict cap expansion).

Gate reports, per cap: DCD value, |N(K)|-|K| (the sidecap gap), maxcut slack |dB|-|dM|,
and whether F_K subset dM (needed for the M_good/M_leak split). EXACT integer counts.
Battery: census R<0 (N<=10) + H?AFBo]x2 (N=18, the 148-cap source). Run from problems/23/writeup.
"""
import subprocess, sys
RAW = '--raw' in sys.argv
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure, deltas_of
from _codex_minimalized_sidecap_gate import minimalize
from _codex_selected_minimality_gate import mask_of, vertices_of
from _codex_selected_interval_hall_gate import laminar_leaves


def dcd_for_switch(name, n, adj, side, st, smask, acc):
    Sset = set(vertices_of(smask, n))
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        acc['no_wit'] += 1
        return
    crossM, bdyB, wit = res
    C = set(crossM); E = set(bdyB)
    if not C or not E:
        return
    exits = {f: set() for f in crossM}
    pref = {}
    for (f, e), pv in wit.items():
        exits[f].add(e)
        pref[(f, e)] = pv
    # caps = laminar leaves of miss-sets
    miss_sets = [set(E) - exits[f] for f in crossM]
    leaves = laminar_leaves(miss_sets) or []
    if not leaves:
        acc['no_cap_switch'] += 1
        return
    acc['switches'] += 1
    for cap in leaves:
        K = set(cap)
        # N(K) = bad edges witnessing some exit in K ; F_K = rows that miss the cap
        NK = set(f for f in crossM if exits[f] & K)
        F_K = set(f for f in crossM if not (exits[f] & K))   # = C \ N(K)
        # U_K = prefix union of cap-missing rows
        U = set()
        for f in F_K:
            for e in exits[f]:
                U |= pref[(f, e)]
        dB, dM = deltas_of(n, adj, side, U)   # sets of blue / bad boundary edges of U
        EK = E - K                            # authorized outside exits
        B_good = dB & EK
        B_leak = dB - EK
        M_leak = dM - F_K
        missing_allowed = EK - B_good         # = EK - dB
        f_sub_dM = F_K <= dM
        dcd = len(missing_allowed) + len(M_leak) - len(B_leak)
        gap = len(NK) - len(K)                # the strict-cap-expansion quantity (sidecap gap, full cap)
        maxcut_slack = len(dB) - len(dM)
        acc['caps'] += 1
        acc['dcd_hist'][dcd] += 1
        acc['gap_hist'][gap] += 1
        if not f_sub_dM:
            acc['F_not_in_dM'] += 1
            if acc['ex_fsub'] is None:
                acc['ex_fsub'] = (name, n, ''.join(map(str, side)), sorted(K), 'F_K=%r dM=%r' % (sorted(F_K), sorted(dM)))
        if maxcut_slack < 0:
            acc['maxcut_violation'] += 1
            if acc['ex_mc'] is None:
                acc['ex_mc'] = (name, n, ''.join(map(str, side)), sorted(K), '|dB|=%d |dM|=%d' % (len(dB), len(dM)))
        if dcd < 1:
            acc['dcd_fail'] += 1
            if acc['ex_dcd'] is None:
                acc['ex_dcd'] = dict(name=name, n=n, side=''.join(map(str, side)), cap=sorted(K),
                                     dcd=dcd, missing=len(missing_allowed), M_leak=len(M_leak),
                                     B_leak=len(B_leak), F_K=len(F_K), NK=len(NK), gap=gap,
                                     dB=len(dB), dM=len(dM), U=sorted(U))
        if gap < 1:
            acc['gap_fail'] += 1
            if acc['ex_gap'] is None:
                acc['ex_gap'] = dict(name=name, n=n, side=''.join(map(str, side)), cap=sorted(K), gap=gap, NK=sorted(NK))


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
            smask = smask0 if RAW else minimalize(n, adj, side, st, gamma0, smask0, v)
            dcd_for_switch(name, n, adj, side, st, smask, acc)


def new_acc():
    from collections import Counter
    return dict(switches=0, caps=0, no_wit=0, no_cap_switch=0, F_not_in_dM=0, maxcut_violation=0,
                dcd_fail=0, gap_fail=0, dcd_hist=Counter(), gap_hist=Counter(),
                ex_dcd=None, ex_gap=None, ex_fsub=None, ex_mc=None)


def main():
    acc = new_acc()
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process('cen%d' % nn, n, E, acc)
        print('census N=%d: switches=%d caps=%d dcd_fail=%d gap_fail=%d' %
              (nn, acc['switches'], acc['caps'], acc['dcd_fail'], acc['gap_fail']), flush=True)
    n, E = vertex_blowup(*dec('H?AFBo]'), 2)
    process('H2x', n, E, acc)
    print('=' * 64)
    print('switches:', acc['switches'], 'caps:', acc['caps'], 'no_wit:', acc['no_wit'], 'no_cap_switch:', acc['no_cap_switch'])
    print('F_not_in_dM:', acc['F_not_in_dM'], acc['ex_fsub'] or '')
    print('maxcut_violation (|dB|<|dM|):', acc['maxcut_violation'], acc['ex_mc'] or '')
    print('DCD value histogram (missing+M_leak-B_leak):', sorted(acc['dcd_hist'].items()))
    print('gap histogram (|N(K)|-|K|):', sorted(acc['gap_hist'].items()))
    print('DCD < 1 failures:', acc['dcd_fail'], acc['ex_dcd'] or '')
    print('gap < 1 failures :', acc['gap_fail'], acc['ex_gap'] or '')
    ok = acc['dcd_fail'] == 0 and acc['gap_fail'] == 0 and acc['maxcut_violation'] == 0 and acc['caps'] > 0
    print('VERDICT:', 'DCD HOLDS (strict cap expansion via dirty defect inequality) -- GPT-Pro reduction SOUND'
          if ok else 'DCD FAILS -- inequality false as stated')


if __name__ == '__main__':
    main()
