"""EXACT gate for the DOOR-OWNER + ENCLOSER certificate (user's section-8 proof of (C) / surplus-touch).

On each minimalized selected switch (R[v]<0 -> seed+moat -> inclusion-minimal), using MY witness_structure,
for each leaf cap K (laminar leaf of the miss-sets {E\\exits(f)}):
  (Atom)      ForAll f in C: K cap Miss(f) in {empty, K}                     [complete cap]
  (DoorSDR)   exists injective omega: K -> touch(K) with omega(e) witnessing e
              == max bipartite matching size in (K, touch(K); e~f iff f witnesses e) equals |K|
  (Encloser)  |touch(K)| >= |K|+1   (a row rho_K in touch(K) \\ omega(K))
Hard certificate = Atom and DoorSDR and Encloser.  Plus DIAGNOSTIC length-structure: does touch(K)
contain a strictly-longest (seed-length Lmax) row PLUS >=|K| shorter door-owner rows? -- tests the
proof's identification rho_K = enclosing seed row distinct from the |K| (shorter) door owners, vs the
alien-door fan (all touch rows equal-length, no extra encloser) the proof claims minimality excludes.
Battery: census R<0 (N<=10) + H?AFBo]x2 (N=18). EXACT. Run from problems/23/writeup."""
import subprocess
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


def bipartite_match(left, adjm):
    matchR = {}
    def aug(l, seen):
        for r in adjm[l]:
            if r in seen:
                continue
            seen.add(r)
            if r not in matchR or aug(matchR[r], seen):
                matchR[r] = l
                return True
        return False
    size = 0
    for l in left:
        if aug(l, set()):
            size += 1
    return size


def gate_switch(name, n, adj, side, st, smask, acc, v):
    M, ell, T, mu, cyc = st
    res = witness_structure(n, adj, side, st, set(vertices_of(smask, n)))
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
    Lmax = max(ell[f] for f in crossM)
    # seed-through-v rows: bad edges whose geodesics pass through v (the negative-residual vertex)
    seedrows = set()
    for f in crossM:
        verts = set()
        for p in cyc[f]:
            verts |= set(p)
        if v in verts:
            seedrows.add(f)
    seedrows_max = set(f for f in seedrows if ell[f] == Lmax)
    acc['switches'] += 1
    for cap in leaves:
        K = set(cap)
        touch = [f for f in crossM if exits[f] & K]
        acc['caps'] += 1
        complete = all(K <= exits[f] for f in touch)
        adjm = {e: [f for f in touch if e in exits[f]] for e in K}
        msize = bipartite_match(list(K), adjm)
        surplus = len(touch) - len(K)
        maxrows = [f for f in touch if ell[f] == Lmax]
        shorter = [f for f in touch if ell[f] < Lmax]
        enc_seed = (len(maxrows) >= 1 and len(shorter) >= len(K))
        # PROOF S7: rho_K = the seed row THROUGH v -- must touch K and be a genuine extra
        touch_seedv = [f for f in touch if f in seedrows]
        touch_seedv_max = [f for f in touch if f in seedrows_max]
        enc_v = (len(touch_seedv) >= 1 and surplus >= 1)
        enc_vmax = (len(touch_seedv_max) >= 1 and surplus >= 1)
        # Codex 19:22 check: is EVERY touch row a seed-through-v row? (=> seed-through-v does NOT distinguish encloser)
        all_touch_v = all(f in seedrows for f in touch)
        acc['all_touch_v_yes' if all_touch_v else 'all_touch_v_no'] += 1
        acc['sig'][(len(K), len(touch))] += 1
        acc['lenstruct'][(len(set(ell[f] for f in touch)), len(maxrows))] += 1
        if not complete:
            acc['noncomplete'] += 1
            acc['ex_nc'] = acc['ex_nc'] or (name, n, ''.join(map(str, side)), sorted(K))
        if msize != len(K):
            acc['sdr_fail'] += 1
            acc['ex_sdr'] = acc['ex_sdr'] or (name, n, ''.join(map(str, side)), sorted(K), msize)
        if surplus < 1:
            acc['surplus_fail'] += 1
            acc['ex_sp'] = acc['ex_sp'] or (name, n, ''.join(map(str, side)), sorted(K))
        acc['enc_v_ok' if enc_v else 'enc_v_no'] += 1
        acc['enc_vmax_ok' if enc_vmax else 'enc_vmax_no'] += 1
        if not enc_v and acc['ex_encv'] is None:
            acc['ex_encv'] = (name, n, ''.join(map(str, side)), 'v=%d' % v, sorted(K),
                              'touch_lens=%s seedrows_in_touch=%d' % (sorted(ell[f] for f in touch), len(touch_seedv)))
        if enc_seed:
            acc['enc_seed_ok'] += 1
        else:
            acc['enc_seed_no'] += 1
            acc['ex_enc'] = acc['ex_enc'] or (name, n, ''.join(map(str, side)), sorted(K),
                                              sorted(ell[f] for f in touch), Lmax)


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
            gate_switch(name, n, adj, side, st, smask, acc, v)


