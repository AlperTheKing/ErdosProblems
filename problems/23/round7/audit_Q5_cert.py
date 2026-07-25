"""A7/A9: verify, by hand-checkable direct code, EVERY explicit minor certificate
printed in Q5.md.

An odd-K5 minor of the ALL-NEGATIVE signed graph (G,E) is certified by
  * disjoint vertex sets B1..B5,
  * a switching set P (the "p-mask"): the sign of uv after switching is
        +  iff exactly one of u,v is in P        (so uv can be contracted)
        -  iff  [u in P] == [v in P]             (so uv can be a K5 edge)
  * each G[Bi] restricted to the POSITIVE edges must be connected (contractible
    to a single vertex by contracting a positive spanning tree),
  * every pair (i,j) must carry at least one NEGATIVE edge between Bi and Bj.
Then contracting gives K5 with all 10 edges negative = odd-K5.
This is written from the definition, not from the target's code.
"""
from fractions import Fraction as F
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q5_lib import g6, E_of, andrasfai, C5n, V8, NAMED_G6, induced, circulant

FAIL = []


def rep(name, ok, detail=""):
    if not ok:
        FAIL.append(name)
    print(f"  {'OK  ' if ok else 'FAIL'} {name} {detail}")


def connected_in(n, A, S, allowed):
    """S connected using only edges in `allowed` (a predicate on (u,v))."""
    S = set(S)
    if not S:
        return False
    start = next(iter(S))
    seen = {start}
    st = [start]
    while st:
        u = st.pop()
        for v in S:
            if v in seen or not (A[u] >> v) & 1:
                continue
            if allowed(u, v):
                seen.add(v)
                st.append(v)
    return seen == S


def check_oddK5(name, n, A, Bs, pmask):
    """Flipping a WHOLE branch set is again a switching that keeps every branch set
    positively connected, so the certificate is only required to work for SOME of
    the 2^5 branch-set flips of the printed p-mask (equivalently: some choice of
    links makes all 10 triangles of the contracted K5 odd)."""
    okdisj = all(not (set(Bs[i]) & set(Bs[j])) for i in range(5) for j in range(i + 1, 5))
    P0 = {v for v in range(n) if (pmask >> v) & 1}
    pos0 = lambda u, v: ((u in P0) != (v in P0))
    okconn = all(connected_in(n, A, B, pos0) for B in Bs)
    best = None
    for flip in range(32):
        P = set(P0)
        for i in range(5):
            if (flip >> i) & 1:
                P ^= set(Bs[i])
        pos = lambda u, v: ((u in P) != (v in P))
        if not all(connected_in(n, A, B, pos) for B in Bs):
            continue
        links, oklink = {}, True
        for i in range(5):
            for j in range(i + 1, 5):
                found = None
                for u in Bs[i]:
                    for v in Bs[j]:
                        if (A[u] >> v) & 1 and ((u in P) == (v in P)):
                            found = (u, v)
                links[(i, j)] = found
                if found is None:
                    oklink = False
        if oklink:
            best = (flip, sorted(P), links)
            break
    rep(f"{name}: branch sets disjoint", okdisj)
    rep(f"{name}: each Bi connected in the POSITIVE subgraph (printed p-mask)", okconn)
    rep(f"{name}: SOME branch-flip makes all 10 links NEGATIVE -> odd-K5", best is not None,
        "" if best is None else f"flip={best[0]} P={best[1]}\n        links={best[2]}")
    return okdisj and okconn and best is not None


def check_K5(name, n, A, Bs):
    okdisj = all(not (set(Bs[i]) & set(Bs[j])) for i in range(5) for j in range(i + 1, 5))
    okconn = all(connected_in(n, A, B, lambda u, v: True) for B in Bs)
    oklink = all(any((A[u] >> v) & 1 for u in Bs[i] for v in Bs[j])
                 for i in range(5) for j in range(i + 1, 5))
    rep(f"{name}: K5 minor certificate (disjoint/connected/pairwise adjacent)",
        okdisj and okconn and oklink, f"({okdisj},{okconn},{oklink})")
    return okdisj and okconn and oklink


print("=== A9  And(4) = Gamma_11 odd-K5 certificate from Q5.md sec 4.3 ===")
n, A = andrasfai(4)
print(f"   And(4): N={n} |E|={len(E_of(n,A))}")
check_oddK5("And(4)", n, A, [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3], [7]], 112)

print("=== A9  And(5) = Gamma_14 odd-K5 certificate ===")
n, A = andrasfai(5)
print(f"   And(5): N={n} |E|={len(E_of(n,A))}")
check_oddK5("And(5)", n, A, [[0, 4, 5, 9, 10, 13], [1, 6, 11], [2, 7, 12], [3], [8]], 209)

print("=== A7  N=14 extremal odd-K5 certificate ===")
n, A = g6(NAMED_G6["N14"])
check_oddK5("N14", n, A, [[0, 5, 10, 13], [1, 3, 6, 9, 12], [2, 11], [4, 8], [7]], 628)

print("=== F4  C5[2] K5-minor certificate ===")
n, A = C5n(2)
# Q5.md prints parts {0,1},{2,3},{4,5},{6,7},{8,9} around the 5-cycle -> that is
# exactly the audit library's C5n(2) labelling (part p = {2p, 2p+1}).
check_K5("C5[2]", n, A, [[0, 3, 9], [1, 2, 5], [4, 7], [6], [8]])

print("=== A4  the Wagner configuration support induces V8 = And(3) ===")
n, A = andrasfai(5)                      # Gamma_14
S = [0, 1, 2, 5, 6, 7, 10, 11]
m, B = induced(n, A, S)
deg = [bin(B[i]).count('1') for i in range(m)]
rep("support is 8 vertices, cubic, 12 edges",
    m == 8 and deg == [3] * 8 and len(E_of(m, B)) == 12, f"deg={deg}")
# explicit isomorphism to C8(1,4): find one by brute force over all 8! maps
from itertools import permutations
n8, A8 = circulant(8, [1, 4])
iso = None
for p in permutations(range(8)):
    good = True
    for i in range(8):
        for j in range(i + 1, 8):
            if bool((B[i] >> j) & 1) != bool((A8[p[i]] >> p[j]) & 1):
                good = False
                break
        if not good:
            break
    if good:
        iso = p
        break
rep("induced subgraph ~= C8(1,4) = Wagner graph V8", iso is not None, f"iso={iso}")
# also check And(3) itself is C8(1,4)
n3, A3 = andrasfai(3)
iso3 = None
for p in permutations(range(8)):
    if all(bool((A3[i] >> j) & 1) == bool((A8[p[i]] >> p[j]) & 1)
           for i in range(8) for j in range(i + 1, 8)):
        iso3 = p
        break
rep("And(3) = Gamma_8 ~= C8(1,4)", iso3 is not None, f"iso={iso3}")

print("=== A5  V8 has no K5 minor: the counting proof, checked ===")
n8, A8 = circulant(8, [1, 4])
degs = [bin(A8[i]).count('1') for i in range(8)]
rep("V8 is cubic on 8 vertices", degs == [3] * 8)
print("      counting argument: a K5-minor branch set must send >= 4 edges out;")
print("      a single vertex of a cubic graph sends 3, so every branch set has >= 2")
print("      vertices, so >= 10 vertices are needed, but N=8.  (Wagner's theorem also")
print("      lists V8 as THE sporadic K5-minor-free graph.)")

print("\nFAILURES:", len(FAIL), FAIL)
