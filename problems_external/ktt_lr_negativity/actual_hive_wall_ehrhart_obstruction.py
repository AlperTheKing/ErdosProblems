#!/usr/bin/env python3
"""Exact audit of the Ehrhart jump at one actual rank-four hive wall.

This is a bounded wall-crossing falsification gate.  It reconstructs the
primitive circuit with cddlib, computes exact stretched-LR polynomials with
the independent rank-four enumerator, and interpolates the chamberwise
coefficient functions on the certified support-number line.
"""

from fractions import Fraction
import sys

sys.path.insert(0, "problems_external/ktt_lr_negativity")
sys.path.insert(0, "problems_external/ktt_lr_negativity/r4_reeve")
sys.path.insert(0, "problems_external/ktt_lr_negativity/engineC")

import ehr as engine_c  # noqa: E402
import ghte_find_r4_wall_pair as wall_gate  # noqa: E402
import hive4  # noqa: E402


LEFT = (
    (11, 3, 1, 0),
    (13, 6, 2, 0),
    (16, 12, 7, 1),
)
RIGHT = (
    (14, 3, 2, 0),
    (12, 5, 3, 0),
    (22, 8, 7, 2),
)
WALL = tuple(tuple(x + y for x, y in zip(left, right))
             for left, right in zip(LEFT, RIGHT))
DIRECTION = tuple(tuple(y - x for x, y in zip(left, right))
                  for left, right in zip(LEFT, RIGHT))

NORMALS = (
    (-1, 1, 0),
    (0, 0, -1),
    (0, 1, 0),
    (1, 0, -1),
)
CIRCUIT = (1, -1, -1, 1)


def determinant3(columns):
    a, b, c = columns
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - b[0] * (a[1] * c[2] - a[2] * c[1])
        + c[0] * (a[1] * b[2] - a[2] * b[1])
    )


