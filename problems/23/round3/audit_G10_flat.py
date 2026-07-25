"""audit_G10_flat.py -- independent test of G10-4 (flat face is C5-colourable) on
DELIBERATELY CONSTRUCTED flat directions, and of G10-2 (odd girth 5) on the whole
h<=14 maximal-triangle-free corpus.  Exact Fractions / integers only.
"""
import sys, random
from fractions import Fraction
sys.path.insert(0, '.')
from audit_G10_lib import adjlist, is_tf, hom_to_C5, cut_mono, psi_frac, odd_girth
from audit_G10_corpus import load_corpus

def solve5(M, b):
    """exact Gaussian elimination on a 5x5 Fraction system (own implementation)."""
    A = [row[:] + [b[i]] for i, row in enumerate(M)]
    n = 5
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [z / pv for z in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [A[r][k] - f * A[c][k] for k in range(n + 1)]
    return [A[i][n] for i in range(n)]

def rand_host_with_diagonals(n, rng):
    E = [(0,1),(1,2),(2,3),(3,4),(0,4)]
    A = adjlist(n, E)
    for w in range(5, n):
        j = rng.randrange(5)                       # attach w to the diagonal pair {j, j+2}
        for u in (j, (j+2) % 5):
            E.append((min(u,w), max(u,w))); A[u].add(w); A[w].add(u)
    P = [(i,j) for i in range(5, n) for j in range(i+1, n)]
    rng.shuffle(P)
    for i,j in P:
        if rng.random() < .5: continue
        if A[i] & A[j]: continue
        E.append((i,j)); A[i].add(j); A[j].add(i)
    return n, sorted(set(E))

def run(trials=400, seed=31337):
    rng = random.Random(seed)
    found = viol = rayviol = 0
    for t in range(trials):
        n = rng.randint(7, 11)
        n, E = rand_host_with_diagonals(n, rng)
        if not is_tf(n, E):    # random extra edges may create a triangle -> skip
            continue
        A = adjlist(n, E)
        cyc = (0,1,2,3,4)
        D = [Fraction(0)]*5
        d = [Fraction(0)]*n
        for w in range(5, n):
            Aw = sorted(u for u in range(5) if u in A[w])
            if len(Aw) != 2: continue
            j = [k for k in range(5) if {k,(k+2)%5} == set(Aw)][0]
            d[w] = Fraction(rng.randint(0,3))
            D[j] += d[w]
        if sum(D) == 0: continue
        M = [[Fraction(1) if k in (i,(i+1)%5) else Fraction(0) for k in range(5)] for i in range(5)]
        rhs = [-(D[i] + D[(i-1)%5]) for i in range(5)]
        dc = solve5(M, rhs)
        for i in range(5): d[cyc[i]] = dc[i]
        assert sum(d) == 0, sum(d)
        F = []
        for i in range(5):
            F.append(d[cyc[i]] + d[cyc[(i+1)%5]] + D[i] + D[(i-1)%5])
        if any(f != 0 for f in F): continue
        found += 1
        S = sorted(set(cyc) | {w for w in range(n) if d[w] > 0})
        idx = {v:i for i,v in enumerate(S)}
        Es = [(idx[u],idx[v]) for u,v in E if u in idx and v in idx]
        if not hom_to_C5(len(S), Es):
            viol += 1; print('G10-4 VIOLATION', n, E, d)
            continue
        mono = cut_mono(n, E)
        x0 = [Fraction(1,5)]*5 + [Fraction(0)]*(n-5)
        for num in range(0, 21):
            tt = Fraction(num, 100)
            z = [x0[v] + tt*d[v] for v in range(n)]
            if any(zz < 0 for zz in z): break
            if psi_frac(mono, z) > Fraction(1,25):
                rayviol += 1; print('RAY > 1/25', n, E, d, tt); break
    print('[G10-4] flat directions constructed=%d  face-not-C5-colourable=%d  ray-above-1/25=%d'
          % (found, viol, rayviol))

def oddgirth_corpus():
    G, order = load_corpus('G10_mtf_all.txt')
    from collections import Counter
    c = Counter()
    for nm in order:
        h, e = G[nm]
        c[odd_girth(h, e)] += 1
    print('[G10-2] odd girth over all 1944 maximal triangle-free h<=14 patterns:', dict(c))

if __name__ == '__main__':
    run()
    oddgirth_corpus()
