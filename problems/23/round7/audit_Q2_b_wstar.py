"""audit_Q2_b_wstar.py -- INDEPENDENT audit of the central object of round7/Q2.md:
   W*(u,r) = C5[2u,2u,3u,2u,3u] with X = c0 u c2 u (c3\\R), Y = c1 u c4 u R, |R|=r.

Everything is exact integer arithmetic.  Two independent engines:
   (E1) vertex level, full 2^N subset enumeration           (u = 1 only, N = 12)
   (E2) six-twin-group count enumeration, exact             (all u)
E2's completeness (Delta depends only on the six counts) is VERIFIED against E1.
"""
import sys
from fractions import Fraction as F
from itertools import product
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_core import (mono_count, maxcut_bip, sigma_vec, delta_set,
                           delta_formula, popcount, g6_encode, edges_of)

OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


# ---------------------------------------------------------------- vertex model
def build_wstar(u, r):
    """returns n, adj, X, groups (list of vertex lists) for the six twin groups
    c0, c1, c2, c3\\R, R, c4."""
    sizes = [2 * u, 2 * u, 3 * u, 2 * u - r, r, 3 * u]     # c0 c1 c2 c3a c3b c4
    # class of each group in the C5 (c3a and c3b are both class 3)
    cls = [0, 1, 2, 3, 3, 4]
    n = sum(sizes)
    start, t = [], 0
    for s in sizes:
        start.append(t)
        t += s
    groups = [list(range(start[i], start[i] + sizes[i])) for i in range(6)]
    adj = [0] * n
    for i in range(6):
        for j in range(i + 1, 6):
            if (cls[i] - cls[j]) % 5 in (1, 4):            # adjacent classes in C5
                for a in groups[i]:
                    for b in groups[j]:
                        adj[a] |= 1 << b
                        adj[b] |= 1 << a
    # cut: side 1 = Y = c1 u c4 u R
    X = 0
    for i in (1, 4, 5):                                     # c1, c3b=R, c4
        for v in groups[i]:
            X |= 1 << v
    return n, adj, X, groups, sizes


# ---------------------------------------------------------------- E2 count engine
def wstar_delta_counts(u, r, s):
    """Delta(S) from the six counts s = (s0,s1,s2,s3a,s3b,s4).  Derived here from
    scratch (NOT copied from Q2.md)."""
    sg = [5 * u, 5 * u, 2 * r, 0, 0, 4 * u - 2 * r]
    # group adjacency + mono/cross status under the cut
    #   c0(X)-c1(Y)  cross ; c1(Y)-c2(X) cross ; c2(X)-c3a(X) MONO ; c2(X)-c3b(Y) cross
    #   c3a(X)-c4(Y) cross ; c3b(Y)-c4(Y) MONO ; c4(Y)-c0(X) cross
    cross = [(0, 1), (1, 2), (2, 4), (3, 5), (5, 0)]
    mono = [(2, 3), (4, 5)]
    d = -sum(sg[i] * s[i] for i in range(6))
    for (i, j) in mono:
        d -= 2 * s[i] * s[j]
    for (i, j) in cross:
        d += 2 * s[i] * s[j]
    return d


