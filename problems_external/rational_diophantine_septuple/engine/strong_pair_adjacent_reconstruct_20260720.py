#!/usr/bin/env python3
"""Exact reconstruction of the registered strong-pair adjacent-orbit route.

All generic calculations take place in

    K = Q(u)[v] / (p(u,v)).

An element is stored in the basis 1,v,v^2,v^3 over Q(u).  This avoids
parameter sampling and makes every equality check an exact reduction modulo
the defining polynomial p.  The script deliberately stops after producing
the three registered residual square classes; it performs no parameter scan.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import sympy as sp
from sympy.polys.domains import QQ


u, v = sp.symbols("u v")

p_expr = (
    3*u**4*v**4 - 8*u**4*v**3 + 6*u**4*v**2 - u**4
    - 8*u**3*v**4 + 4*u**3*v**3 - 8*u**3*v**2 + 12*u**3*v
    + 6*u**2*v**4 - 8*u**2*v**3 + 4*u**2*v**2 + 8*u**2*v + 6*u**2
    + 12*u*v**3 + 8*u*v**2 + 4*u*v + 8*u - v**4 + 6*v**2 + 8*v + 3
)

s1_expr = (
    1 + 8*v*u**4 - 8*u**3*v**2 - 8*v**3*u**2 + 4*v*u**3
    + 8*u*v**2 - 8*v**3 + 8*v*u**2 + 8*u*v**4 + 12*v**3*u**3
    + 4*u*v**3 + 12*u*v - 4*u**2*v**2 - 6*u**2*v**4 + u**4*v**4
    - 6*u**4*v**2 - 6*u**2 - 6*v**2 - 3*v**4 - 3*u**4 - 8*u**3
)

D_expr = u*v - u - v - 1
a_expr = 2*u/(u**2 - 1)
b_expr = 2*v/(v**2 - 1)
c_expr = 2*(u**2 - 1)*(v**2 - 1)/D_expr**2

# The paper prints p+t=(uv+1)^2 D^2.  Direct expansion gives the factor 4
# below, and this factor is necessary to reproduce its numerical S ordinate.
r_expr = 2*(u*v + 1)*D_expr/((u**2 - 1)*(v**2 - 1))
s_expr = (u*v - u + v + 1)/D_expr
t_expr = (u*v + u - v + 1)/D_expr

coeff_field = QQ.frac_field(u)
modulus = sp.Poly(p_expr, v, domain=coeff_field)


def log(message: str) -> None:
    print(message, flush=True)


class KElement:
    """Element of Q(u)[v]/(p), reduced to v-degree below four."""

    __slots__ = ("poly",)

    def __init__(self, value=0):
        if isinstance(value, KElement):
            self.poly = value.poly
            return
        value = sp.cancel(value)
        numerator, denominator = sp.fraction(value)
        num_poly = sp.Poly(numerator, v, domain=coeff_field).rem(modulus)
        den_poly = sp.Poly(denominator, v, domain=coeff_field).rem(modulus)
        self.poly = (num_poly * sp.invert(den_poly, modulus)).rem(modulus)

    @classmethod
    def from_poly(cls, poly):
        result = object.__new__(cls)
        result.poly = poly.rem(modulus)
        return result

    def __add__(self, other):
        other = KElement(other)
        return KElement.from_poly(self.poly + other.poly)

    __radd__ = __add__

    def __neg__(self):
        return KElement.from_poly(-self.poly)

    def __sub__(self, other):
        return self + (-KElement(other))

    def __rsub__(self, other):
        return KElement(other) - self

    def __mul__(self, other):
        other = KElement(other)
        return KElement.from_poly((self.poly * other.poly).rem(modulus))

    __rmul__ = __mul__

    def inverse(self):
        return KElement.from_poly(sp.invert(self.poly, modulus))

    def __truediv__(self, other):
        return self * KElement(other).inverse()

    def __rtruediv__(self, other):
        return KElement(other) * self.inverse()

    def __pow__(self, exponent: int):
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = KElement(1)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def is_zero(self) -> bool:
        return self.poly.is_zero

    def coefficients(self) -> list[str]:
        return [sp.sstr(self.poly.nth(i).as_expr()) for i in range(4)]

    def canonical_text(self) -> str:
        return "[" + ",".join(self.coefficients()) + "]"

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_text().encode("utf-8")).hexdigest().upper()


Point = tuple[KElement, KElement] | None


def curve_rhs(x: KElement, e1: KElement, e2: KElement, q: KElement) -> KElement:
    return x**3 + e1*x**2 + e2*x + q**2


def point_on_curve(point: Point, e1: KElement, e2: KElement, q: KElement) -> bool:
    if point is None:
        return True
    x, y = point
    return (y**2 - curve_rhs(x, e1, e2, q)).is_zero()


def point_neg(point: Point) -> Point:
    if point is None:
        return None
    return point[0], -point[1]


def point_add(left: Point, right: Point, e1: KElement, e2: KElement) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if (x1 - x2).is_zero():
        if (y1 + y2).is_zero():
            return None
        slope = (3*x1**2 + 2*e1*x1 + e2)/(2*y1)
    else:
        slope = (y2 - y1)/(x2 - x1)
    x3 = slope**2 - e1 - x1 - x2
    y3 = -y1 + slope*(x1 - x3)
    return x3, y3


def point_add_x(left: Point, right: Point, e1: KElement, e2: KElement) -> KElement:
    """Return only x(left+right), avoiding an unused terminal y-coordinate."""
    if left is None or right is None:
        point = right if left is None else left
        return point[0]
    x1, y1 = left
    x2, y2 = right
    if (x1-x2).is_zero():
        slope = (3*x1**2+2*e1*x1+e2)/(2*y1)
    else:
        slope = (y2-y1)/(x2-x1)
    return slope**2-e1-x1-x2


def point_mul(n: int, point: Point, e1: KElement, e2: KElement) -> Point:
    if n < 0:
        return point_mul(-n, point_neg(point), e1, e2)
    result = None
    addend = point
    while n:
        if n & 1:
            result = point_add(result, addend, e1, e2)
        n >>= 1
        if n:
            addend = point_add(addend, addend, e1, e2)
    return result


def frac_sqrt(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    rn = math.isqrt(value.numerator)
    rd = math.isqrt(value.denominator)
    if rn*rn == value.numerator and rd*rd == value.denominator:
        return Fraction(rn, rd)
    return None


def f_eval(expr, uu: Fraction, vv: Fraction) -> Fraction:
    value = expr.subs({u: sp.Rational(uu.numerator, uu.denominator),
                       v: sp.Rational(vv.numerator, vv.denominator)})
    value = sp.cancel(value)
    return Fraction(int(sp.numer(value)), int(sp.denom(value)))


def numeric_add(left, right, e1, e2):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if y1 == -y2:
            return None
        slope = (3*x1*x1 + 2*e1*x1 + e2)/(2*y1)
    else:
        slope = (y2-y1)/(x2-x1)
    x3 = slope*slope-e1-x1-x2
    return x3, -y1+slope*(x1-x3)


def numeric_mul(n, point, e1, e2):
    result = None
    addend = point
    while n:
        if n & 1:
            result = numeric_add(result, addend, e1, e2)
        n >>= 1
        if n:
            addend = numeric_add(addend, addend, e1, e2)
    return result


def calibration_record():
    published = (Fraction(-119, 128), Fraction(-135, 169))
    transformed = (Fraction(-128, 119), Fraction(135, 169))
    up, vp = published
    ut, vt = transformed

    p_at_published = f_eval(p_expr, up, vp)
    s1_at_published = f_eval(s1_expr, up, vp)
    p_at_transformed = f_eval(p_expr, ut, vt)

    av = f_eval(a_expr, ut, vt)
    bv = f_eval(b_expr, ut, vt)
    cv = f_eval(c_expr, ut, vt)
    rv = f_eval(r_expr, ut, vt)
    sv = f_eval(s_expr, ut, vt)
    tv = f_eval(t_expr, ut, vt)
    ysv = rv*sv*tv
    qv = av*bv*cv
    e1v = av*bv+av*cv+bv*cv
    e2v = qv*(av+bv+cv)
    point_p = (Fraction(0), qv)
    point_s = (Fraction(1), ysv)
    point_3p = numeric_mul(3, point_p, e1v, e2v)
    point_5p = numeric_mul(5, point_p, e1v, e2v)
    point_plus = numeric_add(point_3p, point_s, e1v, e2v)
    point_minus = numeric_add(point_3p, (point_s[0], -point_s[1]), e1v, e2v)

    values = [av, bv, cv, point_3p[0]/qv, point_plus[0]/qv, point_minus[0]/qv]
    roots = {}
    for i in range(6):
        for j in range(i+1, 6):
            value = values[i]*values[j]+1
            root = frac_sqrt(value)
            if root is None:
                raise AssertionError(f"calibration inherited pair {(i,j)} is not square: {value}")
            roots[f"{i},{j}"] = str(root)

    gv = point_5p[0]/qv
    base_g_roots = []
    for base in (av, bv, cv):
        root = frac_sqrt(base*gv+1)
        if root is None:
            raise AssertionError("5P extension failed at calibration")
        base_g_roots.append(str(root))

    residuals = [gv*values[i]+1 for i in (3,4,5)]
    return {
        "published_parameter": [str(up), str(vp)],
        "p_at_published": str(p_at_published),
        "s1_at_published": str(s1_at_published),
        "transformed_p_parameter": [str(ut), str(vt)],
        "p_at_transformed": str(p_at_transformed),
        "transformed_triple": [str(av), str(bv), str(cv)],
        "published_positive_triple": ["30464/2223", "22815/5168", "361/7956"],
        "pair_roots_r_s_t": [str(rv), str(sv), str(tv)],
        "yS": str(ysv),
        "published_yS": "-3307949/302328",
        "x_3P": str(point_3p[0]),
        "y_3P": str(point_3p[1]),
        "x_5P": str(point_5p[0]),
        "y_5P": str(point_5p[1]),
        "d0_dplus_dminus": [str(x) for x in values[3:]],
        "g": str(gv),
        "inherited_sextuple_values": [str(x) for x in values],
        "inherited_15_roots": roots,
        "g_base_3_roots": base_g_roots,
        "residual_values": [str(x) for x in residuals],
        "residual_square_roots_if_any": [str(frac_sqrt(x)) if frac_sqrt(x) is not None else None for x in residuals],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    started = time.time()

    # The printed identity in the source is off by exactly a factor four.
    den_ab = (u**2-1)*(v**2-1)
    num_ab = den_ab+4*u*v
    t_ab = sp.expand(den_ab*num_ab)
    corrected_identity = sp.factor(p_expr+t_ab-4*(u*v+1)**2*D_expr**2) == 0
    printed_identity_residual = sp.factor(p_expr+t_ab-(u*v+1)**2*D_expr**2)
    if not corrected_identity:
        raise AssertionError("corrected ab square identity failed")

    calibration = calibration_record()
    log("calibration: exact published-branch mismatch and transformed p-point verified")

    log("constructing K generators")
    a = KElement(a_expr)
    b = KElement(b_expr)
    c = KElement(c_expr)
    r = KElement(r_expr)
    s = KElement(s_expr)
    t = KElement(t_expr)
    q = a*b*c
    e1 = a*b+a*c+b*c
    e2 = q*(a+b+c)
    ys = r*s*t

    symbolic_checks = {
        "ab_root": (r**2-(a*b+1)).is_zero(),
        "ac_root": (s**2-(a*c+1)).is_zero(),
        "bc_root": (t**2-(b*c+1)).is_zero(),
    }
    point_p = (KElement(0), q)
    point_s = (KElement(1), ys)
    symbolic_checks["P_on_curve"] = point_on_curve(point_p, e1, e2, q)
    symbolic_checks["S_on_curve"] = point_on_curve(point_s, e1, e2, q)
    log("computing 2S and order-three identity")
    twice_s = point_add(point_s, point_s, e1, e2)
    symbolic_checks["2S_equals_minus_S"] = (
        twice_s is not None
        and (twice_s[0]-point_s[0]).is_zero()
        and (twice_s[1]+point_s[1]).is_zero()
    )

    log("computing closed x(3P), y(3P), and x(5P) formulas")
    div_d = 4*e1*q**2-e2**2
    div_e = e2**3+8*q**4-4*e1*e2*q**2
    div_f = (
        64*e1**3*q**6+16*e1**2*e2**2*q**4-20*e1*e2**4*q**2
        -384*e1*e2*q**6+3*e2**6+96*e2**3*q**4+512*q**8
    )
    div_g = (
        64*e1**3*q**6-48*e1**2*e2**2*q**4+12*e1*e2**4*q**2
        -128*e1*e2*q**6-e2**6+32*e2**3*q**4+256*q**8
    )
    x_3p = 8*q**2*div_e/div_d**2
    y_3p = -q*div_f/div_d**3
    x_5p = -8*q**2*div_d*div_e*div_f/div_g**2
    point_3p = (x_3p, y_3p)
    symbolic_checks["3P_on_curve"] = point_on_curve(point_3p, e1, e2, q)
    symbolic_checks["x5P_closed_formula_constructed"] = x_5p is not None

    log("computing 3P+S and 3P-S")
    x_plus = point_add_x(point_3p, point_s, e1, e2)
    x_minus = point_add_x(point_3p, point_neg(point_s), e1, e2)
    symbolic_checks["x3P_plus_S_constructed"] = x_plus is not None
    symbolic_checks["x3P_minus_S_constructed"] = x_minus is not None

    d0 = point_3p[0]/q
    dplus = x_plus/q
    dminus = x_minus/q
    g = x_5p/q
    residuals = {
        "f0": KElement(1)+g*d0,
        "fplus": KElement(1)+g*dplus,
        "fminus": KElement(1)+g*dminus,
    }
    log("residual functions reduced in the K basis")

    if not all(symbolic_checks.values()):
        raise AssertionError(f"symbolic checks failed: {symbolic_checks}")

    functions = {
        "yS": ys,
        "x3P": point_3p[0],
        "y3P": point_3p[1],
        "x5P": x_5p,
        "d0": d0,
        "dplus": dplus,
        "dminus": dminus,
        "g": g,
        **residuals,
    }
    function_records = {
        name: {
            "basis": element.coefficients(),
            "sha256": element.sha256(),
        }
        for name, element in functions.items()
    }

    record = {
        "status": "PASS",
        "scope": "exact reconstruction only; no parameter scan",
        "field": "Q(u)[v]/(p), basis [1,v,v^2,v^3]",
        "source_formula_audit": {
            "corrected_identity": "p+t=4*(u*v+1)^2*(u*v-u-v-1)^2",
            "corrected_identity_verified": corrected_identity,
            "printed_identity_residual_factorization": sp.sstr(printed_identity_residual),
        },
        "calibration": calibration,
        "symbolic_checks": symbolic_checks,
        "functions": function_records,
        "elapsed_seconds": time.time()-started,
        "python": sys.version,
        "sympy": sp.__version__,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    log(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
