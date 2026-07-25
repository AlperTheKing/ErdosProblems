"""G9: exact search for the C5 blow-up that defeats the single-vertex deletion mechanism
with the SMALLEST ratio delta/N.

"Defeats" means: for EVERY vertex v,  bip(G) - bip(G-v) > (2N-1)/25.
(That is exactly the condition under which the single-vertex induction step
 bip(G) <= bip(G-v) + floor(d(v)/2) <= (N-1)^2/25 + floor(d(v)/2)  gives no vertex whose
 removal fits the budget (N^2-(N-1)^2)/25.)

bip(C5[a]) = min_i a_i a_{i+1} (accepted fact 1 + odd-cut characterisation for C5);
G - v for v in part i is C5[a - e_i].
All arithmetic exact.
"""
from fractions import Fraction
from itertools import product


def bip(a):
    return min(a[i] * a[(i + 1) % 5] for i in range(5))


def defeats(a):
    N = sum(a)
    b = bip(a)
    bud = Fraction(2 * N - 1, 25)
    for i in range(5):
        if a[i] == 0:
            continue
        a2 = list(a); a2[i] -= 1
        if b - bip(a2) <= bud:
            return False
    return True


def delta(a):
    return min(a[(i - 1) % 5] + a[(i + 1) % 5] for i in range(5) if a[i] > 0)


if __name__ == "__main__":
    best = None
    LIM = 60
    for a0 in range(1, LIM + 1):
        for a1 in range(1, LIM + 1 - a0):
            for a2 in range(1, LIM + 1 - a0 - a1):
                for a3 in range(1, LIM + 1 - a0 - a1 - a2):
                    for a4 in range(1, LIM + 1 - a0 - a1 - a2 - a3):
                        a = (a0, a1, a2, a3, a4)
                        N = sum(a)
                        d = delta(a)
                        r = Fraction(d, N)
                        if best is not None and r >= best[0]:
                            continue
                        if defeats(a):
                            best = (r, a, N, d, bip(a))
    print("smallest delta/N among C5 blow-ups with N<=%d defeating the single-vertex mechanism:" % LIM)
    print("   ratio =", best[0], "=", float(best[0]), " a =", best[1],
          " N =", best[2], " delta =", best[3], " bip =", best[4],
          " N^2/25 =", Fraction(best[2] ** 2, 25))
    print("   4/25 =", Fraction(4, 25), "=", 4 / 25)
    print()
    print("check of the announced family W_t = C5[7t,2t,7t,7t,2t]:")
    for t in range(1, 7):
        a = (7 * t, 2 * t, 7 * t, 7 * t, 2 * t)
        N = sum(a)
        print(f"   t={t}: N={N} delta={delta(a)} delta/N={Fraction(delta(a),N)} "
              f"bip={bip(a)} N^2/25={Fraction(N*N,25)} defeats={defeats(a)}")
