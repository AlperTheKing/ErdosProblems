"""
audit_G11_core.py -- INDEPENDENT re-implementation of every acceptance-path
computation in round3/G11.md.  Nothing is imported from G11_verify_*.py.

Own data structures (adjacency bitmasks over Python ints), own max-cut
(popcount over 2^(n-1) bipartitions, computed by a completely different
formula than the target's edge-loop), own bipartiteness test, own
isomorphism test (explicit multiplier map, NOT a WL colour refinement),
own Vega construction retyped from the Brandt-Thomasse verbatim text
quoted in G11.md section b.3.

EXACT integer / Fraction arithmetic everywhere.  No floats on any
acceptance path (floats appear only inside f-strings for readability).

Run:  python audit_G11_core.py
"""

from fractions import Fraction
from itertools import combinations, permutations
import sys

# ------------------------------------------------------------------ helpers

def adjmasks(n, edges):
    """edges: iterable of (u,v) with 0<=u,v<n.  Returns list of bitmasks."""
    adj = [0] * n
    for u, v in edges:
        assert u != v
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def popcount(x):
    return bin(x).count('1')


def maxcut_bip(n, edges):
    """EXACT bip = |E| - maxcut.

    Independent method: enumerate the 2^(n-1) bipartitions S (vertex 0 in S)
    and compute the number of CROSSING edges as
        cross(S) = sum_{v in S} popcount(adj[v] & ~S)
    which is a different formula from the target's per-edge loop.
    Returns (bip, maxcut, |E|).
    """
    E = {(min(u, v), max(u, v)) for u, v in edges}
    m = len(E)
    adj = adjmasks(n, E)
    full = (1 << n) - 1
    best = -1
    for half in range(1 << (n - 1)):
        S = (half << 1) | 1          # vertex 0 always in S
        comp = full ^ S
        c = 0
        T = S
        while T:
            b = T & (-T)
            v = b.bit_length() - 1
            c += popcount(adj[v] & comp)
            T ^= b
        if c > best:
            best = c
    return m - best, best, m


def maxcut_bip_weighted(n, edges, w):
    """EXACT min over cuts of sum_{monochromatic uv} w_u w_v (integer w)."""
    E = {(min(u, v), max(u, v)) for u, v in edges}
    tot = 0
    for u, v in E:
        tot += w[u] * w[v]
    # weighted crossing value, same complement trick but with weights
    best = -1
    adjlist = [[] for _ in range(n)]
    for u, v in E:
        adjlist[u].append(v)
        adjlist[v].append(u)
    for half in range(1 << (n - 1)):
        S = (half << 1) | 1
        c = 0
        for v in range(n):
            if (S >> v) & 1:
                wv = w[v]
                for u in adjlist[v]:
                    if not ((S >> u) & 1):
                        c += wv * w[u]
        if c > best:
            best = c
    return tot - best, tot


def is_bipartite(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    col = [-1] * n
    for s in range(n):
        if col[s] >= 0:
            continue
        col[s] = 0
        st = [s]
        while st:
            x = st.pop()
            for y in adj[x]:
                if col[y] < 0:
                    col[y] = 1 - col[x]
                    st.append(y)
                elif col[y] == col[x]:
                    return False
    return True


def triangle_free(n, edges):
    adj = adjmasks(n, edges)
    for u, v in edges:
        if adj[u] & adj[v]:
            return False
    return True


def maximal_triangle_free(n, edges):
    if not triangle_free(n, edges):
        return False
    adj = adjmasks(n, edges)
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1:
                continue
            if not (adj[u] & adj[v]):
                return False
    return True


def twin_free(n, edges):
    adj = adjmasks(n, edges)
    for u in range(n):
        for v in range(u + 1, n):
            if adj[u] == adj[v]:
                return False
    return True


def min_common_degree(n, edges):
    """delta_2 = min |N(x) cap N(y)| over NON-EDGES xy.  None if complete."""
    adj = adjmasks(n, edges)
    best = None
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1:
                continue
            c = popcount(adj[u] & adj[v])
            if best is None or c < best:
                best = c
    return best


def mindeg(n, edges):
    adj = adjmasks(n, edges)
    return min(popcount(a) for a in adj)


# --------------------------------------------------- Andrasfai constructions

def and_heinig(k):
    """Heinig: V={v_0..v_{3k-2}}, v_i~v_j iff i-j = 1 (mod 3)."""
    n = 3 * k - 1
    E = [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) % 3 == 1]
    return n, E


