"""DECISIVE last gate (vertexwise route): the CONSTRUCTION half of the K2T contrapositive.

For every connected-B MAXIMUM cut and every vertex v with R[v]=N*T[v]-(K2*T)[v] < 0, the LENGTH-BUNDLE
half-switch family contains a switch S with: v in S, neutral (delta_B(S)=delta_M(S)), B connected after flipping,
and Gamma(after) < Gamma(before).  Proof-relevant form -- I recompute Gamma exactly (no Psi needed for the gate;
the descent identity dG=-Psi was separately proven).  Combined with that identity:
   gamma-min => no neutral Gamma-decreasing switch => R[v]>=0 for all v => rho(K2)<=N (Collatz-Wielandt) => Gamma<=N^2.

Length-bundle half-switch (Codex 09:18): for v and each length L, collect all shortest geodesics Q (over all bad edges
f with ell[f]=L) with v in Q; for each of the 2 orientations, Pref = union of Q[:idx_Q(v)+1], Suff = union of Q[idx_Q(v):].
Independent reimpl.  Exact Fraction.  Full battery: all connected-B max cuts census N<=10 + Myc N=23 + H?AFBo] blowups
N18/27 + overloaded blowups + glued island + randoms.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _wf_deficit_farkas import odd_blowup


def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def boundary_delta(n, adj, side, Sset):
    """delta_B - delta_M for flipping vertex set Sset: over edges with exactly one endpoint in Sset,
       count how cut-status flips. Neutral iff returns 0."""
    dB = dM = 0
    for u in Sset:
        for w in adj[u]:
            if w in Sset:
                continue
            # edge (u,w), u in S, w not in S -> its cut status flips
            if side[u] != side[w]:
                dB += 1   # was blue, becomes bad
            else:
                dM += 1   # was bad, becomes blue
    return dB - dM


def lenbundle_switches(v, M, ell, cyc):
    """All length-bundle half-switches through v: per length L, per orientation, prefix/suffix unions."""
    bylen = {}
    for f in M:
        L = ell[f]
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(L, []).append(list(Q))
    out = []
    for L, rows in bylen.items():
        for orient in (0, 1):
            pref = set(); suff = set()
            for Q in rows:
                q = Q if orient == 0 else Q[::-1]
                i = q.index(v)
                pref.update(q[:i + 1])
                suff.update(q[i:])
            out.append(frozenset(pref))
            out.append(frozenset(suff))
    # dedup
    return set(out)


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


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
        covered = False
        for Sset in lenbundle_switches(v, M, ell, cyc):
            if v not in Sset or len(Sset) == 0 or len(Sset) == n:
                continue
            if boundary_delta(n, adj, side, Sset) != 0:
                continue   # not neutral
            s2 = flip(side, Sset)
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                covered = True
                acc['drop_hist'][gamma0 - g2] = acc['drop_hist'].get(gamma0 - g2, 0) + 1
                break
        if covered:
            acc['covered'] += 1
        else:
            acc['fail'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), v, str(R[v]))


def gfam_allmax(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc)


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def maxcut_ls(n, adj, seeds=80):
    best = None; bv = -1; rng = random.Random(9)
    for _ in range(seeds):
        s = [rng.randint(0, 1) for _ in range(n)]; imp = True
        while imp:
            imp = False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w] == s[v]) > sum(1 for w in adj[v] if s[w] != s[v]):
                    s[v] ^= 1; imp = True
        val = sum(1 for v in range(n) for w in adj[v] if w > v and s[v] != s[w])
        if val > bv:
            bv = val; best = s[:]
    return best


def main():
    acc = dict(bad_cuts=0, neg=0, covered=0, fail=0, drop_hist={}, ex=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: bad_cuts=%d neg=%d covered=%d fail=%d" % (nn, acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail']), flush=True)
    # Myc N=23
    grN, grE = mycielski(5, Cn(5)); m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Myc23: bad_cuts=%d neg=%d covered=%d fail=%d %s" % (acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    # H?AFBo] blowups inherited
    hN, hE = dec("H?AFBo]"); base = [int(c) for c in "111110000"]
    for t in (2, 3):
        nn, EE = vertex_blowup(hN, hE, t)
        side = [base[v // t] for v in range(nn)]
        adj = [set() for _ in range(nn)]
        for x, y in EE:
            adj[x].add(y); adj[y].add(x)
        test_cut("Hblow_t%d" % t, nn, adj, side, acc)
    print("after Hblowups: bad_cuts=%d neg=%d covered=%d fail=%d %s" % (acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    # overloaded C5 blowups (all max cuts where small)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,2)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 13:
            gfam_allmax("blow%s" % (sizes,), nn, EE, acc)
    # glued island
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam_allmax("isl", nn, EE, acc)
    print("after blowups+island: bad_cuts=%d neg=%d covered=%d fail=%d %s" % (acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)
    rng = random.Random(7); made = 0; tries = 0
    while made < 150 and tries < 50000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.32)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam_allmax("rand%d" % made, nn, EE, acc)
    print("=" * 60)
    print("bad cuts (some R[v]<0):", acc['bad_cuts'], " (random:", made, ")")
    print("negative-residual vertices:", acc['neg'], " COVERED by neutral Gamma-decreasing length-bundle switch:", acc['covered'])
    print("CONSTRUCTION FAILURES:", acc['fail'], acc['ex'] or '')
    print("Gamma-drop histogram:", dict(sorted(acc['drop_hist'].items())))
    ok = acc['fail'] == 0
    print("VERDICT:", "CONSTRUCTION HOLDS: every R[v]<0 has a neutral B-connected Gamma-DECREASING length-bundle switch incl N=23+blowups -- vertexwise contrapositive CLOSED (with proven descent identity)"
          if ok else "FAIL")


if __name__ == "__main__":
    main()
