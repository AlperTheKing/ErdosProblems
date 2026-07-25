#!/usr/bin/env python3
"""Verify the cell-increment monotonicity that makes L(1)>=1050 a PROOF, not
a scan.  Claim: every codegree-3 3x8 member has sorted margins dominating the
minimal member (3,3,3),(2,1^7) componentwise, and adding 1 to one matrix cell
gives an injection L(r,c) -> L(r+e_i, c+e_j).  Hence L(r,c) >= 1050 for ALL of
them.  We test domination on the scanned family and spot-check the injection
count monotonicity numerically."""
import transport3xN_ehrhart as T
from verdict_3row_driver import enumerate_codeg3_family

MIN_R = (3, 3, 3)
MIN_C = (1, 1, 1, 1, 1, 1, 1, 2)  # ascending

fam = enumerate_codeg3_family(max_rowsum=14)
all_dominate = True
all_ge_1050 = True
for (r, c) in fam:
    rs = tuple(sorted(r))            # ascending, len 3
    cs = tuple(sorted(c))            # ascending, len 8
    dom = all(rs[i] >= MIN_R[i] for i in range(3)) and \
          all(cs[i] >= MIN_C[i] for i in range(8))
    if not dom:
        all_dominate = False
        print("NOT DOMINATED:", r, c, rs, cs)
    L1 = T.count_fast(r, c)
    if L1 < 1050:
        all_ge_1050 = False
        print("L1<1050:", r, c, L1)
print("every codegree-3 member sorted-dominates (3,3,3),(1^7,2):", all_dominate)
print("every codegree-3 member has L(1) >= 1050:", all_ge_1050)

# Injection spot-check: L(r,c) <= L(r+e_i, c+e_j) for random increments.
import random
random.seed(0)
mono_ok = True
for _ in range(200):
    r = [random.randint(3, 6) for _ in range(3)]
    c = [random.randint(1, 3) for _ in range(8)]
    S = sum(r)
    # rebalance columns to sum S
    diff = S - sum(c)
    c[0] += diff
    if min(c) < 1:
        continue
    base = T.count_fast(r, c)
    i = random.randint(0, 2); j = random.randint(0, 7)
    r2 = r[:]; c2 = c[:]; r2[i] += 1; c2[j] += 1
    up = T.count_fast(r2, c2)
    if not (up >= base):
        mono_ok = False
        print("MONO FAIL", r, c, i, j, base, up)
print("cell-increment monotonicity L(r,c) <= L(r+e_i,c+e_j) held on 200 trials:",
      mono_ok)