def gamma_bt(i):
    """Brandt-Thomasse Gamma_i: V={0..3i-2}, j ~ j+i,...,j+2i-1 (mod 3i-1)."""
    n = 3 * i - 1
    E = set()
    for j in range(n):
        for s in range(i, 2 * i):
            t = (j + s) % n
            if t != j:
                E.add((min(j, t), max(j, t)))
    return n, sorted(E)


def iso_by_multiplier(i):
    """EXACT proof that Gamma_i ~= And_i: the map x |-> 3x mod (3i-1).

    3*{i,...,2i-1} = {3i, 3i+3, ..., 6i-3} = {1,4,...,3i-2} (mod 3i-1),
    which is exactly the set of residues == 1 (mod 3) in [1,3i-2].
    Verified here as a set identity, then as an edge-set bijection.
    """
    n = 3 * i - 1
    S_bt = {s % n for s in range(i, 2 * i)}
    S_bt |= {(-s) % n for s in range(i, 2 * i)}
    S_he = {d for d in range(1, n) if d % 3 == 1 or (n - d) % 3 == 1}
    mapped = {(3 * s) % n for s in S_bt}
    if mapped != S_he:
        return False, S_bt, S_he, mapped
    n1, E1 = gamma_bt(i)
    n2, E2 = and_heinig(i)
    img = {(min(3 * u % n, 3 * v % n), max(3 * u % n, 3 * v % n)) for u, v in E1}
    return img == set(E2), S_bt, S_he, mapped


