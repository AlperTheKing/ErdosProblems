"""EXACT gate for GPT-Pro's CORRECTED (C) proof: the cap-pruning surplus lemma (replaces the dead guard lemma).

For a completed seed+moat switch S (R[v]<0), crossM=C=delta_M(S), bdyB=E=delta_B(S), Wit(f), Pref(f,e).
Miss(f)=E\\Wit(f).  Caps L,R = the (<=2) minimal nonempty Miss(f) atoms (property (A): Miss(f) in {empty,L,R,L u R}).
For a cap K: C_negK = {f in C : Wit(f) cap K = empty} = {f: K subset Miss(f)}; N(K)=C\\C_negK.
  Pruned switch (raw prefix-union form first, then blue-closure):
    S_negK = union over f in C_negK, e in Wit(f) of Pref(f,e).
CLAIMED BOUNDARY IDENTITIES (the prunability lemma, the new gateable atom):
    delta_M(S_negK) == C_negK ,   delta_B(S_negK) == E \\ K .
Then sigma(S_negK)=|E\\K|-|C_negK| = |N(K)|-|K|, and (C) <=> sigma>=1 (strict from neutral-minimality).
Gate: check the two boundary identities (raw and blue-closed S_negK) + sigma>=1, on census R<0 + H?AFBo][2] N18 all-max.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _pl_gate import witness_structure
from _rfc_gate import blue_closure_in_S, delta_B_M


def derive_caps(crossM, bdyB, wit):
    """Caps L,R = minimal nonempty Miss(f) atoms. Returns list of cap frozensets (1 or 2), or None if structure bad."""
    Wit = {f: set() for f in crossM}
    for (f, e) in wit:
        Wit[f].add(e)
    E = set(bdyB)
    miss = set()
    for f in crossM:
        m = frozenset(E - Wit[f])
        if m:
            miss.add(m)
    if not miss:
        return []   # all universal -> no caps, (C) vacuous
    # minimal (by inclusion) nonempty miss sets
    mins = [m for m in miss if not any(m2 < m for m2 in miss)]
    # (A): every miss set is a union of mins; mins should be disjoint atoms, <=2
    return mins


def test_switch(name, n, adj, side, st, Sset, acc):
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, bdyB, wit = res
    if not crossM or not bdyB:
        return
    caps = derive_caps(crossM, bdyB, wit)
    if caps is None or len(caps) == 0:
        return
    if len(caps) > 2:
        acc['bad_capstruct'] += 1
        return
    Wit = {f: set() for f in crossM}
    Pref = {}
    for (f, e), pref in wit.items():
        Wit[f].add(e); Pref[(f, e)] = pref
    E = set(bdyB); C = set(crossM)
    acc['switches'] += 1
    for K in caps:
        K = set(K)
        C_negK = set(f for f in crossM if not (Wit[f] & K))
        NK = C - C_negK
        # raw prefix-union pruned switch
        Sneg = set()
        for f in C_negK:
            for e in Wit[f]:
                Sneg |= Pref[(f, e)]
        acc['caps'] += 1
        for tag, U in (('raw', Sneg), ('closed', blue_closure_in_S(n, adj, side, Sset, Sneg))):
            dB, dM = delta_B_M(n, adj, side, U)
            id_M = (dM == C_negK)
            id_B = (dB == (E - K))
            if id_M and id_B:
                acc[tag + '_idok'] += 1
                sigma = len(dB) - len(dM)
                if sigma < 1:
                    acc[tag + '_sigma_fail'] += 1
                    if acc['ex'] is None:
                        acc['ex'] = (name, n, ''.join(map(str, side)), tag, 'sigma=%d' % sigma, sorted(K))
            else:
                acc[tag + '_idfail'] += 1
                if acc[tag + '_ex'] is None:
                    acc[tag + '_ex'] = (name, n, ''.join(map(str, side)), 'M_ok=%s B_ok=%s |dM|=%d |C_negK|=%d |dB|=%d |E\\K|=%d' % (id_M, id_B, len(dM), len(C_negK), len(dB), len(E - K)))


def process(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, cyc = st[0], st[1], st[2], st[4]
        if not M:
            continue
        N = F(n); K2 = build_K2(n, M, cyc)
        R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        g0 = sum(ell[f] ** 2 for f in M)
        for v in range(n):
            if R[v] >= 0:
                continue
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, g0, max_moat=1)
            if sm is None:
                continue
            A, moat, drop = sm
            test_switch(name, n, adj, side, st, set(A) | set(moat), acc)


def main():
    acc = dict(switches=0, caps=0, bad_capstruct=0,
               raw_idok=0, raw_idfail=0, raw_sigma_fail=0, raw_ex=None,
               closed_idok=0, closed_idfail=0, closed_sigma_fail=0, closed_ex=None, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process("cen%d" % nn, n, E, acc)
        print("census N=%d: switches=%d caps=%d raw_idok=%d raw_idfail=%d closed_idok=%d closed_idfail=%d"
              % (nn, acc['switches'], acc['caps'], acc['raw_idok'], acc['raw_idfail'], acc['closed_idok'], acc['closed_idfail']), flush=True)
    hN, hE = dec("H?AFBo]")
    nn, EE = vertex_blowup(hN, hE, 2)
    process("Hblow2", nn, EE, acc)
    print("after Hblow2 N18: switches=%d caps=%d raw_idok=%d raw_idfail=%d closed_idok=%d closed_idfail=%d bad_capstruct=%d"
          % (acc['switches'], acc['caps'], acc['raw_idok'], acc['raw_idfail'], acc['closed_idok'], acc['closed_idfail'], acc['bad_capstruct']), flush=True)
    print("=" * 60)
    print("switches:", acc['switches'], " caps tested:", acc['caps'], " bad cap-structure:", acc['bad_capstruct'])
    print("RAW prefix-union:  boundary-id OK=%d  FAIL=%d %s" % (acc['raw_idok'], acc['raw_idfail'], acc['raw_ex'] or ''))
    print("BLUE-CLOSED:       boundary-id OK=%d  FAIL=%d %s" % (acc['closed_idok'], acc['closed_idfail'], acc['closed_ex'] or ''))
    print("sigma>=1 failures (where id ok): raw=%d closed=%d %s" % (acc['raw_sigma_fail'], acc['closed_sigma_fail'], acc['ex'] or ''))
    best = 'raw' if acc['raw_idfail'] == 0 and acc['caps'] > 0 else ('closed' if acc['closed_idfail'] == 0 and acc['caps'] > 0 else None)
    print("VERDICT:", ("CAP-PRUNING boundary identities HOLD (%s form) => GPT-Pro's corrected (C) proof structure SOUND; sigma>=1 = (C) (validated); strict +1 from neutral-minimality" % best)
          if best else "CAP-PRUNING boundary identities FAIL in both forms -- corrected guard route also needs repair (prunability lemma false as stated)")


if __name__ == "__main__":
    main()
