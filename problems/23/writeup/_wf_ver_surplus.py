"""ADVERSARIAL VERIFY of route 'surplus' (independent re-implementation, exact Fraction).
CENTRAL INEQUALITY claimed to HOLD on full battery with 0 violations:
   V2 + N*(Gamma - N^2) + (N/5)*(TVcut - TVbad) <= Gamma*(N^2/25 - beta)
with V2 = sum_v (T_v-N)^2, Gamma = sum_f ell_f^2, beta=|M|,
TVcut = sum_{cut uv} |T_u-T_v|, TVbad = sum_{bad uv} |T_u-T_v|.

This gate is built FROM SCRATCH off struct_for_side (NOT off the claimant's gate). It:
  (a) recomputes V2, Gamma, beta, TVcut, TVbad in exact Fractions,
  (b) checks the central inequality, finds min margin + first violation,
  (c) cross-checks the algebraic identity V2 + N*(Gamma-N^2) == sum_v T(T-N) (handshake),
  (d) ALSO reports the LOAD-PSC-5 form sum_v T(T-N) + (N/5)(TVcut-TVbad) <= Gamma(N^2/25-beta)
      to confirm they coincide,
  (e) tracks ratio V2/(Gamma*(N^2/25-beta)) to confirm/refute the claimed 151/16.
Filenames of constructors are imported but their machinery (load) is recomputed locally.
"""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def adj_of(n, E):
    a = [set() for _ in range(n)]
    for x, y in E:
        a[x].add(y); a[y].add(x)
    return a

def blowup(parts):
    mm = len(parts); off = [0]*(mm+1)
    for i in range(mm):
        off[i+1] = off[i]+parts[i]
    nn = off[mm]; EE = []
    for i in range(mm):
        j = (i+1) % mm
        for a in range(off[i], off[i+1]):
            for b in range(off[j], off[j+1]):
                EE.append((min(a, b), max(a, b)))
    return nn, sorted(set(EE))

def chk(name, n, adj, side, acc):
    """Recompute everything locally and test the central inequality EXACTLY."""
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, ell, T, mu, cyc = st
    if not M:
        return
    N = F(n)
    beta = len(M)
    Gamma = sum(F(ell[f])**2 for f in M)
    # --- handshake self-check: sum_v T == Gamma ---
    sumT = sum(T)
    if sumT != Gamma:
        acc['handshake_fail'] += 1
        acc['handshake_examples'].append((name, str(sumT), str(Gamma)))
    V2 = sum((t - N)**2 for t in T)                 # sum_v (T_v - N)^2
    sumTTmN = sum(t*(t - N) for t in T)             # sum_v T(T-N)
    # identity check: V2 + N*(Gamma - N^2) ?= sum_v T(T-N)
    lhs_id = V2 + N*(Gamma - N*N)
    if lhs_id != sumTTmN:
        acc['identity_fail'] += 1
        acc['identity_examples'].append((name, str(lhs_id), str(sumTTmN)))
    # --- TVcut / TVbad over each undirected edge once ---
    badset = set((min(a, b), max(a, b)) for (a, b) in M)
    TVcut = F(0); TVbad = F(0)
    for u in range(n):
        for v in adj[u]:
            if v <= u:
                continue
            d = abs(T[u] - T[v])
            if side[u] != side[v]:
                TVcut += d
            else:
                # monochromatic edge == bad edge (triangle-free max-cut setup)
                TVbad += d
                if (u, v) not in badset:
                    acc['badset_mismatch'] += 1
    rhs = Gamma * (F(n*n, 25) - beta)
    # CENTRAL INEQUALITY (claimant form, c=5)
    central_lhs = V2 + N*(Gamma - N*N) + F(n, 5)*(TVcut - TVbad)
    margin = rhs - central_lhs
    # LOAD-PSC-5 form (should be identical to central_lhs since lhs_id==sumTTmN)
    loadpsc5_lhs = sumTTmN + F(n, 5)*(TVcut - TVbad)
    margin_lp5 = rhs - loadpsc5_lhs
    # ratio V2/(Gamma*(N^2/25-beta))  (claimed extremal 151/16)
    denom = Gamma * (F(n*n, 25) - beta)
    acc['n'] += 1
    # track central inequality
    if margin < acc['min_margin'][0]:
        acc['min_margin'] = (margin, name, n, beta, str(Gamma), str(V2), str(TVcut), str(TVbad))
    if margin < 0:
        acc['viol'] += 1
        if acc['first_viol'] is None:
            acc['first_viol'] = (name, ''.join(map(str, side)), n, beta,
                                 str(margin), str(Gamma), str(V2), str(TVcut), str(TVbad))
    # cross-check central vs loadpsc5 forms agree
    if margin != margin_lp5:
        acc['form_mismatch'] += 1
        acc['form_examples'].append((name, str(margin), str(margin_lp5)))
    # ratio (only when denom>0)
    if denom > 0:
        ratio = V2 / denom
        if ratio > acc['max_ratio'][0]:
            acc['max_ratio'] = (ratio, name, n, beta)
    elif denom == 0:
        # extremal C5[t]: Gamma>0 but N^2/25-beta==0 -> denom 0; central margin should be 0
        acc['denom0'] += 1
        if margin != 0:
            acc['denom0_nonzero_margin'] += 1
            acc['denom0_examples'].append((name, str(margin)))