def heinig_F(k):
    """The explicit bipartification used by the target (retyped)."""
    U1 = set()
    for a in range(0, k // 2):
        for b in range(a, k // 2):
            p, q = (3 * k - 4) - 3 * a, (3 * k - 5) - 3 * b
            U1.add((min(p, q), max(p, q)))
    U2 = set()
    for a in range(0, (k - 1) // 2):
        for b in range(0, (k - 1) // 2 - a):
            p, q = 3 * a, (3 * a + 1) + 3 * b
            U2.add((min(p, q), max(p, q)))
    return U1 | U2


def moebius_ladder_8():
    """C8 plus the four main diagonals = Wagner graph V8."""
    E = set()
    for j in range(8):
        for s in (1, 4):
            t = (j + s) % 8
            if t != j:
                E.add((min(j, t), max(j, t)))
    return 8, sorted(E)


def iso_backtrack(n1, E1, n2, E2):
    """Exact isomorphism test by backtracking with degree pruning."""
    if n1 != n2 or len(set(map(frozenset, E1))) != len(set(map(frozenset, E2))):
        return False
    a1, a2 = adjmasks(n1, E1), adjmasks(n2, E2)
    d1 = [popcount(x) for x in a1]
    d2 = [popcount(x) for x in a2]
    if sorted(d1) != sorted(d2):
        return False
    order = sorted(range(n1), key=lambda z: -d1[z])
    img = [-1] * n1
    used = [False] * n1

    def rec(t):
        if t == n1:
            return True
        u = order[t]
        for v in range(n2):
            if used[v] or d2[v] != d1[u]:
                continue
            ok = True
            for s in range(t):
                x = order[s]
                if (((a1[u] >> x) & 1) != ((a2[v] >> img[x]) & 1)):
                    ok = False
                    break
            if ok:
                img[u] = v
                used[v] = True
                if rec(t + 1):
                    return True
                used[v] = False
                img[u] = -1
        return False

    return rec(0)


def iso_exhaustive(n1, E1, n2, E2):
    if n1 != n2 or len(E1) != len(E2):
        return False
    S2 = {(min(u, v), max(u, v)) for u, v in E2}
    for p in permutations(range(n1)):
        if {(min(p[u], p[v]), max(p[u], p[v])) for u, v in E1} == S2:
            return True
    return False


# -------------------------------------------------------- Vega construction
# Retyped independently from the Brandt-Thomasse text quoted in G11.md b.3:
#   "start with Gamma_i on {1,...,3i-1} and add an edge xy and an induced
#    6-cycle (a,v,c,u,b,w) such that x is joined to a,b,c and y is joined to
#    u,v,w.  N(a),N(u) on Gamma_i is {1,...,i}.  N(b),N(v) is {i+1,...,2i}.
#    N(c),N(w) is {2i+1,...,3i-1}."
# Here vertices are integers: 0..3i-2 are the Gamma_i labels 1..3i-1 shifted
# down by one; then x,y,a,b,c,u,v,w get indices 3i-1 .. 3i+6.

def vega_upsilon(i):
    n0 = 3 * i - 1
    _, Eg = gamma_bt(i)          # labels 0..3i-2  == BT labels 1..3i-1
    E = set(Eg)
    X, Y, A, B, C, U, V, W = (n0, n0 + 1, n0 + 2, n0 + 3,
                              n0 + 4, n0 + 5, n0 + 6, n0 + 7)
    n = n0 + 8                                    # 3i+7
    E.add((X, Y))
    six = [(A, V), (V, C), (C, U), (U, B), (B, W), (W, A)]
    for u, v in six:
        E.add((min(u, v), max(u, v)))
    for t in (A, B, C):
        E.add((min(X, t), max(X, t)))
    for t in (U, V, W):
        E.add((min(Y, t), max(Y, t)))
    # BT labels 1..i  ->  indices 0..i-1 ; i+1..2i -> i..2i-1 ; 2i+1..3i-1 -> 2i..3i-2
    grpA = list(range(0, i))
    grpB = list(range(i, 2 * i))
    grpC = list(range(2 * i, 3 * i - 1))
    for j in grpA:
        E.add((min(A, j), max(A, j)))
        E.add((min(U, j), max(U, j)))
    for j in grpB:
        E.add((min(B, j), max(B, j)))
        E.add((min(V, j), max(V, j)))
    for j in grpC:
        E.add((min(C, j), max(C, j)))
        E.add((min(W, j), max(W, j)))
    names = {X: 'x', Y: 'y', A: 'a', B: 'b', C: 'c', U: 'u', V: 'v', W: 'w'}
    return n, sorted(E), names, (X, Y, A, B, C, U, V, W)


def relabel_delete(n, E, kill):
    keep = [z for z in range(n) if z not in kill]
    idx = {z: t for t, z in enumerate(keep)}
    E2 = [(idx[u], idx[v]) for u, v in E if u not in kill and v not in kill]
    return len(keep), sorted((min(a, b), max(a, b)) for a, b in E2), idx


def vega_family(i):
    """The four Vega graphs from Upsilon_i, with the BT integer weights."""
    n, E, names, spec = vega_upsilon(i)
    X, Y, A, B, C, U, V, W = spec
    one = 0                      # BT label 1   -> index 0
    twoi = 2 * i - 1             # BT label 2i  -> index 2i-1
    lab_i = i - 1                # BT label i   -> index i-1
    out = {}

    # Upsilon_i
    w = [3] * n
    for z in (X, Y, one, twoi):
        w[z] = 1
    for z in (C, W):
        w[z] = 3 * i - 3
    for z in (U, V, A, B):
        w[z] = 3 * i - 2
    out['Ups_%d' % i] = (n, E, w, 9 * i - 6, 27 * i - 19)

    # Upsilon_i - {y}
    n1, E1, id1 = relabel_delete(n, E, {Y})
    w1 = [3] * n1
    for z in (one, twoi):
        w1[id1[z]] = 1
    w1[id1[X]] = 2
    w1[id1[W]] = 3 * i - 4
    for z in (U, V, C):
        w1[id1[z]] = 3 * i - 3
    for z in (A, B):
        w1[id1[z]] = 3 * i - 2
    out['Ups_%d-y' % i] = (n1, E1, w1, 9 * i - 7, 27 * i - 22)

    # Upsilon_i - {2i}
    n2, E2, id2 = relabel_delete(n, E, {twoi})
    w2 = [3] * n2
    for z in (X, Y):
        w2[id2[z]] = 1
    for z in (one, lab_i):
        w2[id2[z]] = 2
    for z in (B, V, C, W):
        w2[id2[z]] = 3 * i - 3
    for z in (U, A):
        w2[id2[z]] = 3 * i - 2
    out['Ups_%d-2i' % i] = (n2, E2, w2, 9 * i - 7, 27 * i - 22)

    # Upsilon_i - {y, 2i}
    n3, E3, id3 = relabel_delete(n, E, {Y, twoi})
    w3 = [3] * n3
    for z in (X, one, lab_i):
        w3[id3[z]] = 2
    for z in (V, W):
        w3[id3[z]] = 3 * i - 4
    for z in (U, B, C):
        w3[id3[z]] = 3 * i - 3
    w3[id3[A]] = 3 * i - 2
    out['Ups_%d-y-2i' % i] = (n3, E3, w3, 9 * i - 8, 27 * i - 25)
    return out


def grotzsch():
    """Mycielskian of C5 -- the standard Grotzsch graph, 11 vertices, 20 edges."""
    E = set()
    for j in range(5):
        E.add((min(j, (j + 1) % 5), max(j, (j + 1) % 5)))     # C5 on 0..4
    for j in range(5):                                        # u_j = 5+j
        for t in ((j + 1) % 5, (j - 1) % 5):
            E.add((min(5 + j, t), max(5 + j, t)))
        E.add((min(5 + j, 10), max(5 + j, 10)))               # apex = 10
    return 11, sorted(E)


def chromatic_number(n, E, cap=6):
    adj = adjmasks(n, E)
    order = sorted(range(n), key=lambda z: -popcount(adj[z]))
    for k in range(1, cap + 1):
        col = [-1] * n

        def bt(idx, used_max):
            if idx == n:
                return True
            z = order[idx]
            forb = 0
            t = adj[z]
            while t:
                b = t & (-t)
                y = b.bit_length() - 1
                if col[y] >= 0:
                    forb |= 1 << col[y]
                t ^= b
            for cc in range(min(k, used_max + 1)):
                if (forb >> cc) & 1:
                    continue
                col[z] = cc
                if bt(idx + 1, max(used_max, cc + 1)):
                    return True
                col[z] = -1
            return False

        if bt(0, 0):
            return k
    return None


# ------------------------------------------------------------------- checks

def sep(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def main():
    fails = []

    def check(name, cond, detail=""):
        print(("  [OK]   " if cond else "  [FAIL] ") + name + ("  " + detail if detail else ""))
        if not cond:
            fails.append(name)

    # ------------------------------------------------------------------ A
    sep("A. bip(And_k) by INDEPENDENT exhaustive max-cut vs floor(k^2/4)")
    for k in range(2, 8):
        n, E = and_heinig(k)
        assert triangle_free(n, E), k
        b, mc, m = maxcut_bip(n, E)
        pred = (k * k) // 4
        r = Fraction(b, n * n)
        print(f"   k={k}  n={n:3d}  |E|={m:3d}  maxcut={mc:3d}  bip={b:3d}  "
              f"floor(k^2/4)={pred:3d}  bip/n^2={r}={float(r):.6f}")
        check(f"bip(And_{k}) == floor(k^2/4)", b == pred, f"({b} vs {pred})")
        check(f"bip(And_{k})/n^2 <= 1/25", r <= Fraction(1, 25))

    # ------------------------------------------------------------------ B
    sep("B. Heinig F_k: subset, bipartification, |F_k| = floor(k^2/4)")
    for k in range(2, 12):
        n, E = and_heinig(k)
        Es = set(E)
        F = heinig_F(k)
        sub = F <= Es
        rest = sorted(Es - F)
        bipq = is_bipartite(n, rest)
        pred = (k * k) // 4
        pred2 = ((n + 1) ** 2) // 36
        print(f"   k={k:2d} n={n:3d} |F|={len(F):3d} floor(k^2/4)={pred:3d} "
              f"floor((n+1)^2/36)={pred2:3d} subset={sub} bipartite={bipq}")
        check(f"F_{k} subset E(And_{k})", sub)
        check(f"And_{k}-F_{k} bipartite", bipq)
        check(f"|F_{k}| == floor(k^2/4) == floor((n+1)^2/36)",
              len(F) == pred == pred2)

    # ------------------------------------------------------------------ C
    sep("C. floor((n+1)^2/36) <= n^2/25 for n=3k-1: EXACT, ALL k (not a finite check)")
    print("   k^2/4 <= (3k-1)^2/25  <=>  25k^2 <= 36k^2-24k+4  <=>  11k^2-24k+4 >= 0")
    print("   roots of 11k^2-24k+4: k = (24 +- 20)/22 = 2 and 2/11")
    for k in range(2, 40):
        q = 11 * k * k - 24 * k + 4
        assert q >= 0
        if k <= 6 or q == 0:
            print(f"     k={k}: 11k^2-24k+4 = {q}  ({'EQUALITY' if q == 0 else 'strict'})")
    check("11k^2-24k+4 >= 0 for all integers k>=2, =0 only at k=2",
          all(11 * k * k - 24 * k + 4 >= 0 for k in range(2, 2000)) and
          [k for k in range(2, 2000) if 11 * k * k - 24 * k + 4 == 0] == [2])
    for k in range(2, 15):
        n = 3 * k - 1
        lhs = Fraction(((n + 1) ** 2) // 36)
        rhs = Fraction(n * n, 25)
        check(f"floor((n+1)^2/36) <= n^2/25 at k={k}", lhs <= rhs,
              f"{lhs} vs {rhs}" + ("  EQUALITY" if lhs == rhs else ""))

    # ------------------------------------------------------------------ D
    sep("D. Gamma_i == And_i by an EXPLICIT multiplier map (x -> 3x mod 3i-1)")
    for i in range(2, 12):
        ok, Sbt, She, mapped = iso_by_multiplier(i)
        check(f"Gamma_{i} --(x->3x)--> And_{i} is an edge-set bijection", ok,
              f"3*S_BT={sorted(mapped)}  S_Heinig={sorted(She)}")
    n1, E1 = gamma_bt(3)
    n2, E2 = moebius_ladder_8()
    check("Gamma_3 iso Moebius ladder M_8 (exhaustive 8! search)",
          iso_exhaustive(n1, E1, n2, E2))
    b, mc, m = maxcut_bip(*moebius_ladder_8())
    check("bip(Wagner V8) == 2 and 2/64 == 1/32", b == 2 and Fraction(b, 64) == Fraction(1, 32),
          f"bip={b} maxcut={mc} |E|={m}")

    # ------------------------------------------------------------------ E
    sep("E. VEGA graphs: independent construction + structure + exact bip and psi")
    print("   name            n   TF  maxTF twinF  wreg  deg  totw   bip   bip/n^2      psi_BT")
    best = None
    for i in range(2, 7):
        for name, (n, E, w, degp, totp) in sorted(vega_family(i).items()):
            tf = triangle_free(n, E)
            mtf = maximal_triangle_free(n, E)
            tw = twin_free(n, E)
            adj = adjmasks(n, E)
            wdeg = set()
            for z in range(n):
                s = 0
                t = adj[z]
                while t:
                    bb = t & (-t)
                    s += w[bb.bit_length() - 1]
                    t ^= bb
                wdeg.add(s)
            wreg = (len(wdeg) == 1)
            dv = next(iter(wdeg)) if wreg else None
            tw_tot = sum(w)
            if n <= 22:
                b, mc, m = maxcut_bip(n, E)
                num, tot2 = maxcut_bip_weighted(n, E, w)
                psi = Fraction(num, tw_tot * tw_tot)
                rb = Fraction(b, n * n)
                if best is None or rb > best[0]:
                    best = (rb, name, b, n)
                s_b = f"{b:4d}  {str(rb):>10s}"
                s_p = f"{psi} = {float(psi):.6f}"
            else:
                s_b = "   -           -"
                s_p = "skipped(n>22)"
                rb = None
                psi = None
            print(f"   {name:14s} {n:3d}  {tf!s:5s} {mtf!s:5s} {tw!s:5s} {wreg!s:5s} "
                  f"{dv}={degp}? {tw_tot}={totp}?  {s_b}   psi={s_p}")
            check(f"{name}: triangle-free", tf)
            check(f"{name}: maximal triangle-free", mtf)
            check(f"{name}: twin-free", tw)
            check(f"{name}: BT weights regular with degree {degp}", wreg and dv == degp,
                  f"got {dv}")
            check(f"{name}: total weight {totp}", tw_tot == totp, f"got {tw_tot}")
            if rb is not None:
                check(f"{name}: bip/n^2 <= 1/25", rb <= Fraction(1, 25), str(rb))
                check(f"{name}: psi_BT <= 1/25", psi <= Fraction(1, 25), str(psi))
    print(f"   MAX bip/n^2 over the Vega graphs tested: {best}")
    check("report's max bip/n^2 = 8/225 on Ups_3-2i",
          best is not None and best[0] == Fraction(8, 225) and best[1] == 'Ups_3-2i',
          str(best))

    # ------------------------------------------------------------------ F
    sep("F. Ups_2 - {y,2i} vs the Grotzsch graph (Mycielskian of C5)")
    fam2 = vega_family(2)
    n, E, w, _, _ = fam2['Ups_2-y-2i']
    ng, Eg = grotzsch()
    print(f"   Ups_2-y-2i: n={n} |E|={len(E)}   Grotzsch: n={ng} |E|={len(Eg)}")
    check("Ups_2-y-2i has 11 vertices and 20 edges", n == 11 and len(E) == 20)
    check("chi(Ups_2-y-2i) == 4", chromatic_number(n, E) == 4)
    check("Ups_2-y-2i IS ISOMORPHIC to the Grotzsch graph (exact backtracking)",
          iso_backtrack(n, E, ng, Eg),
          f"degseq {sorted(popcount(a) for a in adjmasks(n,E))} vs "
          f"{sorted(popcount(a) for a in adjmasks(ng,Eg))}")

    # ------------------------------------------------------------------ G
    sep("G. delta_2 vs delta: is {delta_2 > floor(n/8)} a SUPERSET of {delta > floor(3n/8)}?")
    # K_{8,8} minus a perfect matching
    n = 16
    E = [(u, 8 + v) for u in range(8) for v in range(8) if u != v]
    d = mindeg(n, E)
    d2 = min_common_degree(n, E)
    b, mc, m = maxcut_bip(n, E)
    print(f"   G = K_{{8,8}} - perfect matching: n={n} |E|={m} delta={d} "
          f"floor(3n/8)={(3*n)//8}  delta_2={d2} floor(n/8)={n//8}  bip={b}")
    check("FALSIFIER: triangle-free", triangle_free(n, E))
    check("FALSIFIER: delta > floor(3n/8)", d > (3 * n) // 8, f"{d} > {(3*n)//8}")
    check("FALSIFIER: delta_2 <= floor(n/8)  => region containment FAILS",
          d2 <= n // 8, f"delta_2={d2} <= {n//8}")
    # the report's own witness G_2 (C5 blow-up 1,2,1,1,2 scaled by 7 -> n=49)
    parts = [7, 14, 7, 7, 14]
    off = [0]
    for p in parts:
        off.append(off[-1] + p)
    nb = off[-1]
    Eb = []
    for i in range(5):
        j = (i + 1) % 5
        for a in range(off[i], off[i + 1]):
            for c in range(off[j], off[j + 1]):
                Eb.append((min(a, c), max(a, c)))
    db = mindeg(nb, Eb)
    d2b = min_common_degree(nb, Eb)
    print(f"   G_2 = C5[7,14,7,7,14]: n={nb} delta={db} floor(3n/8)={(3*nb)//8} "
          f"delta_2={d2b} floor(n/8)={nb//8}  maximal-TF={maximal_triangle_free(nb,Eb)}")
    check("G_2: delta_2 > floor(n/8)", d2b > nb // 8, f"{d2b} > {nb//8}")
    check("G_2: delta <= floor(3n/8)", db <= (3 * nb) // 8, f"{db} <= {(3*nb)//8}")

    # ------------------------------------------------------------------ H
    sep("H. EFPS Theorem 1 second term:  c - 4c^2 <= 1/25 iff c<=1/20 or c>=1/5")
    for c in [Fraction(1, 20), Fraction(1, 5), Fraction(1, 8), Fraction(21, 100),
              Fraction(1, 4), Fraction(3, 50)]:
        val = c - 4 * c * c
        print(f"   c={c}: c-4c^2 = {val} = {float(val):.6f}   <=1/25? {val <= Fraction(1,25)}")
    check("equality at c=1/20", Fraction(1, 20) - 4 * Fraction(1, 20) ** 2 == Fraction(1, 25))
    check("equality at c=1/5", Fraction(1, 5) - 4 * Fraction(1, 5) ** 2 == Fraction(1, 25))
    check("100c^2-25c+1 = (5c-1)(20c-1)",
          all(100 * c * c - 25 * c + 1 == (5 * c - 1) * (20 * c - 1)
              for c in [Fraction(a, 97) for a in range(1, 40)]))
    check("max over c of min{c/2, c-4c^2, 1/4-c} = 1/16 at c=1/8",
          min(Fraction(1, 16), Fraction(1, 8) - 4 * Fraction(1, 64),
              Fraction(1, 4) - Fraction(1, 8)) == Fraction(1, 16))
    check("1/4 - c <= 1/25 iff c >= 21/100",
          Fraction(1, 4) - Fraction(21, 100) == Fraction(1, 25))

    # ------------------------------------------------------------------ I
    sep("I. exact constants quoted in the report")
    check("1/23.5 == 2/47", Fraction(2, 47) == Fraction(1, Fraction(47, 2)))
    check("0.0409 < 2/47", Fraction(409, 10000) < Fraction(2, 47),
          f"2/47={float(Fraction(2,47)):.7f}")
    check("Clebsch 8/256 = 1/32", Fraction(8, 256) == Fraction(1, 32))
    check("HoffmanSingleton 50/2500 = 1/50", Fraction(50, 2500) == Fraction(1, 50))
    check("Gewirtz 84/3136 = 3/112", Fraction(84, 3136) == Fraction(3, 112))
    check("HigmanSims 350/10000 = 7/200", Fraction(350, 10000) == Fraction(7, 200))
    check("8/225 < 1/25 (= 9/225)", Fraction(8, 225) < Fraction(1, 25))
    check("all four SRG ratios < 1/25",
          max(Fraction(1, 32), Fraction(1, 50), Fraction(3, 112), Fraction(7, 200))
          < Fraction(1, 25))
    check("BT weighted delta (9i-6)/(27i-19) > 1/3 for i=2..40",
          all(Fraction(9 * i - 6, 27 * i - 19) > Fraction(1, 3) for i in range(2, 41)))

    sep("SUMMARY")
    print(f"   checks failed: {len(fails)}")
    for f in fails:
        print("     FAIL:", f)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    sys.exit(main())
