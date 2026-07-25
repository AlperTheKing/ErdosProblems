"""ROOT-AGENT GATE (Claude): re-verify round 8 family "transport/flow" from scratch.

The family proposed a NEW certificate scheme and then killed it.  I re-implement only the two
witnesses that do the killing, plus the claim that makes the scheme interesting, since those are the
acceptance path.  Nothing here is imported from the family's code.

THE SCHEME.  min <= weighted geometric mean, so for any distribution lambda over cuts
        psi(H,x) = min_S nu_S(x)  <=  prod_S nu_S(x)^{lambda_S},          nu_S(x) = q_S(x).
This is strictly tighter than the DEAD arithmetic-averaging family A6 (GM <= AM), and it is exactly
tight on the whole extremal family C5[n] by AM-GM, which is precisely where A6 fails at 1/20.

THE KILL.  Evaluate at x = uniform 1/5 on the vertices of an induced C5 called C.  Then
        nu_S(x) = k_S(C)/25,   k_S(C) = #{monochromatic edges of S lying inside C}.
Any bipartition of an odd cycle leaves an ODD number of monochromatic edges, so k_S(C) in {1,3,5}.
For the bound to be <= 1/25 at that point we need prod_S k_S(C)^{lambda_S} <= 1, i.e. k_S(C) = 1 for
every S in supp(lambda).  This must hold SIMULTANEOUSLY for every induced C5 of H.  Call such a cut
ADMISSIBLE.  If H has no admissible cut, no lambda exists and the scheme is dead on H.

Claims re-verified here:
  (a) Gamma_11 = And(4) has 33 induced C5s and ZERO admissible cuts among all 1024;
  (b) Grotzsch HAS admissible cuts, but at x = (0^5, (1/10)^5, 1/2) every one of them gives
      nu_S = 1/20 while psi = 0 exactly -- so the scheme fails there by 25% even where it exists;
  (c) "Conjecture T" (every vertex is incident to a monochromatic edge for at most 2/5 of the cuts)
      is false at uniform x on six named triangle-free graphs.
"""
from fractions import Fraction as F
from itertools import combinations


def gamma(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i + 1) % 5), (5 + i, (i + 4) % 5), (10, 5 + i)]
    return 11, E


def petersen():
    return 10, ([(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]
                + [(5 + i, 5 + (i + 2) % 5) for i in range(5)])


def g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    i = 1
    bits = []
    for x in b[i:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E, p = [], 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def adjacency(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v)
        A[v].add(u)
    return A


def induced_c5s(n, E):
    """EVERY induced 5-cycle, no cap.  In a triangle-free graph every C5 subgraph is induced."""
    A = adjacency(n, E)
    out = []
    for S in combinations(range(n), 5):
        Ss = set(S)
        if all(len(A[v] & Ss) == 2 for v in S):
            out.append(S)
    return out


def c5_edges(C, A):
    return [(u, v) for u, v in combinations(C, 2) if v in A[u]]


def admissible_cuts(n, E, verbose=""):
    A = adjacency(n, E)
    C5 = induced_c5s(n, E)
    good, parity_ok = [], True
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        ok = True
        for C in C5:
            k = sum(1 for (u, v) in c5_edges(C, A) if ((S >> u) & 1) == ((S >> v) & 1))
            if k % 2 == 0:
                parity_ok = False
            if k != 1:
                ok = False
                break
        if ok:
            good.append(S)
    if verbose:
        print(f"{verbose}: n={n} |E|={len(E)} induced C5s={len(C5)} cuts={1 << (n-1)}  "
              f"admissible cuts={len(good)}   (odd-parity law held everywhere: {parity_ok})")
    return good, C5, A


def psi_exact(n, E, x):
    best = None
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        s = sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
        if best is None or s < best:
            best = s
    return best


def nu(E, S, x):
    return sum(x[u] * x[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))


print("=== (a) does Gamma_11 = And(4) admit ANY cut usable by the scheme? ===")
n11, E11 = gamma(11)
good11, C511, _ = admissible_cuts(n11, E11, "Gamma_11")
print(f"    -> scheme is {'DEAD on Gamma_11' if not good11 else 'alive, admissible cuts exist'}")

print("\n=== (b) Grotzsch: admissible cuts exist, but do they certify? ===")
n_g, E_g = grotzsch()
good_g, C5_g, A_g = admissible_cuts(n_g, E_g, "Grotzsch")
x = [F(0)] * 5 + [F(1, 10)] * 5 + [F(1, 2)]
assert sum(x) == 1, sum(x)
ps = psi_exact(n_g, E_g, x)
vals = sorted({nu(E_g, S, x) for S in good_g})
print(f"    x = (0^5, (1/10)^5, 1/2): psi = {ps}   nu over the admissible cuts = {vals}")
if vals and all(v > F(1, 25) for v in vals):
    print(f"    -> every admissible cut gives nu >= {min(vals)} > 1/25 while psi = {ps}: "
          f"scheme FAILS by {float(min(vals) * 25):.2f}x")
print(f"    support of x induces a bipartite subgraph (hence psi = 0): {ps == 0}")

print("\n=== (c) Conjecture T at uniform x: fraction of cuts where a vertex is on a mono edge ===")
tests = [("Wagner=And(3)", gamma(8)), ("Petersen", petersen()), ("Grotzsch", grotzsch()),
         ("And(4)=Gamma_11", gamma(11)), ("M?AE@bH{AYN_LgBs?", g6("M?AE@bH{AYN_LgBs?"))]
for name, (n, E) in tests:
    A = adjacency(n, E)
    worst = F(0)
    tot = 1 << (n - 1)
    for v in range(n):
        c = 0
        for m in range(tot):
            S = (m << 1) | 1
            if any(((S >> v) & 1) == ((S >> w) & 1) for w in A[v]):
                c += 1
        worst = max(worst, F(c, tot))
    print(f"  {name:20s} max over vertices = {worst} = {float(worst):.4f}  "
          f"{'EXCEEDS 2/5' if worst > F(2, 5) else 'within 2/5'}")

print("\n=== (d) bip <= |E|/5 on the N=14 extremal graph ===")
n14, E14 = g6("M?AE@bH{AYN_LgBs?")
t14 = psi_exact(n14, E14, [F(1)] * n14)
print(f"  |E| = {len(E14)}, bip = {t14}, |E|/5 = {F(len(E14), 5)}  -> "
      f"bip <= |E|/5 is {'FALSE' if t14 > F(len(E14), 5) else 'not contradicted'}")
