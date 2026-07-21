"""Exact arithmetic on induced Diophantine-triple elliptic curves.

The affine model used by the septuple search is

    y^2 = a3*x^3 + a2*x^2 + a1*x + a0.

It deliberately stays in that model: changing to a monic or short
Weierstrass equation is unnecessary and is an easy place to lose a rational
scale factor.  ``None`` denotes the point at infinity.

For a Diophantine triple ``(a, b, c)``, the induced curve is

    y^2 = (a*x + 1)(b*x + 1)(c*x + 1).

If all three factors are rational squares, multiplying their square roots
therefore reconstructs an exact rational point on the curve.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import TypeAlias


RationalLike: TypeAlias = int | Fraction
AffinePoint: TypeAlias = tuple[Fraction, Fraction]
Point: TypeAlias = AffinePoint | None


def _q(value: RationalLike) -> Fraction:
    """Coerce an integer or Fraction without accepting inexact floats."""

    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    raise TypeError(f"expected int or Fraction, got {type(value).__name__}")


def rational_sqrt(value: RationalLike) -> Fraction | None:
    """Return the nonnegative rational square root, or ``None`` if absent."""

    q = _q(value)
    if q < 0:
        return None
    numerator_root = isqrt(q.numerator)
    denominator_root = isqrt(q.denominator)
    if numerator_root * numerator_root != q.numerator:
        return None
    if denominator_root * denominator_root != q.denominator:
        return None
    return Fraction(numerator_root, denominator_root)


@dataclass(frozen=True, slots=True)
class CubicCurve:
    """A nonsingular rational cubic ``y^2 = a3*x^3+...+a0``."""

    a3: Fraction
    a2: Fraction
    a1: Fraction
    a0: Fraction

    def __post_init__(self) -> None:
        for name in ("a3", "a2", "a1", "a0"):
            object.__setattr__(self, name, _q(getattr(self, name)))
        if self.a3 == 0:
            raise ValueError("the right-hand side must have degree three")
        if self.discriminant == 0:
            raise ValueError("the cubic is singular, so it is not elliptic")

    @classmethod
    def from_diophantine_triple(
        cls, a: RationalLike, b: RationalLike, c: RationalLike
    ) -> "CubicCurve":
        """Construct ``y^2=(a*x+1)(b*x+1)(c*x+1)`` exactly."""

        a_q, b_q, c_q = _q(a), _q(b), _q(c)
        return cls(
            a_q * b_q * c_q,
            a_q * b_q + a_q * c_q + b_q * c_q,
            a_q + b_q + c_q,
            Fraction(1),
        )

    @property
    def discriminant(self) -> Fraction:
        """Discriminant of the cubic polynomial on the right-hand side."""

        a, b, c, d = self.a3, self.a2, self.a1, self.a0
        return (
            18 * a * b * c * d
            - 4 * b**3 * d
            + b**2 * c**2
            - 4 * a * c**3
            - 27 * a**2 * d**2
        )

    def rhs(self, x: RationalLike) -> Fraction:
        x_q = _q(x)
        return ((self.a3 * x_q + self.a2) * x_q + self.a1) * x_q + self.a0

    def is_on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return _q(y) ** 2 == self.rhs(x)

    def _checked(self, point: Point) -> Point:
        if point is None:
            return None
        normalized = (_q(point[0]), _q(point[1]))
        if not self.is_on_curve(normalized):
            raise ValueError(f"point is not on the curve: {normalized!r}")
        return normalized

    def neg(self, point: Point) -> Point:
        """Return the elliptic inverse of ``point``."""

        checked = self._checked(point)
        if checked is None:
            return None
        return checked[0], -checked[1]

    def add(self, left: Point, right: Point) -> Point:
        """Add two points by the exact chord-and-tangent law.

        If the chord is ``y=m*x+n``, its three intersection x-coordinates
        satisfy ``x1+x2+x3=(m^2-a2)/a3``.  Reflecting the third
        intersection gives the group sum.
        """

        p = self._checked(left)
        q = self._checked(right)
        if p is None:
            return q
        if q is None:
            return p

        x1, y1 = p
        x2, y2 = q
        if x1 == x2:
            if y1 == -y2:
                return None
            # On a y^2=f(x) curve, the only remaining case is doubling.
            # The y=0 doubling case was already caught because y=-y.
            slope = (3 * self.a3 * x1**2 + 2 * self.a2 * x1 + self.a1) / (
                2 * y1
            )
        else:
            slope = (y2 - y1) / (x2 - x1)

        intercept = y1 - slope * x1
        x3 = (slope**2 - self.a2) / self.a3 - x1 - x2
        result = (x3, -(slope * x3 + intercept))
        if not self.is_on_curve(result):
            # This should be unreachable; retaining the exact check prevents
            # a silent convention error from contaminating a point search.
            raise ArithmeticError("chord-and-tangent result failed curve closure")
        return result

    def scalar_mul(self, multiplier: int, point: Point) -> Point:
        """Return ``multiplier * point`` using exact double-and-add."""

        if not isinstance(multiplier, int):
            raise TypeError("scalar multiplier must be an integer")
        addend = self._checked(point)
        if multiplier < 0:
            return self.scalar_mul(-multiplier, self.neg(addend))

        result: Point = None
        n = multiplier
        while n:
            if n & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            n >>= 1
        return result


def extension_roots(
    a: RationalLike, b: RationalLike, c: RationalLike, x: RationalLike
) -> tuple[Fraction, Fraction, Fraction] | None:
    """Return roots of ``a*x+1``, ``b*x+1``, ``c*x+1`` when all exist."""

    x_q = _q(x)
    roots = tuple(rational_sqrt(_q(t) * x_q + 1) for t in (a, b, c))
    if any(root is None for root in roots):
        return None
    # The check above narrows these values for humans and static analyzers.
    return roots[0], roots[1], roots[2]  # type: ignore[return-value]


def extension_point(
    a: RationalLike, b: RationalLike, c: RationalLike, x: RationalLike
) -> AffinePoint:
    """Reconstruct the canonical positive-y induced-curve point for ``x``.

    Raises ``ValueError`` when ``x`` does not extend the triple.
    """

    roots = extension_roots(a, b, c, x)
    if roots is None:
        raise ValueError(f"x={_q(x)} does not extend the supplied triple")
    point = (_q(x), roots[0] * roots[1] * roots[2])
    curve = CubicCurve.from_diophantine_triple(a, b, c)
    if not curve.is_on_curve(point):
        raise ArithmeticError("extension roots did not reconstruct a curve point")
    return point
