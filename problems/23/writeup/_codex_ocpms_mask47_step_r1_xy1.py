"""Two-variable r=1 step probe for mask-47.

Face:
  x=y=1, q=p+e, current r=1.

This contains the observed hardest ray at e=1.  The script checks positivity
of F(current)-F(previous) for all p>=1, e>=1 by shifted coefficient expansion.
"""

import sympy as sp

from _codex_ocpms_mask47_step_r1_d_le_s import pms_margin_expr


def main() -> None:
    p, e = sp.symbols("p e", positive=True)
    P, E = sp.symbols("P E", nonnegative=True)
    q = p + e
    x = y = sp.Integer(1)
    r = sp.Integer(1)
    a = sp.factor((x * p + y * q + q * p - y - p) / p)
    r_prev = sp.factor(1 + p / (y + p))

    current = (a, x, y, y, x, p, q, q, r, p)
    previous = (a - 1, x, y, y, x, p, q, q, r_prev, p)
    diff = pms_margin_expr(current) - pms_margin_expr(previous)
    num, den = sp.together(diff).as_numer_denom()
    shifted = sp.Poly(sp.expand(num.subs({p: P + 1, e: E + 1})), P, E)
    neg = [(monom, c) for monom, c in shifted.terms() if c < 0]
    print("a", a)
    print("r_prev", r_prev)
    print("den", sp.factor(den))
    print("terms", len(shifted.terms()), "negative", len(neg), "min_coeff", min(c for _, c in shifted.terms()))
    if neg:
        print("first_negative", neg[0])
        raise SystemExit(1)
    print("VERDICT PASS")


if __name__ == "__main__":
    main()
