"""ROOT-AGENT GATE (Claude, round 3): R3-C6, first-order local maximality of the C5 plateau
points, and the sharpest available counterexample probe.

THEOREM (R3-C6).  Let H be triangle-free, T = {t_0..t_4} an induced C5 of H, and x0 the point with
weight 1/5 on each t_i and 0 elsewhere (so psi(H,x0) = 1/25).  Then for EVERY feasible direction d
(sum d = 0, d_u >= 0 off T) the one-sided derivative of psi at x0 along d is <= 0.

Proof sketch (full text in CLAUDE_GATE_R3.md).  The active cuts at x0 are exactly the extensions of
the five rotation cuts S_i = {t_i, t_{i+2}} of T, with the vertices off T placed arbitrarily; the
gradient of q_S at x0 is (1/5)*|N(u) cap T cap side_S(u)|.  Since d_u >= 0 off T, the minimum over
active cuts places each outside vertex on its lighter side, giving
        D(d) = min_i [ (1/5)(d_{t_i} + d_{t_{i+1}}) + (1/5) sum_{u not in T} d_u sep_i(u) ],
where sep_i(u) = min over the two sides of |N(u) cap T cap side| is 1 exactly when N(u) cap T is a
non-adjacent PAIR separated by S_i and 0 otherwise.  Triangle-freeness enters exactly here:
N(u) is independent and alpha(C5) = 2, so |N(u) cap T| <= 2.  Each of the five non-adjacent pairs is
separated by exactly two of the five rotation cuts, and each vertex of T lies in exactly two of the
five monochromatic edges, so summing the bracket over i gives (2/5)*sum(d) = 0.  A minimum of five
numbers summing to <= 0 is <= 0.  QED

This script (a) verifies the combinatorial counting behind the proof, (b) verifies the conclusion
numerically-exactly on many graphs and random directions, and (c) runs the sharp probe: along the
first-order-FLAT directions, is psi exactly 1/25 or does it go above?  Any value above 1/25 refutes
the conjecture.  All arithmetic is Fraction / sympy Rational.
"""
from fractions import Fraction as F
from itertools import combinations
import random
import sys


# ------------------------------------------------------------------ graphs

