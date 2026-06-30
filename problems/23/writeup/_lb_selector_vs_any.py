"""DIVERSE hunt distinguishing two claims at every R[v]<0 site (max cut, not nec. gamma-min):
  (A) LENGTH-BUNDLE selector:  does the length-bundle half-switch family through v contain a neutral
      B-conn Gamma-DECREASING switch?   [the SELECTOR as written in the LB lemma]
  (B) ANY neutral switch:      does ANY neutral B-conn switch through v (|S|<=6) decrease Gamma?
      [the DESCENT MECHANISM -- weaker selector requirement]

A true BREAK of the descent route = a site where (B) FAILS (no neutral Gamma-drop switch exists at all).
A SELECTOR gap = a site where (A) fails but (B) holds (length-bundle too narrow; witness exists elsewhere).

Diverse R<0 sites: ALL max cuts on census N<=10 + sampled N=11; ALL max cuts on t=2/t=3 blowups of the
R<0-producing census graphs; glued odd-gadget combos; randoms N=11..14.  Exact Fraction.
Run: python _lb_selector_vs_any.py
"""
import subprocess, random, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free


def vertex_blowup(n, E, t):
    EE = []
    for (u, v) in E:
        for a in range(t):
            for b in range(t):
                EE.append((u * t + a, v * t + b))
    return n * t, EE


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


def lb_covered(n, adj, side, v, M, ell, cyc, gamma0):
    for Sset in lenbundle_switches(v, M, ell, cyc):
        if v not in Sset or len(Sset) in (0, n):
            continue
        if boundary_delta(n, adj, side, Sset) != 0:
            continue
        s2 = flip(side, Sset)
        g2 = gamma_of(n, adj, s2)
        if g2 is not None and g2 < gamma0:
            return int(gamma0 - g2)
    return None


def any_covered(n, adj, side, v, gamma0, maxsize=6):
    others = [u for u in range(n) if u != v]
    for k in range(0, maxsize):
        for combo in itertools.combinations(others, k):
            Sset = frozenset((v,) + combo)
            if boundary_delta(n, adj, side, Sset) != 0:
                continue
            s2 = flip(side, list(Sset))
            if not Bconn(n, adj, s2):
                continue
            g2 = gamma_of(n, adj, s2)
            if g2 is not None and g2 < gamma0:
                return int(gamma0 - g2)
    return None


def test_cut(name, n, adj, side, acc, any_size=6):
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
    acc['len_sigs'].add(tuple(sorted(set(ell.values()))))
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        lb = lb_covered(n, adj, side, v, M, ell, cyc, gamma0)
        if lb is not None:
            acc['lb_cov'] += 1
            continue
        # length-bundle FAILED -> escalate to ANY neutral switch
        acc['lb_miss'] += 1
        an = any_covered(n, adj, side, v, gamma0, maxsize=any_size)
        if an is not None:
            acc['any_cov'] += 1
            if acc['first_selgap'] is None:
                acc['first_selgap'] = (name, n, ''.join(map(str, side)), v, str(R[v]), an)
        else:
            acc['any_miss'] += 1
            if acc['first_break'] is None:
                acc['first_break'] = (name, n, ''.join(map(str, side)), v, str(R[v]),
                                      tuple(sorted(set(ell.values()))), int(gamma0))
                print("  *** TRUE BREAK CANDIDATE *** %s N=%d v=%d R=%s lens=%s : NO neutral Gamma-drop switch |S|<=%d"
                      % (name, n, v, R[v], tuple(sorted(set(ell.values()))), any_size), flush=True)


def gfam_allmax(name, n, E, acc, any_size=6):
    adj = [set() for _ in range(n)]
    for x, y in E:
        adj[x].add(y); adj[y].add(x)
    for side in maxcut_all(n, adj):
        test_cut(name, n, adj, side, acc, any_size)
        if acc['first_break']:
            return


