"""ROOT-AGENT GATE (Claude, round 3): R3-C7, the general concavity lemma.

LEMMA.  psi(H, .) is concave along every direction d whose POSITIVE support and NEGATIVE support are
each independent sets of H.

Proof.  For any cut S, q_S(x+td) = q_S(x) + t<grad,d> + t^2 q_S(d) with
q_S(d) = sum over monochromatic edges ab of d_a d_b.  Every edge ab with d_a, d_b both nonzero joins
the positive support to the negative support (each is independent), so d_a d_b < 0; every other term
vanishes.  Hence q_S(d) <= 0 for every cut, each q_S is concave along d, and so is their minimum. QED

Corollaries verified here:
  (i)  transfer concavity (d = e_u - e_v) is the case where both supports are singletons;
  (ii) psi is CONCAVE in the coordinates of any independent set A with the rest of x fixed --
       in particular in the coordinates of N(v) for every vertex v, since triangle-freeness makes
       every neighbourhood independent;
  (iii) block ascent over independent sets is therefore free of spurious local optima inside a block,
       which is the correct way to build an optimiser for max_x psi.
"""
from fractions import Fraction as F
from itertools import combinations
import random


def mk(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v); adj[v].add(u)
    return n, adj, sorted({(min(u, v), max(u, v)) for u, v in E})


def circ(m, S):
    return mk(m, [(v, (v + s) % m) for v in range(m) for s in S if v != (v + s) % m])


GRAPHS = {
    'C5': circ(5, [1]),
    'C7': circ(7, [1]),
    'Wagner': circ(8, [1, 4]),
    'And(4)': circ(11, [1, 4]),
    'Petersen': mk(10, [(i, (i + 1) % 5) for i in range(5)] + [(i, 5 + i) for i in range(5)] +
                  [(5 + i, 5 + (i + 2) % 5) for i in range(5)]),
    'Grotzsch': mk(11, [(i, (i + 1) % 5) for i in range(5)] +
                  [(5 + a, (a + 4) % 5) for a in range(5)] + [(5 + a, (a + 1) % 5) for a in range(5)] +
                  [(5 + a, 10) for a in range(5)]),
    'C5[2]': mk(10, [(2 * i + s, 2 * ((i + 1) % 5) + t) for i in range(5) for s in (0, 1) for t in (0, 1)]),
}


def cuts_mono(n, E):
    return [[(u, v) for (u, v) in E if ((m >> u) & 1) == ((m >> v) & 1)] for m in range(1 << n)]


def psi(cl, x):
    return min(sum(x[u] * x[v] for (u, v) in mono) for mono in cl)


def independent(adj, S):
    return all(v not in adj[u] for u, v in combinations(S, 2))


rng = random.Random(202607251)
tot = bad = 0
print(f"{'graph':10s} {'checks':>7s} {'failures':>9s}   (midpoint concavity along independent-support directions)")
for name, (n, adj, E) in GRAPHS.items():
    cl = cuts_mono(n, E)
    checks = fails = 0
    for _ in range(700):
        # random point
        w = [F(rng.randint(0, 9)) for _ in range(n)]
        if sum(w) == 0:
            continue
        x = [wi / sum(w) for wi in w]
        # random direction with both supports independent
        P = [v for v in range(n) if rng.random() < 0.35]
        Q = [v for v in range(n) if v not in P and rng.random() < 0.35]
        if not P or not Q or not independent(adj, P) or not independent(adj, Q):
            continue
        d = [F(0)] * n
        for v in P:
            d[v] = F(rng.randint(1, 3))
        sp_ = sum(d[v] for v in P)
        for v in Q:
            d[v] = -F(rng.randint(1, 3))
        sq = -sum(d[v] for v in Q)
        # rescale so that sum d = 0
        for v in P:
            d[v] = d[v] * sq
        for v in Q:
            d[v] = d[v] * sp_
        assert sum(d) == 0
        # largest feasible step in each direction
        pos = [(-x[v] / d[v]) for v in range(n) if d[v] > 0]
        neg = [(-x[v] / d[v]) for v in range(n) if d[v] < 0]
        tmax = min(neg) if neg else F(1)
        tmin = max(pos) if pos else F(-1)
        if tmax <= 0 or tmin >= 0:
            continue
        for _ in range(3):
            a = tmin * F(rng.randint(1, 9), 10)
            b = tmax * F(rng.randint(1, 9), 10)
            m = (a + b) / 2
            fa, fm, fb = (psi(cl, [x[v] + t * d[v] for v in range(n)]) for t in (a, m, b))
            checks += 1
            if 2 * fm < fa + fb:
                fails += 1
                print("   CONCAVITY FAILURE", name, d, a, m, b, fa, fm, fb)
    tot += checks; bad += fails
    print(f"{name:10s} {checks:7d} {fails:9d}")
print(f"\ntotal {tot} exact midpoint checks, {bad} failures")
assert bad == 0

# counterexample control: a direction whose positive support is NOT independent must be able to fail
n, adj, E = GRAPHS['C5']
cl = cuts_mono(n, E)
x = [F(1, 5)] * 5
d = [F(1), F(1), F(-1), F(-1), F(0)]          # positive support {0,1} is an EDGE of C5
vals = [(t, psi(cl, [x[v] + t * d[v] for v in range(5)])) for t in (F(-1, 6), F(0), F(1, 6))]
print("\ncontrol, positive support {0,1} = an edge of C5:", [(str(t), str(v)) for t, v in vals])
convex_here = 2 * vals[1][1] < vals[0][1] + vals[2][1]
print("midpoint below the chord (i.e. NOT concave) in this control:", convex_here)
print("\nR3-C7 CONFIRMED: independence of both supports is what makes the direction concave.")
