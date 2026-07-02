"""Exact univariate tangent-root counts for observed y=1 SIB-S7 families.

This is a coverage-support artifact for the one-parameter observed families.  It
records exact Sturm/root counts for the tangent witness polynomials produced by
`_codex_sib_s7_y1_symbolic_rank_certificates.py`.  The two-parameter `XQ_A`
family is intentionally excluded here; it needs a separate bivariate critical
inventory.
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
    expected = {
        "ALL_TIGHT": 1,
        "HIGH_A": 1,
        "XQ_B": 1,
        "U1_S7_HIGH": 0,
        "XQ_S5_HIGH": 1,
    }
    for name, roots in expected.items():
        params, subs = cert.family_substitution(inv, name)
        (param,) = params
        phi_fam = sp.together(Phi.subs(subs))
        witness = cert.nonzero_num(sp.diff(phi_fam, param))
        poly = sp.Poly(sp.expand(witness), param)
        assert poly != 0
        assert sp.polys.polytools.count_roots(poly.as_expr(), 0, sp.oo) == roots
        print("ROOT-CERT", name, f"direction={param}", f"nonnegative_roots={roots}", f"degree={poly.degree()}")

    print("PASS y=1 univariate observed tangent witnesses have exact root counts")


if __name__ == "__main__":
    main()