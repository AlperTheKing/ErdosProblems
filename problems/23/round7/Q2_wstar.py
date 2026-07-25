"""Q2_wstar.py -- the closed-form obstruction W*(u), verified twice in exact
integers: once from the explicit vertex-level graph, once from the blow-up
formulas.

W*(u):   G = C5[w0,w1,w2,w3,w4] with (w0,w1,w2,w3,w4) = (2u,2u,3u,2u,3u),
         C5 classes in cyclic order c0~c1~c2~c3~c4~c0,  N = 12u.
Cut:     X = c0 u c2 u (c3 \\ {z}),   Y = c1 u c4 u {z},   z a single vertex of c3.

Claims verified here for u = 1..8:
   |M| = 6u^2 = N^2/24    (so 25|M| - N^2 = 6u^2 > 0)
   sigma(v) >= 0 for every v
   every switch-star inequality holds
   every family-(*) inequality Delta(N(v) u T) <= 0 holds (T independent)
   the true bip(G) = 4u^2 = N^2/36  (so G itself obeys the conjecture)
   minimum improving switch |S| = ceil((5u+1)/2) + 2  ->  (5/24) N
"""
import sys
from fractions import Fraction as Fr
from itertools import combinations


def build(u):
    w = [2 * u, 2 * u, 3 * u, 2 * u, 3 * u]
    cls, V = [], 0
    for i in range(5):
        cls.append(list(range(V, V + w[i]))); V += w[i]
    n = V
    adj = [set() for _ in range(n)]
    for i in range(5):
        j = (i + 1) % 5
        for x in cls[i]:
            for y in cls[j]:
                adj[x].add(y); adj[y].add(x)
    # cut: side[v] = 0 (X) or 1 (Y)
    side = [0] * n
    for v in cls[1]:
        side[v] = 1
    for v in cls[4]:
        side[v] = 1
    z = cls[3][0]
    side[z] = 1                      # the single moved vertex; rest of c3 stays in X
    return n, adj, side, cls, w, z


def stats(n, adj, side):
    E = sum(len(adj[v]) for v in range(n)) // 2
    M = sum(1 for v in range(n) for u2 in adj[v] if u2 > v and side[u2] == side[v])
    sig = [sum(1 if side[u2] != side[v] else -1 for u2 in adj[v]) for v in range(n)]
    return E, M, sig


def delta(adj, side, sig, S):
    S = set(S)
    val = -sum(sig[v] for v in S)
    for v in S:
        for u2 in adj[v]:
            if u2 > v and u2 in S:
                val += -2 if side[u2] == side[v] else 2
    return val


def bip_C5_blowup(w):
    """exact bip of C5[w] (multilinearity: max cut is class-respecting)."""
    best = None
    for m in range(32):
        col = [(m >> i) & 1 for i in range(5)]
        M = sum(w[i] * w[(i + 1) % 5] for i in range(5) if col[i] == col[(i + 1) % 5])
        best = M if best is None else min(best, M)
    return best


def main():
    print("u |  N | |E| | |M| | 25|M|-N^2 | |M|/N^2 | bip(G) | sigma>=0 | switch-star | family(*) | min improving |S|")
    for u in range(1, 9):
        n, adj, side, cls, w, z = build(u)
        E, M, sig = stats(n, adj, side)
        assert M == 6 * u * u, (M, u)
        assert n == 12 * u
        sigok = all(s >= 0 for s in sig)
        # switch-star: sigma(v) >= sum over B-nbrs a with sigma(a)<=1 of (2-sigma(a))
        ssok = True
        for v in range(n):
            rhs = sum(2 - sig[a] for a in adj[v] if side[a] != side[v] and sig[a] <= 1)
            if sig[v] < rhs:
                ssok = False
                print(f"   switch-star VIOLATED at v={v}: {sig[v]} < {rhs}")
        # family (*): Delta(N(v) u T) <= 0 for T independent, T disjoint from N(v).
        # linear in T, so max-weight independent set with
        #   c(w) = -sigma(w) + 2 b_v(w) - 2 m_v(w)
        starok = True
        worst = None
        for v in range(n):
            Nv = adj[v]
            base = -sum(sig[a] for a in Nv)
            cw = {}
            for x in range(n):
                if x in Nv:
                    continue
                b = sum(1 for t in adj[x] if t in Nv and side[t] != side[x])
                m = sum(1 for t in adj[x] if t in Nv and side[t] == side[x])
                cw[x] = -sig[x] + 2 * b - 2 * m
            # greedy over classes is exact here: candidates are unions of classes/parts
            # -- do it exactly by brute force over class-level independent sets, since
            #    every vertex outside N(v) is in a class and classes are independent.
            best = base
            groups = []
            for i in range(5):
                gX = [x for x in cls[i] if x not in Nv and side[x] == 0]
                gY = [x for x in cls[i] if x not in Nv and side[x] == 1]
                if gX:
                    groups.append((i, gX))
                if gY:
                    groups.append((i, gY))
            for r in range(len(groups) + 1):
                for sel in combinations(range(len(groups)), r):
                    idx = [groups[k][0] for k in sel]
                    if any((abs(p - q) % 5) in (1, 4) for p, q in combinations(idx, 2)):
                        continue          # not independent in C5
                    tot = base
                    for k in sel:
                        # each group is a set of twins: take the positive-weight ones
                        tot += sum(max(cw[x], 0) for x in groups[k][1])
                    best = max(best, tot)
            if best > 0:
                starok = False
                worst = (v, best)
        # minimum improving switch: search over class-level counts (twins => counts only)
        # groups: (c0),(c1),(c2),(c3\z),(z),(c4)
        gl = [cls[0], cls[1], cls[2], cls[3][1:], [z], cls[4]]
        sizes = [len(g) for g in gl]
        bestS = None
        def rec(k, cur, tot):
            nonlocal bestS
            if bestS is not None and tot >= bestS[0]:
                return
            if k == len(gl):
                S = []
                for kk in range(len(gl)):
                    S += gl[kk][:cur[kk]]
                d = delta(adj, side, sig, S)
                if d > 0 and (bestS is None or tot < bestS[0]):
                    bestS = (tot, tuple(cur), d)
                return
            for c in range(sizes[k] + 1):
                rec(k + 1, cur + [c], tot + c)
        rec(0, [], 0)
        bipG = bip_C5_blowup(w)
        pred = (5 * u + 1 + 1) // 2 + 2
        print(f"{u} | {n:2d} | {E:3d} | {M:3d} | {25*M-n*n:9d} | {str(Fr(M,n*n)):7s} | {bipG:6d} | "
              f"{str(sigok):8s} | {str(ssok):11s} | {str(starok):9s} | "
              f"{bestS[0]} = {Fr(bestS[0],n)}N ({float(Fr(bestS[0],n)):.4f}) counts={bestS[1]} "
              f"[formula ceil((5u+1)/2)+2 = {pred}]")


main()
