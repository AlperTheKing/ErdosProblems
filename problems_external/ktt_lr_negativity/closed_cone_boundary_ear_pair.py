#!/usr/bin/env python3
"""Exact intrinsic-lattice obstruction to a combinatorial boundary-ear rule.

Two actual size-four hive vertex cones contain the identical labelled boundary
rhombus A(1,1) as an extreme normal ray.  Deleting that ray leaves an abstract
two-ray facet in both cases, but the primitive quotient-lattice multiplicity is
two in the first closed cone and one in the second.  Hence an ear label and
abstract cone incidence do not determine the lattice correction.
"""

from fractions import Fraction
from math import gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "r4_reeve"))
from hive4 import _affine_rank, _det3, build_hive4, vertices  # noqa: E402
sys.path.insert(0, str(HERE / "r5_rational"))
from hiveR import fixed_A  # noqa: E402


DET4 = {
    "lambda": (12, 8, 4, 0),
    "mu": (12, 8, 4, 0),
    "nu": (18, 14, 10, 6),
    "vertex": (26, 32, 38),
    "active": (2, 3, 7, 8, 9, 10, 12, 13, 15),
    "extreme_rows": (8, 9, 10),
    "remaining_rows": (9, 10),
    "full_index": 4,
    "facet_index": 2,
    "quotient_multiplicity": 2,
}

UNI = {
    "lambda": (12, 9, 3, 0),
    "mu": (10, 8, 3, 0),
    "nu": (18, 14, 8, 5),
    "vertex": (29, 32, 39),
    "active": (4, 8, 12),
    "extreme_rows": (4, 8, 12),
    "remaining_rows": (4, 12),
    "full_index": 1,
    "facet_index": 1,
    "quotient_multiplicity": 1,
}

EAR_ROW = 8


def dot(a, b):
    return sum(Fraction(x) * Fraction(y) for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def primitive(v):
    divisor = 0
    for value in v:
        divisor = gcd(divisor, abs(value))
    assert divisor > 0
    return tuple(value // divisor for value in v)


def active_rows(A, b, vertex):
    return tuple(i for i, row in enumerate(A) if dot(row, vertex) == b[i])


def verify_case(case):
    hive = build_hive4(case["lambda"], case["mu"], case["nu"])
    assert hive["ok"]
    verts = vertices(hive["A"], hive["b"])
    assert _affine_rank(verts) == 3
    vertex = tuple(Fraction(value) for value in case["vertex"])
    assert list(vertex) in verts
    assert active_rows(hive["A"], hive["b"], vertex) == case["active"]

    centroid = tuple(sum(v[j] for v in verts) / len(verts) for j in range(3))
    assert all(dot(row, centroid) < rhs for row, rhs in zip(hive["A"], hive["b"]))

    rays = tuple(tuple(hive["A"][i]) for i in case["extreme_rows"])
    assert all(gcd(*(abs(value) for value in ray)) == 1 for ray in rays)
    assert abs(_det3(rays)) == case["full_index"]

    remaining = tuple(tuple(hive["A"][i]) for i in case["remaining_rows"])
    normal = cross(*remaining)
    facet_index = gcd(*(abs(value) for value in normal))
    quotient_covector = primitive(normal)
    ear = tuple(hive["A"][EAR_ROW])
    quotient_multiplicity = abs(dot(quotient_covector, ear))
    assert facet_index == case["facet_index"]
    assert quotient_multiplicity == case["quotient_multiplicity"]

    # The primitive covector has kernel equal to the saturated real span of
    # the retained facet.  Thus x -> <quotient_covector,x> is the intrinsic
    # quotient map N -> N/(N cap span_R(facet)) = Z.
    assert all(dot(quotient_covector, ray) == 0 for ray in remaining)
    assert gcd(*(abs(value) for value in quotient_covector)) == 1

    return {
        "active": case["active"],
        "rays": rays,
        "remaining": remaining,
        "quotient_covector": quotient_covector,
        "full_index": case["full_index"],
        "facet_index": facet_index,
        "quotient_multiplicity": quotient_multiplicity,
    }


def main():
    _, _, tags = fixed_A(4)
    assert tags[EAR_ROW] == ("A", 1, 1)

    first = verify_case(DET4)
    second = verify_case(UNI)

    # Exact redundancy certificates for the determinant-four closed cone.
    u8, u9, u10 = first["rays"]
    assert tuple((u9[j] + u10[j]) // 2 for j in range(3)) == (-1, 0, 0)
    assert tuple((u8[j] + u10[j]) // 2 for j in range(3)) == (0, -1, 0)
    assert tuple((u8[j] + u9[j]) // 2 for j in range(3)) == (0, 0, -1)

    assert first["quotient_multiplicity"] != second["quotient_multiplicity"]
    print("PASS")
    print(f"common_boundary_ear_row={EAR_ROW}")
    print(f"common_boundary_ear_tag={tags[EAR_ROW]}")
    print(f"det4_case={first}")
    print(f"unimodular_case={second}")
    print("same_abstract_move=delete one extreme ray from a simplicial 3-cone")
    print("quotient_multiplicities=(2,1)")
    print("verdict=ear label and abstract incidence do not determine lattice correction")


if __name__ == "__main__":
    main()
