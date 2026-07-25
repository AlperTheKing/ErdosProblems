"""audit_Q3_family.py -- independent check of the pass-2 "worst direction" family:
   C5[k] minus a j-matching in each consecutive class pair  ==>  claim bip = k^2 - j,
   dist = 5j, R = 5 exactly (Q3.md P2.2 table, last row; "verified k=2,3,4, all j").
Emits g6 for my own engine to evaluate.
"""
import sys
from audit_Q3_named import g6enc

def fam(k, j):
    n = 5 * k
    def V(i, a):
        return i * k + a
    E = set()
    for i in range(5):
        for a in range(k):
            for b in range(k):
                E.add((min(V(i, a), V((i + 1) % 5, b)), max(V(i, a), V((i + 1) % 5, b))))
    # delete a j-matching between class i and class i+1: pairs (i,a)-(i+1,a), a < j
    for i in range(5):
        for a in range(j):
            e = (min(V(i, a), V((i + 1) % 5, a)), max(V(i, a), V((i + 1) % 5, a)))
            E.discard(e)
    return n, sorted(E)

if __name__ == '__main__':
    for k in (2, 3, 4):
        for j in range(1, k + 1):
            n, E = fam(k, j)
            print("%s\tC5[%d]-%dmatch\tk=%d\tj=%d\tpredict_bip=%d\tpredict_dist=%d" %
                  (g6enc(n, E), k, j, k, j, k * k - j, 5 * j))
