#!/usr/bin/env python3
"""Exact witness for a local-strip / intrinsic-lattice obstruction.

We realize a full-dimensional size-four hive with exactly the same active
hypotenuse-strip rows as the determinant-four vertex of the standard
determinant-two tangent-cone example, but without its remote active rows.
The resulting closed normal cone is unimodular.  Floating point only proposes
the boundary and points; every displayed witness is replayed over Fraction.
"""

from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "r5_rational"))
from hiveR import boundary_map, fixed_A, rows_symbolic  # noqa: E402


RANK = 4
# These are precisely the active rows in the deleted hypotenuse unit strip at
# the determinant-four vertex.  Rows 3/12 and 13/15 are duplicate directions
# but distinct rhombi.
ACTIVE = (3, 8, 12, 13, 15)


def dot(a, b):
    return sum(Fraction(x) * Fraction(y) for x, y in zip(a, b))


def solve():
    A, D, tags = fixed_A(RANK)
    # variables: p[12], vertex x[3], strict interior z[3], epsilon
    n = 19
    inequalities = []

    # Three weakly decreasing nonnegative boundary sequences.
    for offset in (0, 4, 8):
        for i in range(3):
            row = [0.0] * n
            row[offset + i + 1] = 1.0
            row[offset + i] = -1.0
            inequalities.append(row)
        row = [0.0] * n
        row[offset + 3] = -1.0
        inequalities.append(row)

    # Pure-boundary hive inequalities, const(p) <= 0.
    B = boundary_map(RANK)
    for co, bc, _ in rows_symbolic(RANK):
        if any(co):
            continue
        row = [0.0] * n
        for vertex, coefficient in bc.items():
            for i, value in enumerate(B[vertex]):
                row[i] += coefficient * value
        inequalities.append(row)

    # The proposed vertex: active equalities, every other row strict.
    equalities = []
    for i in range(len(A)):
        if i not in ACTIVE:
            row = [float(-v) for v in D[i]] + [float(v) for v in A[i]]
            row += [0.0] * 3 + [1.0]
            inequalities.append(row)

    # A strict point certifies full dimension.
    for i in range(len(A)):
        row = [float(-v) for v in D[i]] + [0.0] * 3
        row += [float(v) for v in A[i]] + [1.0]
        inequalities.append(row)

    # Weight equality and a scale normalization.
    equalities.append([1.0] * 4 + [1.0] * 4 + [-1.0] * 4 + [0.0] * 7)
    equalities.append([0.0] * 8 + [1.0] * 4 + [0.0] * 7)
    for i in ACTIVE:
        row = [float(-v) for v in D[i]] + [float(v) for v in A[i]]
        row += [0.0] * 4
        equalities.append(row)

    objective = [0.0] * 18 + [-1.0]
    result = linprog(
        objective,
        A_ub=np.asarray(inequalities),
        b_ub=np.zeros(len(inequalities)),
        A_eq=np.asarray(equalities),
        b_eq=np.asarray([0.0, 1.0] + [0.0] * len(ACTIVE)),
        bounds=[(None, None)] * 18 + [(0.0, None)],
        method="highs",
    )
    if not result.success or result.x[-1] <= 1e-9:
        raise RuntimeError(result.message)

    witness = tuple(Fraction(str(float(v))).limit_denominator(1_000_000)
                    for v in result.x)
    assert all(dot(row, witness) <= 0 for row in inequalities)
    rhs = (Fraction(0), Fraction(1)) + (Fraction(0),) * len(ACTIVE)
    assert all(dot(row, witness) == value for row, value in zip(equalities, rhs))
    return A, D, tags, witness


def primitive(v):
    divisor = 0
    for value in v:
        divisor = gcd(divisor, abs(value))
    return tuple(value // divisor for value in v)


def det3(rows):
    (a, b, c), (d, e, f), (g, h, i) = rows
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def main():
    A, D, tags, witness = solve()
    p, x, z, epsilon = witness[:12], witness[12:15], witness[15:18], witness[18]

    denominator = 1
    for value in p + x + z:
        denominator = lcm(denominator, value.denominator)
    p_int = tuple(int(value * denominator) for value in p)
    x_int = tuple(int(value * denominator) for value in x)
    z_int = tuple(int(value * denominator) for value in z)

    slacks_x = tuple(dot(D[i], p_int) - dot(A[i], x_int)
                     for i in range(len(A)))
    slacks_z = tuple(dot(D[i], p_int) - dot(A[i], z_int)
                     for i in range(len(A)))
    active = tuple(i for i, value in enumerate(slacks_x) if value == 0)
    assert active == ACTIVE
    assert min(value for i, value in enumerate(slacks_x) if i not in ACTIVE) > 0
    assert min(slacks_z) > 0

    rays = []
    for i in ACTIVE:
        ray = primitive(tuple(A[i]))
        if ray not in rays:
            rays.append(ray)
    assert len(rays) == 3
    full_index = abs(det3(rays))
    facet_index = gcd(*(abs(v) for v in cross(rays[0], rays[1])))
    quotient_multiplicity = full_index // facet_index
    assert (full_index, facet_index, quotient_multiplicity) == (1, 1, 1)

    print("PASS")
    print(f"active_rows={ACTIVE}")
    print(f"active_tags={tuple(tags[i] for i in ACTIVE)}")
    print(f"scale={denominator}")
    print(f"lambda={p_int[:4]}")
    print(f"mu={p_int[4:8]}")
    print(f"nu={p_int[8:12]}")
    print(f"vertex={x_int}")
    print(f"strict_point={z_int}")
    print(f"minimum_strict_slack={min(slacks_z)}")
    print(f"primitive_extreme_rays={tuple(rays)}")
    print(f"full_lattice_index={full_index}")
    print(f"deleted_facet_lattice_index={facet_index}")
    print(f"quotient_multiplicity={quotient_multiplicity}")


if __name__ == "__main__":
    main()
