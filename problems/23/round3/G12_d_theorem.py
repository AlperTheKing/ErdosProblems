"""G12 task (d): the unconditional covering theorem, an INDEPENDENT second
implementation, and the exact algebra of the density band it closes.

THEOREM G12-C.  Let G be triangle-free on N vertices with m edges and max degree D.
   (1)  bip(G) <= min_v e(G - N(v)) = m - max_v sum_{u in N(v)} d(u)
   (2)  bip(G) <= m - (1/N) sum_v d(v)^2  <=  m - 4 m^2 / N^2  <=  N^2/16
   (3)  bip(G) <= floor((N - D)^2 / 4)
   (4)  bip(G) <= m/2                                          (max cut >= m/2)
Consequences (all unconditional):
   (A)  m >= N^2/5   ==>  bip(G) <= N^2/25       [ (2), decreasing branch ]
   (B)  m <= 2N^2/25 ==>  bip(G) <= N^2/25       [ (4) ]
   (C)  D >= 3N/5    ==>  bip(G) <= N^2/25       [ (3) ]
   (D)  always        bip(G) <= N^2/16 = 0.0625 N^2
The open density band left by (A)+(B) is  2N^2/25 < m < N^2/5, i.e. 0.08 N^2 < m < 0.2 N^2.
Equality in (2) at m = N^2/5 is attained exactly by C5[n] (regular, N(v) a maximum
independent set), where the bound returns exactly n^2 = N^2/25.
"""
from fractions import Fraction as F
import itertools
import random
import subprocess
import sympy as sp
import G12_core as C

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


# --------- INDEPENDENT implementation of the bound: build the cut explicitly ----
def bound_by_explicit_cut(n, E):
    """For every v, build the cut (N(v), V \\ N(v)) explicitly, count monochromatic
    edges directly (no degree formula), and return the minimum.  This is the
    'exhibit an explicit edge set meeting all odd cycles' form."""
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    best = None
    bestF = None
    for v in range(n):
        S = A[v]
        mono = [(a, b) for (a, b) in E if ((a in S) == (b in S))]
        if best is None or len(mono) < best:
            best = len(mono)
            bestF = mono
    return best, bestF


def check_transversal(n, E, Fset):
    rem = [e for e in E if e not in set(Fset)]
    return C.bip_bruteforce_fast(n, rem) == 0


def degree_formula(n, E):
    d = [0] * n
    A = [set() for _ in range(n)]
    for u, v in E:
        d[u] += 1
        d[v] += 1
        A[u].add(v)
        A[v].add(u)
    return len(E) - max(sum(d[u] for u in A[v]) for v in range(n))


def avg_bound(n, E):
    d = [0] * n
    for u, v in E:
        d[u] += 1
        d[v] += 1
    return F(len(E)) - F(sum(x * x for x in d), n)


def random_maximal_trianglefree(n, seed):
    rnd = random.Random(seed)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    A = [set() for _ in range(n)]
    E = []
    for (u, v) in pairs:
        if A[u] & A[v]:
            continue
        A[u].add(v)
        A[v].add(u)
        E.append((u, v))
    return n, sorted(E)


def main():
    print("=" * 78)
    print("exact algebra of the band")
    print("=" * 78)
    x = sp.symbols('x', positive=True)
    sols = sp.solve(sp.Eq(x - 4 * x ** 2, sp.Rational(1, 25)), x)
    print(f"  x - 4x^2 = 1/25  has roots x = {sols}   (x = m/N^2)")
    mx = sp.solve(sp.diff(x - 4 * x ** 2, x), x)[0]
    print(f"  max of x - 4x^2 at x = {mx}, value {sp.simplify((x-4*x**2).subs(x,mx))} = 1/16")
    print(f"  so bip <= N^2/25 whenever m/N^2 <= {min(sols)} = 1/20 or m/N^2 >= {max(sols)} = 1/5")
    print(f"  and bip <= m/2 <= N^2/25 whenever m/N^2 <= 2/25 = 0.08 (this beats 1/20 = 0.05)")
    print(f"  ==> remaining open density band: 2/25 < m/N^2 < 1/5, i.e. 0.08 < m/N^2 < 0.2")

    print()
    print("=" * 78)
    print("independent verification: explicit cut construction vs degree formula")
    print("=" * 78)
    fails = 0
    tested = 0
    for n in range(5, 11):
        out = subprocess.run([GENG, "-tc", str(n)], capture_output=True, text=True)
        gs = [ln.strip() for ln in out.stdout.split("\n") if ln.strip()]
        for g6 in gs:
            nn, E = C.graph6_to_edges(g6)
            b1, Fset = bound_by_explicit_cut(nn, E)
            b2 = degree_formula(nn, E)
            b = C.bip_bruteforce_fast(nn, E)
            ok = check_transversal(nn, E, Fset)
            tested += 1
            if b1 != b2 or b > b1 or not ok or b1 > avg_bound(nn, E) or avg_bound(nn, E) > F(nn * nn, 16):
                fails += 1
                if fails < 5:
                    print("   FAIL", g6, b, b1, b2, ok)
        print(f"  n={n}: {len(gs)} graphs, cumulative failures = {fails}", flush=True)
    print(f"  total tested {tested}, failures {fails}")

    print()
    print("=" * 78)
    print("stress test on random MAXIMAL triangle-free graphs (dense regime)")
    print("=" * 78)
    dense = 0
    for n in (14, 16, 18, 20):
        for s in range(60):
            nn, E = random_maximal_trianglefree(n, 1000 * n + s)
            b = C.bip_bruteforce_fast(nn, E)
            b1, Fset = bound_by_explicit_cut(nn, E)
            av = avg_bound(nn, E)
            assert b <= b1 <= av <= F(nn * nn, 16), (n, s, b, b1, av)
            if F(len(E)) >= F(nn * nn, 5):
                dense += 1
                assert b <= F(nn * nn, 25)
        print(f"  n={n}: 60 random maximal triangle-free graphs OK "
              f"(bip <= explicit-cut <= avg <= N^2/16)", flush=True)
    print(f"  of which {dense} had m >= N^2/5; all satisfied bip <= N^2/25")

    print()
    print("=" * 78)
    print("unbalanced C5 blow-ups C5[a1..a5] (the dense non-bipartite triangle-free family)")
    print("=" * 78)
    worst = None
    for N in (20, 25, 30):
        for a in itertools.combinations_with_replacement(range(0, N + 1), 5):
            if sum(a) != N:
                continue
            for perm in set(itertools.permutations(a)):
                m = sum(perm[i] * perm[(i + 1) % 5] for i in range(5))
                # bip by the blow-up identity: min over the 2-colourings of C5
                best = None
                for S in range(32):
                    mono = sum(perm[i] * perm[(i + 1) % 5]
                               for i in range(5) if ((S >> i) & 1) == ((S >> ((i + 1) % 5)) & 1))
                    best = mono if best is None else min(best, mono)
                if 5 * m >= N * N:                       # m >= N^2/5
                    assert best <= F(N * N, 25), (perm, m, best)
                r = F(best, N * N)
                if worst is None or r > worst[0]:
                    worst = (r, perm, m, best, N)
        print(f"  N={N}: all compositions checked; densest ones satisfy bip <= N^2/25", flush=True)
    print(f"  worst bip/N^2 over all C5-blow-ups scanned: {worst[0]} = {float(worst[0]):.6f}"
          f"  at parts {worst[1]} (N={worst[4]}, m={worst[2]}, bip={worst[3]})")


if __name__ == "__main__":
    main()
