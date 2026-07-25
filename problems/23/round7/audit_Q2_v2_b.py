"""audit_Q2_v2_b.py -- AUDIT pass 2, block B: the obstruction W*(u,r).

Independent construction: vertices are laid out INTERLEAVED (v -> class v mod 5
never used by Q2_wstar*.py), Delta is obtained by RECOMPUTING the cut, and the
minimum improving switch is found by ITERATIVE DEEPENING on |S| (a different
algorithm from Q2's pruned DFS).  Exact integers only.
"""
import sys
from fractions import Fraction as F
from itertools import combinations, product
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q2_v2_core import (g6_encode, pc, edges, is_trianglefree, is_maximal_tf,
                              mono, maxcut_bip, sigma, delta_recompute, delta_formula,
                              indep_sets)

HR = "=" * 78
W = lambda u: [2 * u, 2 * u, 3 * u, 2 * u, 3 * u]


def build_wstar(u, r):
    """C5[2u,2u,3u,2u,3u] with an INTERLEAVED vertex order (round-robin over classes),
    cut X = c0 u c2 u (c3 \\ R), Y = c1 u c4 u R, |R| = r."""
    w = W(u)
    cls = [[] for _ in range(5)]
    v = 0
    # round-robin: fill classes in rotation, so vertex ids do not respect classes
    rem = list(w)
    i = 0
    while sum(rem) > 0:
        if rem[i]:
            cls[i].append(v); v += 1; rem[i] -= 1
        i = (i + 1) % 5
    n = v
    adj = [0] * n
    for i in range(5):
        j = (i + 1) % 5
        for x in cls[i]:
            for y in cls[j]:
                adj[x] |= 1 << y
                adj[y] |= 1 << x
    Y = 0
    for x in cls[1] + cls[4]:
        Y |= 1 << x
    R = cls[3][:r]
    for x in R:
        Y |= 1 << x
    groups = [cls[0], cls[1], cls[2], cls[3][r:], R, cls[4]]   # c0,c1,c2,c3\R,R,c4
    return n, adj, Y, cls, groups


def group_delta_fn(n, adj, Y, groups):
    """Delta as an exact quadratic form in the six group counts (derived from the
    graph, not assumed): returns (sig_g, coef[A][B])."""
    sg = sigma(n, adj, Y)
    g = len(groups)
    sigg = [sg[G[0]] for G in groups]
    coef = [[0] * g for _ in range(g)]
    for A in range(g):
        for B in range(A + 1, g):
            a0, b0 = groups[A][0], groups[B][0]
            if (adj[a0] >> b0) & 1:
                coef[A][B] = -2 if ((Y >> a0) & 1) == ((Y >> b0) & 1) else 2
    return sigg, coef, sg


def delta_counts(sigg, coef, s):
    g = len(s)
    d = -sum(s[i] * sigg[i] for i in range(g))
    for A in range(g):
        for B in range(A + 1, g):
            if coef[A][B]:
                d += coef[A][B] * s[A] * s[B]
    return d


def min_improving_iterdeep(sizes, sigg, coef, cap=None):
    """ITERATIVE DEEPENING on k=|S|: enumerate every composition of k over the
    six groups (bounded by sizes) and test Delta>0.  Returns first k that works."""
    g = len(sizes)
    k = 1
    while cap is None or k <= cap:
        # enumerate compositions of k with s_i <= sizes[i]
        found = None
        def rec(i, rem, cur):
            nonlocal found
            if found is not None:
                return
            if i == g - 1:
                if rem <= sizes[i]:
                    s = cur + [rem]
                    if delta_counts(sigg, coef, s) > 0:
                        found = tuple(s)
                return
            lo = max(0, rem - sum(sizes[i + 1:]))
            for x in range(lo, min(sizes[i], rem) + 1):
                rec(i + 1, rem - x, cur + [x])
                if found is not None:
                    return
        rec(0, k, [])
        if found is not None:
            return k, found
        k += 1
        if k > sum(sizes):
            return None, None


