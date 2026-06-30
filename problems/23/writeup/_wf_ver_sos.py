"""ADVERSARIAL independent verification of route "sos" (a previous agent's claim).
INDEPENDENT re-implementation -- does NOT import their gate file.

Claims being verified (all EXACT Fraction):
  (B-RES)      5*sum_v(N - T_v) >= TV_cut(T) - TV_bad(T)
               equivalently RES - PEN >= 0 with RES=N*(N^2-Gamma), PEN=(N/5)*(TV_cut-TV_bad),
               since sum_v(N-T_v) = N*N - Gamma = N(N - Gamma/N)... see note below.
  Slack decomp S = (Q1 - ||x||^2) + (RES - PEN),  Q1=Gamma*(N^2/25 - beta), x_v = T_v - N.
               S is exactly the LOAD-PSC-5 slack:  LHS_5 <= Q1.
  Constants:   V2 rigidity sup (n*||x||^2)/Q1 = 151/16 ;
               reduction tightness sup (n*||x||^2 - Q1)/(RES-PEN) = 427/429 ;
               B-RES inf (RES-PEN) = 0.

I recompute T, Gamma, TV_cut, TV_bad, beta from scratch (only reuse struct_for_side / geos = PROVEN setup),
sanity-check the handshake sum_v T = Gamma, then test:
  * B-RES holds (RES-PEN >= 0) with 0 violations?  binding config + exact constant.
  * LOAD-PSC-5 slack S = (Q1-||x||^2)+(RES-PEN) >= 0 with 0 violations? (the thing that "does the work")
  * the three claimed extremal constants.
  * whether B-RES => LOAD-PSC (algebra check below; empirical decomposition cross-check).

Run from E:/Projects/ErdosProblems/problems/23/writeup."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords


def quantities(n, adj, side):
    """Return dict of exact quantities for one (graph, max-cut side), or None if no bad edge / invalid."""
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = n
    beta = len(M)
    Gamma = sum(F(ell[f]) ** 2 for f in M)
    # handshake sanity (PROVEN identity sum_v T_v = Gamma)
    sumT = sum(T)
    if sumT != Gamma:
        return dict(_handshake_fail=True, name_n=n, sumT=sumT, Gamma=Gamma)
    badset = set((min(a, b), max(a, b)) for (a, b) in M)
    # TV_cut over CUT edges, TV_bad over BAD (= monochromatic) edges.
    tvcut = F(0); tvbad = F(0)
    nbad_seen = 0
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            d = abs(T[u] - T[v])
            if side[u] != side[v]:
                tvcut += d
            else:
                # monochromatic edge. Bad edges are exactly the monochromatic ones.
                tvbad += d
                if (u, v) in badset:
                    nbad_seen += 1
    # sanity: number of monochromatic edges equals beta (every mono edge is a bad edge)
    # (we count distinct mono edges)
    mono = sum(1 for u in range(n) for v in adj[u] if v > u and side[u] == side[v])
    x = [T[v] - F(N) for v in range(n)]
    nx2 = sum(xi * xi for xi in x)                  # ||x||^2 = sum (T_v - N)^2
    RES = F(N) * (F(N) ** 2 - Gamma)                # N*(N^2 - Gamma)
    PEN = F(N, 5) * (tvcut - tvbad)                 # (N/5)(TV_cut - TV_bad)
    Q1 = Gamma * (F(N * N, 25) - F(beta))           # Gamma*(N^2/25 - beta)
    sumNmT = F(N) * F(N) - Gamma                    # sum_v (N - T_v) = N*N - sum T = N^2 - Gamma
    return dict(N=N, beta=beta, Gamma=Gamma, tvcut=tvcut, tvbad=tvbad,
                nx2=nx2, RES=RES, PEN=PEN, Q1=Q1, sumNmT=sumNmT, mono=mono, M=M, side=side,
                _handshake_fail=False)


def chk(name, n, adj, side, acc):
    q = quantities(n, adj, side)
    if q is None:
        return
    if q.get('_handshake_fail'):
        acc['handshake_fail'].append((name, q['sumT'], q['Gamma']))
        return
    acc['n'] += 1
    N = q['N']; Gamma = q['Gamma']; beta = q['beta']
    nx2 = q['nx2']; RES = q['RES']; PEN = q['PEN']; Q1 = q['Q1']
    tvcut = q['tvcut']; tvbad = q['tvbad']; sumNmT = q['sumNmT']

    # --- (B-RES): 5*sum_v(N-T_v) >= TV_cut - TV_bad ;  equivalently RES-PEN>=0 only up to N factor. ---
    # raw B-RES exactly as stated: lhs = 5*sumNmT, rhs = tvcut - tvbad
    bres_lhs = 5 * sumNmT
    bres_rhs = tvcut - tvbad
    bres_slack = bres_lhs - bres_rhs            # >= 0 claimed
    if bres_slack < 0:
        acc['bres_viol'] += 1
        if acc['bres_first'] is None:
            acc['bres_first'] = (name, n, beta, str(bres_slack), ''.join(map(str, side)))
    # RES - PEN form (the decomposition's second bracket). RES-PEN = N*(sumNmT) - (N/5)(tvcut-tvbad)
    #   = N*[ sumNmT - (1/5)(tvcut-tvbad) ] = (N/5)*[5*sumNmT - (tvcut-tvbad)] = (N/5)*bres_slack.
    resmpen = RES - PEN
    # cross-check RES-PEN == (N/5)*bres_slack  (algebra consistency)
    if resmpen != F(N, 5) * bres_slack:
        acc['algebra_fail'].append((name, str(resmpen), str(F(N, 5) * bres_slack)))
    if resmpen < 0:
        acc['resmpen_viol'] += 1
    # track inf of RES-PEN (claimed 0)
    if acc['resmpen_min'] is None or resmpen < acc['resmpen_min'][0]:
        acc['resmpen_min'] = (resmpen, name, n, beta)

    # --- LOAD-PSC-5 slack S (the inequality that "does the work") ---
    # S = (Q1 - nx2) + (RES - PEN).   S>=0  <=>  LOAD-PSC-5 holds.
    S = (Q1 - nx2) + resmpen
    if S < 0:
        acc['psc5_viol'] += 1
        if acc['psc5_first'] is None:
            acc['psc5_first'] = (name, n, beta, str(S), ''.join(map(str, side)))
    if acc['psc5_min'] is None or S < acc['psc5_min'][0]:
        acc['psc5_min'] = (S, name, n, beta)

    # --- LOAD-PSC-25 slack (the actual Erdos-strength inequality, c=25) ---
    PEN25 = F(N, 25) * (tvcut - tvbad)
    S25 = (Q1 - nx2) + (RES - PEN25)
    if S25 < 0:
        acc['psc25_viol'] += 1
        if acc['psc25_first'] is None:
            acc['psc25_first'] = (name, n, beta, str(S25), ''.join(map(str, side)))
    if acc['psc25_min'] is None or S25 < acc['psc25_min'][0]:
        acc['psc25_min'] = (S25, name, n, beta)

    # --- constant 1: V2 rigidity sup nx2/Q1  (claimed 151/16); nx2 = ||x||^2 = V2 ---
    if Q1 > 0:
        r = nx2 / Q1
        if acc['v2_max'] is None or r > acc['v2_max'][0]:
            acc['v2_max'] = (r, name, n, beta)
    elif nx2 > 0 and Q1 == 0:
        acc['v2_inf'].append((name, n, beta))   # Q1==0 but nx2>0 would be +inf

    # --- constant 2: reduction tightness sup (nx2 - Q1)/(RES-PEN)  (claimed 427/429) ---
    if resmpen > 0:
        r2 = (nx2 - Q1) / resmpen
        if acc['red_max'] is None or r2 > acc['red_max'][0]:
            acc['red_max'] = (r2, name, n, beta)


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


def adj_of(n, E):
    a = [set() for _ in range(n)]
    for x, y in E:
        a[x].add(y); a[y].add(x)
    return a


def bridge(b1, b2, u, v):
    nn, E = union_disjoint(b1, b2); n1 = b1[0]
    return nn, E + [(u, n1 + v)]


if __name__ == "__main__":
    acc = dict(n=0,
               bres_viol=0, bres_first=None,
               resmpen_viol=0, resmpen_min=None,
               psc5_viol=0, psc5_first=None, psc5_min=None,
               psc25_viol=0, psc25_first=None, psc25_min=None,
               v2_max=None, v2_inf=[], red_max=None,
               handshake_fail=[], algebra_fail=[])
    print("=== INDEPENDENT adversarial verify of route 'sos' (B-RES + LOAD-PSC-5 slack decomp) ===", flush=True)

    # two-lane L=8..20
    for L in range(8, 21, 2):
        n, E, side, _ = build_two_lane(L)
        chk("two-lane-L%d" % L, n, adj_of(n, E), side, acc)
    # k-lane dense breakers
    for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, E, side, bad = build_k_lane(Ll, k, bad)
        chk("klane-L%dk%d" % (Ll, k), n, adj_of(n, E), side, acc)
    print("  two-lane+k-lane done: bres_viol=%d psc5_viol=%d psc25_viol=%d" %
          (acc['bres_viol'], acc['psc5_viol'], acc['psc25_viol']), flush=True)

    # census geng -tc N=7..11, ALL gmin cuts
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        b0 = acc['bres_viol']; p0 = acc['psc5_viol']
        for g6 in outg:
            n, E = dec(g6); adj, cuts = gmins(n, E)
            for s in cuts:
                chk("cen%s" % g6, n, adj, s, acc)
        print("  census N=%d (bres+%d psc5+%d)  configs=%d" %
              (nn, acc['bres_viol'] - b0, acc['psc5_viol'] - p0, acc['n']), flush=True)

    # C5/C7/C9[t] uniform blow-ups
    for cyc in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t] * cyc)
            if n > 26:
                continue
            adj, cuts = gmins(n, E)
            for s in (cuts[:1] if cuts else []):
                chk("C%d[%d]" % (cyc, t), n, adj, s, acc)
    # non-uniform blow-ups (the STAR-O1 killers etc.)
    for parts in [[2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2],
                  [1, 3, 2, 2, 3], [1, 6, 2, 2, 6], [1, 48, 6, 8, 48] if False else [1, 8, 2, 2, 8]]:
        n, E = blowup(parts)
        if n > 26:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:1] if cuts else []):
            chk("nu%s" % parts, n, adj, s, acc)

    # Mycielskians + glued islands (the route-killers)
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])
    extra = [("Grotzsch", grot), ("Myc(Grotzsch)N23", mycg),
             ("M(C7)", mycielski(7, Cn(7))), ("M(C9)", mycielski(9, Cn(9))),
             ("bridge(C7,Grotzsch)", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
             ("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), 0, 0))]
    for name, (nn, E) in extra:
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]:
            chk(name, nn, adj, s, acc)
    print("  blow-ups + Mycielskians + glued done", flush=True)

    print("\n  === RESULTS  (total configs=%d) ===" % acc['n'], flush=True)
    if acc['handshake_fail']:
        print("  !!! HANDSHAKE FAIL (sum T != Gamma): %s" % acc['handshake_fail'][:3], flush=True)
    else:
        print("  handshake sum_v T = Gamma: VERIFIED on all configs", flush=True)
    if acc['algebra_fail']:
        print("  !!! ALGEBRA FAIL RES-PEN != (N/5)*bres_slack: %s" % acc['algebra_fail'][:3], flush=True)
    else:
        print("  algebra RES-PEN == (N/5)*bres_slack: VERIFIED", flush=True)

    print("  B-RES (5*sum(N-T) >= TV_cut-TV_bad): violations=%d  %s" %
          (acc['bres_viol'], "HOLDS" if not acc['bres_viol'] else "FAILS"), flush=True)
    if acc['bres_first']:
        print("     first B-RES violation: %s" % (acc['bres_first'],), flush=True)
    print("     inf(RES-PEN) = %s = %.6f at %s  (claimed 0)" %
          (str(acc['resmpen_min'][0]), float(acc['resmpen_min'][0]), acc['resmpen_min'][1:]), flush=True)
    print("     RES-PEN<0 count = %d" % acc['resmpen_viol'], flush=True)

    print("  LOAD-PSC-5 slack S>=0: violations=%d  %s" %
          (acc['psc5_viol'], "HOLDS" if not acc['psc5_viol'] else "FAILS"), flush=True)
    if acc['psc5_first']:
        print("     first LOAD-PSC-5 violation: %s" % (acc['psc5_first'],), flush=True)
    print("     min S(c=5) = %s = %.6f at %s" %
          (str(acc['psc5_min'][0]), float(acc['psc5_min'][0]), acc['psc5_min'][1:]), flush=True)

    print("  LOAD-PSC-25 slack S25>=0: violations=%d  %s" %
          (acc['psc25_viol'], "HOLDS" if not acc['psc25_viol'] else "FAILS"), flush=True)
    if acc['psc25_first']:
        print("     first LOAD-PSC-25 violation: %s" % (acc['psc25_first'],), flush=True)
    print("     min S(c=25) = %s = %.6f at %s" %
          (str(acc['psc25_min'][0]), float(acc['psc25_min'][0]), acc['psc25_min'][1:]), flush=True)

    if acc['v2_inf']:
        print("  !!! V2 rigidity: Q1==0 but ||x||^2>0 at %s -> sup is +inf" % acc['v2_inf'][:3], flush=True)
    if acc['v2_max']:
        print("  V2 rigidity sup ||x||^2/Q1 = %s = %.6f at %s  (claimed 151/16=%.6f)" %
              (str(acc['v2_max'][0]), float(acc['v2_max'][0]), acc['v2_max'][1:], 151 / 16), flush=True)
    if acc['red_max']:
        print("  reduction tightness sup (||x||^2 - Q1)/(RES-PEN) = %s = %.6f at %s  (claimed 427/429=%.6f)" %
              (str(acc['red_max'][0]), float(acc['red_max'][0]), acc['red_max'][1:], 427 / 429), flush=True)

    print("\n  === VERDICT ===", flush=True)
    print("  B-RES %s ; LOAD-PSC-5 %s ; LOAD-PSC-25 %s" % (
        "HOLDS" if not acc['bres_viol'] else "FAILS",
        "HOLDS" if not acc['psc5_viol'] else "FAILS",
        "HOLDS" if not acc['psc25_viol'] else "FAILS"), flush=True)
