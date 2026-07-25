"""AUDIT of the independence/novelty claims: which of the certified patterns follow for free
from a homomorphism into an already-certified pattern.

FACT (proved inline, 3 lines): if phi: H -> K is a graph homomorphism then for every x >= 0,
psi(H,x) <= psi(K, phi_* x), where (phi_* x)_a = sum_{u in phi^{-1}(a)} x_u.  Indeed a cut S of K
pulls back to the cut phi^{-1}(S) of H, and the H-edges monochromatic for it map into K-edges
monochromatic for S, so q_{phi^{-1}(S)}(x) <= q_S(phi_* x).  Hence max psi(H) <= max psi(K).

So: a psi-ceiling for K is inherited by every H that maps to K.  This script tests all the
homomorphisms that would make one of the two Q4 'PROVED' items a corollary of the other, or of C5.
"""
from fractions import Fraction as F
from itertools import combinations


def gamma_graph(n):
    third = F(1, 3)
    return [[(i != j and min(F((i - j) % n, n), F((j - i) % n, n)) > third) for j in range(n)]
            for i in range(n)]


def petersen():
    V = sorted(combinations(range(5), 2))
    return [[(i != j and not (set(V[i]) & set(V[j]))) for j in range(len(V))] for i in range(len(V))]


def cycle(n):
    return [[(i != j and ((i - j) % n in (1, n - 1))) for j in range(n)] for i in range(n)]


def hom(H, K):
    """exhaustive backtracking: does a homomorphism H -> K exist?  returns the map or None."""
    nH, nK = len(H), len(K)
    col = [-1] * nH

    def rec(v):
        if v == nH:
            return True
        for k in range(nK):
            ok = True
            for u in range(v):
                if H[v][u] and not K[k][col[u]]:
                    ok = False
                    break
            if ok:
                col[v] = k
                if rec(v + 1):
                    return True
                col[v] = -1
        return False
    return col[:] if rec(0) else None


def aut_order(A):
    n = len(A)
    cnt = 0
    perm = [-1] * n
    used = [False] * n

    def rec(v):
        nonlocal cnt
        if v == n:
            cnt += 1
            return
        for k in range(n):
            if used[k]:
                continue
            if all(A[v][u] == A[k][perm[u]] for u in range(v)):
                perm[v] = k
                used[k] = True
                rec(v + 1)
                used[k] = False
                perm[v] = -1
    rec(0)
    return cnt


NAMES = {"C5": cycle(5), "Gamma_8": gamma_graph(8), "Petersen": petersen(),
         "Gamma_11": gamma_graph(11), "Gamma_14": gamma_graph(14)}

print("homomorphism table (row -> column exists?)  --  a YES makes the row's ceiling a corollary")
keys = list(NAMES)
print("            " + "".join(f"{k:>10s}" for k in keys))
for a in keys:
    row = ""
    for b in keys:
        row += f"{('YES' if hom(NAMES[a], NAMES[b]) is not None else '.'):>10s}"
    print(f"{a:>12s}" + row)

print()
for k in ("Gamma_8", "Petersen", "Gamma_11"):
    print(f"|Aut({k})| = {aut_order(NAMES[k])}")