def main():
    acc = dict(switches=0, caps=0, no_wit=0, no_cap_switch=0, noncomplete=0, sdr_fail=0, surplus_fail=0,
               enc_seed_ok=0, enc_seed_no=0, enc_v_ok=0, enc_v_no=0, enc_vmax_ok=0, enc_vmax_no=0,
               all_touch_v_yes=0, all_touch_v_no=0,
               sig=Counter(), lenstruct=Counter(),
               ex_nc=None, ex_sdr=None, ex_sp=None, ex_enc=None, ex_encv=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process('cen%d' % nn, n, E, acc)
        print('census N=%d: caps=%d noncomplete=%d sdr_fail=%d surplus_fail=%d' %
              (nn, acc['caps'], acc['noncomplete'], acc['sdr_fail'], acc['surplus_fail']), flush=True)
    n, E = vertex_blowup(*dec('H?AFBo]'), 2)
    process('H2x', n, E, acc)
    print('=' * 66)
    print('switches:', acc['switches'], 'caps:', acc['caps'])
    print('HARD CERTIFICATE: noncomplete=%d  sdr_fail=%d  surplus_fail=%d' %
          (acc['noncomplete'], acc['sdr_fail'], acc['surplus_fail']))
    print('  ex_nc:', acc['ex_nc'] or '-', '| ex_sdr:', acc['ex_sdr'] or '-', '| ex_sp:', acc['ex_sp'] or '-')
    print('cap signature (|K|,|touch|):', sorted(acc['sig'].items()))
    print('DIAGNOSTIC encloser=seed-length-row + >=|K| shorter door-owners: ok=%d no=%d' % (acc['enc_seed_ok'], acc['enc_seed_no']))
    print('  (n_distinct_lengths, n_maxlen_rows) histogram:', sorted(acc['lenstruct'].items()))
    print('  first enc_seed_no (|K|,touch-lengths,Lmax):', acc['ex_enc'] or 'NONE')
    print('PROOF S7 rho_K = seed-row-THROUGH-v in touch(K) (genuine extra): ok=%d no=%d' % (acc['enc_v_ok'], acc['enc_v_no']))
    print('  (Lmax seed-through-v specifically): ok=%d no=%d' % (acc['enc_vmax_ok'], acc['enc_vmax_no']))
    print('  first enc_v_no:', acc['ex_encv'] or 'NONE')
    print('CODEX-19:22 every-touch-row-is-seed-through-v: yes=%d no=%d  => if yes=all, enc_v is VACUOUS (no distinguished encloser)'
          % (acc['all_touch_v_yes'], acc['all_touch_v_no']))
    hard_ok = acc['noncomplete'] == 0 and acc['sdr_fail'] == 0 and acc['surplus_fail'] == 0 and acc['caps'] > 0
    print('VERDICT:', 'DOOR-OWNER+ENCLOSER CERTIFICATE HOLDS (atom+injective door SDR+distinct encloser) over all caps'
          if hard_ok else 'CERTIFICATE FAILS -- see example')


if __name__ == '__main__':
    main()
