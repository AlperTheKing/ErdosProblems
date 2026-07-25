"""ROUND 2 / G1 core computation: the Andrasfai family against the 1/25 ceiling.

Context. Chen-Jin-Koh: every triangle-free graph with delta > N/3 is either homomorphic to a graph
in an explicit finite Andrasfai-type family, or contains an induced Grotzsch graph. By the blow-up
identity, if G -> H then bip(G)/N^2 <= max_x psi(H,x), where
psi(H,x) = min over cuts S of sum_{uv monochromatic} x_u x_v on the simplex. So the finite
computation "max_x psi <= 1/25 for every H in that family" would close the whole regime
delta > N/3 for the graphs that map into the family. This script performs that computation for the
Andrasfai graphs themselves.

And(k) = circulant on Z_{3k-1} with connection set {k, k+1, ..., 2k-1}: k-regular, triangle-free,
vertex-transitive, n = 3k-1. Note And(2) = C5 (the extremal graph itself) and And(3) is isomorphic
to the Wagner graph C_8(1,4) (multiply the connection set by 3 mod 8).

Reported for each k: the exact uniform value psi(And(k), uniform) = bip(And(k))/n^2 computed by
exhaustive maximum cut, and a hill-climb maximum over the simplex re-evaluated in exact rationals.
The uniform value is a rigorous exact number; the maximum is a LOWER bound (hill-climbing only).
"""

import random
from fractions import Fraction


def andrasfai(k):
    n = 3 * k - 1
    conn = set()
    for d in range(k, 2 * k):
        conn.add(d % n)
        conn.add((-d) % n)
    adj = [0] * n
    for v in range(n):
        for d in conn:
            w = (v + d) % n
            if w != v:
                adj[v] |= 1 << w
    return n, adj


def edges_of(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def is_triangle_free(n, adj):
    return all(not (adj[u] & adj[v])
               for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1)


def maxcut_exhaustive(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best = cut
    for m in range(1, 1 << (n - 1)):
        v = (m & -m).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]; S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a; S |= 1 << v
        if cut > best:
            best = cut
    return best


def psi_float(n, E, x):
    best = None
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        t = 0.0
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                t += x[u] * x[v]
        if best is None or t < best:
            best = t
    return best


def psi_exact(n, E, x):
    best = None
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        t = Fraction(0)
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                t += x[u] * x[v]
        if best is None or t < best:
            best = t
    return best


def maximize(n, E, restarts, iters, seed):
    rnd = random.Random(seed)
    bv, bx = -1.0, None
    for _ in range(restarts):
        x = [rnd.random() + 1e-3 for _ in range(n)]
        s = sum(x); x = [t / s for t in x]
        cur = psi_float(n, E, x)
        step = 0.10
        for it in range(iters):
            i, j = rnd.randrange(n), rnd.randrange(n)
            if i == j:
                continue
            d = step * rnd.random() * x[i]
            if x[i] - d <= 0:
                continue
            y = list(x); y[i] -= d; y[j] += d
            v = psi_float(n, E, y)
            if v > cur:
                x, cur = y, v
            if it % 500 == 499:
                step *= 0.7
        if cur > bv:
            bv, bx = cur, x
    return bv, bx


LIMIT = Fraction(1, 25)
print("=" * 88)
print("Andrasfai graphs And(k): n = 3k-1, k-regular, triangle-free, vertex-transitive")
print("=" * 88)
print(f"{'k':>2} {'n':>3} {'|E|':>4} {'tri-free':>9} {'bip (exact)':>12} "
      f"{'uniform psi = bip/n^2':>22} {'max_x psi (lower bd)':>21} {'vs 1/25':>9}")
for k in range(2, 7):
    n, adj = andrasfai(k)
    E = edges_of(n, adj)
    tf = is_triangle_free(n, adj)
    mc = maxcut_exhaustive(n, adj)
    bip = len(E) - mc
    unif = Fraction(bip, n * n)
    restarts = 25 if n <= 14 else 8
    iters = 2500 if n <= 14 else 900
    v, xf = maximize(n, E, restarts, iters, 4242 + k)
    den = 2520
    xr = [Fraction(max(1, round(t * den)), den) for t in xf]
    s = sum(xr); xr = [t / s for t in xr]
    ve = psi_exact(n, E, xr)
    verdict = "ABOVE" if ve > LIMIT else ("EQUAL" if ve == LIMIT else "below")
    print(f"{k:>2} {n:>3} {len(E):>4} {str(tf):>9} {bip:>12} "
          f"{str(unif) + ' = ' + format(float(unif), '.5f'):>22} "
          f"{format(float(ve), '.6f'):>21} {verdict:>9}")

print()
print("=" * 88)
print("""Reading. And(2) = C5 is the extremal graph itself and sits exactly at 1/25. And(3) is the
Wagner graph C_8(1,4), the closest non-C5 competitor found anywhere in this project. From k = 4 on
the family recedes from the ceiling. The uniform column is exact (exhaustive maximum cut); the
max_x column is a hill-climb LOWER bound re-evaluated in exact rationals, so it can only refute the
ceiling, never confirm it -- see section 3g of round1/CLAUDE_GATE_RESULTS.md for what a rigorous
confirmation would require.""")