print(HR); print("B1  W*(u,r): closed forms re-derived from the vertex-level graph")
print(HR)
print("  u  r |   N |  |E| | |M| | 25|M|-N^2 | 25|M|/N^2 | bip(G) exact | N^2/25 | sigma per group")
for u in range(1, 10):
    r = u
    n, adj, Y, cls, groups = build_wstar(u, r)
    E = len(edges(n, adj))
    M = mono(n, adj, Y)
    sg = sigma(n, adj, Y)
    sigg = [sg[G[0]] for G in groups if G]
    # bip via corner enumeration over the 5 C5-classes (Lemma 2, verified in block A)
    bip = min(sum(W(u)[i] * W(u)[(i + 1) % 5] for i in range(5)
                  if ((m >> i) & 1) == ((m >> ((i + 1) % 5)) & 1)) for m in range(32))
    if n <= 14:
        bipbf = maxcut_bip(n, adj)
        assert bipbf == bip, (bipbf, bip)
    tf = is_trianglefree(n, adj)
    print(f"  {u:2d} {r:2d} | {n:3d} | {E:4d} | {M:3d} | {25*M-n*n:9d} | {str(F(25*M,n*n)):9s} | "
          f"{bip:6d} = N^2/{F(n*n,bip)} | {str(F(n*n,25)):7s} | {sigg}  tri-free={tf}")
print("  Q2.md: |E|=28u^2, |M|=6u^2, 25|M|/N^2=25/24, bip=4u^2=N^2/36, sigma=[5u,5u,2r,0,0,4u-2r]")

print(); print(HR); print("B2  Delta depends only on the six group counts?  (justifies the reduction)")
print(HR)
import random
random.seed(7)
for u in (1, 2, 3):
    n, adj, Y, cls, groups = build_wstar(u, u)
    sigg, coef, sg = group_delta_fn(n, adj, Y, groups)
    bad = 0
    trials = 4000 if u > 1 else (1 << n)
    for t in range(trials):
        S = random.getrandbits(n) if u > 1 else t
        s = [pc(S & sum(1 << x for x in G)) for G in groups]
        if delta_recompute(n, adj, Y, S) != delta_counts(sigg, coef, s):
            bad += 1
    print(f"   u={u}: {'ALL 2^%d subsets' % n if u==1 else '%d random subsets' % trials}: "
          f"count-formula mismatches = {bad}")