def polynomial_multiply(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            answer[i + j] += x * y
    return answer


def interpolate(nodes):
    """Return ordinary coefficients of the exact interpolant through nodes."""
    answer = [Fraction(0)] * len(nodes)
    for i, (x_i, y_i) in enumerate(nodes):
        basis = [Fraction(1)]
        denominator = Fraction(1)
        for j, (x_j, _) in enumerate(nodes):
            if i == j:
                continue
            basis = polynomial_multiply(basis, [-x_j, Fraction(1)])
            denominator *= x_i - x_j
        for degree, value in enumerate(basis):
            answer[degree] += y_i * value / denominator
    return answer


def scaled_boundary(multiplier, sign):
    """Integer boundary multiplier*WALL + sign*DIRECTION."""
    return tuple(
        tuple(multiplier * x + sign * y for x, y in zip(wall, direction))
        for wall, direction in zip(WALL, DIRECTION)
    )


def normalized_coefficients(multiplier, sign):
    """Coefficients for WALL + sign*DIRECTION/multiplier.

    The enumerated integral hive is multiplier times this rational hive, so
    its degree-j Ehrhart coefficient is divided by multiplier**j.
    """
    analysis = hive4.analyze(*scaled_boundary(multiplier, sign))
    assert analysis["dim"] == 3
    assert analysis["verified"]
    assert analysis["max_denominator"] == 1
    coefficients = list(analysis["poly"]) + [Fraction(0)] * 4
    independent = engine_c.ehrhart(*scaled_boundary(multiplier, sign))
    assert independent["status"] == "OK" and independent["d"] == 3
    independent_coefficients = tuple(Fraction(value)
                                     for value in independent["coeffs"])
    assert independent_coefficients == tuple(coefficients[:4])
    return tuple(Fraction(coefficients[j], multiplier ** j) for j in range(4))


def main():
    # Saturated intrinsic lattices are M=N=Z^3.  The circuit is primitive,
    # and every circuit basis is unimodular, so no hidden quotient index is
    # available to alter the local jump.
    assert all(
        sum(CIRCUIT[i] * NORMALS[i][coordinate] for i in range(4)) == 0
        for coordinate in range(3)
    )
    determinants = tuple(
        determinant3(tuple(NORMALS[j] for j in range(4) if j != omitted))
        for omitted in range(4)
    )
    assert tuple(abs(value) for value in determinants) == (1, 1, 1, 1)

    left_fan = wall_gate.exact_fan(*LEFT)
    right_fan = wall_gate.exact_fan(*RIGHT)
    assert left_fan is not None and right_fan is not None
    left_only = left_fan["cones"] - right_fan["cones"]
    right_only = right_fan["cones"] - left_fan["cones"]
    changed = tuple(left_only | right_only)
    wall = wall_gate.wall_boundary(LEFT, RIGHT, changed, left_fan, right_fan)
    assert wall is not None
    assert wall["scale"] == 2 and wall["boundary"] == WALL
    assert wall["normals"] == NORMALS and wall["coefficients"] == CIRCUIT
    assert wall["omega_left"] == 1 and wall["omega_right"] == -1

    # Convexity of each type cone puts the whole half-segment in the endpoint
    # fan.  We nevertheless replay every rational sample after clearing its
    # denominator and check the exact fan signature.
    samples = {}
    for sign, reference in ((-1, left_fan), (1, right_fan)):
        for multiplier in range(1, 7):
            boundary = scaled_boundary(multiplier, sign)
            fan = wall_gate.exact_fan(*boundary)
            assert fan is not None
            assert fan["facets"] == reference["facets"]
            assert fan["cones"] == reference["cones"]
            samples[sign, multiplier] = normalized_coefficients(multiplier, sign)

    # On a fixed normal fan, the degree-j Ehrhart coefficient is homogeneous
    # polynomial of degree j in the supports.  Along this line it therefore
    # has degree at most j.  The first j+1 exact samples determine it.
    fitted = {}
    for sign in (-1, 1):
        for ehrhart_degree in range(4):
            nodes = []
            for multiplier in range(1, ehrhart_degree + 2):
                z = Fraction(sign, multiplier)
                nodes.append((z, samples[sign, multiplier][ehrhart_degree]))
            fitted[sign, ehrhart_degree] = tuple(interpolate(nodes))

    expected = {
        (-1, 0): (Fraction(1),),
        (1, 0): (Fraction(1),),
        (-1, 1): (Fraction(13, 2), Fraction(1, 6)),
        (1, 1): (Fraction(13, 2), Fraction(-1, 6)),
        (-1, 2): (Fraction(27, 2), Fraction(0), Fraction(-3, 2)),
        (1, 2): (Fraction(27, 2), Fraction(0), Fraction(-3, 2)),
        (-1, 3): (Fraction(9), Fraction(0), Fraction(-3), Fraction(-2, 3)),
        (1, 3): (Fraction(9), Fraction(0), Fraction(-3), Fraction(2, 3)),
    }
    assert fitted == expected

    # Multipliers 5 and 6 are held out from every interpolation of degree <=3.
    for sign in (-1, 1):
        for multiplier in (5, 6):
            z = Fraction(sign, multiplier)
            for degree in range(4):
                polynomial = fitted[sign, degree]
                value = sum(coefficient * z ** exponent
                            for exponent, coefficient in enumerate(polynomial))
                assert value == samples[sign, multiplier][degree]

    wall_analysis = hive4.analyze(*WALL)
    assert wall_analysis["verified"] and wall_analysis["dim"] == 3
    assert tuple(wall_analysis["poly"]) == (
        Fraction(1), Fraction(13, 2), Fraction(27, 2), Fraction(9)
    )
    wall_independent = engine_c.ehrhart(*WALL)
    assert wall_independent["status"] == "OK" and wall_independent["d"] == 3
    assert tuple(Fraction(value) for value in wall_independent["coeffs"]) == (
        Fraction(1), Fraction(13, 2), Fraction(27, 2), Fraction(9)
    )

    # Right extension minus left extension at the same support h(z).
    jump = {
        "q=0,n^3": "4*z^3/3 = -Omega^3/6",
        "q=1,n^2": "0",
        "q=2,n^1": "-z/3 = Omega/6",
        "q=3,n^0": "0",
    }
    print("PASS")
    print("intrinsic_lattices M=Z^3 N=Z^3")
    print("determinants", determinants)
    print("wall", wall)
    print("left_only", sorted(left_only))
    print("right_only", sorted(right_only))
    print("fitted", fitted)
    print("jump", jump)
    print("factor", "binomial((-Omega)*n+1,3) on the Omega<0 side")


if __name__ == "__main__":
    main()
