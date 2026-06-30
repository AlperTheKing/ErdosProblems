"""HARD counterexample hunt for the SOLE OPEN LEMMA (LB) of Erdos #23.

(LB):  For a connected-B MAX cut (not nec. gamma-min) and a vertex v with R[v]=N*T[v]-(K2*T)[v] < 0,
       the LENGTH-BUNDLE half-switch family through v contains a switch S with:
         v in S, neutral (delta_B(S)=delta_M(S)), B-connected after flip, Gamma(after) < Gamma(before).
A SINGLE exact counterexample (a R[v]<0 site with NO such switch) BREAKS the route.

This hunt MANUFACTURES DIVERSE R[v]<0 sites (validated previously only on H?AFBo]+blowups, a thin base):
 (1) ALL connected-B max cuts on census N<=11 -> filter to R[v]<0 sites, test (LB) on every neg vertex.
 (2) vertex-blowups [2,3,4] of EVERY census graph (N<=9) that has an R<0 max cut.
 (3) glued/bridged combos of two DIFFERENT odd gadgets (C5+C7, Grotzsch+C5, C7+C9, ...).
 (4) Mycielskians of mixed graphs.
 (5) 1000+ random triangle-free N=11..15, scanning ALL max cuts for R<0.

Independent reimpl of struct/K2/R/switch; reuse SHARED gates (_h, _satzmu_conn, _csmspec) read-only.
Exact Fraction for any pass/fail claim.  Run: python _lb_counterhunt.py
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _wf_deficit_farkas import odd_blowup


# ---------------- switch machinery (independent reimpl) ----------------
def gamma_of(n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return F(0)
    M, ell = st[0], st[1]
    return sum(ell[f] * ell[f] for f in M)


def boundary_delta(n, adj, side, Sset):
    dB = dM = 0
    for u in Sset:
        for w in adj[u]:
            if w in Sset:
                continue
            if side[u] != side[w]:
                dB += 1
            else:
                dM += 1
    return dB - dM


def lenbundle_switches(v, M, ell, cyc):
    bylen = {}
    for f in M:
        L = ell[f]
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(L, []).append(list(Q))
    out = set()
    for L, rows in bylen.items():
        for orient in (0, 1):
            pref = set(); suff = set()
            for Q in rows:
                q = Q if orient == 0 else Q[::-1]
                i = q.index(v)
                pref.update(q[:i + 1])
                suff.update(q[i:])
            out.add(frozenset(pref))
            out.add(frozenset(suff))
    return out


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


# ---------------- per-cut (LB) test ----------------
def test_cut(name, n, adj, side, acc, track_blowup=None):
    """Test (LB) on every R[v]<0 vertex of this (connected-B) max cut.
    track_blowup: optional set to collect names of graphs that produced an R<0 site (for stage 2)."""
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
    # record length-multiplicity signature (diversity diagnostic)
    lens = sorted(set(ell[f] for f in M))
    acc['len_sigs'].add(tuple(lens))
    if track_blowup is not None:
        track_blowup.add(name)
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        covered = False
        best_drop = None
        for Sset in lenbundle_switches(v, M, ell, cyc):
            if v not in Sset or len(Sset) == 0 or len(Sset) == n:
                continue
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, Sset)
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                covered = True
                best_drop = gamma0 - g2
                break
        if covered:
            acc['covered'] += 1
            acc['drop_hist'][best_drop] = acc['drop_hist'].get(best_drop, 0) + 1
        else:
            acc['fail'] += 1
            if acc['ex'] is None:
                acc['ex'] = (name, n, ''.join(map(str, side)), v, str(R[v]),
                             "mixedlens=%s" % (tuple(lens),))
                print("  *** (LB) COUNTEREXAMPLE *** %s N=%d side=%s v=%d R=%s lens=%s"
                      % (name, n, ''.join(map(str, side)), v, R[v], tuple(lens)), flush=True)


def gfam_allmax(name, n, E, acc, track_blowup=None):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc, track_blowup)


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


def maxcut_ls(n, adj, seeds=120, seed=9):
    best = None; bv = -1; rng = random.Random(seed)
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
    acc = dict(bad_cuts=0, neg=0, covered=0, fail=0, drop_hist={}, ex=None, len_sigs=set())

    # ---- STAGE 1: ALL max cuts, census; FULL N<=10, SAMPLED N=11 (90842 graphs too many to
    #              brute all-max-cuts exactly).  Remember R<0-producing graphs for blowups. ----
    r0_graphs = {}  # nn -> list of (g6, n, E)
    rng_cen = random.Random(31337)
    for nn in range(5, 12):
        outg = subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split()
        if nn == 11:
            # sample 6000 of the 90842 connected triangle-free graphs for the heavy all-max-cuts scan
            rng_cen.shuffle(outg)
            outg = outg[:6000]
        r0_graphs[nn] = []
        for g6 in outg:
            n, E = dec(g6)
            tb = set()
            gfam_allmax("cen%d:%s" % (nn, g6), n, E, acc, track_blowup=tb)
            if tb:
                r0_graphs[nn].append((g6, n, E))
        print("census N=%d (%d graphs%s): bad_cuts=%d neg=%d covered=%d fail=%d  (R<0 graphs this N: %d)"
              % (nn, len(outg), " sampled" if nn == 11 else "", acc['bad_cuts'], acc['neg'],
                 acc['covered'], acc['fail'], len(r0_graphs[nn])),
              flush=True)

    # ---- STAGE 2: vertex-blowups [2,3,4] of EVERY census graph that had an R<0 max cut (N<=9) ----
    blown = 0
    for nn in range(5, 10):
        for (g6, n, E) in r0_graphs.get(nn, []):
            for t in (2, 3, 4):
                bn, BE = vertex_blowup(n, E, t)
                if bn > 30:
                    continue
                blown += 1
                gfam_allmax("blow_t%d:%s" % (t, g6), bn, BE, acc)
    print("after blowups of R<0 census graphs (%d blow-instances): bad_cuts=%d neg=%d covered=%d fail=%d %s"
          % (blown, acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)

    # ---- STAGE 3: glued/bridged combos of two DIFFERENT odd gadgets ----
    gadgets = {
        'C5': (5, Cn(5)),
        'C7': (7, Cn(7)),
        'C9': (9, Cn(9)),
        'C11': (11, Cn(11)),
        'Grotzsch': mycielski(5, Cn(5)),  # N=11
        'MycC7': mycielski(7, Cn(7)),      # N=15
    }
    pairs = [('C5', 'C7'), ('C5', 'C9'), ('C7', 'C9'), ('C5', 'C11'), ('C7', 'C11'),
             ('Grotzsch', 'C5'), ('Grotzsch', 'C7'), ('C5', 'MycC7'), ('C7', 'MycC7'),
             ('C9', 'C11'), ('Grotzsch', 'C9')]
    for an, bn_ in pairs:
        (na, Ea), (nb, Eb) = gadgets[an], gadgets[bn_]
        if na + nb > 28:
            continue
        # single bridge, double bridge (different offsets) -> mixed lengths near the join
        for bridges in ([(0, na)], [(0, na), (1, na + 1)], [(0, na + 2)]):
            n, E = union_disjoint((na, Ea), (nb, Eb))
            n, E = add_edges((n, E), bridges)
            if not is_triangle_free(n, E):
                continue
            if n <= 13:
                gfam_allmax("glue_%s_%s_%s" % (an, bn_, bridges), n, E, acc)
            else:
                adj = [set() for _ in range(n)]
                for x, y in E:
                    adj[x].add(y); adj[y].add(x)
                for seed in range(6):
                    side = maxcut_ls(n, adj, seeds=80, seed=seed)
                    test_cut("glue_%s_%s_%s_s%d" % (an, bn_, bridges, seed), n, adj, side, acc)
    print("after glued gadget combos: bad_cuts=%d neg=%d covered=%d fail=%d %s"
          % (acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)

    # ---- STAGE 4: Mycielskians of mixed graphs ----
    myc_bases = []
    # mixed base: C5 + C7 bridged, then Mycielskian
    n, E = union_disjoint((5, Cn(5)), (7, Cn(7)))
    n, E = add_edges((n, E), [(0, 5)])
    myc_bases.append(('C5_C7_bridge', n, E))
    # mixed base: C5 + C9 bridged
    n, E = union_disjoint((5, Cn(5)), (9, Cn(9)))
    n, E = add_edges((n, E), [(0, 5)])
    myc_bases.append(('C5_C9_bridge', n, E))
    for bname, bn_, BE in myc_bases:
        mn, ME = mycielski(bn_, BE)
        if mn > 32 or not is_triangle_free(mn, ME):
            continue
        adj = [set() for _ in range(mn)]
        for x, y in ME:
            adj[x].add(y); adj[y].add(x)
        for seed in range(8):
            side = maxcut_ls(mn, adj, seeds=100, seed=seed)
            test_cut("Myc_%s_s%d" % (bname, seed), mn, adj, side, acc)
    print("after Mycielskians of mixed bases: bad_cuts=%d neg=%d covered=%d fail=%d %s"
          % (acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''), flush=True)

    # ---- STAGE 5: 1000+ random triangle-free N=11..15, ALL max cuts (small) / LS cuts (large) ----
    rng = random.Random(20250630); made = 0; tries = 0
    while made < 1200 and tries < 400000:
        tries += 1
        nn = rng.choice([11, 12, 13, 14, 15])
        p = rng.uniform(0.12, 0.34)
        EE = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1
        if nn <= 12:
            gfam_allmax("rand%d" % made, nn, EE, acc)
        else:
            # N=13..15: brute maxcut_all is 2^(n-1) <= 16384, still cheap; use it for completeness
            gfam_allmax("rand%d" % made, nn, EE, acc)
        if acc['fail']:
            break
    print("after %d random N=11..15 (tries=%d): bad_cuts=%d neg=%d covered=%d fail=%d %s"
          % (made, tries, acc['bad_cuts'], acc['neg'], acc['covered'], acc['fail'], acc['ex'] or ''),
          flush=True)

    print("=" * 64)
    print("distinct bad cuts (some R[v]<0):", acc['bad_cuts'])
    print("distinct mixed-length signatures seen at R<0 sites:", sorted(acc['len_sigs']))
    print("negative-residual vertices tested:", acc['neg'],
          " COVERED by neutral B-conn Gamma-DECREASING length-bundle switch:", acc['covered'])
    print("(LB) FAILURES (counterexamples):", acc['fail'], acc['ex'] or '')
    print("Gamma-drop histogram:", dict(sorted(acc['drop_hist'].items())))
    ok = acc['fail'] == 0 and acc['neg'] > 0
    print("VERDICT:", ("(LB) HOLDS on diverse hunt: every R[v]<0 site has a neutral B-conn Gamma-DECREASING "
                       "length-bundle switch; NO counterexample found." if ok
                       else ("(LB) COUNTEREXAMPLE FOUND -- ROUTE BREAKS: %s" % (acc['ex'],) if acc['fail']
                             else "NO R<0 SITES PRODUCED (inconclusive)")))


if __name__ == "__main__":
    main()
