"""Gate Codex 554 NO-CROSSING ORDER / biconvexity: is the terminal-shadow witness graph an INTERVAL bigraph?
If so, Hall reduces to consecutive (interval) sets -- a tractable, refuted-leakage-free route.

For each R<0 switch S (length-bundle seed + <=1 moat), build the witness graph (crossM bad edges <-> bdyB blue exits,
f witnesses e). Check the CONVEXITY (consecutive-ones) property:
  (A) exists an ordering of bdyB (exits) s.t. every crossM bad edge f's witness set Wit^{-1}(f)={e: f witnesses e} is a
      contiguous interval;  AND
  (B) exists an ordering of crossM s.t. every exit e's witness set {f: f witnesses e} is contiguous.
Biconvex = both. Brute-force orderings for small sides. Reuses _pl_gate.witness_structure (independent reimpl).
"""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat
from _pl_gate import witness_structure


def has_consecutive_order(items, neighbor_sets):
    """Is there an ordering of `items` s.t. every set in neighbor_sets is a contiguous interval?"""
    if len(items) > 8:
        return None  # too big to brute-force
    for perm in itertools.permutations(items):
        pos = {x: i for i, x in enumerate(perm)}
        ok = True
        for ns in neighbor_sets:
            if not ns:
                continue
            idxs = sorted(pos[x] for x in ns)
            if idxs[-1] - idxs[0] != len(idxs) - 1:
                ok = False; break
        if ok:
            return True
    return False


def test_switch(name, n, adj, side, st, Sset, acc):
    res = witness_structure(n, adj, side, st, Sset)
    if res is None:
        return
    crossM, bdyB, wit = res
    if not bdyB or not wit:
        return
    bdyB = list(bdyB); crossM = list(crossM)
    # Wit^{-1}(f) = exits witnessed by f ; Wit(e) = bad edges witnessing e
    by_f = {f: set() for f in crossM}
    by_e = {e: set() for e in bdyB}
    for (f, e) in wit:
        by_f[f].add(e); by_e[e].add(f)
    acc['switches'] += 1
    # (A) order bdyB so each by_f[f] is interval
    A = has_consecutive_order(bdyB, list(by_f.values()))
    # (B) order crossM so each by_e[e] is interval
    B = has_consecutive_order(crossM, list(by_e.values()))
    if A is None or B is None:
        acc['toobig'] += 1
        return
    if A:
        acc['convexA'] += 1
    if B:
        acc['convexB'] += 1
    if A and B:
        acc['biconvex'] += 1
    else:
        acc['notbi'] += 1
        if acc['ex'] is None:
            acc['ex'] = (name, n, ''.join(map(str, side)), A, B, len(crossM), len(bdyB))


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
        N = F(n)
        K2 = build_K2(n, M, cyc)
        R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        gamma0 = sum(ell[f] ** 2 for f in M)
        for v in range(n):
            if R[v] >= 0:
                continue
            sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
            if sm is None:
                continue
            A, moat, drop = sm
            test_switch(name, n, adj, side, st, set(A) | set(moat), acc)


def main():
    acc = dict(switches=0, convexA=0, convexB=0, biconvex=0, notbi=0, toobig=0, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); process("cen%d" % nn, n, E, acc)
        print("census N=%d: switches=%d convexA=%d convexB=%d biconvex=%d notbi=%d toobig=%d"
              % (nn, acc['switches'], acc['convexA'], acc['convexB'], acc['biconvex'], acc['notbi'], acc['toobig']), flush=True)
    # H?AFBo] blowup t=2 all-max (the breaking battery)
    hN, hE = dec("H?AFBo]")
    from _seedmoat_gate import vertex_blowup
    nn, EE = vertex_blowup(hN, hE, 2)
    process("Hblow2", nn, EE, acc)
    print("after Hblow2 N18: switches=%d biconvex=%d notbi=%d toobig=%d %s" % (acc['switches'], acc['biconvex'], acc['notbi'], acc['toobig'], acc['ex'] or ''), flush=True)
    print("=" * 55)
    print("switches:", acc['switches'], " convexA(bdyB-order):", acc['convexA'], " convexB(crossM-order):", acc['convexB'])
    print("BICONVEX (interval bigraph):", acc['biconvex'], " NOT biconvex:", acc['notbi'], " too-big:", acc['toobig'])
    print("first non-biconvex:", acc['ex'] or 'NONE')
    print("VERDICT:", "WITNESS GRAPH IS BICONVEX (interval bigraph) on all enumerable R<0 switches -- Hall reduces to INTERVALS (Codex 554 no-crossing route LIVE)"
          if acc['notbi'] == 0 else "NOT always biconvex -- no-crossing route needs the specific geometric order")


if __name__ == "__main__":
    main()
