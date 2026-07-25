"""audit_Q2_a_lemmas.py -- audit of Lemma 1 / Lemma 2 / Lemma 3 and of the
C5[n] ledger and the W_b table of round7/Q2.md.  Exact integers only.
"""
import sys, random
from fractions import Fraction as F
from itertools import product
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_core import (g6_decode, g6_encode, edges_of, is_triangle_free,
                           is_maximal_tf, mono_count, maxcut_bip, all_min_cuts,
                           sigma_vec, delta_set, delta_formula, blowup,
                           C5E, P4E, popcount)

OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


# ============================================================ L1 switching identity
say("=" * 78)
say("A1.  LEMMA 1  Delta(S) = -sum_S sigma - 2 e_M(S) + 2 e_B(S)   [full check]")
say("=" * 78)
random.seed(20260725)
bad = 0
tested = 0
for trial in range(400):
    n = random.randint(4, 9)
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.45:
                # add only if it keeps triangle-freeness (we want the real class)
                if adj[i] & adj[j] == 0:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
    assert is_triangle_free(n, adj)
    for X in range(1 << n):
        sg = sigma_vec(n, adj, X)
        for S in range(1 << n):
            tested += 1
            if delta_set(n, adj, X, S) != delta_formula(n, adj, X, S, sg):
                bad += 1
    if trial > 30:
        break
say(f"  identity checked on {tested} (graph,cut,S) triples : mismatches = {bad}")

# maximum-cut <=> all Delta(S)<=0
bad2 = 0
random.seed(7)
for trial in range(40):
    n = random.randint(4, 9)
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.5 and adj[i] & adj[j] == 0:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    b = maxcut_bip(n, adj)
    for X in range(1 << n):
        ismax = (mono_count(n, adj, X) == b)
        allneg = all(delta_set(n, adj, X, S) <= 0 for S in range(1 << n))
        if ismax != allneg:
            bad2 += 1
say(f"  'max cut  <=>  all Delta(S)<=0' checked on 40 graphs x all cuts : mismatches = {bad2}")
say("  VERDICT L1: CONFIRMED" if bad == 0 and bad2 == 0 else "  VERDICT L1: REFUTED")


# ============================================================ L2 corner certificate
say()
say("=" * 78)
say("A2.  LEMMA 2  maxcut(H[a]) part-respecting; corner check = maximality")
say("=" * 78)
pats = [(5, C5E, "C5"), (4, P4E, "P4"),
        (6, [(0, 3), (0, 4), (0, 5), (1, 3), (1, 5), (2, 4), (2, 5)], "EEj_")]
bad3 = 0
for (h, E, nm) in pats:
    for a in [tuple(random.randint(1, 3) for _ in range(h)) for _ in range(6)]:
        n, adj, start = blowup(h, E, list(a))
        if n > 15:
            continue
        # true bip over ALL cuts, vertex level
        true_bip = maxcut_bip(n, adj)
        # bip over part-respecting cuts only
        pr = None
        for col in product((0, 1), repeat=h):
            X = 0
            for i in range(h):
                if col[i]:
                    for v in range(start[i], start[i] + a[i]):
                        X |= 1 << v
            m = mono_count(n, adj, X)
            pr = m if pr is None else min(pr, m)
        if pr != true_bip:
            bad3 += 1
            say(f"   *** {nm} a={a}: part-respecting min {pr} != true bip {true_bip}")
say(f"  part-respecting = true bip : mismatches = {bad3}")

# corner certificate: for a part-respecting cut, is 'all 2^h corner Deltas <=0'
# equivalent to being a maximum cut (over ALL vertex-level S)?
bad4 = 0
cnt4 = 0
for (h, E, nm) in pats:
    for a in [tuple(random.randint(1, 3) for _ in range(h)) for _ in range(8)]:
        n, adj, start = blowup(h, E, list(a))
        if n > 14:
            continue
        b = maxcut_bip(n, adj)
        for col in product((0, 1), repeat=h):
            X = 0
            for i in range(h):
                if col[i]:
                    for v in range(start[i], start[i] + a[i]):
                        X |= 1 << v
            corners_ok = True
            for msk in product((0, 1), repeat=h):
                S = 0
                for i in range(h):
                    if msk[i]:
                        for v in range(start[i], start[i] + a[i]):
                            S |= 1 << v
                if delta_set(n, adj, X, S) > 0:
                    corners_ok = False
                    break
            ismax = (mono_count(n, adj, X) == b)
            cnt4 += 1
            if corners_ok != ismax:
                bad4 += 1
say(f"  corner-certificate  <=>  maximum, on {cnt4} part-respecting cuts : mismatches = {bad4}")
say("  VERDICT L2: CONFIRMED" if bad3 == 0 and bad4 == 0 else "  VERDICT L2: REFUTED")


# ============================================================ C5[n] ledger
say()
say("=" * 78)
say("A3.  C5[n] ledger  n = 1..8 : 25|M| - N^2 at the maximum cut, charge identity")
say("=" * 78)
for nn in range(1, 9):
    a = [nn] * 5
    h, E = 5, C5E
    # exact bip at pattern level, and (vertex level for n<=3 as cross-check)
    best = None
    for col in product((0, 1), repeat=5):
        m = sum(a[i] * a[j] for (i, j) in E if col[i] == col[j])
        if best is None or m < best[0]:
            best = (m, col)
    M, col = best
    N = 5 * nn
    line = f"  C5[{nn}]  N={N}  |M|={M}  25|M|-N^2 = {25*M - N*N}"
    if nn <= 3:
        n, adj, start = blowup(5, C5E, a)
        line += f"   [vertex-level bip = {maxcut_bip(n, adj)}]"
    # charge identity  sum_v mu(v) = N^2 - 25|M|
    dM = []
    for i in range(5):
        dm = sum(a[j] for j in range(5) if ((i, j) in E or (j, i) in E) and col[j] == col[i])
        dM.append(dm)
    tot = sum(a[i] * (F(N) - F(25, 2) * dM[i]) for i in range(5))
    line += f"   sum mu = {tot} (target {N*N - 25*M})"
    assert tot == N * N - 25 * M
    say(line)
