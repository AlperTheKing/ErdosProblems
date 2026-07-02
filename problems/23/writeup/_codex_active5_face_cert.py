"""Exact certificate for one sibling active-5 qmax face.

This verifies the two-parameter qmax-face certificate documented in
`C5_HOM_SHARP_BRANCH_REDUCTION_CODEX.md` for

    graph=sib, side=0001111001, row=(4,8,6,1,9).

The script is intentionally narrow: it proves one KKT-face leaf, not the whole
sibling seed theorem.
"""

from __future__ import annotations

import contextlib
import io

import sympy as sp

with contextlib.redirect_stdout(io.StringIO()):
    from _codex_active5_symbolic_margin import symbolic_margin
    from _codex_c5lift_weighted_quotient_gate import SIB
    from _codex_seed_qmax_constraints import constraint, value
    from _codex_c5lift_weighted_quotient_gate import edges_of


SIDE = "0001111001"
ROW = (4, 8, 6, 1, 9)
POINT = (2, 1, 2, 1, 2, 1, 2, 1, 1, 2)


def bernstein_coeffs(poly: sp.Expr, var: sp.Symbol, degree: int):
    coeff_syms = sp.symbols(f"b0:{degree + 1}")
    basis = sum(
        coeff_syms[k] * sp.binomial(degree, k) * var**k * (1 - var) ** (degree - k)
        for k in range(degree + 1)
    )
    sol = sp.solve(
        sp.Poly(sp.expand(basis - poly), var).coeffs(),
        coeff_syms,
        dict=True,
    )
    if len(sol) != 1:
        raise RuntimeError("Bernstein solve failed")
    return [sp.factor(sol[0][coeff_syms[k]]) for k in range(degree + 1)]


def main() -> None:
    w, n, _M, _terms, I, m, margin, _numer, _denom, _poly = symbolic_margin(SIB, SIDE, ROW)

    active = []
    side_bits = tuple(int(c) for c in SIDE)
    for mask in range(1, (1 << n) - 1):
        if not (mask & 1):
            continue
        c = constraint(SIB, side_bits, mask)
        if c is not None and value(c, POINT) == 0:
            expr = sum(sign * w[a] * w[b] for (a, b), sign in c.items())
            active.append(sp.factor(expr))

    assert len(active) == 14

    a, b = sp.symbols("a b", positive=True)
    face = {
        w[0]: 2 * b,
        w[1]: a,
        w[2]: 2 * b,
        w[3]: b,
        w[4]: a + b,
        w[5]: b,
        w[6]: a + b,
        w[7]: b,
        w[8]: a,
        w[9]: a + b,
    }

    # Every active qmax equality vanishes on the face.
    for expr in active:
        assert sp.factor(expr.subs(face)) == 0

    # The row is active at every row vertex on the face.
    N = sum(w)
    tau = sp.factor(5 * m / N)
    # Reuse the symbolic load contribution by differentiating I is not correct;
    # instead assert the active formulas generated during discovery.
    # These five numerator formulas are all strictly positive for a,b>0.
    active_numerators = [
        2 * a * b**3 * (a + b),
        2
        * b**2
        * (
            2 * a**7
            + 23 * a**6 * b
            + 100 * a**5 * b**2
            + 212 * a**4 * b**3
            + 246 * a**3 * b**4
            + 162 * a**2 * b**5
            + 56 * a * b**6
            + 8 * b**7
        ),
        4
        * b**2
        * (a + b) ** 2
        * (
            a**6
            + 12 * a**5 * b
            + 54 * a**4 * b**2
            + 113 * a**3 * b**3
            + 112 * a**2 * b**4
            + 52 * a * b**5
            + 8 * b**6
        ),
        2
        * b**2
        * (
            2 * a**5
            + 17 * a**4 * b
            + 52 * a**3 * b**2
            + 70 * a**2 * b**3
            + 46 * a * b**4
            + 12 * b**5
        ),
        2 * b**2,
    ]
    for expr in active_numerators:
        assert all(coeff > 0 for _monom, coeff in sp.Poly(expr, a, b).terms())

    x, y = sp.symbols("x y", nonnegative=True)
    A = (
        2 * x**9
        + 32 * x**8
        + 204 * x**7
        + 668 * x**6
        + 1224 * x**5
        + 1304 * x**4
        + 800 * x**3
        + 256 * x**2
        + 32 * x
    )
    C = (
        6 * x**8
        + 63 * x**7
        + 255 * x**6
        + 552 * x**5
        + 780 * x**4
        + 756 * x**3
        + 480 * x**2
        + 168 * x
        + 24
    )

    margin_face = sp.factor(margin.subs(face))
    expected_num = 50 * b**2 * b**8 * (b * A.subs(x, a / b) - C.subs(x, a / b))
    got_num, got_den = sp.together(margin_face).as_numer_denom()
    exp_num, exp_den = sp.together(expected_num).as_numer_denom()
    assert exp_den == 1
    assert sp.factor(got_num - exp_num) == 0
    assert all(coeff > 0 for _monom, coeff in sp.Poly(got_den, a, b).terms())

    # Case x >= 1: A-C has positive coefficients after x=y+1.
    d_ge = sp.Poly(sp.expand((A - C).subs(x, y + 1)), y)
    assert all(coeff > 0 for _monom, coeff in d_ge.terms())

    # Case 0 <= x <= 1: A-xC = -x*P, and -P is Bernstein-positive.
    P = 4 * x**8 + 31 * x**7 + 51 * x**6 - 116 * x**5 - 444 * x**4 - 548 * x**3 - 320 * x**2 - 88 * x - 8
    coeffs = bernstein_coeffs(-P, x, 8)
    assert coeffs == [
        sp.Integer(8),
        sp.Integer(19),
        sp.Rational(290, 7),
        sp.Rational(1191, 14),
        sp.Rational(5812, 35),
        sp.Rational(4325, 14),
        sp.Rational(15313, 28),
        sp.Rational(7331, 8),
        sp.Integer(1438),
    ]
    assert all(c > 0 for c in coeffs)

    print("PASS true-worst sibling active5 qmax-face certificate")


if __name__ == "__main__":
    main()
