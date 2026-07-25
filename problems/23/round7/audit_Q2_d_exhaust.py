"""audit_Q2_d_exhaust.py -- INDEPENDENT exhaustive re-run of section 6 of round7/Q2.md:
all maximal triangle-free graphs on N <= 12.

Own graph6 decoder, own max-cut, own switching algebra, own (*) evaluation.
Exact integers only.
"""
import sys, subprocess, os
from fractions import Fraction as F
from itertools import product
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_core import (g6_decode, g6_encode, edges_of, is_triangle_free,
                           is_maximal_tf, mono_count, popcount)

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
DIR = r"E:\Projects\ErdosProblems\problems\23\round7"
OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


def gen_mtf(n):
    f = os.path.join(DIR, f"audit_tf{n}.g6")
    if not os.path.exists(f):
        subprocess.run([GENG, "-qtc", str(n), f], check=True)
    out = []
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        nn, adj = g6_decode(line)
        assert nn == n
        if is_maximal_tf(nn, adj):
            out.append((line, nn, adj))
    return out


say("=" * 78)
say("D1.  counts of maximal triangle-free graphs  (own geng run + own filter)")
say("=" * 78)
q2counts = {3: 1, 4: 2, 5: 3, 6: 4, 7: 6, 8: 10, 9: 16, 10: 31, 11: 61, 12: 147}
G = {}
tot = 0
ok = True
for n in range(3, 13):
    G[n] = gen_mtf(n)
    c = len(G[n])
    m = "ok" if q2counts[n] == c else "<<< MISMATCH"
    if q2counts[n] != c:
        ok = False
    if n >= 5:
        tot += c
    say(f"   n={n:3d}:  {c:5d}   Q2.md says {q2counts[n]:5d}   {m}")
say(f"   total for 5<=n<=12 : {tot}    Q2.md says 278   "
    f"{'ok' if tot == 278 else '<<< MISMATCH'}")
say(f"   VERDICT counts: {'CONFIRMED' if ok and tot == 278 else 'REFUTED'}")


# ------------------------------------------------------------------ machinery
def cut_data(n, adj, X):
    """returns (M, sigma list)."""
    M = 0
    sg = [0] * n
    for i in range(n):
        db = dm = 0
        xi = (X >> i) & 1
        a = adj[i]
        j = 0
        while a:
            if a & 1:
                if ((X >> j) & 1) == xi:
                    dm += 1
                else:
                    db += 1
            a >>= 1
            j += 1
        sg[i] = db - dm
        M += dm
    return M // 2, sg


def switch_star_ok(n, adj, X, sg):
    for v in range(n):
        rhs = 0
        xv = (X >> v) & 1
        for w in range(n):
            if (adj[v] >> w) & 1 and ((X >> w) & 1) != xv and sg[w] <= 1:
                rhs += 2 - sg[w]
        if sg[v] < rhs:
            return False
    return True


def delta_of_set(n, adj, X, S, sg):
    val = 0
    for v in range(n):
        if (S >> v) & 1:
            val -= sg[v]
    for i in range(n):
        if not ((S >> i) & 1):
            continue
        for j in range(i + 1, n):
            if not ((S >> j) & 1):
                continue
            if (adj[i] >> j) & 1:
                val += 2 if (((X >> i) & 1) != ((X >> j) & 1)) else -2
    return val


def star_family_max(n, adj, X, sg):
    """max over v and independent T subset V\\N(v) of Delta(N(v) u T).
    Uses the exact linearity Delta = Delta(N(v)) + sum_{w in T} c_v(w);
    the MWIS is computed by exhaustive recursion (n<=12)."""
    best = None
    for v in range(n):
        Nv = adj[v]
        base = delta_of_set(n, adj, X, Nv, sg)
        rest = [w for w in range(n) if not ((Nv >> w) & 1)]
        c = {}
        for w in rest:
            bw = mw = 0
            for z in range(n):
                if (adj[w] >> z) & 1 and (Nv >> z) & 1:
                    if ((X >> w) & 1) != ((X >> z) & 1):
                        bw += 1
                    else:
                        mw += 1
            c[w] = -sg[w] + 2 * bw - 2 * mw
        # max weight independent set among 'rest' (positive weights only matter,
        # but independence forces a real search)
        pos = [w for w in rest if c[w] > 0]
        bestw = 0

        def rec(idx, avail, acc):
            nonlocal bestw
            if acc > bestw:
                bestw = acc
            for k in range(idx, len(pos)):
                w = pos[k]
                if (avail >> w) & 1:
                    rec(k + 1, avail & ~adj[w] & ~(1 << w), acc + c[w])
        rec(0, (1 << n) - 1, 0)
        val = base + bestw
        if best is None or val > best[0]:
            best = (val, v)
    return best


