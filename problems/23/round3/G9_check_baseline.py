"""G9 baseline checks:
 (a) bip(C5[n]) = n^2 for n=1..8 (via weighted blow-up formula, exact).
 (b) deleting one vertex of C5[n] drops bip by exactly n.
 (c) deleting N[v] (closed neighbourhood, 1+2n vertices) drops bip by ...? -> naive N[v] peel test.
 (d) budget checks.
"""
from fractions import Fraction
from G9_lib import C5_EDGES, bip_weighted, blowup, bip_bruteforce

print("=== (a) bip(C5[w]) via weighted cut min ===")
for n in range(1, 9):
    w = [n] * 5
    b = bip_weighted(5, C5_EDGES, w)
    N = 5 * n
    print(f"n={n} N={N} bip={b} n^2={n*n} N^2/25={Fraction(N*N,25)} ok={b==n*n}")

print()
print("=== (b) delete one vertex: C5[n] minus a vertex = C5[n-1,n,n,n,n] ===")
for n in range(1, 9):
    w = [n - 1, n, n, n, n]
    b = bip_weighted(5, C5_EDGES, w)
    N = 5 * n
    drop = n * n - b
    print(f"n={n}: bip(G-v)={b}, drop={drop}, n={n}, budget (2N-1)/25={Fraction(2*N-1,25)}"
          f" floor(d/2)={(2*n)//2}  need drop>=floor(d/2)? {drop >= (2*n)//2}")

print()
print("=== (c) delete N[v]: removes v plus its 2n neighbours = parts (n-1,0,n,n,0) ===")
# v in part 0; N(v) = parts 1 and 4 entirely.
for n in range(1, 9):
    w = [n - 1, 0, n, n, 0]
    b = bip_weighted(5, C5_EDGES, w)
    N = 5 * n
    k = 1 + 2 * n  # vertices removed
    Nn = N - k
    print(f"n={n}: bip(G-N[v])={b} (should be 0: parts 0,2,3 with edge 2-3 only... )"
          f"  removed k={k}, N'={Nn}, N'^2/25={Fraction(Nn*Nn,25)}, N^2/25={Fraction(N*N,25)},"
          f" need bip(G)<=bip(G-N[v]) + cost; actual bip(G)={n*n}, gap={n*n-b}")

print()
print("=== (c') edges incident to N[v] in C5[n] ===")
for n in range(1, 6):
    # edges within N[v] union edges leaving: v has 2n edges; each neighbour in part1 has n
    # nbrs in part2 plus n in part0; etc.
    pass

print()
print("=== (d) sanity: bip via brute force on small blow-ups matches weighted ===")
for n in range(1, 4):
    w = [n] * 5
    N, E, off = blowup(5, C5_EDGES, w)
    bf = bip_bruteforce(N, E)
    wt = bip_weighted(5, C5_EDGES, w)
    print(f"n={n} N={N} brute={bf} weighted={wt} match={bf==wt}")