print(); print(HR); print("B3  minimum improving switch of W*(u,u) -- iterative deepening")
print(HR)
q2 = {1: 5, 2: 9, 3: 12, 4: 16, 5: 19, 6: 23, 7: 26, 8: 30, 9: 33}
print("   u |   N | min|S| | ceil((7u+3)/2) | |S|/N          | witness (c0,c1,c2,c3-R,R,c4) | Q2.md")
ratios = []
for u in list(range(1, 13)):
    n, adj, Y, cls, groups = build_wstar(u, u)
    sigg, coef, sg = group_delta_fn(n, adj, Y, groups)
    sizes = [len(G) for G in groups]
    k, wit = min_improving_iterdeep(sizes, sigg, coef)
    pred = -((-(7 * u + 3)) // 2)
    if u <= 9:
        ratios.append(F(k, n))
    flag = ""
    if u in q2:
        flag = "ok" if q2[u] == k else f"<<< MISMATCH Q2.md says {q2[u]}"
    print(f"  {u:3d} | {n:3d} | {k:5d}  | {pred:13d}  | {str(F(k,n)):8s} = {float(F(k,n)):.5f} | "
          f"{wit} | {flag} {'[formula ok]' if k==pred else '[FORMULA WRONG]'}")
print(f"   min over u<=9 of |S|/N = {min(ratios)} = {float(min(ratios)):.5f}   (Q2.md: >= 0.3055 for N<=108)")
print(f"   7/24 = {float(F(7,24)):.6f} ; every improving S has |S| > (7/24)N ?",
      all(F(k, 12 * u) > F(7, 24) for u, k in
          [(u, min_improving_iterdeep([len(G) for G in build_wstar(u, u)[4]],
            *group_delta_fn(*build_wstar(u, u)[:3], build_wstar(u, u)[4])[:2])[0]) for u in range(1, 10)]))

print(); print(HR); print("B4  which families does the W*(u,u) cut satisfy?  (exact, corner method)")
print(HR)


def max_delta_over(sizes, sigg, coef, lo, hi):
    """max of the multilinear Delta over the box [lo_i, hi_i] -- attained at a corner."""
    g = len(sizes)
    best = None; arg = None
    for m in range(1 << g):
        s = [hi[i] if (m >> i) & 1 else lo[i] for i in range(g)]
        d = delta_counts(sigg, coef, s)
        if best is None or d > best:
            best, arg = d, tuple(s)
    return best, arg


for u in range(1, 8):
    n, adj, Y, cls, groups = build_wstar(u, u)
    sigg, coef, sg = group_delta_fn(n, adj, Y, groups)
    sizes = [len(G) for G in groups]
    g = 6
    # class of each group in the C5 (c0,c1,c2,c3,c3,c4)
    gcls = [0, 1, 2, 3, 3, 4]
    sigok = all(x >= 0 for x in sg)
    # switch-star, vertex level
    ssok = True
    for v in range(n):
        yv = (Y >> v) & 1
        NB = adj[v] & (Y if not yv else ~Y) & ((1 << n) - 1)
        rhs = 0
        j = NB
        while j:
            bb = j & -j; kk = bb.bit_length() - 1; j ^= bb
            if 2 - sg[kk] > 0:
                rhs += 2 - sg[kk]
        if sg[v] < rhs:
            ssok = False
    # family (*), SUP, NBRU, PAIRNBR at the group/corner level
    def nbr_counts(gi):
        """counts of N(v) for v in group gi"""
        c = gcls[gi]
        out = [0] * g
        for k in range(g):
            if (gcls[k] - c) % 5 in (1, 4):
                out[k] = sizes[k]
        return out
    best_star = best_sup = best_nbru = best_pair = None
    for gi in range(g):
        if sizes[gi] == 0:
            continue
        lo = nbr_counts(gi)
        # (*) : S = N(v) u T, T independent (support = pairwise non-adjacent classes),
        #       T disjoint from N(v)
        free = [k for k in range(g) if lo[k] == 0]
        for m in range(1 << len(free)):
            sel = [free[i] for i in range(len(free)) if (m >> i) & 1]
            if any((gcls[a] - gcls[b]) % 5 in (1, 4) for a, b in combinations(sel, 2)):
                continue
            s = list(lo)
            for k in sel:
                s[k] = sizes[k]
            d = delta_counts(sigg, coef, s)
            if best_star is None or d > best_star[0]:
                best_star = (d, tuple(s), gi)
        # SUP: every superset of N(v) -> corners of the box [lo, sizes]
        d, arg = max_delta_over(sizes, sigg, coef, lo, sizes)
        if best_sup is None or d > best_sup[0]:
            best_sup = (d, arg, gi)
    # NBRU: unions of neighbourhoods
    for m in range(1, 1 << g):
        s = [0] * g
        for gi in range(g):
            if (m >> gi) & 1 and sizes[gi]:
                lo = nbr_counts(gi)
                s = [max(s[k], lo[k]) for k in range(g)]
        d = delta_counts(sigg, coef, s)
        if best_nbru is None or d > best_nbru[0]:
            best_nbru = (d, tuple(s))
    # PAIRNBR: N(u) u N(v) over adjacent pairs
    for a in range(g):
        for b in range(g):
            if sizes[a] == 0 or sizes[b] == 0:
                continue
            if (gcls[a] - gcls[b]) % 5 not in (1, 4):
                continue
            la, lb = nbr_counts(a), nbr_counts(b)
            s = [max(la[k], lb[k]) for k in range(g)]
            d = delta_counts(sigg, coef, s)
            if best_pair is None or d > best_pair[0]:
                best_pair = (d, tuple(s))
    print(f"  u={u}: sigma>=0 {sigok}  switch-star {ssok}   max Delta:  (*)={best_star[0]}  "
          f"SUP={best_sup[0]}  NBRU={best_nbru[0]}  PAIRNBR={best_pair[0]}")
    print(f"        SUP argmax {best_sup[1]} (|S|={sum(best_sup[1])}, N={n}, |S|/N={float(F(sum(best_sup[1]),n)):.4f})")

print(); print(HR); print("B5  vertex-level family (*) at u=1,2 by FULL independent-set enumeration")
print(HR)
for u in (1, 2):
    n, adj, Y, cls, groups = build_wstar(u, u)
    full = (1 << n) - 1
    worst = None
    cnt = 0
    for v in range(n):
        Nv = adj[v]
        for T in indep_sets(n, adj, full & ~Nv):
            S = Nv | T
            d = delta_recompute(n, adj, Y, S)
            cnt += 1
            if worst is None or d > worst[0]:
                worst = (d, S, v)
    print(f"   u={u}: N={n}, {cnt} instances of (*), max Delta = {worst[0]}  "
          f"({'SATISFIED' if worst[0] <= 0 else 'VIOLATED'})")
