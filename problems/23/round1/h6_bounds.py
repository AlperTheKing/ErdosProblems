"""H6 bounds ledger for Erdos #23.

Inputs (all cited, none re-derived here):
  [CENSUS]  a(N) exact for N = 4..14                      (this project, 2026-07-25)
  [PUB]     a(5n) = n^2 for 1 <= n <= 40                  (arXiv:2606.28041)
  [BCL]     Balogh-Clemen-Lidicky, arXiv:2103.14179, Thm 1.3, FOR n LARGE ENOUGH:
              (a) D2(G) <= n^2/23.5
              (b) D2(G) <= n^2/25 if |E| >= 0.3197*C(n,2)
              (c) D2(G) <= n^2/25 if |E| <= 0.2486*C(n,2)
  [HAG]     Haggkvist 1982: triangle-free, delta > floor(3n/8)  ==>  hom to C5
              (and G -> C5 implies G subgraph of a C5 blow-up, so bip <= n^2/25)

H6 TRANSFER LEMMA (proved in h6.md, verified in h6_blowup_identity.py):
  bip(G[t_1..t_n]) = min over cuts (S,S^c) of G of sum_{ij in E, same side} t_i t_j.
  Consequences used below:
   (T1) a(tN) >= t^2 a(N); with [PUB] this gives a(N) <= floor(N^2/25) for ALL N <= 40.
   (T2) any ASYMPTOTIC bound transfers to every finite N: if D2 <= c n^2 holds for all
        large n in a density class D, then D2(G) <= c N^2 for every G whose blow-up
        density 2m/N^2 lies in D.  So [BCL] becomes a rigorous FINITE-N filter:
          * every triangle-free G on N vertices has bip(G) <= N^2/23.5
          * a counterexample must have  0.2486 <= 2m/N^2 <= 0.3197.
   (T3) delta/N is blow-up invariant, so [HAG] gives: a counterexample has
        delta <= floor(3N/8).
  Peeling (classical): bip(G) <= bip(G-v) + floor(deg(v)/2) <= a(N-1) + floor(delta/2).
"""
from math import floor, isqrt

CENSUS = {4:0,5:1,6:1,7:1,8:2,9:2,10:4,11:4,12:5,13:6,14:7}
PUB = {5*n: n*n for n in range(1, 41)}          # a(5n) = n^2, n <= 40

print("=" * 78)
print("PART 1.  Corollary B check: a(N) <= floor(a(5N)/25) = floor(N^2/25) for N <= 40")
print("=" * 78)
print(f"{'N':>3} {'census a(N)':>11} {'floor(N^2/25)':>13} {'reduction bound':>15} {'sharp?':>7}")
sharp = 0
for N in range(4, 15):
    bound = PUB[5*N] // 25          # = floor(N^2/25) since a(5N)=N^2
    assert bound == (N*N)//25
    ok = "TIGHT" if CENSUS[N] == bound else f"slack {bound-CENSUS[N]}"
    sharp += (CENSUS[N] == bound)
    print(f"{N:>3} {CENSUS[N]:>11} {(N*N)//25:>13} {bound:>15} {ok:>7}")
print(f"--> reduction bound is attained at {sharp}/11 orders in 4..14 (only N=9 has slack).")
print("--> CONSEQUENCE: the Erdos conjecture is TRUE for every N <= 40.")
print("    In particular the 'tight' hunt targets N = 16,21,22,23,24,26,27,28,29,")
print("    31..34,36..39 are all DEAD, and a(16) <= 10 (so 'is a(16) >= 11?' is UNSAT).")

print()
print("=" * 78)
print("PART 2.  Surviving orders N > 40: how much room a counterexample has")
print("=" * 78)
print("A(N) = best rigorous upper bound on a(N) known after the transfer lemma.")
print(f"{'N':>4} {'target':>7} {'need>=':>7} {'A(N)':>6} {'window':>7} {'m range':>15} "
      f"{'delta<=':>8} {'bip/m>':>7} {'source of A(N)':>16}")

A = {}
for N in range(1, 41):
    A[N] = (N*N)//25
for N in PUB:
    A[N] = PUB[N]

rows = []
for N in range(41, 81):
    target = (N*N)//25                       # conjecture allows a(N) <= this
    need = target + 1                        # a violation needs bip >= need
    cand = {}
    # (i) monotonicity + [PUB]: a(N) <= a(5*ceil(N/5)) when that order is published
    up = 5 * ((N + 4)//5)
    if up in PUB:
        cand["mono"] = PUB[up]
    # (ii) [BCL](a) transferred to finite N
    cand["bcl23.5"] = floor(N*N/23.5)
    # (iii) peeling with delta bounded by the band [BCL](b) and by [HAG]
    dmax = min(floor(0.3197*N), (3*N)//8)
    if N-1 in A:
        cand["peel"] = A[N-1] + dmax//2
    src = min(cand, key=lambda k: cand[k])
    A[N] = min(cand.values())
    if N in PUB:                             # published exact value wins
        A[N] = PUB[N]; src = "PUB"
    mlo, mhi = -(-int(0.1243*N*N*1000)//1000), floor(0.15985*N*N)
    mlo = int(0.1243*N*N) + (0 if abs(0.1243*N*N - int(0.1243*N*N)) < 1e-9 else 1)
    window = A[N] - need + 1
    rows.append((N, target, need, A[N], window, mlo, mhi, dmax, need/mhi if mhi else 0, src))

for (N, target, need, AN, window, mlo, mhi, dmax, ratio, src) in rows:
    star = " <== TIGHT ORDER" if N % 25 in (1, 24) else ""
    if window <= 0:
        print(f"{N:>4} {target:>7} {need:>7} {AN:>6} {'CLOSED':>7} {'-':>15} {dmax:>8} {'-':>7} {src:>16}{star}")
    else:
        print(f"{N:>4} {target:>7} {need:>7} {AN:>6} {window:>7} {f'{mlo}-{mhi}':>15} "
              f"{dmax:>8} {ratio:>7.4f} {src:>16}{star}")

print()
print("window = number of integer values of bip that would refute the conjecture at N")
print("         (i.e. bip in [need, A(N)]);  'CLOSED' = conjecture proved at that N.")
print("m range = forced edge count from the BCL density band 0.2486 <= 2m/N^2 <= 0.3197")
print("bip/m>  = forced lower bound on the fraction of edges that must be deleted")
print("          (C5 blow-ups need only 1/5 = 0.2000 of their edges deleted)")

print()
print("=" * 78)
print("PART 3.  Best blow-up lower bounds at the tight orders (exact integer arithmetic)")
print("=" * 78)
def best_c5_blowup(N):
    best, arg = -1, None
    for a in range(1, N):
        for b in range(1, N - a):
            for c in range(1, N - a - b):
                for d in range(1, N - a - b - c):
                    e = N - a - b - c - d
                    if e < 1: continue
                    v = min(a*b, b*c, c*d, d*e, e*a)
                    if v > best: best, arg = v, (a,b,c,d,e)
    return best, arg
for N in [41, 44, 46, 49, 51, 54, 56, 59]:
    v, arg = best_c5_blowup(N)
    print(f"N={N:>3}: best C5 blow-up bip = {v:>4} (parts {arg}), "
          f"floor(N^2/25) = {(N*N)//25:>4}, gap to target = {(N*N)//25 - v}")
