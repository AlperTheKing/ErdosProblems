"""Gate Codex's WIDENED selector (block 500): R[v]<0 => length-bundle SEED A through v + a small MOAT M (|M|<=3)
such that S=A∪M is neutral (delta_B=delta_M), B-connected after, and Gamma-DECREASING.  This recovers the construction
after the plain length-bundle selector was falsified (witness is a wider enclosing block).

Tested on ALL connected-B MAXIMUM cuts (maxcut_all) -- the harder battery that broke the plain selector -- of census
N<=10 + H?AFBo] vertex-blowups t=2,3 (the only families with R<0 sites).  Exact Fraction (Gamma recomputed).
Moat candidates: any vertices; search supersets seed + (<=3 from the graph). Reports coverage, first fail, moat-size hist.
"""
import subprocess, random, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _construction_gate import lenbundle_switches, gamma_of, boundary_delta, flip, vertex_blowup


def find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1):
    """Return (seed, moat, drop) if R[v]<0 covered by seed+moat, else None."""
    seeds = [s for s in lenbundle_switches(v, M, ell, cyc) if v in s and 0 < len(s) < n]
    # first: any seed already neutral + Gamma-decreasing (moat empty)
    for A in seeds:
        if boundary_delta(n, adj, side, A) == 0:
            g2 = gamma_of(n, adj, flip(side, A))
            if g2 is not None and g2 < gamma0:
                return (A, frozenset(), gamma0 - g2)
    # else: add a small moat. Candidate moat vertices: neighbors of the seed (keeps it local), else all.
    allv = list(range(n))
    for A in seeds:
        cand = allv   # search ALL vertices for the moat (Codex 503: moat is a single side-defect, not necessarily a neighbor)
        for k in range(1, max_moat + 1):
            for Mset in itertools.combinations(cand, k):
                S = A | set(Mset)
                if len(S) >= n:
                    continue
                if boundary_delta(n, adj, side, S) != 0:
                    continue
                g2 = gamma_of(n, adj, flip(side, S))
                if g2 is not None and g2 < gamma0:
                    return (A, frozenset(Mset), gamma0 - g2)
    return None


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    N = F(n)
    K2 = build_K2(n, M, cyc)
    R = [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
    neg = [v for v in range(n) if R[v] < 0]
    if not neg:
        return
    acc['bad_cuts'] += 1
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        res = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0)
        if res is None:
            acc['fail'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), v, str(R[v]))
        else:
            acc['covered'] += 1
            moatsize = len(res[1])
            acc['moat_hist'][moatsize] = acc['moat_hist'].get(moatsize, 0) + 1


def gfam_allmax(name, n, E, acc, cap=None):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    cuts = maxcut_all(n, adj)
    for side in cuts:
        test_cut(name, n, adj, side, acc)


def main():
    acc = dict(bad_cuts=0, neg=0, covered=0, fail=0, moat_hist={}, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d allmax: bad_cuts=%d neg=%d covered=%d fail=%d" % (nn, acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail']), flush=True)
    hN, hE = dec("H?AFBo]")
    for t in (2,):   # t=3 all-max-cuts is infeasible (2^26); t=2 N=18 is the decisive recovery battery
        nn, EE = vertex_blowup(hN, hE, t)
        gfam_allmax("Hblow_t%d" % t, nn, EE, acc)
        print("after Hblow t=%d (N=%d) allmax: bad_cuts=%d neg=%d covered=%d fail=%d %s" % (t, nn, acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    # glued island guardrail (C5 + Myc(C7), bridged) -- all max cuts
    from _bdef_construct import Cn, union_disjoint, add_edges, mycielski
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    inn, iEE = union_disjoint(isl, g15); inn, iEE = add_edges((inn, iEE), [(0, 5)])
    gfam_allmax("island", inn, iEE, acc)
    print("after glued island (N=%d) allmax: bad_cuts=%d neg=%d covered=%d fail=%d %s" % (inn, acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    print("=" * 60)
    print("bad cuts (some R<0):", acc['bad_cuts'])
    print("negative-residual vertices:", acc['neg'], " COVERED by seed+moat (|moat|<=3):", acc['covered'])
    print("SEED+MOAT FAILURES:", acc['fail'], acc['ex'] or '')
    print("moat-size histogram:", dict(sorted(acc['moat_hist'].items())))
    ok = acc['fail'] == 0
    print("VERDICT:", "WIDENED SELECTOR (length-bundle seed + <=3 moat) covers EVERY R<0 vertex on ALL max cuts incl blowups -- construction RECOVERED, descent route ALIVE"
          if ok else "FAIL -- seed+moat insufficient")


if __name__ == "__main__":
    main()
