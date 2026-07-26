"""TASK 1 -- adversarial audit of Theorem D.

Theorem D (verbatim):  H triangle-free, C an induced C5, T_i the full twins,
R the rest outside C, rho = x(R), eta = x(V\\C).  Then
        psi(H,x) <= (1-rho)^2/25 + rho*eta .

Integer form used everywhere (x = a/q, all quantities integers):
        25 * M(a)  <=  (q-r)^2 + 25*r*e ,
   M(a) = min_S sum_mono a_u a_v,  r = sum_{v in R} a_v,  e = q - sum_{c in C} a_c.

Every test below is exact integer arithmetic.
"""
import sys, random, itertools
from fractions import Fraction as F
import numpy as np
import R9_thmD_lib as L

VIOL = []          # every violation found, ever
STATS = {'inst': 0, 'graphs': 0, 'c5': 0}


def check(G, C, a, tag):
    """exact Theorem D check for one (graph, pentagon, weight) instance."""
    q = sum(a)
    if q == 0:
        return True
    T, R, Rj, Rnone = L.classify(G, C)
    if Rj is None:
        VIOL.append(('CLASSIFY', tag, L.to_graph6(G), C, list(a)))
        return False
    r = sum(a[v] for v in R)
    e = q - sum(a[c] for c in C)
    M = L.psi_int(G, a)
    STATS['inst'] += 1
    lhs, rhs = 25 * M, (q - r) ** 2 + 25 * r * e
    if lhs > rhs:
        VIOL.append(('THMD', tag, L.to_graph6(G), C, list(a), lhs, rhs))
        return False
    return True


def compositions(n, q):
    """all integer vectors of length n, >=0, summing to q (zeros included)."""
    if n == 1:
        yield (q,)
        return
    for first in range(q + 1):
        for rest in compositions(n - 1, q - first):
            yield (first,) + rest


def sweep_exhaustive(name, G, q, limit=None):
    C5s = L.induced_C5s(G)
    STATS['graphs'] += 1
    STATS['c5'] += len(C5s)
    if not C5s:
        print("  %-18s n=%2d q=%2d : no induced C5 (theorem vacuous)" % (name, G[0], q))
        return
    cnt = 0
    bad = 0
    for a in compositions(G[0], q):
        for C in C5s:
            if not check(G, C, a, "%s q=%d" % (name, q)):
                bad += 1
        cnt += 1
        if limit and cnt >= limit:
            break
    print("  %-18s n=%2d q=%2d : %d weight vectors x %d pentagons = %d instances, %d violations"
          % (name, G[0], q, cnt, len(C5s), cnt * len(C5s), bad))


def sweep_random(name, G, q, trials, seed=0):
    rnd = random.Random(seed)
    C5s = L.induced_C5s(G)
    STATS['graphs'] += 1
    STATS['c5'] += len(C5s)
    if not C5s:
        print("  %-18s n=%2d q=%2d : no induced C5 (theorem vacuous)" % (name, G[0], q))
        return
    n = G[0]
    bad = 0
    for _ in range(trials):
        # random composition with many zeros allowed
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        for C in C5s:
            if not check(G, C, a, "%s rand q=%d" % (name, q)):
                bad += 1
    print("  %-18s n=%2d q=%2d : %d random weight vectors x %d pentagons, %d violations"
          % (name, G[0], q, trials, len(C5s), bad))


def ascent(name, G, q, starts, seed=0, steps=400):
    """hill-climb the exact violation  25M - (q-r)^2 - 25 r e  by unit transfers.
    Requirement: every induced C5 at weight q/5 is a start point."""
    rnd = random.Random(seed)
    C5s = L.induced_C5s(G)
    if not C5s:
        return
    n = G[0]

    def score(a, C, T, R):
        r = sum(a[v] for v in R)
        e = q - sum(a[c] for c in C)
        return 25 * L.psi_int(G, a) - (q - r) ** 2 - 25 * r * e

    best_overall = None
    inits = []
    if q % 5 == 0:
        for C in C5s:                       # MANDATORY C5-concentration starts
            a = [0] * n
            for c in C:
                a[c] = q // 5
            inits.append((a, C))
    for _ in range(starts):
        C = rnd.choice(C5s)
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        inits.append((a, C))
    for a0, C in inits:
        T, R, Rj, Rnone = L.classify(G, C)
        a = list(a0)
        cur = score(a, C, T, R)
        for _ in range(steps):
            bestmove, bestval = None, cur
            for u in range(n):
                if a[u] == 0:
                    continue
                for v in range(n):
                    if u == v:
                        continue
                    a[u] -= 1
                    a[v] += 1
                    s = score(a, C, T, R)
                    a[u] += 1
                    a[v] -= 1
                    if s > bestval:
                        bestval, bestmove = s, (u, v)
            if bestmove is None:
                break
            a[bestmove[0]] -= 1
            a[bestmove[1]] += 1
            cur = bestval
        if best_overall is None or cur > best_overall[0]:
            best_overall = (cur, list(a), C)
        if cur > 0:
            check(G, C, a, "%s ascent" % name)
    v, a, C = best_overall
    print("  %-18s q=%2d ascent over %d starts: max(25M-(q-r)^2-25re) = %d  %s  C=%s"
          % (name, q, len(inits), v, a, C))


# --------------------------------------------------------------- run --------
if __name__ == '__main__':
    N = L.named_graphs()
    print("=" * 78)
    print("A. EXHAUSTIVE integer sweeps (all compositions, zeros included), every pentagon")
    print("=" * 78)
    for name, q in [('C5', 20), ('C5', 21), ('C5', 13), ('C5[2,2,1,1,1]', 12),
                    ('C5[3,1,2,2,1]', 10), ('C5[3,1,0,2,1]', 10), ('C5+K1', 12),
                    ('K33', 12), ('C7', 12)]:
        sweep_exhaustive(name, N[name], q)

    print("=" * 78)
    print("B. EXHAUSTIVE at q=10 for the 10-11 vertex graphs")
    print("=" * 78)
    for name, q in [('Petersen', 10), ('C5[2]', 10), ('Wagner=And(3)', 12)]:
        sweep_exhaustive(name, N[name], q)

    print("=" * 78)
    print("C. RANDOM sweeps for the large graphs (many zeros)")
    print("=" * 78)
    for name, q, tr in [('Grotzsch', 15, 300), ('And(4)=G11', 15, 300),
                        ('And(5)=G14', 14, 120), ('MTF14', 14, 60),
                        ('C5[3,3,3,3,2]', 14, 120), ('C5+C5', 20, 200),
                        ('C5+C7', 24, 150), ('Petersen+K1', 11, 200)]:
        sweep_random(name, N[name], q, tr, seed=hash(name) % 1000)

    print("=" * 78)
    print("D. Exact hill-climbing on the violation (starts: every C5-concentration)")
    print("=" * 78)
    for name, q, st in [('C5', 25, 20), ('C5[2]', 20, 20), ('Petersen', 20, 20),
                        ('Wagner=And(3)', 25, 20), ('Grotzsch', 15, 10),
                        ('And(4)=G11', 15, 10), ('MTF14', 15, 6), ('And(5)=G14', 15, 6)]:
        ascent(name, N[name], q, st, seed=7)

    print("=" * 78)
    print("TOTAL exact instances checked: %d   graphs: %d   pentagons: %d"
          % (STATS['inst'], STATS['graphs'], STATS['c5']))
    print("VIOLATIONS: %d" % len(VIOL))
    for v in VIOL[:20]:
        print("   ", v)
