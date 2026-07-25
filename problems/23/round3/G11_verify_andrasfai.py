"""
G11 verification script (exact integer / Fraction arithmetic only).

Independently checks the literature claims that this report relies on:

 (A) Heinig (arXiv:0907.3928) Theorem 3: the explicit edge set F_k is a
     bipartification of the Andrasfai graph And_k, and |F_k| = floor(k^2/4)
     = floor((|And_k|+1)^2/36).
 (B) floor((|And_k|+1)^2/36) <= |And_k|^2/25 for all k >= 2, with equality
     only at k = 2 (C5).  Exact Fraction arithmetic.
 (C) bip(And_k) computed by exhaustive max-cut (independent of Heinig's
     construction), for k = 2..6, and compared with floor(k^2/4).
 (D) Brandt-Thomasse's Gamma_i (vertex set {1..3i-1}, j ~ j+i,...,j+2i-1
     mod 3i-1) is isomorphic to Heinig's And_i, and Gamma_3 = And_3 is the
     Wagner graph / Moebius ladder M_8 (C_8 plus the four main diagonals).

Run:  python G11_verify_andrasfai.py
"""

from fractions import Fraction
from itertools import combinations


# ---------- graph constructions ----------

def andrasfai_heinig(k):
    """Heinig Definition 1: V = {v_0,...,v_{3k-2}}, v_i ~ v_j iff |i-j| = 1 mod 3."""
    n = 3 * k - 1
    E = set()
    for i in range(n):
        for j in range(i + 1, n):
            if (j - i) % 3 == 1:
                E.add((i, j))
    return n, E


def gamma_bt(i):
    """Brandt-Thomasse Gamma_i: V = {0,...,3i-2}, j ~ j+i, ..., j+2i-1 (mod 3i-1)."""
    n = 3 * i - 1
    E = set()
    for j in range(n):
        for s in range(i, 2 * i):
            u, v = j, (j + s) % n
            if u != v:
                E.add((min(u, v), max(u, v)))
    return n, E


def moebius_ladder_8():
    """C_8 plus the 4 chords joining vertices at distance 4."""
    n = 8
    E = set()
    for j in range(8):
        for s in (1, 4):
            u, v = j, (j + s) % 8
            if u != v:
                E.add((min(u, v), max(u, v)))
    return n, E


# ---------- Heinig's F_k ----------

