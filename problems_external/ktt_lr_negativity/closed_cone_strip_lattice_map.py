#!/usr/bin/env python3
"""Exact intrinsic-lattice map for the B(0,2),B(1,2) strip obstruction."""

from fractions import Fraction


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def main():
    # Side-four coordinates are h_(1,1), h_(1,2), h_(2,1).
    # Deleting the left boundary strip sends (x,y) to (x-1,y), so the unique
    # side-three interior coordinate h_(1,1) is old h_(2,1).  The induced dual
    # restriction is pi(a,b,c)=c.
    u = (1, -1, 0)  # B(0,2), deleted ear
    v = (0, -1, 1)  # B(1,2), becomes side-three B(0,2)
    pi_u, pi_v = u[2], v[2]
    assert (pi_u, pi_v) == (0, 1)

    # The integral strip map is incompatible with the fixed Euclidean BV
    # complements.  Orthogonal projection to Zu takes v to u/2, and the
    # orthogonal quotient norm of [v] modulo u is 3/2, while the standard
    # side-three primitive dual ray has squared norm one.
    orthogonal_coefficient = Fraction(dot(u, v), dot(u, u))
    quotient_norm = Fraction(dot(v, v)) - Fraction(dot(u, v) ** 2, dot(u, u))
    assert orthogonal_coefficient == Fraction(1, 2)
    assert quotient_norm == Fraction(3, 2)

    print("PASS")
    print(f"deleted_normal={u} retained_normal={v}")
    print(f"strip_dual_map_images=({pi_u},{pi_v})")
    print(f"orthogonal_projection_coefficient={orthogonal_coefficient}")
    print(f"old_orthogonal_quotient_norm={quotient_norm}")
    print("new_side3_standard_dual_norm=1")
    print("verdict=INTEGRAL_STRIP_MAP_DOES_NOT_PRESERVE_BV_COMPLEMENT")


if __name__ == "__main__":
    main()

