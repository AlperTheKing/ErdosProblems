"""F1: exactly what the published data a(5m)=m^2 (m<=40) forces for all N<=200.

Inputs used (and ONLY these):
   (K)  a(5m) = m^2 for 1 <= m <= 40        [arXiv:2606.28041]
   (M)  a is nondecreasing                  [add an isolated vertex]
   (B)  a(t*N) >= t^2 a(N)                  [Lemma A, balanced blow-up]

(B) is used in the contrapositive form a(N) <= a(tN)/t^2.
Everything is exact rational / integer arithmetic (Fraction).
"""
from fractions import Fraction as F

MMAX = 40          # a(5m)=m^2 known for m <= MMAX
NKNOWN = 5 * MMAX  # = 200


def a_upper_known(n):
    """Best upper bound on a(n) from (K)+(M) alone: a(n) <= ceil(n/5)^2 (n<=200)."""
    if n > NKNOWN:
        return None
    m = -(-n // 5)
    return F(m * m)


def U(n):
    """Best upper bound on a(n) from (K)+(M)+(B)."""
    best = None
    t = 1
    while t * n <= NKNOWN:
        u = a_upper_known(t * n) / (t * t)
        if best is None or u < best:
            best = u
            bt = t
        t += 1
    return best, bt


def main():
    print("N   5|N   floor(N^2/25)   best-derivable-bound   floor(bound)  deficit  t*")
    worst = []
    settled = []
    for n in range(1, NKNOWN + 1):
        tgt = (n * n) // 25          # conjecture: a(n) <= N^2/25, a integer => <= floor
        b, t = U(n)
        fb = b.numerator // b.denominator
        deficit = fb - tgt
        if deficit <= 0:
            settled.append(n)
        else:
            worst.append((n, tgt, b, fb, deficit, t))
    print("SETTLED (derivable bound <= floor(N^2/25)) for N in:", settled)
    print("count settled:", len(settled), " max settled N:", max(settled))
    print()
    print("NOT settled, N <= 200:", len(worst))
    for (n, tgt, b, fb, deficit, t) in worst[:20]:
        print(f"{n:4d}  {tgt:6d}  {float(b):12.4f} {fb:8d} {deficit:6d}  t={t}")
    print("...")
    for (n, tgt, b, fb, deficit, t) in worst[-6:]:
        print(f"{n:4d}  {tgt:6d}  {float(b):12.4f} {fb:8d} {deficit:6d}  t={t}")
    # is any multiple of 5 unsettled?
    print("unsettled multiples of 5:", [w[0] for w in worst if w[0] % 5 == 0])
    print("smallest unsettled N:", worst[0][0])
    print("deficit at N=41..49:", [(w[0], w[4]) for w in worst if w[0] < 50])


if __name__ == "__main__":
    main()
