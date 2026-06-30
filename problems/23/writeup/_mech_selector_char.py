"""MECHANISM CHARACTERIZATION of the descent selector for R[v]<0.

Goal (exact, Fraction): on EVERY connected-B max cut with an R[v]<0 site (incl N=23 + H?AFBo] blowups +
overloaded blowups + glued island + randoms), characterize the descent bundle EXACTLY.

For a vertex v with R[v]=N*T[v]-(K2*T)[v] < 0, define the lengths v "sees":
  Lset(v) = { ell[f] : f in M, exists Q in cyc[f] with v in Q }       (lengths of bad edges whose shortest geodesic passes through v)
  L_min(v)=min Lset(v), L_max(v)=max Lset(v).

Questions answered, per R<0 site, with 0-fail / counterexample:
  Q1  R[v]<0  =>  L_max(v) > L_min(v)  (strictly MIXED lengths through v).
  Q2  among all neutral B-connected length-bundle half-switches S through v with Gamma(after)<Gamma(before),
      what length L does the witness live at?  Is it ALWAYS L_max(v) (the longest enclosing bundle)?
  Q3  among Gamma-decreasing witnesses, is the MAXIMUM Gamma-drop achieved at L_max(v)?  Record the
      (length, orientation) of the BEST (max-drop) witness; tabulate length==L_max and length==L_min frequencies.
  Q4  Does the deterministic rule "L=L_max(v), try both orientations, take any Gamma-decreasing one" cover
      every R<0 site?  (the precise selector candidate).

Recompute Gamma EXACTLY (no Psi).  Reuse shared infra; do not modify it.
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


def lenbundle_switches_by_L(v, M, ell, cyc):
    """Return dict L -> list of (orient, frozenset) for the prefix/suffix unions at that length."""
    bylen = {}
    for f in M:
        L = ell[f]
        for Q in cyc[f]:
            if v in Q:
                bylen.setdefault(L, []).append(list(Q))
    out = {}
    for L, rows in bylen.items():
        switches = []
        for orient in (0, 1):
            pref = set(); suff = set()
            for Q in rows:
                q = Q if orient == 0 else Q[::-1]
                i = q.index(v)
                pref.update(q[:i + 1])
                suff.update(q[i:])
            switches.append((orient, 'pref', frozenset(pref)))
            switches.append((orient, 'suff', frozenset(suff)))
        out[L] = switches
    return out


def flip(side, Sset):
    s = side[:]
    for u in Sset:
        s[u] ^= 1
    return s


def Lset_of_v(v, M, ell, cyc):
    s = set()
    for f in M:
        L = ell[f]
        for Q in cyc[f]:
            if v in Q:
                s.add(L)
                break
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
    gamma0 = sum(ell[f] ** 2 for f in M)
    for v in neg:
        acc['neg'] += 1
        Ls = Lset_of_v(v, M, ell, cyc)
        Lmin = min(Ls); Lmax = max(Ls)
        # Q1: strictly mixed?
        if Lmax > Lmin:
            acc['mixed'] += 1
        else:
            acc['notmixed'] += 1
            if acc['ex_notmixed'] is None:
                acc['ex_notmixed'] = (name, n, ''.join(map(str, side)), v, str(R[v]), sorted(Ls))

        bylenSW = lenbundle_switches_by_L(v, M, ell, cyc)
        # gather all Gamma-decreasing witnesses with their length & drop
        witnesses = []  # (drop, L, orient, kind)
        for L, sws in bylenSW.items():
            for (orient, kind, Sset) in sws:
                if v not in Sset or len(Sset) == 0 or len(Sset) == n:
                    continue
                if boundary_delta(n, adj, side, Sset) != 0:
                    continue
                s2 = flip(side, Sset)
                g2 = gamma_of(n, adj, s2)
                if g2 is not None and g2 < gamma0:
                    witnesses.append((gamma0 - g2, L, orient, kind))
        if not witnesses:
            acc['no_witness'] += 1
            if acc['ex_nowit'] is None:
                acc['ex_nowit'] = (name, n, ''.join(map(str, side)), v, str(R[v]))
            continue
        acc['has_witness'] += 1
        # lengths that produced ANY witness
        wit_lengths = set(w[1] for w in witnesses)
        # Q2: is there a witness at Lmax?
        if Lmax in wit_lengths:
            acc['wit_at_Lmax'] += 1
        else:
            acc['wit_not_at_Lmax'] += 1
            if acc['ex_notLmax'] is None:
                acc['ex_notLmax'] = (name, n, ''.join(map(str, side)), v, str(R[v]),
                                     'Lmax=%d wit_lengths=%s' % (Lmax, sorted(wit_lengths)))
        # is there a witness at Lmin only (not at Lmax)?
        if wit_lengths == {Lmin} and Lmin != Lmax:
            acc['wit_only_Lmin'] += 1
        # Q3: best (max-drop) witness length
        best = max(witnesses)  # max drop; ties broken by length then orient
        bestdrop, bestL, bestor, bestkind = best
        if bestL == Lmax:
            acc['best_at_Lmax'] += 1
        if bestL == Lmin:
            acc['best_at_Lmin'] += 1
        acc['best_len_hist'][('=Lmax' if bestL == Lmax else ('=Lmin' if bestL == Lmin else 'mid'))] = \
            acc['best_len_hist'].get(('=Lmax' if bestL == Lmax else ('=Lmin' if bestL == Lmin else 'mid')), 0) + 1
        # Q4: deterministic rule L=Lmax both orientations: does some Gamma-decreasing witness exist there?
        if Lmax in wit_lengths:
            acc['rule_Lmax_covers'] += 1
        # ALSO check: does Lmin rule (the naive/peak short bundle) ever cover when Lmax doesn't?  (sanity)
        if Lmax not in wit_lengths and Lmin in wit_lengths:
            acc['only_Lmin_covers'] += 1


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
    acc = dict(neg=0, mixed=0, notmixed=0, has_witness=0, no_witness=0,
               wit_at_Lmax=0, wit_not_at_Lmax=0, wit_only_Lmin=0,
               best_at_Lmax=0, best_at_Lmin=0, rule_Lmax_covers=0, only_Lmin_covers=0,
               best_len_hist={},
               ex_notmixed=None, ex_nowit=None, ex_notLmax=None)
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); gfam_allmax("cen%d" % nn, n, E, acc)
        print("census N=%d: neg=%d mixed=%d notmixed=%d  wit@Lmax=%d notLmax=%d nowit=%d" %
              (nn, acc['neg'], acc['mixed'], acc['notmixed'], acc['wit_at_Lmax'], acc['wit_not_at_Lmax'], acc['no_witness']), flush=True)
    # Myc N=23
    grN, grE = mycielski(5, Cn(5)); m2N, m2E = mycielski(grN, grE)
    adj = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj[x].add(y); adj[y].add(x)
    side = maxcut_ls(m2N, adj)
    test_cut("MycGrotzsch_N23", m2N, adj, side, acc)
    print("after Myc23: neg=%d mixed=%d notmixed=%d wit@Lmax=%d notLmax=%d nowit=%d" %
          (acc['neg'], acc['mixed'], acc['notmixed'], acc['wit_at_Lmax'], acc['wit_not_at_Lmax'], acc['no_witness']), flush=True)
    # H?AFBo] blowups
    hN, hE = dec("H?AFBo]"); base = [int(c) for c in "111110000"]
    for t in (2, 3):
        nn, EE = vertex_blowup(hN, hE, t)
        side = [base[v // t] for v in range(nn)]
        adj = [set() for _ in range(nn)]
        for x, y in EE:
            adj[x].add(y); adj[y].add(x)
        test_cut("Hblow_t%d" % t, nn, adj, side, acc)
    # overloaded C5 blowups
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,2)]:
        nn, EE = odd_blowup(5, list(sizes))
        if nn <= 13:
            gfam_allmax("blow%s" % (sizes,), nn, EE, acc)
    # glued island
    isl = (5, Cn(5)); g15 = mycielski(7, Cn(7))
    nn, EE = union_disjoint(isl, g15); nn, EE = add_edges((nn, EE), [(0, 5)])
    gfam_allmax("isl", nn, EE, acc)
    print("after blowups+island: neg=%d mixed=%d notmixed=%d wit@Lmax=%d notLmax=%d nowit=%d" %
          (acc['neg'], acc['mixed'], acc['notmixed'], acc['wit_at_Lmax'], acc['wit_not_at_Lmax'], acc['no_witness']), flush=True)
    # randoms
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

    print("=" * 70)
    print("R[v]<0 sites total:", acc['neg'])
    print("Q1 strictly MIXED (Lmax>Lmin):", acc['mixed'], " NOT mixed:", acc['notmixed'], acc['ex_notmixed'] or '')
    print("witness exists:", acc['has_witness'], " NO witness:", acc['no_witness'], acc['ex_nowit'] or '')
    print("Q2 witness-at-Lmax:", acc['wit_at_Lmax'], " witness-NOT-at-Lmax:", acc['wit_not_at_Lmax'], acc['ex_notLmax'] or '')
    print("    (of sites w/ witness) lengths == {Lmin} only:", acc['wit_only_Lmin'])
    print("Q3 BEST(max-drop) witness length histogram:", dict(sorted(acc['best_len_hist'].items())))
    print("    best-at-Lmax:", acc['best_at_Lmax'], " best-at-Lmin:", acc['best_at_Lmin'])
    print("Q4 rule [L=Lmax, both orientations] covers:", acc['rule_Lmax_covers'], "/", acc['has_witness'])
    print("    sites where ONLY Lmin covers (Lmax fails):", acc['only_Lmin_covers'])
    print("-" * 70)
    q1 = acc['notmixed'] == 0
    q4 = acc['rule_Lmax_covers'] == acc['has_witness'] and acc['no_witness'] == 0
    print("VERDICT Q1 (R<0 => strictly mixed lengths through v):", "HOLDS 0-fail" if q1 else "FALSE " + str(acc['ex_notmixed']))
    print("VERDICT Q4 (L=Lmax selector covers every R<0 site):", "HOLDS 0-fail" if q4 else "FALSE only_Lmin=%d nowit=%d" % (acc['only_Lmin_covers'], acc['no_witness']))


if __name__ == "__main__":
    main()
