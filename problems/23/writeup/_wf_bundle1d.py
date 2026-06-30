"""EXACT-gate BUNDLE-SBC: terminal 1D inequality of the GPT-Pro architecture.

For odd ell in {5,7,9,11,13} and positive integer layer sizes n_0..n_{ell-1},
positive integer m with cyclic max-cut product constraints m <= n_i*n_{i+1} for
every i (mod ell), let n = sum_i n_i and c = sum_{i=1}^{ell-2} 1/n_i (Fraction).

Gate EXACTLY:
   BUNDLE-SBC:  n_0 + n_{ell-1} + m*(1 + c)  <=  n + n^2/25.

EXACT integer comparison (no floats, no rounding). The rational inequality is
cleared to integers by multiplying through by  25 * P  where
P = prod_{i=1}^{ell-2} n_i  is the exact common denominator of (1+c):
   25*P*(n_0+n_{ell-1}) + 25*m*( P + sum_{i=1}^{ell-2} P/n_i )  <=  P*(25*n + n^2).
Every quantity is an integer; P/n_i is integer since n_i | P.

Reduction (logically exact, not a heuristic):
  For a FIXED tuple, LHS is strictly increasing in m since (1+c) > 0, and RHS is
  independent of m. Hence over valid m in 1..cap (cap = min_i n_i*n_{i+1}):
    the maximum LHS, hence any violation and any equality, occurs ONLY at m=cap;
    if the gate holds at m=cap it holds for every valid m.
  Evaluating m=cap per tuple is EQUIVALENT to evaluating all m for the verdict.
  We still count the true total number of (tuple, m) pairs for `tested`.
  An independent Fraction brute-force on a small slice confirms the reduction.
"""
from fractions import Fraction as F
from itertools import product
from collections import Counter

RANGES = {5: range(1, 8), 7: range(1, 8), 9: range(1, 8),
          11: range(1, 5), 13: range(1, 5)}

def cap_m(ell, ns):
    return min(ns[i] * ns[(i+1) % ell] for i in range(ell))

def lhs_rhs_frac(ell, ns, m):
    """Reference rational LHS, RHS (used for tight-case display + sanity)."""
    n = sum(ns)
    c = sum(F(1, ns[i]) for i in range(1, ell-1))
    LHS = F(ns[0]) + F(ns[ell-1]) + F(m) * (F(1) + c)
    RHS = F(n) + F(n*n, 25)
    return LHS, RHS

def int_terms(ell, ns):
    """Return (P, base_int, slope_int, rhs_int) of the cleared integer inequality
       LHS_int(m) = base_int + m*slope_int ;  gate holds  iff  LHS_int(m) <= rhs_int.
       (everything multiplied by 25*P)."""
    n = sum(ns)
    P = 1
    for i in range(1, ell-1):
        P *= ns[i]
    sum_PoverNi = 0
    for i in range(1, ell-1):
        sum_PoverNi += P // ns[i]           # exact, ns[i] | P
    base_int = 25 * P * (ns[0] + ns[ell-1])
    slope_int = 25 * (P + sum_PoverNi)      # = 25*P*(1+c)
    rhs_int = P * (25 * n + n * n)
    return P, base_int, slope_int, rhs_int

def run():
    tested = 0
    tuples_seen = 0
    violations = 0
    first_violation = None
    tight = []
    for ell in (5, 7, 9, 11, 13):
        rng = list(RANGES[ell])
        for ns in product(rng, repeat=ell):
            tuples_seen += 1
            cap = cap_m(ell, ns)            # >= 1 always
            tested += cap                    # m = 1..cap all valid
            P, base_int, slope_int, rhs_int = int_terms(ell, ns)
            lhs_cap = base_int + cap * slope_int
            if lhs_cap > rhs_int:
                # strictly increasing -> count violating m exactly:
                # smallest m0 with base+ m0*slope > rhs  => m0 = floor((rhs-base)/slope)+1
                num = rhs_int - base_int
                m0 = num // slope_int + 1     # floor div then +1 (num,slope>0)
                if m0 < 1:
                    m0 = 1
                nviol = cap - m0 + 1
                if nviol < 0:
                    nviol = 0
                violations += nviol
                if first_violation is None:
                    L, R = lhs_rhs_frac(ell, ns, cap)
                    first_violation = (ell, ns, cap, str(L), str(R))
            elif lhs_cap == rhs_int:
                tight.append((ell, ns, cap))
    return tested, tuples_seen, violations, first_violation, tight

if __name__ == "__main__":
    tested, tuples_seen, violations, first_violation, tight = run()
    print("tuples_seen =", tuples_seen)
    print("tested      =", tested, " (true total (tuple,m) pairs)")
    print("violations  =", violations)
    print("holds       =", violations == 0)
    print("first_viol  =", first_violation)
    print("n_tight     =", len(tight))
    by_ell = Counter(t[0] for t in tight)
    print("tight_by_ell=", dict(by_ell))
    balanced_only = True
    nonbal = []
    for (ell, ns, m) in tight:
        bal = (ell == 5) and (len(set(ns)) == 1) and (m == ns[0]*ns[0])
        if not bal:
            balanced_only = False
            if len(nonbal) < 30:
                nonbal.append((ell, ns, m))
    print("ALL tight are ell=5 balanced (n_i equal, m=n0^2):", balanced_only)
    if nonbal:
        print("NON-balanced tight examples:", nonbal)
    print("tight examples (first 20):")
    for t in tight[:20]:
        print("   ", t)
    print("--- spot check ell=5 balanced k=1..7, m=k^2 ---")
    for k in range(1, 8):
        ns = (k,)*5
        L, R = lhs_rhs_frac(5, ns, k*k)
        print(f"   k={k}: m={k*k}  LHS={L}  RHS={R}  equal={L==R}")
    # independent reduction sanity: brute all m via Fraction on ell=5 rng 1..4
    print("--- reduction sanity (Fraction brute all m vs cap) ell=5 rng 1..4 ---")
    bad = 0
    for ns in product(range(1, 5), repeat=5):
        cap = cap_m(5, ns)
        worst = None
        for m in range(1, cap+1):
            L, R = lhs_rhs_frac(5, ns, m)
            d = L - R
            if worst is None or d > worst[0]:
                worst = (d, m)
        if worst[1] != cap:
            bad += 1
    print("   tuples where brute worst-m != cap:", bad, "(expect 0)")
    # also cross-check integer-clearing equals Fraction verdict on the same slice
    print("--- integer vs Fraction verdict cross-check ell=5 rng 1..4, all m ---")
    mism = 0
    for ns in product(range(1, 5), repeat=5):
        P, b, s, r = int_terms(5, ns)
        for m in range(1, cap_m(5, ns)+1):
            iv = (b + m*s <= r)
            L, R = lhs_rhs_frac(5, ns, m)
            fv = (L <= R)
            if iv != fv:
                mism += 1
    print("   integer-vs-Fraction mismatches:", mism, "(expect 0)")
