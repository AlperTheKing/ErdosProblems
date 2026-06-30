"""Route 'sos' part 2: (a) does B-RES IMPLY LOAD-PSC?  (b) extra adversarial counterexample hunt.

(a) NON-IMPLICATION test. LOAD-PSC-5 slack S = (Q1 - ||x||^2) + (RES-PEN).
    B-RES gives only RES-PEN >= 0. If there EXISTS a config with Q1 - ||x||^2 < 0 AND
    (Q1 - ||x||^2) + (RES-PEN) ... we want to show B-RES (2nd bracket) does NOT by itself force S>=0.
    Concretely: count configs where bracket1 := Q1 - ||x||^2 < 0 (so B-RES on bracket2 is doing
    real work but is NOT sufficient by linearity). Report the worst bracket1, and the worst case where
    bracket1 < 0 while RES-PEN is small -- i.e. the binding 427/429 case where they nearly cancel.
    The decisive fact: B-RES bounds ONLY bracket2; bracket1 alone violates >=0, so B-RES !=> LOAD-PSC.

(b) Extra adversarial families: random triangle-free graphs (exact max-cut by brute force for small n),
    extra Mycielskians, double-bridged glued islands, asymmetric two-/three-lane variants.
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free
from _wf_ver_sos import quantities


def brutemax_gmins(n, E):
    """All gamma-min connected-B max cuts via brute force (small n)."""
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b); adj[b].add(a)
    cuts = [s for s in maxcut_all(n, adj) if Bconn(n, adj, s)]
    cand = []
    from _h import bdist_restr
    for s in cuts:
        Mb = [(u, v) for u in range(n) for v in adj[u] if v > u and s[u] == s[v]]
        if not Mb:
            continue
        G = 0; ok = True
        for (u, v) in Mb:
            d = bdist_restr(adj, s, u, v)
            if d < 0:
                ok = False; break
            G += (d + 1) ** 2
        if ok:
            cand.append((s, G))
    if not cand:
        return adj, []
    gm = min(g for _, g in cand)
    return adj, [s for s, g in cand if g == gm]


def probe(name, n, adj, side, acc):
    q = quantities(n, adj, side)
    if q is None or q.get('_handshake_fail'):
        return
    acc['n'] += 1
    N = q['N']; Gamma = q['Gamma']; beta = q['beta']
    nx2 = q['nx2']; RES = q['RES']; PEN = q['PEN']; Q1 = q['Q1']
    sumNmT = q['sumNmT']; tvcut = q['tvcut']; tvbad = q['tvbad']
    br1 = Q1 - nx2              # bracket1 (can be < 0)
    br2 = RES - PEN            # bracket2 (= (N/5)*bres_slack, B-RES => >=0)
    S = br1 + br2
    bres_slack = 5 * sumNmT - (tvcut - tvbad)
    # tallies
    if br1 < 0:
        acc['br1neg'] += 1
        if acc['br1min'] is None or br1 < acc['br1min'][0]:
            acc['br1min'] = (br1, name, n, beta)
    if br2 < 0:
        acc['br2neg'] += 1   # would refute B-RES
    if bres_slack < 0:
        acc['bres_viol'] += 1
        if acc['bres_first'] is None:
            acc['bres_first'] = (name, n, beta, str(bres_slack))
    if S < 0:
        acc['psc5_viol'] += 1
        if acc['psc5_first'] is None:
            acc['psc5_first'] = (name, n, beta, str(S), ''.join(map(str, side)))
    if acc['Smin'] is None or S < acc['Smin'][0]:
        acc['Smin'] = (S, name, n, beta)
    # the "B-RES not sufficient" witness: br1<0 AND br1 + br2 only barely >=0 (i.e. br2 has to pay a lot)
    if br1 < 0:
        # how much of B-RES's slack (br2) is consumed: ratio (-br1)/br2 in (0,1] when S>=0
        if br2 > 0:
            consume = (-br1) / br2
            if acc['consume_max'] is None or consume > acc['consume_max'][0]:
                acc['consume_max'] = (consume, name, n, beta, str(br1), str(br2), str(S))


if __name__ == "__main__":
    acc = dict(n=0, br1neg=0, br2neg=0, bres_viol=0, bres_first=None,
               psc5_viol=0, psc5_first=None, Smin=None, br1min=None, consume_max=None)
    print("=== route 'sos' part 2: B-RES =?> LOAD-PSC  + extra adversarial hunt ===", flush=True)

    # extra Mycielskians and triple
    grot = mycielski(5, Cn(5))
    mycg = mycielski(*grot)               # N=23
    extra_constructs = []
    extra_constructs.append(("Grotzsch", grot))
    extra_constructs.append(("Myc(Grotzsch)N23", mycg))
    extra_constructs.append(("M(C7)", mycielski(7, Cn(7))))
    extra_constructs.append(("M(C9)", mycielski(9, Cn(9))))
    extra_constructs.append(("M(C11)", mycielski(11, Cn(11))))

    def bridge(b1, b2, pairs):
        nn, E = union_disjoint(b1, b2); n1 = b1[0]
        for (u, v) in pairs:
            E = E + [(u, n1 + v)]
        return nn, E
    # glued islands: single + double bridges
    extra_constructs.append(("bridge(C7,Grotzsch)", bridge((7, Cn(7)), grot, [(0, 0)])))
    extra_constructs.append(("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), [(0, 0)])))
    extra_constructs.append(("bridge(C5,C5)", bridge((5, Cn(5)), (5, Cn(5)), [(0, 0)])))
    extra_constructs.append(("bridge2(C7,C7)", bridge((7, Cn(7)), (7, Cn(7)), [(0, 0), (2, 2)])))
    extra_constructs.append(("bridge(C7,M(C7))", bridge((7, Cn(7)), mycielski(7, Cn(7)), [(0, 0)])))
    extra_constructs.append(("bridge(C5,Grotzsch)", bridge((5, Cn(5)), grot, [(0, 0)])))

    for name, (nn, E) in extra_constructs:
        if nn > 26 or not is_triangle_free(nn, E):
            continue
        adj, cuts = gmins(nn, E)
        for s in cuts[:3]:
            probe(name, nn, adj, s, acc)

    # extra non-uniform blow-ups (asymmetric, the rigidity-stressing kind)
    def blowup(parts):
        mm = len(parts); off = [0] * (mm + 1)
        for i in range(mm):
            off[i + 1] = off[i] + parts[i]
        nn = off[mm]; EE = []
        for i in range(mm):
            j = (i + 1) % mm
            for a in range(off[i], off[i + 1]):
                for b in range(off[j], off[j + 1]):
                    EE.append((min(a, b), max(a, b)))
        return nn, sorted(set(EE))
    nuparts = [[1, 1, 1, 1, 2], [1, 1, 1, 2, 1], [1, 2, 1, 3, 1], [1, 5, 1, 5, 1],
               [2, 1, 4, 1, 2], [1, 1, 5, 1, 1], [3, 1, 1, 1, 3], [1, 9, 1, 1, 9],
               [1, 1, 1, 1, 1, 1, 2], [1, 1, 1, 1, 1, 2, 1], [2, 1, 2, 1, 2, 1, 2],
               [1, 3, 1, 3, 1, 3, 1], [1, 1, 1, 1, 1, 1, 1, 1, 2]]
    for parts in nuparts:
        n, E = blowup(parts)
        if n > 26:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:2] if cuts else []):
            probe("nu%s" % parts, n, adj, s, acc)

    # random triangle-free graphs, exact brute-force max-cut, ALL gamma-min cuts
    random.seed(20260629)
    rtested = 0
    for trial in range(4000):
        n = random.randint(8, 12)
        p = random.choice([0.18, 0.22, 0.28, 0.33, 0.4])
        E = []
        adj = [set() for _ in range(n)]
        for a in range(n):
            for b in range(a + 1, n):
                if random.random() < p:
                    if adj[a] & adj[b]:
                        continue   # keep triangle-free
                    E.append((a, b)); adj[a].add(b); adj[b].add(a)
        if not E:
            continue
        a2, cuts = brutemax_gmins(n, E)
        if not cuts:
            continue
        rtested += 1
        for s in cuts[:2]:
            probe("rand%d" % trial, n, a2, s, acc)
    print("  random triangle-free graphs with a valid gamma-min cut tested: %d" % rtested, flush=True)

    print("\n  === RESULTS (configs=%d) ===" % acc['n'], flush=True)
    print("  B-RES violations (bracket2<0 in raw form): %d  %s" %
          (acc['bres_viol'], "HOLDS" if not acc['bres_viol'] else "FAILS"), flush=True)
    if acc['bres_first']:
        print("     first B-RES violation: %s" % (acc['bres_first'],), flush=True)
    print("  LOAD-PSC-5 violations (S<0): %d  %s" %
          (acc['psc5_viol'], "HOLDS" if not acc['psc5_viol'] else "FAILS"), flush=True)
    if acc['psc5_first']:
        print("     first LOAD-PSC-5 violation: %s" % (acc['psc5_first'],), flush=True)
    print("  min S = %s = %.6f at %s" %
          (str(acc['Smin'][0]), float(acc['Smin'][0]), acc['Smin'][1:]), flush=True)
    print("\n  --- B-RES => LOAD-PSC ? (non-implication evidence) ---", flush=True)
    print("  configs with bracket1 = Q1-||x||^2 < 0: %d / %d" % (acc['br1neg'], acc['n']), flush=True)
    if acc['br1min']:
        print("  worst (most negative) bracket1 = %s = %.4f at %s" %
              (str(acc['br1min'][0]), float(acc['br1min'][0]), acc['br1min'][1:]), flush=True)
    if acc['consume_max']:
        cm = acc['consume_max']
        print("  max fraction of B-RES slack (bracket2) consumed by -bracket1 = %s = %.6f at %s" %
              (str(cm[0]), float(cm[0]), cm[1:4]), flush=True)
        print("     (br1=%s br2=%s S=%s)" % (cm[4], cm[5], cm[6]), flush=True)
    print("  bracket2<0 count (would refute B-RES): %d" % acc['br2neg'], flush=True)