# ------------------------------------------------------------------ PART A / B
say()
say("=" * 78)
say("D2.  PART A (maximum cuts) and PART B (locally-good but bound-violating cuts)")
say("=" * 78)
nmaxcuts = 0
failA = 0
failCharge = 0
failStarAtMax = 0
partB = []
for n in range(5, 13):
    for (g6, nn, adj) in G[n]:
        best = None
        cuts = []
        for X in range(1 << (n - 1)):
            M, sg = cut_data(n, adj, X)
            cuts.append((X, M, sg))
            if best is None or M < best:
                best = M
        for (X, M, sg) in cuts:
            if M == best:
                nmaxcuts += 1
                if 25 * M > n * n:
                    failA += 1
                    say(f"   *** PART A FAILURE {g6} X={X:#x} M={M}")
                # charge identity
                tot = sum(F(n) - F(25, 2) * ((sum(1 for w in range(n)
                          if (adj[v] >> w) & 1 and ((X >> w) & 1) == ((X >> v) & 1)))) for v in range(n))
                if tot != n * n - 25 * M:
                    failCharge += 1
                sf = star_family_max(n, adj, X, sg)
                if sf[0] > 0:
                    failStarAtMax += 1
                    say(f"   *** (*) VIOLATED AT A MAXIMUM CUT {g6} X={X:#x} Delta={sf[0]}")
            else:
                if 25 * M <= n * n:
                    continue
                if min(sg) < 0:
                    continue
                if not switch_star_ok(n, adj, X, sg):
                    continue
                sf = star_family_max(n, adj, X, sg)
                if sf[0] > 0:
                    continue
                partB.append((g6, n, X, M, 25 * M - n * n))
say(f"   maximum cuts examined (vertex 0 pinned) = {nmaxcuts}    Q2.md says 587  "
    f"{'ok' if nmaxcuts == 587 else '<<< MISMATCH'}")
say(f"   PART A failures of 25|M| <= N^2 : {failA}   (Q2.md: 0)")
say(f"   charge-identity failures        : {failCharge}   (Q2.md: 0)")
say(f"   (*) violated at a maximum cut   : {failStarAtMax}   (Q2.md: 0)")
say()
say(f"   PART B: cuts with sigma>=0, all switch-stars, all (*), yet 25|M|>N^2 : {len(partB)}"
    f"    Q2.md says 15   {'ok' if len(partB) == 15 else '<<< MISMATCH'}")
for (g6, n, X, M, d) in sorted(partB):
    say(f"      {g6:14s} N={n} cut={X:#x} M={M} 25M-N^2=+{d}")
gs = sorted(set(g for (g, _, _, _, _) in partB))
say(f"   distinct graphs carrying them: {len(gs)}  {gs}")

# ------------------------------------------------------------------ champion id
say()
say("=" * 78)
say("D3.  Is the champion K??FF?^Fvw^_  equal to C5[2,2,3,2,3] = W*(1,1)?")
say("=" * 78)
champ = "K??FF?^Fvw^_"
n, adj = g6_decode(champ)
say(f"   decoded: n={n} |E|={len(edges_of(n,adj))} triangle-free={is_triangle_free(n,adj)} "
    f"maximal={is_maximal_tf(n,adj)}")
# twin classes
tw = {}
for v in range(n):
    tw.setdefault(adj[v], []).append(v)
say(f"   twin classes (by identical neighbourhood): {[sorted(c) for c in tw.values()]}")
say(f"   class sizes: {sorted(len(c) for c in tw.values())}")
# quotient graph
reps = [c[0] for c in tw.values()]
qadj = [[bool((adj[a] >> b) & 1) for b in reps] for a in reps]
say(f"   quotient adjacency on the {len(reps)} classes:")
for i, row in enumerate(qadj):
    say("      " + "".join('1' if x else '0' for x in row))
# build C5[2,2,3,2,3] here, independently
w = [2, 2, 3, 2, 3]
n1 = sum(w)
st, t = [], 0
for x in w:
    st.append(t)
    t += x
adj1 = [0] * n1
for i in range(5):
    j = (i + 1) % 5
    for a in range(st[i], st[i] + w[i]):
        for b in range(st[j], st[j] + w[j]):
            adj1[a] |= 1 << b
            adj1[b] |= 1 << a
say(f"   C5[2,2,3,2,3] built here: graph6 = {g6_encode(n1, adj1)}  |E|={len(edges_of(n1,adj1))}")


def isomorphic(n, a1, a2):
    """backtracking isomorphism test (n<=12)."""
    d1 = sorted(popcount(x) for x in a1)
    d2 = sorted(popcount(x) for x in a2)
    if d1 != d2:
        return False
    perm = [-1] * n
    used = [False] * n

    def bt(i):
        if i == n:
            return True
        for j in range(n):
            if used[j] or popcount(a1[i]) != popcount(a2[j]):
                continue
            ok = True
            for k in range(i):
                if bool((a1[i] >> k) & 1) != bool((a2[j] >> perm[k]) & 1):
                    ok = False
                    break
            if ok:
                perm[i] = j
                used[j] = True
                if bt(i + 1):
                    return True
                used[j] = False
                perm[i] = -1
        return False
    return bt(0)


say(f"   isomorphic(K??FF?^Fvw^_ , C5[2,2,3,2,3]) = {isomorphic(12, adj, adj1)}")

open(os.path.join(DIR, "audit_Q2_d_out.txt"), "w").write("\n".join(OUT))
