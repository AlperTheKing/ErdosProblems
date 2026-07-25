"""AUDIT addendum: (a) is And(k) an INDUCED subgraph of And(k+1)?  (this would make
the section 6.3 block propagate from And(4) to every k >= 4);
(b) arc-cut claim of section 4 tested at STRUCTURED points (all induced subgraphs
with uniform weights: min over all cuts = bip(H[S]) vs min over cyclic-interval cuts;
and C5-blow-up points of And(3) with all integer class splittings).
Integer arithmetic only (scale invariance makes Fractions unnecessary here).
"""
import sys, itertools
from audit_G8_core import and_circulant, edges_of


def induced_iso(nA, adjA, nB, adjB):
    degA = sorted(bin(m).count("1") for m in adjA)
    for S in itertools.combinations(range(nB), nA):
        M = [0] * nA
        for i, v in enumerate(S):
            for j, u in enumerate(S):
                if (adjB[v] >> u) & 1:
                    M[i] |= 1 << j
        if sorted(bin(m).count("1") for m in M) != degA:
            continue
        perm = [-1] * nA
        used = [False] * nA

        def rec(i):
            if i == nA:
                return True
            for c in range(nA):
                if used[c]:
                    continue
                ok = True
                for j in range(i):
                    if ((adjA[i] >> j) & 1) != ((M[c] >> perm[j]) & 1):
                        ok = False
                        break
                if ok:
                    perm[i] = c
                    used[c] = True
                    if rec(i + 1):
                        return True
                    used[c] = False
                    perm[i] = -1
            return False

        if rec(0):
            return S
    return None


def kpk(k):
    p = 3 * k - 1
    return p, [(i, j) for i in range(p) for j in range(i + 1, p) if k <= (j - i) % p <= p - k]


def sides_all(p):
    return [[0] + [(mask >> (v - 1)) & 1 for v in range(1, p)] for mask in range(1 << (p - 1))]


def sides_arc(p):
    out = set()
    for i in range(p):
        for m in range(1, p):
            side = [0] * p
            for t in range(m):
                side[(i + t) % p] = 1
            if side[0] == 1:
                side = [1 - s for s in side]
            out.add(tuple(side))
    return [list(s) for s in out]


def minval(E, sides, x):
    best = None
    for side in sides:
        s = 0
        for (u, v) in E:
            if side[u] == side[v]:
                s += x[u] * x[v]
        if best is None or s < best:
            best = s
    return best


if __name__ == "__main__":
    print("(a) And(k) induced in And(k+1)?  (propagates the 6.3 block upward)")
    for k in (3, 4, 5, 6):
        nA, adjA = and_circulant(k)
        nB, adjB = and_circulant(k + 1)
        S = induced_iso(nA, adjA, nB, adjB)
        print(f"   And({k}) (n={nA}) induced in And({k+1}) (n={nB}): "
              f"{'YES at ' + str(S) if S else 'NO'}", flush=True)
    print()

    print("(b) arc-cut optimality, structured points, integer weights")
    for k in (2, 3, 4, 5):
        p, E = kpk(k)
        SA = sides_all(p)
        SR = sides_arc(p)
        bad = 0
        tested = 0
        # every induced subgraph, uniform weight 1
        for r in range(2, p + 1):
            for S in itertools.combinations(range(p), r):
                x = [0] * p
                for v in S:
                    x[v] = 1
                a = minval(E, SA, x)
                b = minval(E, SR, x)
                tested += 1
                if a != b:
                    bad += 1
                    if bad <= 3:
                        print(f"   K_{{{p}/{k}}} ARC GAP at uniform support {S}: all={a} arc={b}")
        print(f"   K_{{{p}/{k}}}: {tested} uniform-support points, arc-cut failures = {bad}",
              flush=True)
    print()

    # C5-blow-up points of And(3) with all integer class splittings summing to 5 per class
    p, E = kpk(3)
    SA = sides_all(p)
    SR = sides_arc(p)
    # induced C5s of K_{8/3}
    c5s = []
    for S in itertools.combinations(range(p), 5):
        Ss = set(S)
        sub = [(u, v) for (u, v) in E if u in Ss and v in Ss]
        if len(sub) != 5:
            continue
        deg = {v: 0 for v in S}
        for (u, v) in sub:
            deg[u] += 1
            deg[v] += 1
        if all(d == 2 for d in deg.values()):
            c5s.append(S)
    bad = 0
    tested = 0
    for S in c5s:
        for x0 in itertools.product(range(6), repeat=5):
            x = [0] * p
            for v, t in zip(S, x0):
                x[v] = t
            if sum(x) == 0:
                continue
            a = minval(E, SA, x)
            b = minval(E, SR, x)
            tested += 1
            if a != b:
                bad += 1
                if bad <= 3:
                    print(f"   K_{{8/3}} ARC GAP at C5-support {S} weights {x0}: all={a} arc={b}")
    print(f"   K_{{8/3}}: {tested} C5-support integer points, arc-cut failures = {bad}")