def main():
    acc = dict(bad_cuts=0, neg=0, lb_cov=0, lb_miss=0, any_cov=0, any_miss=0,
               first_selgap=None, first_break=None, len_sigs=set())

    # census all-max-cuts, full N<=10, sampled N=11; remember R<0 graphs
    r0 = {}
    rng = random.Random(31337)
    for nn in range(5, 12):
        outg = subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split()
        if nn == 11:
            rng.shuffle(outg); outg = outg[:5000]
        r0[nn] = []
        for g6 in outg:
            n, E = dec(g6)
            before = acc['bad_cuts']
            gfam_allmax("cen%d:%s" % (nn, g6), n, E, acc)
            if acc['bad_cuts'] > before:
                r0[nn].append((g6, n, E))
            if acc['first_break']:
                break
        print("census N=%d: bad_cuts=%d neg=%d lb_cov=%d lb_miss=%d any_cov=%d any_miss=%d"
              % (nn, acc['bad_cuts'], acc['neg'], acc['lb_cov'], acc['lb_miss'], acc['any_cov'], acc['any_miss']),
              flush=True)
        if acc['first_break']:
            break

    # blowups t=2,3 of R<0 census graphs (N<=9 base)
    if not acc['first_break']:
        for nn in range(5, 10):
            for (g6, n, E) in r0.get(nn, []):
                for t in (2, 3):
                    bn, BE = vertex_blowup(n, E, t)
                    if bn > 27:
                        continue
                    gfam_allmax("blow_t%d:%s" % (t, g6), bn, BE, acc)
                    if acc['first_break']:
                        break
                if acc['first_break']:
                    break
            if acc['first_break']:
                break
        print("after blowups: bad_cuts=%d neg=%d lb_cov=%d lb_miss=%d any_cov=%d any_miss=%d"
              % (acc['bad_cuts'], acc['neg'], acc['lb_cov'], acc['lb_miss'], acc['any_cov'], acc['any_miss']),
              flush=True)

    # glued odd-gadget combos (small)
    if not acc['first_break']:
        gad = {'C5': (5, Cn(5)), 'C7': (7, Cn(7)), 'C9': (9, Cn(9))}
        for a, b in [('C5', 'C7'), ('C5', 'C9'), ('C7', 'C9')]:
            (na, Ea), (nb, Eb) = gad[a], gad[b]
            for bridges in ([(0, na)], [(0, na), (1, na + 1)]):
                n, E = union_disjoint((na, Ea), (nb, Eb))
                n, E = add_edges((n, E), bridges)
                if n <= 14 and is_triangle_free(n, E):
                    gfam_allmax("glue_%s_%s" % (a, b), n, E, acc)
                if acc['first_break']:
                    break
            if acc['first_break']:
                break
        print("after glued combos: bad_cuts=%d neg=%d lb_cov=%d lb_miss=%d any_cov=%d any_miss=%d"
              % (acc['bad_cuts'], acc['neg'], acc['lb_cov'], acc['lb_miss'], acc['any_cov'], acc['any_miss']),
              flush=True)

    # randoms N=11..14
    if not acc['first_break']:
        rng2 = random.Random(424242); made = 0; tries = 0
        while made < 600 and tries < 200000 and not acc['first_break']:
            tries += 1
            nn = rng2.choice([11, 12, 13, 14])
            p = rng2.uniform(0.12, 0.32)
            EE = [(x, y) for x in range(nn) for y in range(x + 1, nn) if rng2.random() < p]
            if not EE or not is_triangle_free(nn, EE):
                continue
            adj = [set() for _ in range(nn)]
            for x, y in EE:
                adj[x].add(y); adj[y].add(x)
            if any(len(adj[w]) == 0 for w in range(nn)):
                continue
            made += 1
            gfam_allmax("rand%d" % made, nn, EE, acc)
        print("after %d randoms (tries=%d): bad_cuts=%d neg=%d lb_cov=%d lb_miss=%d any_cov=%d any_miss=%d"
              % (made, tries, acc['bad_cuts'], acc['neg'], acc['lb_cov'], acc['lb_miss'], acc['any_cov'], acc['any_miss']),
              flush=True)

    print("=" * 64)
    print("distinct R<0 max cuts:", acc['bad_cuts'], " mixed-length signatures:", sorted(acc['len_sigs']))
    print("R<0 vertices tested:", acc['neg'])
    print("  length-bundle SELECTOR covered:", acc['lb_cov'], " / missed:", acc['lb_miss'])
    print("  of the misses -> ANY-neutral-switch covered:", acc['any_cov'], " / TRUE-MISS:", acc['any_miss'])
    print("  first SELECTOR-GAP (lb miss, any cover):", acc['first_selgap'])
    print("  first TRUE BREAK (no neutral Gamma-drop switch):", acc['first_break'])
    if acc['first_break']:
        print("VERDICT: TRUE (LB) BREAK -- a R<0 site with NO neutral B-conn Gamma-decreasing switch:", acc['first_break'])
    elif acc['lb_miss'] > 0:
        print("VERDICT: DESCENT MECHANISM survives (every R<0 site has SOME neutral Gamma-drop switch), but the "
              "LENGTH-BUNDLE SELECTOR is PROVABLY INCOMPLETE -- %d/%d R<0 vertices missed by length-bundle, all "
              "rescued by a wider neutral switch. Selector must be widened." % (acc['lb_miss'], acc['neg']))
    else:
        print("VERDICT: length-bundle selector covered ALL R<0 sites in this battery (no gap found here).")


if __name__ == "__main__":
    main()
