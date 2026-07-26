"""ROOT-AGENT GATE (Claude): re-verify the round-9 "discharging with a global potential" death.

The family's decisive claim is structural, so I check the structure and then the arithmetic witnesses.

THE THEOREM.  For a sound reduction system (every move G -> G' has bip(G) <= bip(G') + c), define
        U(G) = min over moves [ c + U(G') ],   U(bipartite) = 0.
Then a potential Phi >= 0 with the amortised step Phi(G) - Phi(G') <= (f(G) - f(G')) - c exists iff
U <= f, and the pointwise-largest such potential is Phi* = f - U.  So the "global potential" is NOT
a free parameter: it is determined by the move family.

COROLLARY 1 (circularity).  U >= bip ALWAYS.  Induction: U(G) = min[c + U(G')] >= min[c + bip(G')]
>= bip(G), the last step by soundness.  So demanding U <= f is at least as strong as bip <= f, and
when U = bip identically the mechanism is exactly the conjecture restated.

COROLLARY 2 (strength ceiling).  For the only non-circular local cost, floor(d/2), the counting
identity sum_i d_{G_i}(v_i) = |E| forces U(G) >= (|E| - N)/2.  On K_{m,m} that is N^2/8 - N/2 while
bip = 0, so this mechanism cannot prove bip <= c*N^2 for ANY c < 1/8 -- far behind the published
N^2/23.5, let alone N^2/25.

Checked here: the C5[2] sign failure, the K_{m,m} ceiling, C7 killing pentagon charging, and the
Motzkin-Straus-deficit line together with the claim that its complementary piece psi <= W/5 fails at
the N = 14 extremal graph.
"""
from fractions import Fraction as F
from itertools import combinations


def blowup(a):
    n = sum(a)
    part, k = [], 0
    for s in a:
        part.append(list(range(k, k + s)))
        k += s
    E = []
    for i in range(5):
        for u in part[i]:
            for v in part[(i + 1) % 5]:
                E.append((min(u, v), max(u, v)))
    return n, E, part


def g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for x in b[1:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E, p = [], 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def bip(n, E):
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(1 for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def induced_c5_count(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return sum(1 for S in combinations(range(n), 5)
               if all(len(A[v] & set(S)) == 2 for v in S))


print("=== Corollary 2, the strength ceiling: K_{m,m} ===")
print(f"  {'m':>3s} {'N':>4s} {'|E|':>5s} {'bip':>4s} {'U >= (|E|-N)/2':>15s} {'N^2/25':>8s} "
      f"{'N^2/8 - N/2':>12s}  method can prove bip <= c N^2 only for")
for m in (2, 3, 4, 5, 8, 12, 20, 50):
    N = 2 * m
    Em = m * m
    lb = F(Em - N, 2)
    print(f"  {m:3d} {N:4d} {Em:5d} {0:4d} {str(lb):>15s} {str(F(N*N,25)):>8s} "
          f"{str(F(N*N,8) - F(N,2)):>12s}  c >= {float(lb)/(N*N):.4f}")
print("  -> the floor is 1/8 = 0.125, while the target is 1/25 = 0.04 and the published bound is")
print("     1/23.5 = 0.0426: the mechanism is bounded away from all of them.")

print("\n=== the C5[2] sign failure: Phi* = f - U < 0, so no nonnegative potential exists ===")
n, E, _ = blowup([2, 2, 2, 2, 2])
b = bip(n, E)
f = F(n * n, 25)
U_lb = F(len(E) - n, 2)
print(f"  C5[2]: N = {n}, |E| = {len(E)}, bip = {b}, f = N^2/25 = {f}, "
      f"U >= (|E|-N)/2 = {U_lb}")
print(f"  Phi* = f - U <= {f} - {U_lb} = {f - U_lb}  -> negative: {f - U_lb < 0}")
print("  and on the whole extremal family C5[n]: 5n^2 > 2n^2 + 5n for n >= 2, i.e.")
for k in (2, 3, 4, 10):
    n2, E2, _ = blowup([k] * 5)
    print(f"    C5[{k}]: N = {n2}, |E| = {len(E2)}, f = {F(n2*n2,25)}, "
          f"(|E|-N)/2 = {F(len(E2)-n2,2)}, Phi* <= {F(n2*n2,25) - F(len(E2)-n2,2)}")

print("\n=== pentagon charging dies on C7 ===")
n7, E7 = 7, [(i, (i + 1) % 7) for i in range(7)]
print(f"  C7: bip = {bip(n7, E7)}, induced pentagons = {induced_c5_count(n7, E7)}"
      f"  -> charge has nowhere to go: {induced_c5_count(n7, E7) == 0 and bip(n7, E7) > 0}")

print("\n=== the Motzkin-Straus-deficit line, and its complementary piece ===")
print("  claim: psi + (4/5) W <= 1/5 with margin exactly 0 on every C5[n]  (W = total edge weight)")
for k in (1, 2, 3, 4):
    n3, E3, part = blowup([k] * 5)
    x = [F(1, n3)] * n3
    ps = F(bip(n3, E3), n3 * n3)
    W = sum(x[u] * x[v] for (u, v) in E3)
    print(f"    C5[{k}]: psi = {ps}, W = {W}, psi + (4/5)W = {ps + F(4,5)*W}  "
          f"margin from 1/5 = {F(1,5) - ps - F(4,5)*W}")
n14, E14 = g6("M?AE@bH{AYN_LgBs?")
x14 = [F(1, n14)] * n14
ps14 = F(bip(n14, E14), n14 * n14)
W14 = sum(x14[u] * x14[v] for (u, v) in E14)
print(f"  complementary piece psi <= W/5 at the N=14 extremal graph: psi = {ps14}, "
      f"W/5 = {W14/5}  -> {'FALSE' if ps14 > W14/5 else 'holds'}")
print(f"     (equivalently bip = {bip(n14, E14)} > |E|/5 = {F(len(E14),5)})")
