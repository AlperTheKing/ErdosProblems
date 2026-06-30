"""CRITICAL: does (LB) need to hold only on GAMMA-MIN cuts, and do the 56 covered sites lie on gamma-min cuts?

The chain is: gamma-min connected-B max cut => (want) R[v]>=0 all v.  Contrapositive used by the construction:
R[v]<0 => exists neutral B-connected GAMMA-DECREASING switch => the cut is NOT gamma-min.  So the construction
ONLY needs: for a gamma-min cut, R[v]>=0.  Equivalently: any cut with an R[v]<0 admits a gamma-decreasing
neutral switch (then it cannot be gamma-min).  The length-bundle (LB) is the proposed witness.

The break (N=18, side=011111111111000000, Gamma=296 > gamma_min=200) shows: on a NON-gamma-min max cut the
length-bundle family can FAIL to provide the gamma-decreasing switch -- BUT some OTHER neutral gamma-decreasing
switch must still exist (since the cut is not gamma-min, just not necessarily a length-bundle one).

This file re-runs the census battery and, for EVERY R[v]<0 site, records whether the cut is GAMMA-MIN among all
max cuts of that graph, splitting the covered/failed counts by gamma-min status.  KEY OUTPUTS:
  - #(R<0 vertices on gamma-min cuts)  and whether length-bundle covers ALL of them,
  - #(R<0 vertices on non-gamma-min cuts) covered vs failed by length-bundle,
  - whether ANY gamma-min cut has an R[v]<0 vertex (if a gamma-min cut had R<0 that the construction can't
    cover, THAT would be fatal).

Exact Fraction.  Census N<=10 all max cuts + Hblow t=2/3 all max cuts.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import lenbundle_switches, boundary_delta, flip, gamma_of
from _bdef_construct import Cn, mycielski, is_triangle_free, union_disjoint, add_edges
from _wf_deficit_farkas import odd_blowup


def cutval(n, adj, side):
    return sum(1 for v in range(n) for w in adj[v] if w > v and side[v] != side[w])


def gamma_min_among_maxcuts(n, adj):
    gmax = max(cutval(n, adj, s) for s in maxcut_all(n, adj))
    best = None
    for s in maxcut_all(n, adj):
        if cutval(n, adj, s) != gmax:
            continue
        g = gamma_of(n, adj, s)
        if g is None:
            continue
        if best is None or g < best:
            best = g
    return best, gmax


def covers(n, adj, side, M, ell, cyc, gamma0, v):
    for Sset in lenbundle_switches(v, M, ell, cyc):
        if v not in Sset or len(Sset) in (0, n):
            continue
        if boundary_delta(n, adj, side, Sset) != 0:
            continue
        s2 = flip(side, Sset)
        g2 = gamma_of(n, adj, s2)
        if g2 is not None and g2 < gamma0:
            return True
    return False


def any_gamma_decreasing_neutral_switch(n, adj, side, gamma0):
    """Brute force: does ANY neutral B-connected switch (any subset is too big; restrict to the union of all
       geodesics' vertices' single-vertex and small flips) decrease Gamma?  For a *certificate that the cut is
       not gamma-min*, it suffices that some max cut has smaller Gamma -- which we know from gamma_min<gamma0.
       So here we only REPORT gamma0 vs gamma_min."""
    return None


def process(name, n, adj, acc):
    gm, gmax = gamma_min_among_maxcuts(n, adj)
    if gm is None:
        return
    for side in maxcut_all(n, adj):
        if cutval(n, adj, side) != gmax:
            continue
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
        neg = [v for v in range(n) if R[v] < 0]
        if not neg:
            continue
        gamma0 = sum(ell[f] ** 2 for f in M)
        is_gmin = (gamma0 == gm)
        for v in neg:
            cov = covers(n, adj, side, M, ell, cyc, gamma0, v)
            if is_gmin:
                acc['gmin_neg'] += 1
                if cov:
                    acc['gmin_cov'] += 1
                else:
                    acc['gmin_fail'] += 1
                    if acc['ex_gmin_fail'] is None:
                        acc['ex_gmin_fail'] = (name, n, ''.join(map(str, side)), v, str(R[v]), 'Gamma=%d=gmin' % gamma0)
            else:
                acc['ngmin_neg'] += 1
                if cov:
                    acc['ngmin_cov'] += 1
                else:
                    acc['ngmin_fail'] += 1
                    if acc['ex_ngmin_fail'] is None:
                        acc['ex_ngmin_fail'] = (name, n, ''.join(map(str, side)), v, str(R[v]), 'Gamma=%d gmin=%d' % (gamma0, gm))


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def main():
    acc = dict(gmin_neg=0, gmin_cov=0, gmin_fail=0, ngmin_neg=0, ngmin_cov=0, ngmin_fail=0,
               ex_gmin_fail=None, ex_ngmin_fail=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            adj = [set() for _ in range(n)]
            for x, y in E:
                adj[x].add(y); adj[y].add(x)
            process(g6, n, adj, acc)
        print("census N=%d: gmin_neg=%d gmin_cov=%d gmin_fail=%d | ngmin_neg=%d ngmin_cov=%d ngmin_fail=%d"
              % (nn, acc['gmin_neg'], acc['gmin_cov'], acc['gmin_fail'], acc['ngmin_neg'], acc['ngmin_cov'], acc['ngmin_fail']), flush=True)
    print("(skipping Hblow t=2/3 here: 2^18+ maxcut_all too slow; handled exactly in _break_confirm.py -- both N=18 cuts are NON-gamma-min, Gamma=296>gmin=200)", flush=True)
    # odd blowups (small)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,2)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 13:
            adj = [set() for _ in range(nn)]
            for x, y in EE:
                adj[x].add(y); adj[y].add(x)
            process("blow%s" % (sizes,), nn, adj, acc)
    print("=" * 72)
    print("GAMMA-MIN cuts: R<0 vertices=%d  covered=%d  FAIL=%d" % (acc['gmin_neg'], acc['gmin_cov'], acc['gmin_fail']))
    print("NON-gamma-min cuts: R<0 vertices=%d  covered=%d  FAIL=%d" % (acc['ngmin_neg'], acc['ngmin_cov'], acc['ngmin_fail']))
    print("ex gamma-min FAIL (FATAL if present):", acc['ex_gmin_fail'])
    print("ex non-gamma-min FAIL (harmless):", acc['ex_ngmin_fail'])
    fatal = acc['gmin_fail'] > 0 or acc['gmin_neg'] > 0
    print("VERDICT:",
          "FATAL: a GAMMA-MIN cut has an R[v]<0 vertex" + (" the construction cannot cover" if acc['gmin_fail'] > 0 else " at all (contradicts rho(K2)<=N target directly)")
          if fatal else
          "SOUND: NO gamma-min cut has any R[v]<0 vertex; all R<0 sites are on NON-gamma-min cuts (length-bundle failures there are harmless)")


if __name__ == "__main__":
    main()
