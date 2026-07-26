"""ROOT-AGENT (Claude): kill my own R3-C44 route -- and the whole "psi <= c*W" family with it.

R3-C44 proposed closing piece (i) via psi <= (4/25) W at odd girth >= 7, measured max psi/W = 1/7
over 934 graphs on n <= 11 with 10.7% headroom. I flagged the next step: look for an odd-girth-7
analogue of the N=14 witness at larger n. Here it is, and it is a whole family.

TWICE-SUBDIVIDED K_n. Replacing every edge by a path of length 3 gives a triangle-free graph of odd
girth 9, and an odd subdivision PRESERVES bip (round-9 Lemma S). So with n even,

        bip = C(n,2) - n^2/4 = n(n-2)/4,     |E| = 3 C(n,2) = 3n(n-1)/2,
        psi/W at uniform = bip/|E| = (n-2) / (6(n-1))   ->   1/6 as n -> infinity.

(n-2)/(6(n-1)) > 4/25 exactly when 25(n-2) > 24(n-1), i.e. n > 26. So twice-subdivided K_28 already
violates psi <= (4/25) W.

THE FAMILY-LEVEL CONSEQUENCE, which is the real result. Any bound of the form psi <= c*W valid at odd
girth >= 7 needs c >= 1/6. Combined with the Motzkin-Straus cap W <= 1/4, the best such bound gives

        psi <= (1/6)(1/4) = 1/24 = 0.041666... > 1/25 = 0.04,

so NO bound of the form psi <= c*W can close piece (i). The entire family is dead, not just the 4/25
member. Verified below with exact integer arithmetic; bip(K_n) = C(n,2) - floor(n^2/4) is exact since
the maximum cut of K_n is the balanced bipartition.
"""
from fractions import Fraction as F


def bip_Kn(n):
    return n * (n - 1) // 2 - (n * n) // 4


print(f"{'n':>4s} {'|E(K_n)|':>9s} {'bip(K_n)':>9s} {'subdiv |E|':>11s} {'N':>7s} "
      f"{'psi/W = bip/|E|':>18s} {'> 4/25 ?':>10s} {'psi at uniform':>16s}")
worst = None
for n in (5, 6, 7, 9, 10, 12, 20, 26, 27, 28, 30, 40, 100, 1000):
    m = n * (n - 1) // 2
    b = bip_Kn(n)
    Esub = 3 * m
    N = n + 2 * m
    ratio = F(b, Esub)
    psi = F(b, N * N)
    over = ratio > F(4, 25)
    if over and worst is None:
        worst = (n, ratio, psi)
    print(f"{n:4d} {m:9d} {b:9d} {Esub:11d} {N:7d} {str(ratio):>18s} "
          f"{('YES' if over else 'no'):>10s} {float(psi):16.8f}")

print(f"\nlimit of bip/|E| for twice-subdivided K_n (n even): (n-2)/(6(n-1)) -> 1/6 = {1/6:.8f}")
print(f"4/25 = {4/25:.8f};  first even violator n = 28: "
      f"{float(F(26, 6*27)):.8f} > {4/25:.8f}")
print(f"\nCONSEQUENCE: any psi <= c*W valid at odd girth >= 7 needs c >= 1/6, and then")
print(f"  c * (Motzkin-Straus cap 1/4) = 1/24 = {1/24:.8f} > 1/25 = {1/25:.8f}")
print(f"  so NO bound of the form psi <= c*W can close piece (i). The family is dead.")
first = None
for n in range(4, 60, 2):
    if F(bip_Kn(n), 3 * (n * (n - 1) // 2)) > F(4, 25):
        first = n
        break
print(f"\nfirst even n with twice-subdivided K_n violating psi <= (4/25)W: {first}")
n = first
m = n * (n - 1) // 2
print(f"  K_{n}: |E| = {m}, bip = {bip_Kn(n)}; twice-subdivided: N = {n + 2*m}, "
      f"|E| = {3*m}, odd girth 9")
print(f"  psi/W = {F(bip_Kn(n), 3*m)} = {float(F(bip_Kn(n), 3*m)):.8f} > 4/25")
print(f"  psi at uniform = {F(bip_Kn(n), (n+2*m)**2)} = "
      f"{float(F(bip_Kn(n), (n+2*m)**2)):.10f}  -- the CONJECTURE is untouched "
      f"({float(F(bip_Kn(n), (n+2*m)**2)) < 0.04})")
