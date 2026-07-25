#!/usr/bin/env python3
"""
(b) What exactly are the hive facet normals for general r?

Build the size-r hive polytope in the D=(r-1)(r-2)/2 INTERIOR coordinates,
using EXACTLY the boundary convention of hive4.py / engine A, and classify the
resulting distinct primitive normal rows:

  ALCOVED (type-A root directions in the chosen interior basis):
      +- e_i           (support 1)
      +- (e_i - e_j)   (support 2, opposite signs)
  NON-ALCOVED ("odd"): everything else.

Rows are recorded up to nothing (we keep both n and -n if both occur), and we
report which of them are ATTAINED as genuine facets on real hive polytopes.
"""
import itertools, sys
from fractions import Fraction

def interior(r):
    return [(x, y) for x in range(1, r) for y in range(1, r) if x + y <= r - 1]

def rows_for_r(r):
    """Return (coords, rows) where rows are the coefficient vectors (as tuples)
    of all rhombus inequalities written as  row . h <= const  in the interior
    coordinates.  Rows that are identically zero (pure boundary) are dropped."""
    I = interior(r)
    idx = {v: i for i, v in enumerate(I)}
    D = len(I)
    rows = []
    def add(plus, minus):
        co = [0]*D
        for v in plus:
            if v in idx: co[idx[v]] -= 1
        for v in minus:
            if v in idx: co[idx[v]] += 1
        if any(co):
            rows.append(tuple(co))
    for x in range(r+1):
        for y in range(r+1):
            if x + y <= r-2:
                add([(x+1,y),(x,y+1)], [(x,y),(x+1,y+1)])
            if y >= 1 and x + y <= r-1:
                add([(x,y),(x+1,y)], [(x,y+1),(x+1,y-1)])
            if x >= 1 and x + y <= r-1:
                add([(x,y),(x,y+1)], [(x+1,y),(x-1,y+1)])
    return I, rows

def classify(v):
    s = [i for i,c in enumerate(v) if c != 0]
    vals = sorted(v[i] for i in s)
    if len(s) == 1 and abs(v[s[0]]) == 1:
        return "e"          # +- e_i
    if len(s) == 2 and vals == [-1,1]:
        return "e-e"        # +- (e_i - e_j)
    if len(s) == 2:
        return "e+e"        # +-(e_i + e_j)   NOT alcoved
    return "odd%d" % len(s)

for r in range(4, 9):
    I, rows = rows_for_r(r)
    D = len(I)
    uniq = sorted(set(rows))
    from collections import Counter
    cnt = Counter(classify(v) for v in uniq)
    alc = cnt.get("e",0) + cnt.get("e-e",0)
    print("r=%d  D=%d  #ineqs=%d  #distinct normals=%d   alcoved=%d (%d e, %d e-e)  non-alcoved=%d  %s"
          % (r, D, len(rows), len(uniq), alc, cnt.get("e",0), cnt.get("e-e",0),
             len(uniq)-alc, dict(sorted(cnt.items()))))
    if r <= 5:
        for v in uniq:
            print("     ", v, classify(v))
