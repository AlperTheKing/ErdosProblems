"""G9: the exact integrality-sharpened min-degree bound for a minimal counterexample, and
the exact edge-density window from THEOREM A.

Sharpened bound (proved in the report):
  minimal counterexample G on N vertices  =>  bip(G) >= floor(N^2/25)+1 and
  bip(G-v) <= floor((N-1)^2/25), and bip(G)-bip(G-v) <= floor(d(v)/2), hence
      delta(G) >= 2*( floor(N^2/25) + 1 - floor((N-1)^2/25) ) =: L(N).
Compare with the recorded bound  delta > (4N-2)/25, i.e. delta >= floor((4N-2)/25)+1 =: L0(N).

Edge-density window (THEOREM A + bip <= m/2):
  minimal counterexample  =>  2N^2/25 < m < N^2/5,
  i.e.  m >= floor(2N^2/25)+1  and  m <= ceil(N^2/5)-1.
"""
from fractions import Fraction


def L(N):
    return 2 * (N * N // 25 + 1 - (N - 1) * (N - 1) // 25)


def L0(N):
    return (4 * N - 2) // 25 + 1


def window(N):
    lo = 2 * N * N // 25 + 1          # m > 2N^2/25
    # m < N^2/5 : largest integer strictly below N^2/5
    q, r = divmod(N * N, 5)
    hi = q - 1 if r == 0 else q
    return lo, hi


if __name__ == "__main__":
    print("N   L(N)=sharpened  L0(N)=recorded  gain   4N/25      m-window (exclusive of ends)")
    worst = None
    for N in list(range(20, 60)) + [75, 100, 125, 200, 250, 500, 1000, 2500]:
        g = L(N) - L0(N)
        lo, hi = window(N)
        if worst is None or g < worst[0]:
            worst = (g, N)
        print(f"{N:5d} {L(N):6d} {L0(N):9d} {g:8d}   {float(Fraction(4*N,25)):8.2f}   "
              f"[{lo}, {hi}]  N^2/4={N*N//4}")
    print()
    print("minimum gain over the sampled range:", worst)
    # verify L(N) >= L0(N) for all N up to 100000
    bad = [N for N in range(2, 100001) if L(N) < L0(N)]
    print("N <= 100000 where the sharpened bound is WEAKER than the recorded one:", bad[:20], "count", len(bad))
    # asymptotic form
    print()
    print("L(N) - 4N/25 for N = 25t:")
    for t in range(1, 11):
        N = 25 * t
        print(f"  t={t} N={N}: L(N)={L(N)}  4N/25={4*N//25}  difference={L(N)-4*N//25}")
