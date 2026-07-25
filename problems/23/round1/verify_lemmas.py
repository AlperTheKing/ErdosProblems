"""
Exact verification of the two structural lemmas used in the write-up.

LEMMA 1 (blow-up formula).   bip(H[n_1..n_h]) = min_{X} sum_{uv mono under X} n_u n_v.
LEMMA 2 (odd-cycle template). If G -> C_{2k+1} (k>=2) then bip(G) <= N^2/(2k+1)^2,
        and for a COMPLETE blow-up of C_5 the value is exactly min_i n_i n_{i+1},
        which is <= (prod n_i)^{2/5} <= (N/5)^2 by AM-GM, with equality iff balanced.
"""
import subprocess, os, itertools
from fractions import Fraction
from f5lib import parse_graph6, bip

GENG = os.environ.get("GENG", r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe")


def blowup(h, edges, n):
    off = [0] * (h + 1)
    for i in range(h):
        off[i + 1] = off[i] + n[i]
    E = []
    for (u, v) in edges:
        for a in range(off[u], off[u + 1]):
            for b in range(off[v], off[v + 1]):
                E.append((min(a, b), max(a, b)))
    return off[h], sorted(set(E))


def formula(h, edges, n):
    best = None
    for rest in range(1 << (h - 1)):
        S = 1 | (rest << 1)
        tot = 0
        for (u, v) in edges:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += n[u] * n[v]
        if best is None or tot < best:
            best = tot
    return best


def check_lemma1():
    print("=== LEMMA 1: bip(H[n]) == min_X sum_{mono} n_u n_v ===")
    tested = 0
    for h in (4, 5, 6):
        p = subprocess.run([GENG, "-tcq", str(h)], capture_output=True, text=True)
        for g6 in p.stdout.split():
            hh, E = parse_graph6(g6)
            for n in itertools.product(range(1, 4), repeat=hh):
                if sum(n) > 13:
                    continue
                N, EB = blowup(hh, E, list(n))
                b = bip(N, EB)
                f = formula(hh, E, list(n))
                assert b == f, (g6, n, b, f)
                tested += 1
    print(f"    verified on {tested} (template, multiplicity-vector) pairs: identity holds")


def check_lemma2():
    print()
    print("=== LEMMA 2: complete C5 blow-ups.  bip = min_i n_i n_{i+1} <= (N/5)^2 ===")
    C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
    worst = []
    tested = 0
    for n in itertools.product(range(0, 7), repeat=5):
        N = sum(n)
        if N == 0 or N > 16:
            continue
        f = formula(5, C5, list(n))
        mn = min(n[i] * n[(i + 1) % 5] for i in range(5))
        assert f == mn, (n, f, mn)
        assert Fraction(f) <= Fraction(N * N, 25), (n, f, N)
        if Fraction(f) == Fraction(N * N, 25):
            worst.append(n)
        tested += 1
    print(f"    verified on {tested} multiplicity vectors: "
          f"bip = min_i n_i n_(i+1) and bip <= N^2/25 always")
    print(f"    equality cases (all balanced, as AM-GM predicts): "
          f"{sorted(set(tuple(sorted(w)) for w in worst))}")
    # small blow-ups verified against the true bip too
    for n in [(1,1,1,1,1),(2,2,2,2,2),(3,1,1,1,1),(2,2,1,1,1),(3,2,2,1,1)]:
        N, EB = blowup(5, C5, list(n))
        assert bip(N, EB) == formula(5, C5, list(n))
    print("    (cross-checked against exhaustive bip for several blow-ups)")


def check_unbalanced_obstruction():
    print()
    print("=== the 'uniform 5-rotation averaging' certificate fails off balance ===")
    print("    G_a = C5[a,a,1,1,1]:  N = 2a+3, |E| = a^2+2a+2, bip = 1,")
    print("    but every phi has W(phi) >= |E|, so the averaged bound is >= |E|/5.")
    print(f"    {'a':>3s} {'N':>4s} {'|E|':>5s} {'bip':>4s} {'|E|/5':>10s} {'N^2/25':>10s} {'avg fails?':>11s}")
    C5 = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
    for a in range(1, 8):
        n = [a, a, 1, 1, 1]
        N = sum(n)
        m = a * a + 2 * a + 2
        NB, EB = blowup(5, C5, n)
        assert len(EB) == m, (a, len(EB), m)
        b = bip(NB, EB) if NB <= 16 else formula(5, C5, n)
        assert b == 1
        e5 = Fraction(m, 5)
        cap = Fraction(N * N, 25)
        print(f"    {a:3d} {N:4d} {m:5d} {b:4d} {str(e5):>10s} {str(cap):>10s} "
              f"{'YES' if e5 > cap else 'no':>11s}")
    print("    (5*(a^2+2a+2) - (2a+3)^2 = (a-1)^2 >= 0, equality only at a=1)")


if __name__ == "__main__":
    check_lemma1()
    check_lemma2()
    check_unbalanced_obstruction()
