"""How much must a graph beat the C5-blow-up ceiling B(N) by, to refute Erdos #23 at order N?

    need(N) = (smallest bip with 25*bip > N^2) - B(N) = floor(N^2/25) + 1 - B(N).

Since every C5-colourable triangle-free graph has bip <= B(N) (see h5.md), need(N) is exactly
the "excess over the C5-colourable world" a counterexample of order N must exhibit.
The whole H5 campaign measured this excess empirically: it is +1 at scattered N = 2 mod 5
and 0 at every N we tested with N = +-1 mod 5.
"""
import sys

def B(N):
    best = -1
    for a in range(N + 1):
        for b in range(N - a + 1):
            ab = a * b
            for c in range(N - a - b + 1):
                for d in range(N - a - b - c + 1):
                    e = N - a - b - c - d
                    v = min(ab, b * c, c * d, d * e, e * a)
                    if v > best:
                        best = v
    return best


def main():
    hi = int(sys.argv[1]) if len(sys.argv) > 1 else 130
    rows = []
    for N in range(5, hi + 1):
        b = B(N)
        need = N * N // 25 + 1 - b
        rows.append((need, N, b, N * N // 25, N % 5, N % 25))
    print(f"{'N':>4}{'N%5':>4}{'N%25':>5}{'B(N)':>7}{'floor(N^2/25)':>14}"
          f"{'need':>6}{'B/N^2':>10}   status")
    for need, N, b, fl, m5, m25 in rows:
        pub = "PUBLISHED-VERIFIED (5n, n<=40)" if (N % 5 == 0 and N <= 200) else \
              ("census N<=14" if N <= 14 else "UNVERIFIED")
        print(f"{N:>4}{m5:>4}{m25:>5}{b:>7}{fl:>14}{need:>6}{b/(N*N):>10.6f}   {pub}")
    print("\nsmallest need(N) among UNVERIFIED orders, grouped:")
    unv = [(need, N, b) for need, N, b, fl, m5, m25 in rows
           if not (N % 5 == 0 and N <= 200) and N > 14]
    unv.sort()
    for need, N, b in unv[:25]:
        print(f"   N={N:>4}  need={need:>3}  B(N)={b:>5}  B/N^2={b/(N*N):.6f}")


if __name__ == "__main__":
    main()
