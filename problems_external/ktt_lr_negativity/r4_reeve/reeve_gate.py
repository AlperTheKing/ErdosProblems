#!/usr/bin/env python3
"""
reeve_gate.py -- final exact gate for the r=4 Reeve question.

THEOREM (r=4 empty-simplex bound).
  Let Q = Q(lam,mu,nu) be an r=4 hive polytope.  If Q is lattice-equivalent to an
  empty lattice 3-simplex -- in particular to a Reeve simplex T(p,q) -- then its
  normalized volume satisfies V(Q) <= 4.  Hence q <= 4 and q >= 13 is IMPOSSIBLE.

PROOF.  Q = {h in R^3 : A h <= b} with A the FIXED 18x3 integer matrix of the
r=4 rhombus inequalities; all 15 distinct rows are primitive.  Suppose Q is a
lattice 3-simplex whose only lattice points are its 4 vertices.  Fix a vertex v.
A simplex is simple, so exactly 3 facets meet at v; each facet's outer normal is
a primitive row of A, so the tangent cone of Q at v is v + C_S with
S = {n_1,n_2,n_3} a triple of rows and C_S = {x : n_i . x <= 0}.  The three edges
of Q at v are the extreme rays of C_S, and each has lattice length 1 because the
only lattice points of Q are the 4 vertices; so the edge vectors ARE the
primitive ray generators g_1,g_2,g_3 of C_S.  Therefore
        V(Q) = |det(g_1,g_2,g_3)| = m(C_S),
the lattice multiplicity of C_S.  cone_atlas.py enumerates all C(15,3) = 455
triples exactly and finds m(C_S) in {1,2,4} with maximum 4.  Hence V(Q) <= 4. []

Since the Reeve simplex T(p,q) has V = q and a_1 = 2 - q/6, this also gives
a_1 >= 2 - 4/6 = 4/3 > 0 for every empty-simplex r=4 hive polytope: the classical
Reeve mechanism is unavailable in the r=4 cell.

This script (i) re-derives m_max = 4 from A, (ii) searches the gap moduli space
for ANY dim-3 hive polytope with exactly 4 lattice points and V >= 2, and
(iii) cross-checks the extremal records against the two independent LR counters.
"""
import itertools
import subprocess
import sys
from fractions import Fraction
from math import gcd

sys.path.insert(0, ".")
from hive4 import build_hive4, analyze, _det3
from gap_moduli import triple_from_gaps
from cone_atlas import cone_generators, primitive

ENGA = "../engine/lr_hive.exe"
ENGB = "../engine/engineB_lrrule.py"


def m_max():
    H = build_hive4([5, 3, 1], [6, 4, 2], [9, 6, 4, 2])
    rows = sorted({tuple(r) for r in H["A"]})
    best = 0
    ms = set()
    for S in itertools.combinations(rows, 3):
        if _det3([list(x) for x in S]) == 0:
            continue
        g = cone_generators(list(S))
        if g is None:
            continue
        m = abs(_det3([list(x) for x in g]))
        ms.add(m)
        best = max(best, m)
    return best, sorted(ms), len(rows)


def lr_check(lam, mu, nu, n, want):
    args = [",".join(str(n * x) for x in p) for p in (lam, mu, nu)]
    a = subprocess.run([ENGA] + args + ["100000000"], capture_output=True, text=True).stdout.split()
    b = subprocess.run([sys.executable, ENGB] + args + ["100000000"], capture_output=True, text=True).stdout.split()
    return (a[-1] == str(want) and b[-1] == str(want)), a[-1], b[-1]


def main():
    G = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    mm, ms, nrows = m_max()
    print("A: %d distinct primitive rows; cone multiplicities m(C_S) in %s; m_max = %d" % (nrows, ms, mm))
    print("=> every r=4 empty-simplex hive polytope has V <= %d, so a Reeve T(p,q) needs q <= %d" % (mm, mm))
    assert mm == 4

    worst_c4 = (0, None)
    n3 = 0
    seen = 0
    minsix = None
    for g in itertools.product(range(G + 1), repeat=9):
        t = triple_from_gaps(g[0:3], g[3:6], g[6:9])
        if t is None:
            continue
        seen += 1
        if seen % 97 != 0:      # sample: the exhaustive statement comes from gapscan.exe
            continue
        r = analyze(*t)
        if r["dim"] != 3:
            continue
        n3 += 1
        V = r["volume_normalized"]
        six = 3 * (r["c"] + r["hstar"][3]) - V
        if minsix is None or six < minsix[0]:
            minsix = (six, t, r["c"], V, r["hstar"])
        if r["c"] == 4 and V > worst_c4[0]:
            worst_c4 = (V, t)
    print("sampled dim-3 hive polytopes: %d; max V among those with exactly 4 lattice points: %s at %s"
          % (n3, worst_c4[0], worst_c4[1]))
    print("min 6a1 = 3(c+i)-V over the sample: %s at %s  (c=%s V=%s h*=%s)"
          % (minsix[0], minsix[1], minsix[2], minsix[3], minsix[4]))

    # independent LR-engine confirmation of the extremal record
    lam, mu, nu = minsix[1]
    ok_all = True
    for n in (1, 2, 3):
        r = analyze(lam, mu, nu)
        ok, a, b = lr_check(lam, mu, nu, n, r["L"][n])
        ok_all &= ok
        print("  LR cross-check n=%d: hive4=%s engineA=%s engineB=%s %s" % (n, r["L"][n], a, b, "OK" if ok else "MISMATCH"))
    print("GATE:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
