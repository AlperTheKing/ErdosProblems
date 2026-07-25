"""audit_Q3_invariants.py -- independent check of the structural claims about the
worst perfect-stability witness and of the k=2 family variant.
"""
from itertools import combinations, permutations
from fractions import Fraction as F
from audit_Q3_named import g6enc, g6dec, circulant, c5blowup

def indep_number(n, E):
    adj = [0]*n
    for u, v in E:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    best = 0
    # brute force over subsets via recursion
    def rec(v, chosen, allowed):
        nonlocal best
        if bin(chosen).count('1') + bin(allowed).count('1') <= best:
            return
        if allowed == 0:
            best = max(best, bin(chosen).count('1'))
            return
        u = (allowed & -allowed).bit_length() - 1
        rec(u, chosen | (1 << u), allowed & ~(1 << u) & ~adj[u])   # take u
        rec(u, chosen, allowed & ~(1 << u))                        # skip u
    rec(-1, 0, (1 << n) - 1)
    return best

def count_c5(n, E):
    adj = [[False]*n for _ in range(n)]
    for u, v in E:
        adj[u][v] = adj[v][u] = True
    cnt = 0
    for S in combinations(range(n), 5):
        for p in permutations(S[1:]):
            cyc = (S[0],) + p
            if cyc[1] > cyc[-1]:
                continue
            ok = all(adj[cyc[i]][cyc[(i+1) % 5]] for i in range(5))
            if ok:
                cnt += 1
    return cnt

def deg_seq(n, E):
    d = [0]*n
    for u, v in E:
        d[u] += 1; d[v] += 1
    return sorted(d)

n, E = circulant(13, [1, 5])
print("C13(1,5): n=%d |E|=%d degrees=%s alpha=%d pentagons=%d" %
      (n, len(E), set(deg_seq(n, E)), indep_number(n, E), count_c5(n, E)))
n2, E2 = g6dec('L?`DE`gl@YJODg')
print("report witness L?`DE`gl@YJODg: n=%d |E|=%d degrees=%s alpha=%d pentagons=%d" %
      (n2, len(E2), set(deg_seq(n2, E2)), indep_number(n2, E2), count_c5(n2, E2)))

# --- the k=2 j=2 member of the "worst direction" family, both matching choices
def c5_2_minus(cross):
    """C5[2] minus a perfect matching in every consecutive pair.
    cross=False: delete a_i-a_{i+1}, b_i-b_{i+1} (leaves the 'crossed' matching)
    cross=True : delete a_i-b_{i+1}, b_i-a_{i+1} (leaves two disjoint pentagons)"""
    def A(i): return 2*i
    def B(i): return 2*i+1
    E = set()
    for i in range(5):
        j = (i+1) % 5
        for x in (A(i), B(i)):
            for y in (A(j), B(j)):
                E.add((min(x, y), max(x, y)))
    for i in range(5):
        j = (i+1) % 5
        if cross:
            rem = [(A(i), B(j)), (B(i), A(j))]
        else:
            rem = [(A(i), A(j)), (B(i), B(j))]
        for (x, y) in rem:
            E.discard((min(x, y), max(x, y)))
    return 10, sorted(E)

for cross in (False, True):
    n3, E3 = c5_2_minus(cross)
    print("C5[2] minus perfect matchings, cross=%s : g6 %s  |E|=%d" % (cross, g6enc(n3, E3), len(E3)))
