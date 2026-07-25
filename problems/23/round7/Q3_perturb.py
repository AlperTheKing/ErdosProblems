"""Q3 round 7 -- near-extremal probe.

Generates every triangle-free graph obtained from a balanced C5 blow-up by toggling at most k
vertex pairs (adding or deleting edges), i.e. the whole edit-distance-<= k shell around the
conjectured extremal configuration.  These are exactly the graphs a stability statement has to
control: they sit at small edit distance from the extremal family and have to lose a definite
amount of bip.

Writes graph6 lines; the exact values bip and d come from Q3_engine.exe.

usage: python Q3_perturb.py <parts, e.g. 2,2,2,2,2> <k> <outfile>
"""
import sys
from itertools import combinations
from Q3_named import g6, is_tf


def blowup_edges(parts):
    idx, c = [], 0
    for p in parts:
        idx.append(list(range(c, c + p)))
        c += p
    E = set()
    for i in range(5):
        for a in idx[i]:
            for b in idx[(i + 1) % 5]:
                E.add((min(a, b), max(a, b)))
    return c, E


def main():
    parts = [int(t) for t in sys.argv[1].split(',')]
    k = int(sys.argv[2])
    out = sys.argv[3]
    n, E = blowup_edges(parts)
    allpairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    adj = [[False] * n for _ in range(n)]
    for (u, v) in E:
        adj[u][v] = adj[v][u] = True

    def tf(A):
        for u in range(n):
            for v in range(u + 1, n):
                if A[u][v]:
                    for w in range(n):
                        if w != u and w != v and A[u][w] and A[v][w]:
                            return False
        return True

    seen = set()
    res = []
    for t in range(0, k + 1):
        for T in combinations(allpairs, t):
            A = [row[:] for row in adj]
            for (u, v) in T:
                A[u][v] = A[v][u] = not A[u][v]
            if not tf(A):
                continue
            EE = [(u, v) for (u, v) in allpairs if A[u][v]]
            s = g6(n, EE)
            if s in seen:
                continue
            seen.add(s)
            res.append(s)
    with open(out, 'w') as f:
        for s in res:
            f.write(s + '\n')
    print('%s parts=%s k=%d n=%d graphs=%d' % (out, parts, k, n, len(res)))


if __name__ == '__main__':
    main()
