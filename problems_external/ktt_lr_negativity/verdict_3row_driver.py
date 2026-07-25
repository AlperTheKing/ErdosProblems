#!/usr/bin/env python3
"""Driver: decisive numbers for the three-row (3xN) transfer verdict.

Uses transport3xN_ehrhart.py (naive+fast counters, exact interpolation).
Adds a THIRD fully-independent brute-force counter and an independent
interior-point (codegree) count for cross-validation.
"""
from fractions import Fraction
from itertools import product
from math import comb
import transport3xN_ehrhart as T


# ---- third independent counter: enumerate columns as compositions -----------
def count_indep(rowsums, colsums):
    """Independent DP: state = tuple of partial row sums (len 3)."""
    R = tuple(rowsums)
    if len(R) != 3 or sum(R) != sum(colsums) or min(R) < 0 or min(colsums, default=0) < 0:
        return 0
    from collections import defaultdict
    states = {(0, 0, 0): 1}
    for cj in colsums:
        nxt = defaultdict(int)
        # all (a,b,c) >=0 with a+b+c = cj
        for a in range(cj + 1):
            for b in range(cj - a + 1):
                cc = cj - a - b
                for (s0, s1, s2), w in states.items():
                    n0, n1, n2 = s0 + a, s1 + b, s2 + cc
                    if n0 <= R[0] and n1 <= R[1] and n2 <= R[2]:
                        nxt[(n0, n1, n2)] += w
        states = nxt
    return states.get(R, 0)


def interior_indep(r, c):
    """# strictly-positive int matrices with margins r,c via all-ones subtract."""
    N = len(c)
    rr = [x - N for x in r]
    cc = [x - 3 for x in c]
    if any(x < 0 for x in rr) or any(x < 0 for x in cc):
        return 0
    return count_indep(rr, cc)


def codegree_via_interior(r, c, tmax=12):
    for t in range(1, tmax + 1):
        if interior_indep([t * x for x in r], [t * x for x in c]) > 0:
            return t, [interior_indep([s * x for x in r], [s * x for x in c])
                       for s in range(t + 1)]
    return None, []


# ---- generate codegree-3 members --------------------------------------------
def compositions_positive(total, parts):
    """All positive integer tuples of length `parts` summing to total (unordered
    reps as sorted descending; permutations give same Ehrhart)."""
    def rec(remaining, slots, mn):
        if slots == 1:
            if remaining >= mn:
                yield (remaining,)
            return
        for first in range(mn, remaining - (slots - 1) * mn + 1):
            for rest in rec(remaining - first, slots - 1, mn):
                yield (first,) + rest
    # partitions of total into exactly `parts` positive parts, descending
    seen = set()
    for comp in rec(total, parts, 1):
        t = tuple(sorted(comp, reverse=True))
        if t not in seen:
            seen.add(t)
            yield t


def enumerate_codeg3_family(max_rowsum=15):
    """Codegree-3 3x8 members: (A) min_r=3 any c; (B) min_r>=4 and min_c=1.
    Row margins r: 3 positive parts summing S. Column margins c: 8 positive
    parts summing S. Codegree=3 <=> [min r=3] OR [min r>=4 AND min c=1]."""
    members = []
    for S in range(9, max_rowsum + 1):  # min total is 3+3+3=9
        rows = list(compositions_positive(S, 3))
        cols = list(compositions_positive(S, 8))
        for r in rows:
            minr = min(r)
            if minr < 3:
                continue
            for c in cols:
                minc = min(c)
                cg = max(-(-8 // minr), -(-3 // minc))  # ceil divisions
                if cg == 3:
                    members.append((r, c))
    return members


if __name__ == "__main__":
    print("### 1. MINIMAL MEMBER r=(3,3,3) c=(2,1^7) ###")
    r = (3, 3, 3); c = (2, 1, 1, 1, 1, 1, 1, 1)
    # three-way L(1) cross-check
    a = T.count_naive(r, c); b = T.count_fast(r, c); d = count_indep(r, c)
    print(f"L(1): naive={a} fast={b} indep={d} allagree={a==b==d}")
    res = T.analyze(r, c)
    print("dim =", res["dim"])
    print("Ehrhart L(t) t=0..16 =", res["vals"])
    print("a1 (linear coeff) =", res["linear_coeff"], "=", float(res["linear_coeff"]))
    print("min coeff over all a_k =", res["min_coeff"],
          " any_negative=", res["any_negative"])
    cg, intseq = codegree_via_interior(r, c)
    print("codegree (independent interior) =", cg, " interior t=0..cg =", intseq)
    print("h* =", res["hstar"])

    print("\n### 2. CODEGREE-3 3x8 FAMILY SCAN (min linear coeff, min L1) ###")
    fam = enumerate_codeg3_family(max_rowsum=14)
    print("family members scanned (up to rowsum 14):", len(fam))
    min_lin = None; min_lin_at = None
    min_L1 = None; min_L1_at = None
    any_neg_family = False; neg_at = None
    for (r, c) in fam:
        res = T.analyze(r, c)
        if res is None:
            print("  INTERP FAIL", r, c); continue
        lin = res["linear_coeff"]; L1 = res["L1"]
        if min_lin is None or lin < min_lin:
            min_lin = lin; min_lin_at = (r, c)
        if min_L1 is None or L1 < min_L1:
            min_L1 = L1; min_L1_at = (r, c)
        if res["any_negative"]:
            any_neg_family = True; neg_at = (r, c, res["coeffs"])
    print("MIN linear coeff over family =", min_lin, "=", float(min_lin),
          "at", min_lin_at)
    print("MIN L(1) over family =", min_L1, "at", min_L1_at)
    print("ANY member with a negative Ehrhart coeff?", any_neg_family, neg_at)

    print("\n### 3. FACET COUNT SANITY (affine invariant) ###")
    print("O(P_{7,7}) facets = 63; 3x8 transportation max facets = 3*8 = 24")

    print("\n### 4. TARGET COMPARISON ###")
    print("O(P_{7,7}): L(1)=255, a1=-3041/1430=", float(Fraction(-3041,1430)),
          ", codegree 3, 63 facets")
    print("min 3x8 codegree-3 transportation: L(1)=", min_L1,
          ", a1=", min_lin, ">0")
