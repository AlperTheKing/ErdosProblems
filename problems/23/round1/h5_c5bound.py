"""B(N) = max over integer part sizes w_1..w_5 >= 0 summing to N of min_i w_i w_{i+1}.

Lemma (elementary, proved in h5.md): if a triangle-free G on N vertices admits a
homomorphism to C5 then G is a subgraph of the blow-up C5[w] for w = fibre sizes, and
since bip is monotone under edge deletion,  bip(G) <= bip(C5[w]) = min_i w_i w_{i+1} <= B(N).
So every counterexample to Erdos #23 must be NON-C5-COLOURABLE.
"""
import sys


def B(N):
    best, arg = -1, None
    for a in range(N + 1):
        for b in range(N - a + 1):
            for c in range(N - a - b + 1):
                for d in range(N - a - b - c + 1):
                    e = N - a - b - c - d
                    v = min(a * b, b * c, c * d, d * e, e * a)
                    if v > best:
                        best, arg = v, (a, b, c, d, e)
    return best, arg


if __name__ == "__main__":
    Ns = [int(x) for x in sys.argv[1:]] or list(range(4, 30)) + [49, 51, 74, 76]
    print(f"{'N':>4} {'floor(N^2/25)':>13} {'B(N)':>6} {'gap':>4} {'B/N^2':>9}  parts")
    for N in Ns:
        b, arg = B(N)
        print(f"{N:>4} {N*N//25:>13} {b:>6} {N*N//25-b:>4} {b/(N*N):>9.6f}  {arg}")
