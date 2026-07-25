#!/usr/bin/env python3
"""
DECISIVE TEST FOR (F4): is the hive normal configuration a subset of a
type-A root system {e_i - e_j} in SOME basis (i.e. is the hive polytope an
alcoved polytope of type A after a linear change of coordinates)?

BASIS-INDEPENDENT CRITERION.  {e_i - e_j : ij in E} is the vector
configuration of a GRAPHIC matroid; graphic => regular => the configuration is
UNIMODULAR: every nonzero maximal (D x D) minor has the same absolute value.
Unimodularity in this sense is invariant under GL_D(Q) (a change of basis T
multiplies every maximal minor by det T) and under rescaling individual
vectors is NOT allowed, but our normals are primitive integer vectors and a
root-system realization would make them primitive too, so scaling is fixed up
to a global unit.  Hence:

   if the set of |maximal minors| of the hive normals takes >= 2 distinct
   nonzero values, the configuration is NOT unimodular, hence NOT (a subset
   of) a type-A root system in any basis, hence the hive polytope is NOT an
   alcoved polytope of type A.

Sanity control: run the same test on the 12 "alcoved" hive normals (must be
unimodular) and on a genuine type-A root system.
"""
import itertools, sys
from fractions import Fraction
from collections import Counter
sys.setrecursionlimit(10000)

sys.path.insert(0, ".")
from hive_normals import rows_for_r, classify

def det(M):
    """exact integer determinant by fraction-free Gaussian elimination"""
    M = [list(map(Fraction, row)) for row in M]
    n = len(M); s = 1; d = Fraction(1)
    for c in range(n):
        p = None
        for i in range(c, n):
            if M[i][c] != 0: p = i; break
        if p is None: return 0
        if p != c: M[c], M[p] = M[p], M[c]; s = -s
        d *= M[c][c]
        for i in range(c+1, n):
            f = M[i][c] / M[c][c]
            if f: M[i] = [M[i][k]-f*M[c][k] for k in range(n)]
    v = s*d
    assert v.denominator == 1
    return int(v)

def minor_spectrum(rows, D, cap=None):
    vals = Counter()
    n = 0
    for S in itertools.combinations(range(len(rows)), D):
        v = abs(det([rows[i] for i in S]))
        if v: vals[v] += 1
        n += 1
        if cap and n >= cap: break
    return vals

for r in (4, 5):
    I, rws = rows_for_r(r)
    D = len(I)
    uniq = sorted(set(rws))
    alcoved = [v for v in uniq if classify(v) in ("e", "e-e")]
    print("=== r=%d  D=%d ===" % (r, D))
    if r == 4:
        print("  ALL %d normals   |minors| spectrum:" % len(uniq),
              dict(sorted(minor_spectrum(uniq, D).items())))
        print("  ALCOVED %d only  |minors| spectrum:" % len(alcoved),
              dict(sorted(minor_spectrum(alcoved, D).items())))
    else:
        # D=6, C(27,6)=296010 -- fine
        print("  ALL %d normals   |minors| spectrum:" % len(uniq),
              dict(sorted(minor_spectrum(uniq, D).items())))
        print("  ALCOVED %d only  |minors| spectrum:" % len(alcoved),
              dict(sorted(minor_spectrum(alcoved, D).items())))

# control: genuine A_3 root system in R^3 (x_0 = 0 convention)
roots = []
for i in range(3):
    e = [0,0,0]; e[i] = 1
    roots.append(tuple(e)); roots.append(tuple(-x for x in e))
for i, j in itertools.combinations(range(3), 2):
    e = [0,0,0]; e[i] = 1; e[j] = -1
    roots.append(tuple(e)); roots.append(tuple(-x for x in e))
print("=== CONTROL: A_3 root system, %d roots ===" % len(roots),
      dict(sorted(minor_spectrum(roots, 3).items())))
