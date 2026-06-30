"""DEEP characterization: confirm the L=Lmax selector and the square-surplus mechanism, with a wider stress net.

Builds on _mech_selector_char.py (Q1: R<0 => strictly mixed; Q4: descent witness ALWAYS at L=Lmax, 56/56).
Here:
  (A) confirm the random N=11/12 batch is actually exercised (count distinct R<0 sites contributed by randoms),
      and widen randoms (more seeds, denser) + add bigger overloaded blowups to grow the R<0 sample.
  (B) refine the deterministic selector: at L=Lmax, does EITHER orientation's prefix/suffix work, or is a
      specific orientation/kind forced?  Record per-site which (orient,kind) at Lmax give a Gamma-decreasing
      neutral B-connected switch.
  (C) confirm the square-surplus MECHANISM: for the best Lmax-witness S, report the Psi decomposition via the
      proven identity Gamma(before)-Gamma(after)=drop, and verify drop <= Lmax^2 (the long bad edge's square is
      an upper envelope on the surplus per long crossing edge), and drop>0.  Also report Lmax^2 - Lmin^2.
Exact Fraction throughout.  Reuse shared infra unmodified.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
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


def lenbundle_at_L(v, M, ell, cyc, L):
    rows = []
    for f in M:
        if ell[f] != L:
            continue
        for Q in cyc[f]:
            if v in Q:
                rows.append(list(Q))
    out = []
    for orient in (0, 1):
        pref = set(); suff = set()
        for Q in rows:
            q = Q if orient == 0 else Q[::-1]
            i = q.index(v)
            pref.update(q[:i + 1])
            suff.update(q[i:])
        out.append((orient, 'pref', frozenset(pref)))
        out.append((orient, 'suff', frozenset(suff)))
    return out


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


def Lset_of_v(v, M, ell, cyc):
    s = set()
    for f in M:
        for Q in cyc[f]:
            if v in Q:
                s.add(ell[f]); break
    return s


def test_cut(name, n, adj, side, acc, source):
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
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        acc['by_source'][source] = acc['by_source'].get(source, 0) + 1
        Ls = Lset_of_v(v, M, ell, cyc)
        Lmin = min(Ls); Lmax = max(Ls)
        if Lmax <= Lmin:
            acc['notmixed'] += 1
            continue
        # selector at L=Lmax
        sws = lenbundle_at_L(v, M, ell, cyc, Lmax)
        good = []  # (orient,kind,drop)
        for (orient, kind, Sset) in sws:
            if v not in Sset or len(Sset) == 0 or len(Sset) == n:
                continue
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, Sset)
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                good.append((orient, kind, gamma0 - g2))
        if not good:
            acc['Lmax_fail'] += 1
            if acc['ex_Lmaxfail'] is None:
                acc['ex_Lmaxfail'] = (name, n, ''.join(map(str, side)), v, str(R[v]), 'Lmax=%d' % Lmax)
            continue
        acc['Lmax_ok'] += 1
        # which (orient,kind) work?
        kinds = set((o, k) for (o, k, d) in good)
        acc['kind_combo_hist'][tuple(sorted(kinds))] = acc['kind_combo_hist'].get(tuple(sorted(kinds)), 0) + 1
        bestdrop = max(d for (o, k, d) in good)
        # (C) surplus envelope: drop>0 and drop<=Lmax^2 ; record Lmax^2-Lmin^2
        if bestdrop <= 0:
            acc['drop_nonpos'] += 1
        if bestdrop <= F(Lmax * Lmax):
            acc['drop_le_Lmax2'] += 1
        else:
            acc['drop_gt_Lmax2'] += 1
            if acc['ex_dropbig'] is None:
                acc['ex_dropbig'] = (name, v, str(bestdrop), Lmax)
        surplus = F(Lmax * Lmax - Lmin * Lmin)
        acc['surplus_pos'] += 1 if surplus > 0 else 0
        # does best drop ever exceed the naive single-edge surplus Lmax^2-Lmin^2? (record both)
        acc['drop_samples'].append((bestdrop, Lmax, Lmin))


def gfam_allmax(name, n, E, acc, source):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc, source)


def maxcut_ls(n, adj, seeds=80, seed=9):
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
    acc = dict(neg=0, notmixed=0, Lmax_ok=0, Lmax_fail=0, drop_nonpos=0,
               drop_le_Lmax2=0, drop_gt_Lmax2=0, surplus_pos=0,
               kind_combo_hist={}, by_source={}, drop_samples=[],
               ex_Lmaxfail=None, ex_dropbig=None)
    # census
    for nn in range(8, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc, 'census')
        print("census N=%d: neg=%d Lmax_ok=%d Lmax_fail=%d" % (nn, acc['neg'], acc['Lmax_ok'], acc['Lmax_fail']), flush=True)
    # bigger overloaded blowups (multiple non-uniform max cuts via maxcut_ls with several seeds)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(3,1,3,1,3),(4,2,4,2,4),(2,2,2,2,3),(3,2,3,1,2)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 15:
            gfam_allmax("blow%s" % (sizes,), nn, EE, acc, 'blowup')
        else:
            adj = [set() for _ in range(nn)]
            for x, y in EE:
                adj[x].add(y); adj[y].add(x)
            for sd in (1, 3, 5, 7, 11):
                side = maxcut_ls(nn, adj, seeds=60, seed=sd)
                test_cut("blowLS%s_s%d" % (sizes, sd), nn, adj, side, acc, 'blowup')
    print("after blowups: neg=%d Lmax_ok=%d Lmax_fail=%d" % (acc['neg'], acc['Lmax_ok'], acc['Lmax_fail']), flush=True)
    # glued island
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam_allmax("isl", nn, EE, acc, 'island')
    # WIDE randoms: more seeds, vary density, N up to 13
    rng = random.Random(123); made = 0; tries = 0
    while made < 400 and tries < 200000:
        tries += 1
        nn = rng.choice([11, 12, 13]); p = rng.uniform(0.14, 0.36)
        EE = [(a, b) for a in range(nn) for b in range(a+1, nn) if rng.random() < p]
        if not EE or not is_triangle_free(nn, EE):
            continue
        adj = [set() for _ in range(nn)]
        for a, b in EE:
            adj[a].add(b); adj[b].add(a)
        if any(len(adj[v]) == 0 for v in range(nn)):
            continue
        made += 1; gfam_allmax("rand%d" % made, nn, EE, acc, 'random')
    print("randoms made=%d (tries=%d): neg now=%d  random-contributed=%d" %
          (made, tries, acc['neg'], acc['by_source'].get('random', 0)), flush=True)

    print("=" * 70)
    print("R[v]<0 sites total:", acc['neg'], " by source:", acc['by_source'])
    print("notmixed (Lmax<=Lmin):", acc['notmixed'])
    print("SELECTOR L=Lmax: ok=%d  FAIL=%d  %s" % (acc['Lmax_ok'], acc['Lmax_fail'], acc['ex_Lmaxfail'] or ''))
    print("which (orient,kind) combos succeed at Lmax (histogram):")
    for k, c in sorted(acc['kind_combo_hist'].items(), key=lambda x: -x[1]):
        print("    %s : %d" % (k, c))
    print("MECHANISM: best-drop>0 always (nonpos count=%d); drop<=Lmax^2: %d  drop>Lmax^2: %d %s" %
          (acc['drop_nonpos'], acc['drop_le_Lmax2'], acc['drop_gt_Lmax2'], acc['ex_dropbig'] or ''))
    # surplus comparison
    ge = sum(1 for (d, lmx, lmn) in acc['drop_samples'] if d >= F(lmx*lmx - lmn*lmn))
    print("best-drop >= Lmax^2-Lmin^2 (square-surplus pays):", ge, "/", len(acc['drop_samples']))
    print("-" * 70)
    ok = (acc['Lmax_fail'] == 0 and acc['notmixed'] == 0 and acc['drop_nonpos'] == 0)
    print("VERDICT selector [L=Lmax(v), some (orient,kind)] covers EVERY R<0 site, all drops>0:",
          "HOLDS 0-fail (neg=%d)" % acc['neg'] if ok else "FALSE")


if __name__ == "__main__":
    main()
