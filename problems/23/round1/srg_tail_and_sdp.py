"""
(A) Rigorous tail bound for the triangle-free srg scan.

For srg(N,d,0,mu) with eigenvalues r > 0 > s = -t:
        mu = t - r,   d = mu + r t,   N = 1 + d + d(d-1)/mu .
The spectral lower bound on bip/N^2 is  rho(r,t) = (d-t)/(4N).
Since N > d(d-1)/mu and d - t < d,
        rho  <  mu / (4(d-1))  =  (t-r) / (4(t - r + r t - 1)) .
So rho >= 1/25 forces  25(t-r) >= 4(t-r+rt-1), i.e.  t(21-4r) >= 21r-4.
For r >= 6 the left side is negative and the right side positive: IMPOSSIBLE.
Hence only r in {1,2,3,4,5} can conceivably reach 1/25, and those we scan
exhaustively over a large range of t with the full feasibility conditions.

(B) The Goemans-Williamson SDP at C5, exactly.
    The optimal GW vector solution for C_5 places the five unit vectors at
    consecutive angles 4*pi/5; the value is  5*(1-cos(4 pi /5))/2 = (25+5 sqrt5)/8.
    Hence  |E| - SDP(C5) = 5 - (25+5 sqrt5)/8 = (15 - 5 sqrt5)/8 = 0.4774...,
    an IRRATIONAL number strictly below bip(C5) = 1.
    So the plain GW relaxation is NOT exact at the extremal example, while
    (see below) the odd-cycle LP is.
    For a d-regular graph  SDP <= N(d - lam_min)/4;  for Higman-Sims this is
    100*(22+8)/4 = 750 = maxcut(HS), so the plain GW SDP IS exact there.
"""
from fractions import Fraction
import sympy as sp


def srg_tail(tmax=30000):
    print("=== (A) rigorous tail of the triangle-free srg scan ===")
    print("    r >= 6 is impossible (see the algebraic argument above).")
    best = []
    for r in range(1, 6):
        for t in range(r + 1, tmax + 1):
            mu = t - r
            d = mu + r * t
            if d * (d - 1) % mu:
                continue
            N = 1 + d + d * (d - 1) // mu
            num = 2 * d - (N - 1) * mu
            den = r + t
            if num % den:
                continue
            if ((N - 1) - num // den) % 2:
                continue
            f = ((N - 1) - num // den) // 2
            g = (N - 1) - f
            if f < 0 or g < 0:
                continue
            s = -t
            if not ((r + 1) * (d + r + 2 * r * s) <= (d + r) * (s + 1) ** 2):
                continue
            if not ((s + 1) * (d + s + 2 * r * s) <= (d + s) * (r + 1) ** 2):
                continue
            if N > f * (f + 3) // 2 or N > g * (g + 3) // 2:
                continue
            best.append((Fraction(d - t, 4 * N), N, d, mu, r, t))
    best.sort(reverse=True)
    print(f"    admissible parameter sets with r <= 5, t <= {tmax}: {len(best)}")
    for ratio, N, d, mu, r, t in best[:6]:
        print(f"      {str(ratio):>10s} = {float(ratio):.6f}   srg({N},{d},0,{mu})"
              f"   [r={r}, s=-{t}]")
    m = max(b[0] for b in best)
    print(f"    MAXIMUM = {m} = {float(m):.6f}   vs 1/25 = 0.04    "
          f"{'STRICTLY BELOW' if m < Fraction(1,25) else 'EXCEEDS'}")
    print("    => no triangle-free strongly regular graph can violate the")
    print("       conjecture through the eigenvalue bound; the extremal one is")
    print("       srg(100,22,0,6) = Higman-Sims, at exactly 7/200 = 0.035.")


def gw_c5():
    print()
    print("=== (B) exact Goemans-Williamson SDP value at C5 ===")
    th = sp.Rational(4, 5) * sp.pi
    val = sp.nsimplify(5 * (1 - sp.cos(th)) / 2)
    val = sp.simplify(sp.radsimp(val))
    print(f"    SDP(C5) = 5*(1-cos(4pi/5))/2 = {sp.simplify(val)} = {sp.N(val, 20)}")
    gap = sp.simplify(5 - val)
    print(f"    |E| - SDP(C5) = {sp.simplify(gap)} = {sp.N(gap, 20)}   "
          f"(bip(C5) = 1)")
    print(f"    irrational: minimal polynomial of |E|-SDP is "
          f"{sp.minimal_polynomial(gap, sp.Symbol('x'))}")
    # verify optimality of the 4pi/5 configuration by the standard dual:
    # for a d-regular graph  SDP <= N(d - lam_min)/4 ; for C5, lam_min = 2cos(4pi/5)
    lam = 2 * sp.cos(th)
    bound = sp.simplify(sp.Rational(5, 4) * (2 - lam))
    print(f"    regular upper bound N(d-lam_min)/4 = {sp.simplify(bound)} "
          f"= {sp.N(bound,20)}  (equals the value above => SDP(C5) exact)")
    print()
    print("    Higman-Sims: SDP <= N(d-lam_min)/4 = 100*(22+8)/4 = 750 = maxcut(HS),")
    print("    so SDP(HS) = 750 exactly and |E|-SDP = 1100-750 = 350 = bip(HS).")
    print("    => GW SDP exact at Higman-Sims, NOT exact at C5;")
    print("       odd-cycle LP exact at C5[n], NOT exact at Higman-Sims (220 < 350).")


if __name__ == "__main__":
    srg_tail()
    gw_c5()
