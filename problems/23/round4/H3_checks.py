"""H3: secondary structural checks on the Vega family."""
import sys, itertools
sys.path.insert(0, 'E:/Projects/ErdosProblems/problems/23/round4')
from H3_build import (gamma, upsilon, vega_family, adjmat, automorphisms, graph6,
                      canon_key, chrom, is_trianglefree, is_maximal_tf, is_twinfree)


def nauty_canon(A):
    """canonical graph6 via a cheap invariant-refined brute force over automorphism-style
    backtracking is too slow for n=12; use pynauty-free approach: exhaustive over the
    orbit of degree-preserving bijections."""
    return None


def iso(A, B):
    n = len(A)
    if n != len(B):
        return False
    if sorted(sum(r) for r in A) != sorted(sum(r) for r in B):
        return False
    p = [-1] * n
    used = [False] * n
    dA = [sum(r) for r in A]
    dB = [sum(r) for r in B]

    def bt(t):
        if t == n:
            return True
        for img in range(n):
            if used[img] or dB[img] != dA[t]:
                continue
            if all(A[t][s] == B[img][p[s]] for s in range(t)):
                p[t] = img; used[img] = True
                if bt(t + 1):
                    return True
                used[img] = False; p[t] = -1
        return False
    return bt(0)


def induced_c5_count(A):
    n = len(A)
    cnt = 0
    ex = None
    for S in itertools.combinations(range(n), 5):
        sub = [[A[p][q] for q in S] for p in S]
        deg = [sum(r) for r in sub]
        if deg != [2] * 5:
            continue
        # 5 vertices all deg 2 and connected => C5
        seen = {0}
        stack = [0]
        while stack:
            t = stack.pop()
            for r in range(5):
                if sub[t][r] and r not in seen:
                    seen.add(r); stack.append(r)
        if len(seen) == 5:
            cnt += 1
            if ex is None:
                ex = S
    return cnt, ex


def main():
    print('--- Gamma_i sanity ---')
    for i in range(1, 6):
        m, E = gamma(i)
        A = adjmat([str(j) for j in range(1, m + 1)], set(frozenset(str(t) for t in e) for e in E))
        print('Gamma_%d: n=%d m=%d regular-deg=%s tf=%s mtf=%s twf=%s chi=%s g6=%s' %
              (i, m, len(E), set(sum(r) for r in A), is_trianglefree(A)[0],
               is_maximal_tf(A)[0], is_twinfree(A)[0], chrom(A), graph6(A)))

    print()
    print('--- i=2 : the paper says Ups2-y and Ups2-2i are isomorphic ---')
    fam = {nm: (V, E) for nm, V, E in vega_family(2)}
    A1 = adjmat(*fam['Ups2-y'])
    A2 = adjmat(*fam['Ups2-2i'])
    print('isomorphic:', iso(A1, A2))

    print()
    print('--- Grotzsch check: Ups2-y-2i ---')
    V, E = fam['Ups2-y-2i']
    A = adjmat(V, E)
    print('labels', V)
    print('n=%d m=%d degseq=%s' % (len(V), len(E), sorted(sum(r) for r in A)))
    print('graph6', graph6(A))
    print('known Grotzsch graph6 (House of Graphs): KhCGGC@?G?_  -- compare by canon')

    print()
    print('--- automorphism group orders + induced C5 ---')
    for i in range(2, 5):
        for nm, V, E in vega_family(i):
            A = adjmat(V, E)
            if len(V) <= 17:
                g = automorphisms(A)
                c5, ex = induced_c5_count(A)
                print('%-12s n=%2d |Aut|=%4d  #inducedC5=%4d  example=%s' %
                      (nm, len(V), len(g), c5, None if ex is None else [V[t] for t in ex]))
            else:
                print('%-12s n=%2d  (skipped)' % (nm, len(V)))


if __name__ == '__main__':
    main()
