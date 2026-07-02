"""Coefficient probe for the H=0 triple face s3=s5=s7=0.

This script tries the direct shifted numerator after substituting

    a=1+A, b=1+B, f=1+F, v=1+V, e=v+S, c=e+R, d=b+R,

and the s5/s7 equality value of u.  It intentionally does not use the
remaining u1/s2 feasibility inequalities; a nonnegative coefficient result
would therefore be an immediate certificate.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    A, B, F, V, S, R = sp.symbols("A B F V S R", nonnegative=True)
    a = 1 + A
    b = 1 + B
    f = 1 + F
    v = 1 + V
    e = v + S
    c = e + R
    d = b + R
    x = b + c - 1
    u = (a * e + b * f + c * f - v * (b + c)) / (b + c - 1)

    core = a + b + c + d + e + f
    n = core + x + 1 + u + v
    m = x * u + x * v + v
    yy = a * c + b * f + c * f
    z = e * yy + d * f * (b + c)
    aa = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    bb = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    phi = 2 * (n * n - 25 * m) - 75 * (x * (u + v) * aa / z + v * bb / (e * yy) - core)

    num, den = sp.together(phi).as_numer_denom()
    poly = sp.Poly(sp.expand(num), A, B, F, V, S, R)
    bad = [(mon, coef) for mon, coef in poly.terms() if coef < 0]
    print(f"H0-COEFF numerator_terms={len(poly.terms())} bad_coeffs={len(bad)}")
    if bad:
        print(f"H0-COEFF first_bad={bad[0]}")
    else:
        assert den != 0
        print("PASS H0 direct shifted numerator has nonnegative coefficients")


if __name__ == "__main__":
    main()