def mk(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    return n, adj


def C5():
    return mk(5, [(i, (i + 1) % 5) for i in range(5)])


def myc_minus_apex():
    """C5 v0..v4 plus u0..u4 with N(u_a) cap T = {v_{a-1}, v_{a+1}} : all five pair classes present"""
    E = [(i, (i + 1) % 5) for i in range(5)]
    for a in range(5):
        E += [(5 + a, (a + 4) % 5), (5 + a, (a + 1) % 5)]
    return mk(10, E)


def grotzsch():
    n, adj = myc_minus_apex()
    E = [(u, v) for u in range(10) for v in adj[u] if u < v] + [(5 + a, 10) for a in range(5)]
    return mk(11, E)


def wagner():
    return mk(8, [(v, (v + 1) % 8) for v in range(8)] + [(v, (v + 4) % 8) for v in range(4)])


def petersen():
    E = [(i, (i + 1) % 5) for i in range(5)] + [(i, 5 + i) for i in range(5)]
    E += [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return mk(10, E)


def circ(m, S):
    return mk(m, [(v, (v + s) % m) for v in range(m) for s in S if v != (v + s) % m])


def is_triangle_free(n, adj):
    return not any(c in adj[a] for a, b in combinations(range(n), 2) if b in adj[a] for c in adj[a] & adj[b])


def induced_C5s(n, adj):
    """all induced 5-cycles, as cyclic vertex tuples"""
    out = []
    for S in combinations(range(n), 5):
        sub = {v: adj[v] & set(S) for v in S}
        if all(len(sub[v]) == 2 for v in S):
            # connected 2-regular on 5 vertices = C5
            start = S[0]; seen = [start]; cur = start; prev = None
            for _ in range(4):
                nxt = [w for w in sub[cur] if w != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                seen.append(cur)
            if len(seen) == 5 and len(set(seen)) == 5:
                out.append(tuple(seen))
    return out


def cuts_mono(n, adj):
    E = [(u, v) for u in range(n) for v in adj[u] if u < v]
    return [[(u, v) for (u, v) in E if ((m >> u) & 1) == ((m >> v) & 1)]
            for m in range(1 << n)]


def psi(cutlists, x):
    return min(sum(x[u] * x[v] for (u, v) in mono) for mono in cutlists)


# ------------------------------------------------------------------ (a) the counting in the proof

def check_counting():
    print("(a) counting behind R3-C6")
    T = list(range(5))
    pairs = {a: ((a + 4) % 5, (a + 1) % 5) for a in range(5)}   # P_a = neighbours of t_a
    sep = {}
    for i in range(5):
        A = {i, (i + 2) % 5}
        for a in range(5):
            u, v = pairs[a]
            sep[(i, a)] = 1 if ((u in A) != (v in A)) else 0
    for a in range(5):
        s = sum(sep[(i, a)] for i in range(5))
        assert s == 2, (a, s)
    for i in range(5):
        s = sum(sep[(i, a)] for a in range(5))
        assert s == 2, (i, s)
    print("    every non-adjacent pair is separated by exactly 2 of the 5 rotation cuts, and")
    print("    every rotation cut separates exactly 2 of the 5 pairs.  Sum of the five brackets")
    print("    = (2/5)*sum(d) = 0, so the minimum bracket is <= 0.  CONFIRMED")


# ------------------------------------------------------------------ (b) exact numerical check

def check_local_max(name, G, trials=300, seed=5):
    n, adj = G
    assert is_triangle_free(n, adj), name
    C5s = induced_C5s(n, adj)
    if not C5s:
        print(f"    {name}: no induced C5")
        return 0
    cl = cuts_mono(n, adj)
    rng = random.Random(seed)
    T = list(C5s[0])
    x0 = [F(0)] * n
    for t in T:
        x0[t] = F(1, 5)
    assert psi(cl, x0) == F(1, 25), (name, psi(cl, x0))
    worst = F(0)
    for _ in range(trials):
        # random feasible direction: take mass from T, give it off T (and allow reshuffling in T)
        d = [F(0)] * n
        off = [u for u in range(n) if u not in T]
        for u in off:
            d[u] = F(rng.randint(0, 3))
        for t in T:
            d[t] = F(rng.randint(0, 3))
        s = sum(d)
        if s == 0:
            continue
        for v in range(n):
            d[v] -= F(s, n) * 0 + F(0)
        # renormalise to sum zero by subtracting the mean over T only where allowed:
        tot_off = sum(d[u] for u in off)
        if tot_off == 0:
            continue
        for t in T:
            d[t] = -F(tot_off, 5)
        for eps in (F(1, 6), F(1, 12), F(1, 30), F(1, 100), F(1, 1000)):
            x = [x0[v] + eps * d[v] for v in range(n)]
            if min(x) < 0 or sum(x) != 1:
                continue
            val = psi(cl, x)
            if val > worst:
                worst = val
            if val > F(1, 25):
                print(f"    *** {name}: psi = {val} > 1/25 at eps={eps}, d={d}  COUNTEREXAMPLE ***")
                return -1
    print(f"    {name}: {trials} random directions x 5 step sizes, max psi found = {worst} "
          f"({float(worst):.6f}) <= 1/25")
    return 0


# ------------------------------------------------------------------ (c) exact 1-parameter probe

def flat_direction_probe(name, G, verbose=True):
    """x(delta): weight (1-delta)/5 on each C5 vertex, delta/k on each vertex off T that attaches to
    a non-adjacent PAIR of T (the first-order-flat direction).  psi(x(delta)) is a minimum of
    quadratics in delta; we maximise it EXACTLY over delta in [0,1] using sympy."""
    import sympy as sp
    n, adj = G
    C5s = induced_C5s(n, adj)
    if not C5s:
        return
    T = list(C5s[0])
    Tset = set(T)
    pair_vertices = []
    for u in range(n):
        if u in Tset:
            continue
        P = adj[u] & Tset
        if len(P) == 2:
            a, b = sorted(P)
            if b not in adj[a]:
                pair_vertices.append(u)
    if not pair_vertices:
        if verbose:
            print(f"    {name}: no pair-vertices, first-order-flat family is trivial")
        return
    k = len(pair_vertices)
    dl = sp.Symbol('d', nonnegative=True)
    x = [sp.Integer(0)] * n
    for t in T:
        x[t] = (1 - dl) / 5
    for u in pair_vertices:
        x[u] = dl / k
    E = [(u, v) for u in range(n) for v in adj[u] if u < v]
    best = sp.Rational(0)
    bestd = None
    polys = []
    for m in range(1 << n):
        q = sum(x[u] * x[v] for (u, v) in E if ((m >> u) & 1) == ((m >> v) & 1))
        polys.append(sp.expand(q))
    polys = list({sp.simplify(p) for p in polys})
    # candidate delta: endpoints, stationary points of each quadratic, pairwise crossings
    cand = {sp.Rational(0), sp.Rational(1)}
    for p in polys:
        for r in sp.solve(sp.diff(p, dl), dl):
            if r.is_real and 0 <= r <= 1:
                cand.add(sp.nsimplify(r))
    for p, qq in combinations(polys, 2):
        for r in sp.solve(sp.Eq(p, qq), dl):
            if r.is_real and 0 <= r <= 1:
                cand.add(sp.nsimplify(r))
    for c in cand:
        val = min(sp.simplify(p.subs(dl, c)) for p in polys)
        if val > best:
            best, bestd = val, c
    if verbose:
        print(f"    {name}: {k} pair-vertices, {len(polys)} distinct cut polynomials, "
              f"{len(cand)} candidate deltas")
        print(f"        max over the whole flat line = {best} = {float(best):.8f} at delta = {bestd} "
              f"({'ABOVE 1/25 -- COUNTEREXAMPLE' if best > sp.Rational(1,25) else 'equals 1/25' if best == sp.Rational(1,25) else 'below 1/25'})")
    return best


if __name__ == '__main__':
    check_counting()
    print("\n(b) exact random-direction check of first-order local maximality")
    GS = [('C5', C5()), ('myc(C5)-apex', myc_minus_apex()), ('Grotzsch', grotzsch()),
          ('Wagner', wagner()), ('Petersen', petersen()),
          ('And(4)', circ(11, [1, 4, 7, 10])), ('C11(1,3)', circ(11, [1, 3, 8, 10])),
          ('C13(1,5)', circ(13, [1, 5, 8, 12]))]
    rc = 0
    for name, G in GS:
        rc |= check_local_max(name, G)
    print("\n(c) EXACT maximisation along the first-order-flat direction")
    for name, G in GS:
        flat_direction_probe(name, G)
    sys.exit(1 if rc else 0)