def run_battery():
    acc = {
        'n': 0, 'viol': 0, 'first_viol': None,
        'min_margin': (F(10**30), '', 0, 0, '', '', '', ''),
        'max_ratio': (F(-1), '', 0, 0),
        'handshake_fail': 0, 'handshake_examples': [],
        'identity_fail': 0, 'identity_examples': [],
        'form_mismatch': 0, 'form_examples': [],
        'badset_mismatch': 0,
        'denom0': 0, 'denom0_nonzero_margin': 0, 'denom0_examples': [],
    }

    def section(label):
        print("  [%s] configs=%d viol=%d min_margin=%s" % (
            label, acc['n'], acc['viol'], float(acc['min_margin'][0])), flush=True)

    # two-lane L=8..20
    for L in range(8, 21):
        n, E, side, _ = build_two_lane(L)
        chk("two-lane-L%d" % L, n, adj_of(n, E), side, acc)
    section("two-lane")

    # k-lane breakers
    for (Ll, k, gap) in [(12, 4, 6), (14, 4, 8), (16, 5, 8)]:
        bad = greedy_chords(Ll, k, gap)
        n, E, side, bad = build_k_lane(Ll, k, bad)
        chk("klane-L%dk%d" % (Ll, k), n, adj_of(n, E), side, acc)
    section("k-lane")

    # census geng -tc N=7..11, ALL gamma-min cuts
    for nn in range(7, 12):
        outg = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split()
        a0 = acc['viol']
        for g6 in outg:
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for s in cuts:
                chk("cen%s" % g6, n, adj, s, acc)
        print("  census N=%d done (viol+%d)" % (nn, acc['viol'] - a0), flush=True)
    section("census")

    # C5/C7/C9[t] blow-ups t=1..5
    for cyc in (5, 7, 9):
        for t in range(1, 6):
            n, E = blowup([t]*cyc)
            if n > 26:
                continue
            adj, cuts = gmins(n, E)
            for s in (cuts[:1] if cuts else []):
                chk("C%d[%d]" % (cyc, t), n, adj, s, acc)
    section("cyclic blow-ups")

    # non-uniform blow-ups
    for parts in [[2, 2, 2, 2, 3], [1, 5, 2, 2, 5], [1, 4, 2, 4, 2, 4, 2], [3, 3, 3, 3, 2],
                  [1, 3, 2, 2, 3], [1, 6, 2, 2, 6], [4, 1, 4, 1, 4], [2, 3, 1, 3, 2],
                  [1, 1, 5, 1, 1], [5, 1, 1, 1, 5]]:
        n, E = blowup(parts)
        if n > 26:
            continue
        adj, cuts = gmins(n, E)
        for s in (cuts[:1] if cuts else []):
            chk("nu%s" % parts, n, adj, s, acc)
    section("non-uniform blow-ups")

    # Mycielskians + glued islands (the killers)
    grot = mycielski(5, Cn(5)); mycg = mycielski(grot[0], grot[1])

    def bridge(b1, b2, u, v):
        nn, E = union_disjoint(b1, b2); n1 = b1[0]
        return nn, E + [(u, n1 + v)]

    extra = [
        ("Grotzsch", grot),
        ("Myc(Grotzsch)N23", mycg),
        ("M(C7)", mycielski(7, Cn(7))),
        ("M(C9)", mycielski(9, Cn(9))),
        ("bridge(C7,Grotzsch)", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ("bridge(C9,C9)", bridge((9, Cn(9)), (9, Cn(9)), 0, 0)),
    ]
    for name, (nn, E) in extra:
        adj, cuts = gmins(nn, E)
        for s in cuts[:3]:
            chk(name, nn, adj, s, acc)
    section("Mycielskians + glued")

    # extra ad-hoc triangle-free graphs of my choosing (adversarial)
    # (1) Petersen graph (triangle-free, vertex-transitive)
    pet_E = [(0,1),(1,2),(2,3),(3,4),(4,0),
             (0,5),(1,6),(2,7),(3,8),(4,9),
             (5,7),(7,9),(9,6),(6,8),(8,5)]
    adj, cuts = gmins(10, pet_E)
    for s in cuts[:3]:
        chk("Petersen", 10, adj, s, acc)
    # (2) more Mycielskians of odd cycles
    for base in (5, 7, 9, 11, 13):
        nn, E = mycielski(base, Cn(base))
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]:
            chk("M(C%d)" % base, nn, adj, s, acc)
    # (3) double-Mycielskian of C7 (N=31) -- bigger killer
    g = mycielski(7, Cn(7)); g2 = mycielski(g[0], g[1])
    if g2[0] <= 33:
        adj, cuts = gmins(g2[0], g2[1])
        for s in cuts[:1]:
            chk("Myc2(C7)N%d" % g2[0], g2[0], adj, s, acc)
    # (4) glued bridges with different attach points and 2-bridges
    def bridge2(b1, b2, pairs):
        nn, E = union_disjoint(b1, b2); n1 = b1[0]
        return nn, E + [(u, n1 + v) for (u, v) in pairs]
    for nm, (nn, E) in [
        ("brg(Grotzsch,Grotzsch)", bridge2(mycielski(5, Cn(5)), mycielski(5, Cn(5)), [(0, 0)])),
        ("brg2(C7,Grotzsch)", bridge2((7, Cn(7)), mycielski(5, Cn(5)), [(0, 0), (3, 5)])),
        ("brg(C5,Grotzsch)", bridge2((5, Cn(5)), mycielski(5, Cn(5)), [(0, 0)])),
        ("brg(C9,Grotzsch)", bridge2((9, Cn(9)), mycielski(5, Cn(5)), [(0, 0)])),
    ]:
        adj, cuts = gmins(nn, E)
        for s in cuts[:2]:
            chk(nm, nn, adj, s, acc)
    section("ad-hoc extras")

    # (5) all triangle-free connected census N=12,13 (sampled) ALL gamma-min cuts -- deeper sweep
    for nn in (12, 13):
        outg = subprocess.run([GENG, "-tc", str(nn), "-d2"], capture_output=True, text=True).stdout.split()
        a0 = acc['viol']
        cnt = 0
        for g6 in outg:
            cnt += 1
            if cnt > 40000:
                break
            n, E = dec(g6)
            adj, cuts = gmins(n, E)
            for s in cuts:
                chk("cen%s" % g6, n, adj, s, acc)
        print("  census N=%d (min-deg2, capped) done graphs=%d (viol+%d)" % (nn, cnt, acc['viol'] - a0), flush=True)
    section("deeper census")

    print("\n==== RESULTS ====", flush=True)
    print("  total configs   = %d" % acc['n'], flush=True)
    print("  CENTRAL viol     = %d" % acc['viol'], flush=True)
    mm = acc['min_margin']
    print("  MIN margin       = %s  (float %.6g)" % (mm[0], float(mm[0])), flush=True)
    print("     at %s N=%d beta=%d Gamma=%s V2=%s TVcut=%s TVbad=%s" % (mm[1], mm[2], mm[3], mm[4], mm[5], mm[6], mm[7]), flush=True)
    mr = acc['max_ratio']
    print("  MAX V2/(Gamma*(N^2/25-beta)) = %s = %.10g at %s N=%d beta=%d" % (mr[0], float(mr[0]), mr[1], mr[2], mr[3]), flush=True)
    print("     claimed 151/16 = %s = %.10g  --> %s" % (F(151,16), float(F(151,16)),
          "MATCH" if mr[0] == F(151, 16) else ("EXCEEDS 151/16!" if mr[0] > F(151,16) else "below 151/16")), flush=True)
    print("  handshake_fail   = %d  identity_fail = %d  form_mismatch = %d  badset_mismatch = %d" % (
        acc['handshake_fail'], acc['identity_fail'], acc['form_mismatch'], acc['badset_mismatch']), flush=True)
    if acc['identity_examples']:
        print("     identity examples: %s" % acc['identity_examples'][:3], flush=True)
    print("  denom0 (extremal C5[t]) configs = %d ; of those with nonzero margin = %d" % (
        acc['denom0'], acc['denom0_nonzero_margin']), flush=True)
    if acc['denom0_examples']:
        print("     denom0 nonzero-margin examples: %s" % acc['denom0_examples'][:5], flush=True)
    if acc['first_viol']:
        print("  FIRST VIOLATION: %s" % (acc['first_viol'],), flush=True)
    print("  === CENTRAL INEQUALITY (surplus route, c=5) %s ===" % (
        "FAILS" if acc['viol'] else "HOLDS (0 violations)"), flush=True)
    return acc

if __name__ == "__main__":
    run_battery()
