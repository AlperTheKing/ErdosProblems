"""Q1_c5spectrum.py -- exact cut spectrum of C5[n] and the entropy budget for route (a).

For a blow-up H[a] the monochromatic count of a cut S depends ONLY on the profile
s_i = |S cap B_i|:   mono(s) = sum_i [ s_i s_{i+1} + (n-s_i)(n-s_{i+1}) ]   (indices mod 5).
Hence the exact histogram A_k = #{cuts of C5[n] with mono = k} is computable in
O(n^5) exact integer operations for any n:  A_k = sum over profiles of prod C(n,s_i).

Outputs (all exact integers / Fractions):
  * A_k for k near the minimum
  * the number of minimum cuts (predicted 10)
  * the entropy budget  H*(M) = max { H(nu) : E_nu[mono] <= M }  = min_beta [ beta*M + log Z(beta) ]
    reported as a certified upper bound via a rational beta (Gibbs variational principle:
    H(nu) <= beta E_nu[mono] + log Z(beta) holds for EVERY beta >= 0 and every nu).
"""
from fractions import Fraction
from math import comb, log, exp
from itertools import product
import sys

FIVE = range(5)


def spectrum(n):
    """exact dict k -> number of cuts of C5[n] with exactly k monochromatic edges"""
    hist = {}
    C = [comb(n, i) for i in range(n + 1)]
    for s in product(range(n + 1), repeat=5):
        mono = 0
        for i in FIVE:
            j = (i + 1) % 5
            mono += s[i] * s[j] + (n - s[i]) * (n - s[j])
        w = C[s[0]] * C[s[1]] * C[s[2]] * C[s[3]] * C[s[4]]
        hist[mono] = hist.get(mono, 0) + w
    return hist


def check_total(hist, n):
    return sum(hist.values()) == 2 ** (5 * n)


def entropy_budget(hist, M, betas):
    """H(nu) <= beta*M + log Z(beta) for every beta>=0; return the best over the given betas.
    log Z computed in exact integer arithmetic where possible: Z = sum A_k exp(-beta k).
    We use Python floats only for the transcendental log/exp; the CERTIFIED statement is
    'for this rational beta, H <= beta*M + log Z(beta)', and both sides are evaluated with
    the exact integers A_k (float only in the final transcendental evaluation)."""
    best = None
    kmin = min(hist)
    for beta in betas:
        # log Z = -beta*kmin + log( sum_k A_k exp(-beta(k-kmin)) )
        s = 0.0
        for k, a in hist.items():
            s += a * exp(-beta * (k - kmin))
        val = beta * M + (-beta * kmin + log(s))
        if best is None or val < best[0]:
            best = (val, beta)
    return best


def main():
    print("=== exact cut spectrum of C5[n] ===")
    for n in range(1, 9):
        hist = spectrum(n)
        assert check_total(hist, n), "histogram does not sum to 2^N"
        kmin = min(hist)
        N = 5 * n
        print(f"n={n}  N={N}  min mono = {kmin}  (n^2 = {n*n}, N^2/25 = {Fraction(N*N,25)})"
              f"   #minimum cuts = {hist[kmin]}   total cuts = 2^{N}")
        ks = sorted(hist)[:8]
        print("      spectrum head:", [(k, hist[k]) for k in ks])
    print()
    print("=== entropy budget on C5[n]:  max H(nu) subject to E_nu[mono] <= (1/25+eps) N^2 ===")
    print("    (Gibbs variational principle; log 2 per vertex = full entropy)")
    betas = [Fraction(1, 1) * b / 8 for b in range(1, 400)]
    betas = [float(b) for b in betas]
    for n in [4, 6, 8]:
        hist = spectrum(n)
        N = 5 * n
        kmin = min(hist)
        print(f"  n={n} N={N} (full entropy N*log2 = {N*log(2):.4f}, min mono = {kmin})")
        for eps in [Fraction(0), Fraction(1, 1000), Fraction(1, 200), Fraction(1, 100), Fraction(1, 50)]:
            M = float((Fraction(1, 25) + eps) * N * N)
            val, beta = entropy_budget(hist, M, betas)
            print(f"      eps={str(eps):>8}  M={M:9.3f}  max entropy <= {val:9.4f} nats"
                  f"   = {val/(N*log(2)):.4f} x (N log 2)   [beta={beta:.3f}]")
    print()
    print("=== exact statement at eps = 0 ===")
    for n in range(1, 9):
        hist = spectrum(n)
        kmin = min(hist)
        print(f"  n={n}: every cut has mono >= {kmin} = n^2; #minimizers = {hist[kmin]};"
              f"  so E_nu[mono] <= N^2/25 forces supp(nu) in the {hist[kmin]} minimizers,"
              f" i.e. H(nu) <= log {hist[kmin]} = {log(hist[kmin]):.4f} nats")


if __name__ == "__main__":
    main()