def wstar_min_switch_counts(u, r):
    """exact min |S| with Delta(S) > 0, over the whole box of six counts.
    Delta is LINEAR in s2 and in s4 separately (no c2-c4 edge), so we enumerate
    (s0,s1,s3a,s3b) and solve the remaining 2-variable integer problem exactly by
    the equal-cost greedy (largest coefficient first), which is optimal."""
    sizes = [2 * u, 2 * u, 3 * u, 2 * u - r, r, 3 * u]
    sg = [5 * u, 5 * u, 2 * r, 0, 0, 4 * u - 2 * r]
    best = None
    A, B = sizes[2], sizes[5]
    for s0 in range(sizes[0] + 1):
        for s1 in range(sizes[1] + 1):
            for s3a in range(sizes[3] + 1):
                for s3b in range(sizes[4] + 1):
                    C = -(sg[0] * s0 + sg[1] * s1) + 2 * s0 * s1
                    # coefficient of s2 : -sg2 - 2*s3a + 2*s1 + 2*s3b
                    al = -sg[2] - 2 * s3a + 2 * s1 + 2 * s3b
                    # coefficient of s4 : -sg5 - 2*s3b + 2*s3a + 2*s0
                    be = -sg[5] - 2 * s3b + 2 * s3a + 2 * s0
                    D = 1 - C                       # need al*s2 + be*s4 >= D
                    base = s0 + s1 + s3a + s3b
                    if best is not None and base >= best[0]:
                        continue
                    if D <= 0:
                        cand = (base, (s0, s1, 0, s3a, s3b, 0))
                        if best is None or cand[0] < best[0]:
                            best = cand
                        continue
                    items = sorted([(al, A, 2), (be, B, 5)], key=lambda t: -t[0])
                    need, cost, use = D, 0, {2: 0, 5: 0}
                    ok = True
                    for (c, cap, idx) in items:
                        if need <= 0:
                            break
                        if c <= 0:
                            ok = False
                            break
                        take = min(cap, -(-need // c))
                        use[idx] = take
                        need -= c * take
                        cost += take
                    if ok and need <= 0:
                        s = (s0, s1, use[2], s3a, s3b, use[5])
                        assert wstar_delta_counts(u, r, s) > 0, (u, r, s)
                        if best is None or base + cost < best[0]:
                            best = (base + cost, s)
    return best


# ---------------------------------------------------------------- E1 vs E2
say("=" * 78)
say("B1.  E1 (full 2^N subsets, vertex level)  vs  E2 (six-group counts)")
say("=" * 78)
n, adj, X, groups, sizes = build_wstar(1, 1)
say(f"  W*(1,1): N={n} sizes={sizes}  |E|={len(edges_of(n,adj))} graph6={g6_encode(n,adj)}")
sg = sigma_vec(n, adj, X)
say(f"  sigma per group = {[sg[g[0]] for g in groups]}   (Q2.md: [5u,5u,2r,0,0,4u-2r] = [5,5,2,0,0,2])")
M = mono_count(n, adj, X)
say(f"  |M| = {M}   25|M|-N^2 = {25*M-n*n}   25|M|/N^2 = {F(25*M, n*n)}")
say(f"  bip(G) (own exhaustive max-cut over 2^(N-1)) = {maxcut_bip(n,adj)}   "
    f"N^2/36 = {F(n*n,36)}   N^2/25 = {F(n*n,25)}")
# full subset enumeration
mins, allpos = None, []
for S in range(1 << n):
    d = delta_set(n, adj, X, S)
    assert d == delta_formula(n, adj, X, S, sg)
    if d > 0:
        k = popcount(S)
        allpos.append((k, S, d))
        if mins is None or k < mins:
            mins = k
say(f"  E1 min improving |S| over ALL 2^{n} subsets = {mins}")
# E2 on the same object
e2 = wstar_min_switch_counts(1, 1)
say(f"  E2 min improving |S| over the six counts      = {e2[0]}  at s={e2[1]}")
# also verify Delta depends only on counts
bad = 0
for S in range(1 << n):
    cnt = tuple(sum(1 for v in g if (S >> v) & 1) for g in groups)
    if delta_set(n, adj, X, S) != wstar_delta_counts(1, 1, cnt):
        bad += 1
say(f"  Delta(S) depends only on the six group counts : violations over 2^{n} subsets = {bad}")
say(f"  E1 == E2 : {'YES' if mins == e2[0] and bad == 0 else 'NO  <<< PROBLEM'}")

# u = 2 : vertex-level check of sigma / |M| / bip, count engine for the switch
n2, adj2, X2, g2, sz2 = build_wstar(2, 2)
sg2 = sigma_vec(n2, adj2, X2)
say(f"  W*(2,2): N={n2} sizes={sz2} sigma per group={[sg2[g[0]] for g in g2]} "
    f"|M|={mono_count(n2,adj2,X2)} 25|M|/N^2={F(25*mono_count(n2,adj2,X2), n2*n2)}")
bad2 = 0
for _ in range(1):
    import random
    random.seed(11)
    for _t in range(20000):
        S = random.getrandbits(n2)
        cnt = tuple(sum(1 for v in g if (S >> v) & 1) for g in g2)
        if delta_set(n2, adj2, X2, S) != wstar_delta_counts(2, 2, cnt):
            bad2 += 1
say(f"  W*(2,2): Delta = count-formula on 20000 random subsets : violations = {bad2}")


# ---------------------------------------------------------------- closed forms
say()
say("=" * 78)
say("B2.  CLOSED FORMS of W*(u,r) -- independent re-derivation, u = 1..9")
say("=" * 78)
say("   u  r   N    |E|    |M|   25|M|-N^2   25|M|/N^2   bip(G)   N^2/25   sigma")
allok = True
for u in range(1, 10):
    r = u
    sizes = [2 * u, 2 * u, 3 * u, 2 * u - r, r, 3 * u]
    N = 12 * u
    w = [2 * u, 2 * u, 3 * u, 2 * u, 3 * u]
    Etot = sum(w[i] * w[(i + 1) % 5] for i in range(5))
    Mval = 3 * u * (2 * u - r) + r * 3 * u
    bipG = min(w[i] * w[(i + 1) % 5] for i in range(5))
    sg = [5 * u, 5 * u, 2 * r, 0, 0, 4 * u - 2 * r]
    ok = (N == 12 * u and Etot == 28 * u * u and Mval == 6 * u * u
          and 25 * Mval - N * N == 6 * u * u and bipG == 4 * u * u)
    allok &= ok
    say(f"  {u:2d} {r:2d} {N:4d} {Etot:6d} {Mval:6d}   {25*Mval-N*N:8d}   "
        f"{F(25*Mval,N*N)}   {bipG:6d}   {F(N*N,25)}   {sg}  {'ok' if ok else 'FAIL'}")
say(f"  Q2.md closed forms |E|=28u^2, |M|=6u^2, 25|M|/N^2=25/24, bip=4u^2=N^2/36 : "
    f"{'CONFIRMED' if allok else 'REFUTED'}")
say(f"  bip(G) = 4u^2 < N^2/25 = 144u^2/25 = 5.76u^2  -> the GRAPH obeys the conjecture: CONFIRMED")


# ---------------------------------------------------------------- families
say()
say("=" * 78)
say("B3.  Does the W*(u,u) cut satisfy sigma>=0, all switch-stars, (*), SUP, NBRU, PAIRNBR?")
say("=" * 78)

# group-level adjacency
GADJ = [[False] * 6 for _ in range(6)]
cls = [0, 1, 2, 3, 3, 4]
for i in range(6):
    for j in range(6):
        if i != j and (cls[i] - cls[j]) % 5 in (1, 4):
            GADJ[i][j] = True
NBR = [[j for j in range(6) if GADJ[i][j]] for i in range(6)]


def maxdelta_over(u, r, lower, upper):
    """max Delta over all count vectors with lower<=s<=upper  (brute force)."""
    best = None
    rngs = [range(lower[i], upper[i] + 1) for i in range(6)]
    for s in product(*rngs):
        d = wstar_delta_counts(u, r, s)
        if best is None or d > best[0]:
            best = (d, s)
    return best


def check_all_families(u, r, verbose=False):
    sizes = [2 * u, 2 * u, 3 * u, 2 * u - r, r, 3 * u]
    sg = [5 * u, 5 * u, 2 * r, 0, 0, 4 * u - 2 * r]
    res = {}
    res['sigma>=0'] = min(sg) >= 0
    # switch-stars: sigma(v) >= sum_{a in T} (2 - sigma(a)),  T subset N_B(v)
    ss_ok, ss_slack = True, []
    side = [0, 1, 0, 0, 1, 1]                     # 1 = Y
    for i in range(6):
        rhs = 0
        for j in NBR[i]:
            if side[j] != side[i] and sg[j] <= 1:
                rhs += sizes[j] * (2 - sg[j])
        ss_slack.append(sg[i] - rhs)
        if sg[i] < rhs:
            ss_ok = False
    res['switch-star'] = ss_ok
    res['ss_slack'] = ss_slack
    # family (*) : S = N(v) u T,  supp(T) an independent set of groups in V \ N(v)
    worst = None
    for i in range(6):
        Nv = NBR[i]
        cand = [j for j in range(6) if j not in Nv]
        for supmask in product((0, 1), repeat=len(cand)):
            sel = [cand[k] for k in range(len(cand)) if supmask[k]]
            if any(GADJ[x][y] for x in sel for y in sel):
                continue
            lower = [0] * 6
            upper = [0] * 6
            for j in Nv:
                lower[j] = upper[j] = sizes[j]
            for j in sel:
                upper[j] = sizes[j]
            b = maxdelta_over(u, r, lower, upper)
            if worst is None or b[0] > worst[0]:
                worst = (b[0], i, b[1])
    res['(*)max'] = worst
    # SUP : any S containing some N(v)
    supworst = None
    for i in range(6):
        lower = [0] * 6
        upper = list(sizes)
        for j in NBR[i]:
            lower[j] = sizes[j]
        b = maxdelta_over(u, r, lower, upper)
        if supworst is None or b[0] > supworst[0]:
            supworst = (b[0], i, b[1])
    res['SUPmax'] = supworst
    # NBRU : unions of neighbourhoods
    nbworst = None
    for msk in range(1, 1 << 6):
        gs = set()
        for i in range(6):
            if (msk >> i) & 1:
                gs |= set(NBR[i])
        s = [sizes[j] if j in gs else 0 for j in range(6)]
        d = wstar_delta_counts(u, r, s)
        if nbworst is None or d > nbworst[0]:
            nbworst = (d, msk, tuple(s))
    res['NBRUmax'] = nbworst
    # PAIRNBR : N(u) u N(v) for adjacent u,v
    pworst = None
    for i in range(6):
        for j in NBR[i]:
            gs = set(NBR[i]) | set(NBR[j])
            s = [sizes[k] if k in gs else 0 for k in range(6)]
            d = wstar_delta_counts(u, r, s)
            if pworst is None or d > pworst[0]:
                pworst = (d, (i, j), tuple(s))
    res['PAIRNBRmax'] = pworst
    return res


for u in range(1, 6):
    r = u
    res = check_all_families(u, r)
    say(f"  u={u} r={r}: sigma>=0 {res['sigma>=0']}, switch-star OK {res['switch-star']} "
        f"(slacks {res['ss_slack']})")
    say(f"        max Delta over (*)   = {res['(*)max'][0]:6d}  (v-class {res['(*)max'][1]}, s={res['(*)max'][2]})")
    say(f"        max Delta over SUP   = {res['SUPmax'][0]:6d}  (v-class {res['SUPmax'][1]}, s={res['SUPmax'][2]})")
    say(f"        max Delta over NBRU  = {res['NBRUmax'][0]:6d}  s={res['NBRUmax'][2]}")
    say(f"        max Delta over PAIRN = {res['PAIRNBRmax'][0]:6d}  s={res['PAIRNBRmax'][2]}")

open(r"E:\Projects\ErdosProblems\problems\23\round7\audit_Q2_b_out.txt", "w").write("\n".join(OUT))