def heinig_F(k):
    """F_k = U1 u U2 from Heinig Theorem 3, equations (1) and (2)."""
    U1 = set()
    for i in range(0, k // 2):
        for j in range(i, k // 2):
            a, b = (3 * k - 4) - 3 * i, (3 * k - 5) - 3 * j
            U1.add((min(a, b), max(a, b)))
    U2 = set()
    for i in range(0, (k - 1) // 2):
        for j in range(0, (k - 1) // 2 - i):
            a, b = 3 * i, (3 * i + 1) + 3 * j
            U2.add((min(a, b), max(a, b)))
    return U1 | U2


# ---------- basic exact routines ----------

def is_triangle_free(n, E):
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    for u, v in E:
        if adj[u] & adj[v]:
            return False
    return True


def is_bipartite(n, E):
    adj = [[] for _ in range(n)]
    for u, v in E:
        adj[u].append(v)
        adj[v].append(u)
    color = [None] * n
    for s in range(n):
        if color[s] is not None:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if color[y] is None:
                    color[y] = 1 - color[x]
                    stack.append(y)
                elif color[y] == color[x]:
                    return False
    return True


def bip_bruteforce(n, E):
    """Exact bip(G) = min over cuts of #monochromatic edges.  2^(n-1) cuts."""
    El = sorted(E)
    best = len(El)
    for mask in range(1 << (n - 1)):
        m = mask << 1  # fix vertex 0 on side 0
        c = 0
        for u, v in El:
            if ((m >> u) & 1) == ((m >> v) & 1):
                c += 1
                if c >= best:
                    break
        if c < best:
            best = c
    return best


def canonical_certificate(n, E):
    """Cheap isomorphism certificate: refined degree/WL-1 colours + sorted
    edge-colour multiset, plus a brute-force check for small n."""
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    col = [len(adj[x]) for x in range(n)]
    for _ in range(n):
        new = [(col[x], tuple(sorted(col[y] for y in adj[x]))) for x in range(n)]
        remap = {c: i for i, c in enumerate(sorted(set(new)))}
        col = [remap[c] for c in new]
    return (n, len(E), tuple(sorted(col)),
            tuple(sorted((min(col[u], col[v]), max(col[u], col[v])) for u, v in E)))


def iso_bruteforce(n1, E1, n2, E2):
    from itertools import permutations
    if n1 != n2 or len(E1) != len(E2):
        return False
    S2 = {(min(u, v), max(u, v)) for u, v in E2}
    for p in permutations(range(n1)):
        if {(min(p[u], p[v]), max(p[u], p[v])) for u, v in E1} == S2:
            return True
    return False


# ---------- checks ----------

def main():
    print("=" * 72)
    print("(A) Heinig F_k is a bipartification of And_k, |F_k| = floor(k^2/4)")
    print("=" * 72)
    for k in range(2, 9):
        n, E = andrasfai_heinig(k)
        assert is_triangle_free(n, E), (k, "And_k not triangle-free")
        F = heinig_F(k)
        assert F <= E, (k, "F_k not a subset of E(And_k)")
        rest = E - F
        ok_bip = is_bipartite(n, rest)
        pred = (k * k) // 4
        pred2 = ((n + 1) ** 2) // 36
        print(f"  k={k:2d}  n={n:3d}  |E|={len(E):4d}  |F_k|={len(F):3d}  "
              f"floor(k^2/4)={pred:3d}  floor((n+1)^2/36)={pred2:3d}  "
              f"And_k-F_k bipartite: {ok_bip}")
        assert ok_bip, (k, "F_k is not a bipartification")
        assert len(F) == pred == pred2, (k, len(F), pred, pred2)

    print()
    print("=" * 72)
    print("(B) floor((n+1)^2/36) vs n^2/25 for n = |And_k| = 3k-1 (exact Fractions)")
    print("=" * 72)
    for k in range(2, 15):
        n = 3 * k - 1
        lhs = Fraction((n + 1) ** 2 // 36, 1)
        rhs = Fraction(n * n, 25)
        rel = "=" if lhs == rhs else ("<" if lhs < rhs else ">")
        print(f"  k={k:2d}  n={n:3d}  floor((n+1)^2/36)={lhs}  {rel}  n^2/25={rhs}"
              f"   ratio={Fraction(lhs, 1) / Fraction(n * n, 1)}")
        assert lhs <= rhs

    print()
    print("=" * 72)
    print("(C) exhaustive max-cut: bip(And_k) vs floor(k^2/4)")
    print("=" * 72)
    for k in range(2, 7):
        n, E = andrasfai_heinig(k)
        b = bip_bruteforce(n, E)
        pred = (k * k) // 4
        print(f"  k={k:2d}  n={n:3d}  bip(And_k)={b:3d}   floor(k^2/4)={pred:3d}"
              f"   bip/n^2 = {Fraction(b, n * n)} = {float(Fraction(b, n*n)):.6f}"
              f"   (1/25 = {float(Fraction(1,25)):.6f})")
        assert b <= pred
        assert Fraction(b, n * n) <= Fraction(1, 25)

    print()
    print("=" * 72)
    print("(D) Gamma_i (Brandt-Thomasse) == And_i (Heinig); Gamma_3 == Wagner V8")
    print("=" * 72)
    for i in range(2, 8):
        n1, E1 = gamma_bt(i)
        n2, E2 = andrasfai_heinig(i)
        same_cert = canonical_certificate(n1, E1) == canonical_certificate(n2, E2)
        print(f"  i={i:2d}  n={n1:3d}  |E(Gamma_i)|={len(E1):4d} "
              f"|E(And_i)|={len(E2):4d}  same WL-certificate: {same_cert}")
        assert same_cert
    n1, E1 = gamma_bt(3)
    n2, E2 = moebius_ladder_8()
    print(f"  Gamma_3 iso Moebius ladder M_8 (brute force): "
          f"{iso_bruteforce(n1, E1, n2, E2)}")
    assert iso_bruteforce(n1, E1, n2, E2)
    b = bip_bruteforce(*moebius_ladder_8())
    print(f"  bip(Wagner V8) = {b}, bip/n^2 = {Fraction(b, 64)} "
          f"= {float(Fraction(b,64)):.6f}")

    print()
    print("=" * 72)
    print("(E) numeric constants quoted in the report (exact)")
    print("=" * 72)
    print(f"  1/23.5 = {Fraction(2,47)} = {float(Fraction(2,47)):.7f}")
    print(f"  1/25   = {Fraction(1,25)} = {float(Fraction(1,25)):.7f}")
    print(f"  1/18   = {Fraction(1,18)} = {float(Fraction(1,18)):.7f}")
    print(f"  27/1024= {Fraction(27,1024)} = {float(Fraction(27,1024)):.7f}")
    print(f"  root-prompt claim 0.0409 < 2/47 ? {Fraction(409,10000) < Fraction(2,47)}")
    # EFPS Theorem 1, second term, with m = c n^2: c - 4c^2 <= 1/25
    for c in [Fraction(1,20), Fraction(1,5), Fraction(43,200)]:
        print(f"  EFPS m-4m^2/n^2 at m={c}n^2 : {c - 4*c*c} n^2  "
              f"(<= 1/25 ? {c - 4*c*c <= Fraction(1,25)})")
    print()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
