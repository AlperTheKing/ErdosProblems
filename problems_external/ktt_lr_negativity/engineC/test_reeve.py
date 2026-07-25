"""Independent correctness test of engineC on NON-hive polytopes with known
Ehrhart polynomials: the Reeve tetrahedra T_q = conv{0,e1,e2,(1,1,q)} and a
rational simplex."""
import sys
from fractions import Fraction
sys.path.insert(0, __file__.rsplit("\\", 1)[0])
from ehr import ehrhart_AB, lagrange_coeffs  # noqa

import itertools


def hrep_from_verts(V):
    """Exact H-rep of conv(V) via cdd."""
    import cdd.gmp as cg
    rows = [[Fraction(1)] + [Fraction(x) for x in v] for v in V]
    mat = cg.matrix_from_array(rows, rep_type=cg.RepType.GENERATOR)
    poly = cg.polyhedron_from_matrix(mat)
    ineq = cg.copy_inequalities(poly)
    A, b = [], []
    for row in ineq.array:
        # row: b0 + a.x >= 0   ->   -a.x <= b0
        b.append(Fraction(row[0]))
        A.append([-Fraction(x) for x in row[1:]])
    return A, b


def scale_int(A, b):
    A2, b2 = [], []
    for row, rb in zip(A, b):
        L = rb.denominator
        for x in row:
            L = L * x.denominator // __import__("math").gcd(L, x.denominator)
        A2.append([int(x * L) for x in row])
        b2.append(int(rb * L))
    return A2, b2


fails = 0
for q in [1, 2, 3, 5, 12, 13, 20, 40]:
    V = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, q)]
    A, b = scale_int(*hrep_from_verts(V))
    r = ehrhart_AB(A, b, 3)
    # known: h* = (1,0,q-1,0); P(n) = (q/6)n^3 + n^2 + (2 - q/6) n + 1
    exp_h = [1, 0, q - 1, 0]
    exp_c = [Fraction(1), Fraction(2) - Fraction(q, 6), Fraction(1), Fraction(q, 6)]
    got_c = [Fraction(x) for x in r["coeffs"]]
    ok = (r["hstar"] == exp_h) and (got_c == exp_c)
    print("Reeve q=%-3d %s hstar=%s coeffs=%s" % (q, "OK " if ok else "FAIL", r["hstar"], r["coeffs"]))
    fails += 0 if ok else 1

# rational (non-lattice) simplex: conv{0, (1/2,0), (0,1/3)} in R^2
V = [(Fraction(0), Fraction(0)), (Fraction(1, 2), Fraction(0)), (Fraction(0), Fraction(1, 3))]
A, b = scale_int(*hrep_from_verts(V))
r = ehrhart_AB(A, b, 2)
print("rational triangle:", r["status"], r["P"][:6], r["coeffs"])
# brute force
for n in range(6):
    cnt = 0
    for x in range(0, 3 * n + 2):
        for y in range(0, 3 * n + 2):
            if x >= 0 and y >= 0 and Fraction(x, 1) * 2 + Fraction(y, 1) * 3 <= n:
                cnt += 1
    if cnt != r["P"][n]:
        print("  MISMATCH n=%d brute=%d engine=%d" % (n, cnt, r["P"][n]))
        fails += 1

# a 4-dim non-simplex lattice polytope: cube [0,1]^4 -> P(n) = (n+1)^4
V = list(itertools.product([0, 1], repeat=4))
A, b = scale_int(*hrep_from_verts([tuple(Fraction(x) for x in v) for v in V]))
r = ehrhart_AB(A, b, 4)
exp = [(n + 1) ** 4 for n in range(len(r["P"]))]
print("cube4:", r["P"], "expected", exp, "OK" if r["P"] == exp else "FAIL")
fails += 0 if r["P"] == exp else 1

print("FAILS =", fails)
sys.exit(1 if fails else 0)