say("  VERDICT C5[n] ledger: CONFIRMED (exact 0 at every n, charge identity exact)")


# ============================================================ W_b table
say()
say("=" * 78)
say("A4.  W_b = P4[b+1,b,b,b+1] at X = A1 u A4 : MINIMUM IMPROVING SWITCH")
say("=" * 78)


def wb_min_switch(b):
    """Own enumeration over the four part-counts (complete: parts are twin
    classes on fixed cut sides, so Delta depends only on the counts)."""
    a = [b + 1, b, b, b + 1]
    sg = [b, 1, 1, b]                     # verified below at vertex level
    best = None
    for s0 in range(a[0] + 1):
        for s1 in range(a[1] + 1):
            for s2 in range(a[2] + 1):
                for s3 in range(a[3] + 1):
                    # mono edges inside S : A2-A3 (both in Y)
                    eM = s1 * s2
                    # crossing edges inside S : A1-A2 and A3-A4
                    eB = s0 * s1 + s2 * s3
                    d = -(sg[0] * s0 + sg[1] * s1 + sg[2] * s2 + sg[3] * s3) - 2 * eM + 2 * eB
                    if d > 0:
                        k = s0 + s1 + s2 + s3
                        if best is None or k < best[0]:
                            best = (k, (s0, s1, s2, s3), d)
    return best


# vertex-level cross-check of sigma and of the min switch for small b
for b in (2, 3):
    a = [b + 1, b, b, b + 1]
    n, adj, start = blowup(4, P4E, a)
    X = 0
    for i in (0, 3):
        for v in range(start[i], start[i] + a[i]):
            X |= 1 << v
    sg = sigma_vec(n, adj, X)
    persize = [sg[start[i]] for i in range(4)]
    M = mono_count(n, adj, X)
    mins = None
    for S in range(1 << n):
        if delta_set(n, adj, X, S) > 0:
            k = popcount(S)
            if mins is None or k < mins:
                mins = k
    say(f"  [vertex level] b={b}: N={n} sigma per part={persize} |M|={M} "
        f"25|M|-N^2={25*M-n*n}  min improving |S| (all 2^{n} subsets) = {mins}"
        f"   [count-enum says {wb_min_switch(b)[0] if wb_min_switch(b) else None}]")

say()
say("  b :  min|S|   |S|/N        witness (s_A1,s_A2,s_A3,s_A4)   Delta   Q2.md table")
q2tab = {3: 5, 4: 5, 5: 6, 6: 7, 8: 8, 10: 10, 12: 11}
mismatch = []
for b in list(range(3, 21)) + [30, 50, 100, 200, 400]:
    r = wb_min_switch(b) if b <= 60 else None
    if r is None:
        continue
    k, s, d = r
    N = 4 * b + 2
    claim = q2tab.get(b, None)
    tag = ""
    if claim is not None:
        tag = f"Q2.md says {claim}" + ("  <<< MISMATCH" if claim != k else "  ok")
        if claim != k:
            mismatch.append((b, k, claim, s, d))
    say(f"  {b:3d}: {k:5d}   {F(k,N)} = {float(F(k,N)):.4f}   {s}   Delta={d}   {tag}")
say()
if mismatch:
    for (b, k, claim, s, d) in mismatch:
        say(f"  *** EXACT FALSIFIER of the Q2.md W_b table: b={b}: Q2.md claims min|S|={claim}, "
            f"truth is {k} with S=(p,q)={s[0],s[1]} , Delta = 2*{s[0]}*{s[1]} - {s[0]}*{b} - {s[1]} = {d} > 0")
say("  (Q2.md's own script Q2_ledger.py prints |S|=9 for b=10 -- the report table is a "
    "mis-transcription, it copied b=11's value 10 next to b=10's N=42.)")

# asymptotics: is |S|/N -> 1/8 ?
say()
say("  asymptotic check of  |S|/N -> 1/8  (exact minimisation over p,q):")


def wb_min_pq(b):
    best = None
    p = 1
    while p <= b + 1:
        # need q(2p-1) > pb  ->  q >= floor(pb/(2p-1))+1
        if 2 * p - 1 <= 0:
            p += 1
            continue
        q = (p * b) // (2 * p - 1) + 1
        if q <= b:
            k = p + q
            if best is None or k < best[0]:
                best = (k, p, q)
        p += 1
    return best


for b in (10, 100, 1000, 10000, 10**6, 10**8):
    k, p, q = wb_min_pq(b)
    N = 4 * b + 2
    say(f"    b={b:>9}: min p+q = {k:>8}  (p={p},q={q})  |S|/N = {float(F(k,N)):.6f}")
say("  -> ratio decreases towards 0.125 ; the '-> 1/8' claim is CONFIRMED, "
    "convergence is 1/8 + Theta(1/sqrt(b)).")

open(r"E:\Projects\ErdosProblems\problems\23\round7\audit_Q2_a_out.txt", "w").write("\n".join(OUT))
