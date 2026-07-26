"""ROOT-AGENT GATE (Claude): Codex's exact induced-C5 face, plus the gap I flagged in TICK-139.

Codex's face derivation, which I checked by hand and confirm: with degree-4 multipliers and target
degree 6, normalization gives sum_S nu_S = 25 L^4, so at x = 1_C (L = 5) we get
sum_S nu_S(1_C) = 25 * 5^4 = 5^6, hence

        T(1_C) = 5^6 - sum_S nu_S(1_C) k_S(C) = - sum_S nu_S(1_C) (k_S(C) - 1).

Odd-cycle parity puts k_S(C) in {1,3,5}, so every term is >= 0 while T(1_C) >= 0 by the SOS
condition; therefore T(1_C) = 0 term by term, and k_S(C) > 1 forces nu_S(1_C) = 0, which by
coefficientwise nonnegativity kills every multiplier coefficient supported inside C. Correct.

CHECKED HERE:
 (1) the k_S(C) distribution over all 56 x 33 = 1848 (cut, pentagon) pairs -- Codex reports
     {1: 814, 3: 737, 5: 297}; my earlier gate independently found 1034 pairs with k > 1, and
     737 + 297 = 1034, so this is a genuine cross-check rather than a restatement.
 (2) THE GAP I RAISED WITH CODEX. Its face imposes tightness only at the 33 pentagon INDICATORS.
     But the equality set on Gamma_11 is strictly larger: a = (2,1,1,0,2,0,1,1,2,0,0), support of
     size 7, has psi = 1/25 EXACTLY (R3-C32). If ARCBOUND is ALSO tight there, then T(a) = 0 too and
     that point imposes FURTHER face conditions which Codex's construction is currently missing --
     which would matter before it solves again.
"""
from fractions import Fraction as F
from itertools import combinations


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def arc_cuts(n):
    seen = {}
    for s in range(n):
        for L in range(1, n):
            S = frozenset((s + t) % n for t in range(L))
            key = min(tuple(sorted(S)), tuple(sorted(set(range(n)) - S)))
            seen[key] = S
    return [frozenset()] + list(seen.values())


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)
arcs = arc_cuts(n)
pent = [T for T in combinations(range(n), 5) if all(len(A[v] & set(T)) == 2 for v in T)]

# ---- (1) the k distribution
dist = {}
for S in arcs:
    for U in pent:
        Us = set(U)
        k = sum(1 for (u, v) in E if u in Us and v in Us and ((u in S) == (v in S)))
        dist[k] = dist.get(k, 0) + 1
print(f"(1) k_S(C) distribution over {len(arcs)}x{len(pent)} = {len(arcs)*len(pent)} pairs: "
      f"{dict(sorted(dist.items()))}")
codex = {1: 814, 3: 737, 5: 297}
print(f"    Codex: {codex}  ->  {'MATCH' if dict(sorted(dist.items())) == codex else 'MISMATCH'}")
print(f"    pairs with k > 1: {sum(v for k, v in dist.items() if k > 1)} "
      f"(my earlier gate found 1034)")
print(f"    parity law holds (all k odd): {all(k % 2 == 1 for k in dist)}")

# ---- (2) does the blow-up equality point impose FURTHER tightness?
a = [2, 1, 1, 0, 2, 0, 1, 1, 2, 0, 0]
q = sum(a)
print(f"\n(2) blow-up equality witness a = {a}, sum = {q}, target (sum)^2/25 = {F(q*q,25)}")
psi = None
for m in range(1 << (n - 1)):
    S = (m << 1) | 1
    s = sum(a[u] * a[v] for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1))
    if psi is None or s < psi:
        psi = s
arcvals = []
for S in arcs:
    s = sum(a[u] * a[v] for (u, v) in E if (u in S) == (v in S))
    arcvals.append(s)
arcmin = min(arcvals)
print(f"    psi (all 1024 cuts) = {psi} = {F(psi, q*q)};  ARCBOUND (56 arc cuts) = {arcmin} = "
      f"{F(arcmin, q*q)}")
print(f"    target = {F(q*q,25)} = {q*q/25:.4f}")
tight_arc = arcmin * 25 == q * q
print(f"    is ARCBOUND TIGHT at the target here: {tight_arc}")
if tight_arc:
    nt = sum(1 for s in arcvals if s == arcmin)
    print(f"    -> T(a) = 0 as well, so this point imposes FURTHER face conditions:")
    print(f"       {nt} of the 56 arc cuts are tight at it, and every non-tight cut S has")
    print(f"       nu_S(a) = 0 forced, exactly as at the pentagon indicators.")
    print(f"    This point is NOT a pentagon indicator: its support has size "
          f"{sum(1 for t in a if t > 0)}, and it is not 0/1.")
    print(f"    CONSEQUENCE FOR CODEX: its face, built only from the 33 indicators 1_C, is")
    print(f"    INCOMPLETE. Imposing it and solving may still fail for this reason.")
else:
    print(f"    -> ARCBOUND is NOT tight here ({arcmin} vs {q*q/25:.4f}), so the arc certificate")
    print(f"       has slack at this point and it imposes NO additional face condition.")
    print(f"    Codex's face, built from the 33 pentagon indicators, is not missing this point.")
