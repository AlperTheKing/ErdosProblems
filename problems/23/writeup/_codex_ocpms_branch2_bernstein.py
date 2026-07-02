"""Symbolic check for the OC-PMS all-seven-active branch-2 certificate.

The all-seven-active face splits into:
  1. r=t, already coefficient-positive after a shift.
  2. x=y and a = 2*x + t - r*(x+t)/t.

For branch 2, the feasible interval is
  1 <= r <= U(t,x) = t*(2*x+t-1)/(x+t).

The PMS margin numerator is cubic in r.  This script computes the Bernstein
coefficients over [1,U] and verifies that, after clearing positive
denominators and shifting t=1+T, x=1+X, every coefficient is nonnegative.
"""

import sympy as sp


def main() -> None:
    t, x, r = sp.symbols("t x r", positive=True)
    T, X = sp.symbols("T X", nonnegative=True)

    # Branch-2 numerator after substituting
    # a = 2*x + t - r*(x+t)/t and clearing the positive factor x.
    P = (
        2 * r**3 * t**2 * x**2
        + 6 * r**3 * t * x**3
        + 4 * r**3 * x**4
        - 18 * r**2 * t**4 * x
        - 76 * r**2 * t**3 * x**2
        - 75 * r**2 * t**3 * x
        - 104 * r**2 * t**2 * x**3
        - 75 * r**2 * t**2 * x**2
        - 48 * r**2 * t * x**4
        - 20 * r * t**6
        - 84 * r * t**5 * x
        + 150 * r * t**5
        - 44 * r * t**4 * x**2
        + 375 * r * t**4 * x
        + 160 * r * t**3 * x**3
        + 150 * r * t**3 * x**2
        + 144 * r * t**2 * x**4
        - 150 * r * t**2 * x**3
        + 20 * t**7
        + 152 * t**6 * x
        - 150 * t**6
        + 368 * t**5 * x**2
        - 525 * t**5 * x
        + 288 * t**4 * x**3
        - 450 * t**4 * x**2
    )

    U = t * (2 * x + t - 1) / (x + t)
    h = U - 1
    dP = sp.diff(P, r)
    bernstein = [
        P.subs(r, 1),
        P.subs(r, 1) + h * dP.subs(r, 1) / 3,
        P.subs(r, U) - h * dP.subs(r, U) / 3,
        P.subs(r, U),
    ]

    for i, coeff in enumerate(bernstein):
        num, den = sp.together(coeff).as_numer_denom()
        shifted = sp.Poly(sp.expand(num.subs({t: T + 1, x: X + 1})), T, X)
        neg = [(monom, c) for monom, c in shifted.terms() if c < 0]
        print(
            "B",
            i,
            "den",
            sp.factor(den),
            "terms",
            len(shifted.terms()),
            "negative",
            len(neg),
            "min_coeff",
            min(c for _, c in shifted.terms()),
        )
        if neg:
            print("first_negative", neg[0])
            raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
