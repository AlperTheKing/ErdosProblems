"""Exact XQ_A bivariate tangent-candidate inventory.

The observed XQ_A support is two-dimensional with parameters X>=0 and
0<=R<=1.  This gate does not yet exclude the remaining candidates from the
R-domain.  It records the exact elimination shape for simultaneous tangent
criticality of Phi on XQ_A: after removing fixed positive factors, the X
eliminant has degree 41 and exactly two roots on X>=0.  A linear Groebner row,
viewed as a polynomial in R with coefficients in Q[X], then determines R at any
candidate whose R-coefficient does not vanish.

Thus the remaining bivariate coverage task is reduced to checking two algebraic
X-candidates against the R-domain and the existing positivity/closure gate.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "_codex_sib_s7_y1_symbolic_rank_certificates.py"


def load_cert():
    spec = importlib.util.spec_from_file_location("cert", CERT_PATH)
    cert = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(cert)
    return cert


def build_phi(inv) -> sp.Expr:
    a, b, c, d, e, f, x, u, v = inv.VARS
    y = sp.Integer(1)
    m = x * u + x * v + v
    N = a + b + c + d + e + f + x + y + u + v
    Y = a * c + b * f + c * f
    Z = e * Y + d * f * (b + c)
    A = b * d + c * d + d * f + a * c + a * e + b * f + b * e + c * f + c * e + e * f
    B = a * c + a * e + b * f + b * e + c * f + c * e + e * f
    return 2 * (N * N - 25 * m) - 75 * (x * (u + v) * A / Z + v * B / (e * Y) - (a + b + c + d + e + f))


def main() -> None:
    cert = load_cert()
    inv = cert.load_inventory()
    Phi = build_phi(inv)
    params, subs = cert.family_substitution(inv, "XQ_A")
    X, R = params
    phi_fam = sp.together(Phi.subs(subs))
    dX = cert.nonzero_num(sp.diff(phi_fam, X))
    dR = cert.nonzero_num(sp.diff(phi_fam, R))

    PX = sp.Poly(sp.expand(dX), R, X)
    PR = sp.Poly(sp.expand(dR), R, X)
    assert sp.gcd(PX, PR).total_degree() == 0

    G = sp.groebner([dX, dR], R, X, order="lex")
    assert len(G.polys) == 4
    degrees = [(sp.Poly(g.as_expr(), R, X).degree(R), sp.Poly(g.as_expr(), R, X).degree(X)) for g in G.polys]
    assert degrees == [(3, 64), (2, 64), (1, 64), (0, 65)]

    # Important: the coefficient of R must be extracted from Poly(row, R).
    # With Poly(row, R, X), coeff_monomial(R) would only read the R*X^0
    # coefficient and would discard the rest of the X-polynomial.
    linear = sp.Poly(G.polys[2].as_expr(), R)
    assert linear.degree() == 1
    coeff_R = sp.Poly(linear.coeff_monomial(R), X)
    const_R = sp.Poly(linear.coeff_monomial(1), X)
    assert coeff_R.degree() == 8
    assert const_R.degree() == 64

    elim = sp.factor(G.polys[-1].as_expr())
    fixed = (
        (X + 2) ** 3
        * (X + 3) ** 9
        * (X**2 + 4 * X + 2) ** 3
        * (X**2 + 5 * X + 5) ** 2
        * (3 * X**2 + 16 * X + 19)
    )
    for factor in [X + 2, X + 3, X**2 + 4 * X + 2, X**2 + 5 * X + 5, 3 * X**2 + 16 * X + 19]:
        assert sp.polys.polytools.count_roots(factor, 0, sp.oo) == 0

    core = sp.Poly(sp.expand(sp.cancel(elim / fixed)), X)
    assert core.degree() == 41
    assert sp.polys.polytools.count_roots(core.as_expr(), 0, sp.oo) == 2
    assert sp.gcd(core, coeff_R).total_degree() == 0

    print("PASS y=1 XQ_A simultaneous tangent criticality has exactly two X>=0 candidates with a nondegenerate linear R-row")


if __name__ == "__main__":
    main()