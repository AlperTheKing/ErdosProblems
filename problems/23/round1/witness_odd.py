"""Non-bipartite / C5-containing versions of the obstruction witness.

W2(L,b): the odd cycle C_L blown up as  [b, b+1, 1,1,...,1, b+1, b]  with the
alternating colouring, so that exactly one pair of consecutive parts (P_{L-1},P_0)
is monochromatic.  Connected, non-bipartite, odd girth L.

W3 = W2(L,b)  disjoint-union  C5[m]:  odd girth 5, contains C5's; sigma is additive
over connected components, so every switching inequality for W3 is the sum of one
for each component -- all verifications transfer.
"""
import sys
from itertools import product
sys.path.insert(0, __file__.replace('\\', '/').rsplit('/', 1)[0])
from witness_verify import Pattern


def CL(L, b, d=1, plus=1):
    a = b + plus
    sizes = [b] + [a] + [d] * (L - 4) + [a, b]
    assert len(sizes) == L
    col = [i % 2 for i in range(L)]          # edge (L-1,0) is the monochromatic one
    edges = [(i, i + 1) for i in range(L - 1)] + [(0, L - 1)]
    return Pattern(L, edges, col, sizes, name=f"W2(L={L},b={b}) = C{L}{sizes}")


def C5m(m):
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
    col = [0, 1, 0, 1, 1]                    # unique monochromatic pair = (3,4)
    return Pattern(5, edges, col, [m] * 5, name=f"C5[{m}] (its blow-up cut IS maximum)")


def bounded_scan(P, K):
    """min sigma over profiles with sum s_i <= K (exact, DFS with pruning on the size)."""
    h, n = P.h, P.n
    best = (10 ** 9, None)

    def rec(i, s, rem):
        nonlocal best
        if i == h:
            v = P.sigma(s)
            if v < best[0]:
                best = (v, tuple(s))
            return
        for t in range(0, min(n[i], rem) + 1):
            s[i] = t
            rec(i + 1, s, rem - t)
        s[i] = 0
    rec(0, [0] * h, K)
    return best


if __name__ == "__main__":
    print("=" * 100)
    print("W2: connected, non-bipartite witnesses (odd girth L)")
    print("=" * 100)
    for (L, b) in [(9, 8), (9, 12), (11, 10), (11, 14)]:
        CL(L, b).report()
        print()

    print("=" * 100)
    print("W3 = W2(9,b)  u  C5[m]   (disjoint union: sigma is additive over components)")
    print("=" * 100)
    for (b, m) in [(12, 1), (15, 1), (20, 2)]:
        A = CL(9, b)
        Bc = C5m(m)
        N = A.N + Bc.N
        M = A.M + Bc.M
        print(f"W3(b={b},m={m}): N = {A.N}+{Bc.N} = {N}   |M| = {A.M}+{Bc.M} = {M}   "
              f"25*|M| = {25*M}  vs  N^2 = {N*N}   -> {'BEATS N^2/25' if 25*M > N*N else 'NO'}")
        negA, minA, tA = A.scan()
        negB, minB, tB = Bc.scan()
        print(f"   component C9-gadget : smallest improving set |S| = {negA[0]} (profile {negA[1]}, sigma={negA[2]})")
        print(f"   component C5[{m}]      : improving set = {negB}  (None means the cut is maximum there)")
        print(f"   => by additivity, sigma(S) >= 0 for every S with |S| <= {negA[0]-1} = {(negA[0]-1)/N:.4f}*N")
        print(f"   odd girth 5 (contains C5), non-bipartite, triangle-free")
        print()
