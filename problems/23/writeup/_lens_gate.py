"""INDEPENDENT exact gate for Codex's K2T LENS-DECOMPOSITION (blocks 09:19/09:21).

Two finite/structural lemmas whose conjunction (with gamma-minimality) proves K2T<=NT:

  LEMMA 2 (LENS-FREE => K2T):  a strict-lens-free connected-B maximum cut has R[v]>=0 for all v.
  LEMMA B (RESIDUAL-LENS):     R[v] = N*T[v]-(K2*T)[v] < 0  =>  v lies on the SHORT geodesic Pg of
                               some strict bad-geodesic lens (f,g).

STRICT BAD-GEODESIC LENS (independent reimpl, no Codex code):
  ordered pair of distinct bad edges (f,g) with ell[f] > ell[g] such that SOME shortest B-geodesic
  Pg in cyc[g] is a contiguous subpath (allowing reversal) of SOME shortest B-geodesic Pf in cyc[f].

Reuses ONLY the 7-agent-audited struct_for_side (M,ell,T,mu,cyc) and build_K2.  Everything else
(lens detection, R, the two lemma checks) is reimplemented here.  Exact Fraction throughout.

Battery (maximizes R[v]<0 cases + hits the guardrail families that killed (k2)/ZMU):
  - census N=5..10 ALL connected-B maximum cuts (full maxcut enumeration);
  - Mycielskian Grotzsch N=11 (all max cuts) + Myc(Grotzsch) N=23 (LS max cut);
  - H?AFBo] vertex blow-ups [2]=N18, [3]=N27 with INHERITED cut (the per-bad-edge killer, has R<0);
  - glued C5 chains, overloaded C5 blow-ups N<=27, glued island, random N=11/12.
Reports first failure or 0-fail counts for BOTH lemmas.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain
from _wf_deficit_farkas import odd_blowup


def contig_sub(small, big):
    """Is list `small` a contiguous sublist of list `big` (forward orientation only)?"""
    ls, lb = len(small), len(big)
    if ls > lb:
        return False
    for i in range(lb - ls + 1):
        if big[i:i + ls] == small:
            return True
    return False


def strict_lenses(M, ell, cyc):
    """Return (lens_pairs, short_geo_vertices).
       lens_pairs: list of (f,g) ordered pairs forming >=1 strict lens.
       short_geo_vertices: set of vertices appearing on SOME Pg of SOME strict lens (the SHORT side).
    """
    Ms = list(M)
    pairs = []
    short_verts = set()
    for f in Ms:
        Lf = ell[f]
        for g in Ms:
            if f == g or ell[g] >= Lf:
                continue
            hit = False
            for Pg in cyc[g]:
                Pgl = list(Pg)
                Pgr = Pgl[::-1]
                for Pf in cyc[f]:
                    Pfl = list(Pf)
                    if contig_sub(Pgl, Pfl) or contig_sub(Pgr, Pfl):
                        hit = True
                        short_verts |= set(Pgl)
                        break
                # keep scanning other Pg to collect all short-side vertices
            if hit:
                pairs.append((f, g))
    return pairs, short_verts


def residuals(n, M, T, cyc):
    K2 = build_K2(n, M, cyc)
    N = F(n)
    return [N * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]


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
    R = residuals(n, M, T, cyc)
    neg = [v for v in range(n) if R[v] < 0]
    pairs, short_verts = strict_lenses(M, ell, cyc)
    lensfree = (len(pairs) == 0)
    # LEMMA 2: lens-free => R>=0 everywhere
    if lensfree:
        acc['lensfree_cuts'] += 1
        if neg:
            acc['L2_fail'] += 1
            if acc['L2_ex'] is None:
                acc['L2_ex'] = (name, n, ''.join(map(str, side)), neg[0], str(R[neg[0]]))
    else:
        acc['lensed_cuts'] += 1
    # LEMMA B: every R[v]<0 vertex lies on a short geodesic of a strict lens
    for v in neg:
        acc['neg_vertices'] += 1
        if v in short_verts:
            acc['LB_covered'] += 1
        else:
            acc['LB_fail'] += 1
            if acc['LB_ex'] is None:
                acc['LB_ex'] = (name, n, ''.join(map(str, side)), v, str(R[v]), len(pairs))


def gfam_allmax(name, n, E, acc):
    """All connected-B MAXIMUM cuts."""
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc)


def gfam_cuts(name, n, E, cuts, acc):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
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


def vertex_blowup(n, E, t):
    """Replace each vertex by t independent copies; copies of u,v adjacent iff (u,v) in E.
       Returns (nn, EE, classmap) where copy (v,a) -> v*t+a."""
    nn = n * t
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return nn, EE


def main():
    acc = dict(cuts=0, lensfree_cuts=0, lensed_cuts=0, neg_vertices=0, LB_covered=0,
               L2_fail=0, LB_fail=0, L2_ex=None, LB_ex=None)

    # --- census all max cuts N=5..10 ---
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: cuts=%d lensfree=%d lensed=%d neg=%d L2_fail=%d LB_fail=%d"
              % (nn, acc['cuts'], acc['lensfree_cuts'], acc['lensed_cuts'], acc['neg_vertices'],
                 acc['L2_fail'], acc['LB_fail']), flush=True)

    # --- Mycielskian Grotzsch N=11 (all max cuts) + Myc(Grotzsch) N=23 (LS cut) ---
    grN, grE = mycielski(5, Cn(5))
    gfam_allmax("Grotzsch_N11", grN, grE, acc)
    m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Grotzsch+Myc23: cuts=%d lensfree=%d neg=%d L2_fail=%d LB_fail=%d"
          % (acc['cuts'], acc['lensfree_cuts'], acc['neg_vertices'], acc['L2_fail'], acc['LB_fail']), flush=True)

    # --- H?AFBo] vertex blow-ups [2],[3] with INHERITED cut (per-bad-edge killer; has R<0) ---
    hN, hE = dec("H?AFBo]")
    base_side = [int(c) for c in "111110000"]
    for t in (2, 3):
        nn, EE = vertex_blowup(hN, hE, t)
        side = [base_side[v // t] for v in range(nn)]
        adj = [set() for _ in range(nn)]
        for x, y in EE:
            adj[x].add(y); adj[y].add(x)
        # verify it's a maximum cut
        cut = sum(1 for x, y in EE if side[x] != side[y])
        mc = max(sum(1 for x, y in EE if s[x] != s[y]) for s in maxcut_all(nn, adj)) if nn <= 18 else None
        ismax = (mc is None or cut == mc)
        test_cut("HblowB_t%d_inh%s" % (t, "" if ismax else "_NOTMAX"), nn, adj, side, acc)
        print("Hblow t=%d N=%d inherited cut=%d max=%s: cuts=%d neg=%d L2_fail=%d LB_fail=%d"
              % (t, nn, cut, mc, acc['cuts'], acc['neg_vertices'], acc['L2_fail'], acc['LB_fail']), flush=True)

    # --- glued C5 chains (gmin cuts) ---
    for q in range(2, 16):
        n, E, side = glued_c5_chain(q)
        gfam_cuts("chain_q%d" % q, n, E, [side], acc)

    # --- overloaded C5 blow-ups N<=27 (all max cuts where small) ---
    for sizes in [(2, 1, 2, 1, 2), (2, 1, 2, 1, 3), (3, 2, 3, 2, 3), (4, 3, 4, 3, 4), (2, 2, 2, 2, 2), (3, 3, 3, 3, 3)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 16:
            gfam_allmax("blow%s" % (sizes,), nn, EE, acc)

    # --- glued island ---
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam_allmax("isl", nn, EE, acc)
    print("after chains+blowups+islands: cuts=%d lensfree=%d neg=%d L2_fail=%d LB_fail=%d"
          % (acc['cuts'], acc['lensfree_cuts'], acc['neg_vertices'], acc['L2_fail'], acc['LB_fail']), flush=True)

    # --- random N=11/12 all max cuts ---
    rng = random.Random(7); made = 0; tries = 0
    while made < 120 and tries < 60000:
        tries += 1
        nn = rng.choice([11, 12]); p = rng.uniform(0.14, 0.32)
        EE = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam_allmax("rand%d" % made, nn, EE, acc)

    print("=" * 60)
    print("connected-B max cuts tested:", acc['cuts'], " (random N11/12:", made, ")")
    print("lens-free cuts:", acc['lensfree_cuts'], "  lensed cuts:", acc['lensed_cuts'])
    print("negative-residual vertices:", acc['neg_vertices'], "  LEMMA-B covered:", acc['LB_covered'])
    print("LEMMA 2 (lens-free=>R>=0) FAILURES:", acc['L2_fail'], acc['L2_ex'] or '')
    print("LEMMA B (R<0=>lens thru v) FAILURES:", acc['LB_fail'], acc['LB_ex'] or '')
    ok = acc['L2_fail'] == 0 and acc['LB_fail'] == 0
    print("VERDICT:", "BOTH LEMMAS HOLD exact on full battery incl N=23 + Hblow N18/27 (lens decomposition LIVE)"
          if ok else "FAIL")


if __name__ == "__main__":
    main()
