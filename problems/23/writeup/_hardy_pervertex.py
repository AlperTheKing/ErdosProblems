"""ANGLE = per-vertex HARDY WEIGHT bound toward proving (H): H := D_{N-T} + Lstar >= 0.

H[v][v] = (N - T_v) + d(v),   d(v) = diagonal of Lstar at v
        = sum_f (beta_{L_f}/|cyc[f]|) sum_{Q in cyc[f], v in Q} deg_Q(v),  deg_Q(v) = #cycle-edges of Q at v.
For a vertex on a cycle deg_Q(v)=2 (two incident cycle edges); endpoints of bad edge f also have 2 (one path
edge + the closing bad edge).  So d(v) = sum_f (beta_{L_f}/|cyc[f]|) * sum_{Q: v in Q} deg_Q(v).

Off-diagonal H[v][w] = - sum_f (beta_{L_f}/|cyc[f]|) * (#cycle-edges of Q between v and w, summed over Q in cyc[f]).
These are <= 0 (Laplacian off-diagonals).  So |H[v][w]| for w!=v equals the magnitude of the negative entry.

We test EXACTLY (Fraction, certified rational beta' <= beta_L from _hardy_gate.BETA):
  (a)  T_v - N  <=  d(v)                       (deficit dominated by incident cycle diagonal)
  (b)  (T_v-N)_+  <=  (1/2) * (sum of incident cycle-edge weights c_e at v)    [c_e = beta_L/|cyc[f]| per cycle-edge]
       NOTE: sum of incident cycle-edge weights at v = d(v) exactly (each incident cycle edge contributes its weight,
       and the diagonal Laplacian entry at v = sum of weights of incident edges).  So (b) is (T_v-N)_+ <= d(v)/2.
  (c)  GERSHGORIN:  H[v][v] >= sum_{w!=v} |H[v][w]|   for all v.
       If (c) holds for all v on the whole battery, (H) follows ELEMENTARILY (diagonally dominant, PSD).

For a Laplacian-plus-diagonal H = D_{N-T} + Lstar, note sum_{w!=v}|H[v][w]| = sum_{w!=v}(-H[v][w]) = (rowsum of Lstar
off-diagonals magnitude) = d(v) (since Lstar is a sum of graph Laplacians, each row sums to 0, so off-diag magnitude
= diagonal d(v)).  Hence Gershgorin (c)  <=>  (N - T_v) + d(v) >= d(v)  <=>  N - T_v >= 0  <=>  T_v <= N.
So (c) is EXACTLY the statement T_v <= N for all v.  We test that directly too (it is the classic deficit bound).

We report which of (a),(b),(c) hold / fail and the first counterexample, plus the T_v<=N status.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _hardy_gate import BETA, build_H, cycle_laplacian_add


def lstar_diag_and_offmag(n, M, ell, cyc, betamap):
    """Return (d, offmag) where d[v] = Lstar diagonal at v, offmag[v] = sum_{w!=v} |Lstar[v][w]|.
       Built directly from cycle Laplacians (exact Fraction)."""
    d = [F(0)] * n
    offmag = [F(0)] * n
    # also build full Lstar to read off-diagonals exactly
    Lstar = [[F(0)] * n for _ in range(n)]
    for f in M:
        Qs = cyc[f]; L = ell[f]
        w = betamap[L] / len(Qs)
        for Q in Qs:
            LQ = [[F(0)] * n for _ in range(n)]
            cycle_laplacian_add(LQ, list(Q))
            for a in set(Q):
                for b in set(Q):
                    if LQ[a][b] != 0:
                        Lstar[a][b] += w * LQ[a][b]
    for v in range(n):
        d[v] = Lstar[v][v]
        offmag[v] = sum(abs(Lstar[v][w]) for w in range(n) if w != v)
    return d, offmag, Lstar


def test_cut(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    if not M:
        return
    acc['cuts'] += 1
    N = F(n)
    d, offmag, Lstar = lstar_diag_and_offmag(n, M, ell, cyc, BETA)
    # build full H to cross-check Gershgorin directly on H
    H = build_H(n, M, ell, T, cyc, BETA)
    for v in range(n):
        deficit = T[v] - N          # overload (positive => T_v > N)
        # (a)  T_v - N <= d(v)
        if deficit > d[v]:
            acc['a_fail'] += 1
            if acc['a_ex'] is None:
                acc['a_ex'] = (name, n, v, str(deficit), str(d[v]))
        # (b)  (T_v-N)_+ <= d(v)/2
        pos = deficit if deficit > 0 else F(0)
        if pos > d[v] / 2:
            acc['b_fail'] += 1
            if acc['b_ex'] is None:
                acc['b_ex'] = (name, n, v, str(pos), str(d[v] / 2))
        # (c) Gershgorin on H:  H[v][v] >= sum_{w!=v}|H[v][w]|
        Hvv = H[v][v]
        offH = sum(abs(H[v][w]) for w in range(n) if w != v)
        if Hvv < offH:
            acc['c_fail'] += 1
            if acc['c_ex'] is None:
                acc['c_ex'] = (name, n, v, str(Hvv), str(offH))
        # T_v <= N  (the classic deficit bound; equals Gershgorin per the docstring identity)
        if T[v] > N:
            acc['Tgt_fail'] += 1
            if acc['Tgt_ex'] is None:
                acc['Tgt_ex'] = (name, n, v, str(T[v]), str(n))
            # record max overload margin
            over = T[v] - N
            if acc['max_over'] is None or over > acc['max_over']:
                acc['max_over'] = over; acc['max_over_ex'] = (name, n, v, str(T[v]))
        # sanity: offmag of Lstar should equal d[v] (Laplacian row identity)
        if offmag[v] != d[v]:
            acc['lap_ident_fail'] += 1


def gfam(name, n, E, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    try:
        _, cuts = gmins(n, E)
    except Exception:
        return
    for side in cuts:
        test_cut(name, n, adj, side, acc)


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
    acc = dict(cuts=0, a_fail=0, b_fail=0, c_fail=0, Tgt_fail=0, lap_ident_fail=0,
               a_ex=None, b_ex=None, c_ex=None, Tgt_ex=None, max_over=None, max_over_ex=None)
    print("beta_5' =", float(BETA[5]), " beta_7' =", float(BETA[7]), flush=True)

    # focused required graphs first
    # H?AFBo] gamma-min cut N=9 (Gamma=50) -- via census N=9 (gmins enumerates gamma-min cuts)
    # C5[2] N=10, C5[3] N=15 (tight extremal)
    for sizes in [(2,1,2,1,2), (3,2,3,3,3)]:
        nn, EE = odd_blowup(5, list(sizes))
        gfam("C5blow%s" % (sizes,), nn, EE, acc)
    # explicit C5[3] = all parts size 3 -> N=15
    nn, EE = odd_blowup(5, [3,3,3,3,3])
    gfam("C5_3_N15", nn, EE, acc)
    print("after C5 blowups: cuts=%d a_fail=%d b_fail=%d c_fail=%d Tgt_fail=%d"
          % (acc['cuts'], acc['a_fail'], acc['b_fail'], acc['c_fail'], acc['Tgt_fail']), flush=True)

    # census N=8,9 (gives the H?AFBo]-type gamma-min cuts and two census N=8/9 graphs)
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d a_fail=%d b_fail=%d c_fail=%d Tgt_fail=%d"
              % (nn, acc['cuts'], acc['a_fail'], acc['b_fail'], acc['c_fail'], acc['Tgt_fail']), flush=True)

    # glued chains
    for q in range(2, 12):
        n, E, side = glued_c5_chain(q)
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        if Bconn(n, adj, side):
            test_cut("chain_q%d" % q, n, adj, side, acc)

    # Myc(Grotzsch) N=23 guardrail
    grN, grE = mycielski(5, Cn(5)); gfam("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    if Bconn(m2N, adj, side):
        test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after chains+Grotzsch+Myc23: cuts=%d a_fail=%d b_fail=%d c_fail=%d Tgt_fail=%d"
          % (acc['cuts'], acc['a_fail'], acc['b_fail'], acc['c_fail'], acc['Tgt_fail']), flush=True)

    # randoms N=11/12
    rng = random.Random(7); made = 0; tries = 0
    while made < 60 and tries < 30000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam("rand%d" % made, nn, EE, acc)

    print("=" * 64)
    print("total gamma-min cuts tested:", acc['cuts'], " (random N11/12 graphs:", made, ")")
    print("Laplacian row-identity check (offmag==d) failures:", acc['lap_ident_fail'])
    print("(a)  T_v - N <= d(v)           : FAILURES =", acc['a_fail'], acc['a_ex'] or '')
    print("(b)  (T_v-N)_+ <= d(v)/2       : FAILURES =", acc['b_fail'], acc['b_ex'] or '')
    print("(c)  GERSHGORIN H[v][v]>=offrow: FAILURES =", acc['c_fail'], acc['c_ex'] or '')
    print("     T_v <= N (deficit bound)  : FAILURES =", acc['Tgt_fail'], acc['Tgt_ex'] or '')
    print("     max overload (T_v - N)    :", acc['max_over'], "at", acc['max_over_ex'])
    print("VERDICT:")
    if acc['c_fail'] == 0:
        print("  GERSHGORIN (c) HOLDS on full battery => ELEMENTARY proof of (H). But check: is c equivalent to T_v<=N?")
    else:
        print("  GERSHGORIN (c) FAILS =>", acc['c_fail'], "vertices; per-vertex localization insufficient, need real cancellation.")
    if acc['a_fail'] == 0:
        print("  (a) holds: deficit T_v-N dominated by incident cycle diagonal d(v) on full battery.")
    else:
        print("  (a) FAILS.")


if __name__ == "__main__":
    main()
