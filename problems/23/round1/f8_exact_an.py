"""
f8_exact_an.py -- EXACT a(N) = max bip(G) over all triangle-free G on N vertices,
for N <= 14, using the pattern reduction:

   every triangle-free G on N vertices reduces (add edges to maximality, then
   merge equal-neighbourhood vertices) to a REDUCED MAXIMAL TRIANGLE-FREE
   pattern H on k <= N vertices carrying positive integer weights a summing to N,
   with  bip(G) <= min_c sum_{ij in E(H), c_i=c_j} a_i a_j  =: Psi(H,a),
   and every blow-up H[a] attains Psi(H,a) exactly.

Hence  a(N) = max over patterns H with |V(H)| <= N and integer compositions a of N
              of Psi(H,a).      All arithmetic is exact integer arithmetic.
"""
import sys, itertools, glob
from f8_core import g6_decode, mono_sets, edges_of

NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 14
PATTERNS = {}      # k -> list of (g6, edges, minimal masks)
for fn in sorted(glob.glob('f8_rmtf_*.g6')):
    if int(fn.split('_')[-1].split('.')[0]) > NMAX:
        continue
    for line in open(fn):
        line = line.strip()
        if not line:
            continue
        n, adj = g6_decode(line)
        E, minimal = mono_sets(n, adj)
        PATTERNS.setdefault(n, []).append((line, E, minimal))
print("patterns loaded:", {k: len(v) for k, v in sorted(PATTERNS.items())})


def Psi(E, minimal, a):
    best = None
    for mask in minimal:
        s = 0
        mm = mask
        while mm:
            b = (mm & -mm).bit_length() - 1
            i, j = E[b]
            s += a[i] * a[j]
            mm &= mm - 1
            if best is not None and s >= best:
                break
        else:
            if best is None or s < best:
                best = s
    return best


def compositions(N, k):
    for cut in itertools.combinations(range(1, N), k - 1):
        prev = 0
        out = []
        for c in cut:
            out.append(c - prev)
            prev = c
        out.append(N - prev)
        yield out


print(f"{'N':>3} {'a(N)':>5} {'N^2/25':>9} {'a(N)/N^2':>12}  witness")
for N in range(5, NMAX + 1):
    best, wit = 0, None
    for k, pats in PATTERNS.items():
        if k > N:
            continue
        for (g6, E, minimal) in pats:
            for a in compositions(N, k):
                v = Psi(E, minimal, a)
                if v > best:
                    best, wit = v, (g6, tuple(a))
    from fractions import Fraction
    print(f"{N:>3} {best:>5} {N*N/25:>9.4f} {str(Fraction(best,N*N)):>12}  {wit}")
