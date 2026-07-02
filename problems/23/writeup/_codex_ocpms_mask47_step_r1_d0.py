"""Three-variable r=1 step probe for mask-47 on d=0.

Face:
  x=y=1+h, q=p+e, current r=1.
"""

import sympy as sp

from _codex_ocpms_mask47_step_r1_d_le_s import pms_margin_expr


def main() -> None:
    p, e, h = sp.symbols("p e h", positive=True)
    P, E, H = sp.symbols("P E H", nonnegative=True)
    q = p + e
    x = y = 1 + h
    r = sp.Integer(1)
    a = sp.factor((x * p + y * q + q * p - y - p) / p)
    r_prev = sp.factor(1 + p / (y + p))

    current = (a, x, y, y, x, p, q, q, r, p)
    previous = (a - 1, x, y, y, x, p, q, q, r_prev, p)
    diff = pms_margin_expr(current) - pms_margin_expr(previous)
    num, den = sp.together(diff).as_numer_denom()
    shifted = sp.Poly(sp.expand(num.subs({p: P + 1, e: E + 1, h: H})), P, E, H)
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
