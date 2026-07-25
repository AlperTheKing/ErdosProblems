"""
G7_wagner.py -- attempt an ELEMENTARY proof of  max_x psi(Gamma_3, x) = 1/25
(Gamma_3 = And(3) = Wagner graph V8), which by Theorem R3 (rung t=4) would give
the unconditional statement

    bip(G) <= N^2/25   for every triangle-free G with delta(G) > 4N/11,

strictly improving Haeggkvist's delta > 3N/8.

Model used here: Gamma_3 ~= C8({1,4}), i.e. V = Z_8 with the 8 cycle edges
{j,j+1} and the 4 diagonals {j,j+4}.  (Verified isomorphic to the
Brandt-Thomasse Gamma_3 below.)

Step 1: locate every cut of C8({1,4}) leaving at most 3 monochromatic edges.
Step 2: for a candidate family C of cuts, test exhaustively over integer
        weightings whether  min_{S in C} Q_S(a) <= q^2/25  can FAIL.
        A failure is a witness that the family C is too small (it does NOT
        refute the conjecture: other cuts remain).
Everything exact (integers / Fraction).
"""
import sys, os, itertools
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G7_patterns import gamma, isomorphic, G

N = 8
EDGES = [(j, (j + 1) % 8) for j in range(8)] + [(j, (j + 4) % 8) for j in range(4)]
EDGES = sorted(set(tuple(sorted(e)) for e in EDGES))


def build():
    g = G(range(8))
    for u, v in EDGES:
        g.add(u, v)
    return g


def mono(S):
    return [(u, v) for (u, v) in EDGES if ((S >> u) & 1) == ((S >> v) & 1)]


def Q(S, a):
    return sum(a[u] * a[v] for (u, v) in mono(S))


def compositions(q, n):
    if n == 1:
        yield (q,); return
    for t in range(q + 1):
        for r in compositions(q - t, n - 1):
            yield (t,) + r


if __name__ == '__main__':
    g = build()
    print('C8({1,4}) ~= Gamma_3 :', isomorphic(g, gamma(3)),
          ' n=%d m=%d' % (g.n(), g.m()))

    small = {}
    for S in range(1 << 7):
        M = mono(S)
        small.setdefault(len(M), []).append((S, tuple(M)))
    for k in sorted(small):
        if k <= 3:
            print('cuts with %d monochromatic edges: %d' % (k, len(small[k])))
            for S, M in small[k]:
                print('    S=%s  mono=%s' % (format(S, '08b')[::-1], list(M)))

    FAM = [S for S, M in small.get(2, [])]
    print()
    print('minimal family FAM (all cuts with exactly 2 mono edges): %d cuts' % len(FAM))
    print('   their monochromatic pairs:', [list(mono(S)) for S in FAM])

    print()
    print('== exhaustive test of  min_{S in FAM} Q_S(a) <= q^2/25 ==')
    worst = Fraction(0)
    for q in range(1, 41):
        loc = Fraction(0); arg = None
        for a in compositions(q, 8):
            m = min(Q(S, a) for S in FAM)
            r = Fraction(25 * m, q * q)
            if r > loc:
                loc, arg = r, a
        if loc > worst:
            worst = loc
        flag = 'FAMILY TOO SMALL' if loc > 1 else 'ok'
        print('   q=%2d  max_a 25*min_FAM/q^2 = %-10s  %-18s argmax=%s'
              % (q, loc, flag, arg))
    print('   overall worst over q<=40 :', worst)
