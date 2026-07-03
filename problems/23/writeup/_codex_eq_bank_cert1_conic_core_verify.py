#!/usr/bin/env python3
"""Exact verifier for the CERT-1 EQ-bank conic core.

This verifies the algebraic Positivstellensatz step quoted in
EQ_HEIGHT_LEMMA_GPTPRO.md:

    eta25 = N^2 - 25m >= 25

after grouping N=A+B and T=m+1.  With auxiliary nonnegative forms

    U_A = A^2 - 9T,
    U_B = B^2 - 4T,

we avoid square roots by multiplying the desired inequality

    (A+B)^2 - 25T >= 0

by the positive factor AB+6T.  The certificate identity is

    (AB+6T)((A+B)^2 - 25T)
      = U_A(AB+14T) + U_B(AB+24T) + 2 U_A U_B.

Substituting U_A=A^2-9T and U_B=B^2-4T makes this an exact polynomial
identity.  The displayed RHS has coefficientwise nonnegative multipliers in
variables A,B,T,U_A,U_B, so it is a degree-4 certificate from U_A,U_B >= 0
and A,B,T >= 0.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def poly_terms_nonnegative(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> tuple[bool, list[dict[str, object]]]:
    poly = sp.Poly(sp.expand(expr), *variables, domain=sp.ZZ)
    bad = []
    for monom, coeff in poly.terms():
        if coeff < 0:
            bad.append({"monomial": monom, "coeff": int(coeff)})
    return not bad, bad


def main() -> int:
    A, B, T, UA, UB = sp.symbols("A B T UA UB")
    target = (A * B + 6 * T) * ((A + B) ** 2 - 25 * T)
    cert_rhs = UA * (A * B + 14 * T) + UB * (A * B + 24 * T) + 2 * UA * UB
    substituted_rhs = cert_rhs.subs({UA: A**2 - 9*T, UB: B**2 - 4*T})
    identity_residual = sp.expand(target - substituted_rhs)

    # Coefficient positivity of the certificate before substituting UA/UB.
    cert_nonneg, cert_bad = poly_terms_nonnegative(cert_rhs, (A, B, T, UA, UB))
    mult_A = A * B + 14 * T
    mult_B = A * B + 24 * T
    mult_A_nonneg, mult_A_bad = poly_terms_nonnegative(mult_A, (A, B, T))
    mult_B_nonneg, mult_B_bad = poly_terms_nonnegative(mult_B, (A, B, T))

    summary = {
        "schema": "eq_bank_cert1_conic_core_v1",
        "identity": "(AB+6T)((A+B)^2-25T)=UA(AB+14T)+UB(AB+24T)+2UAUB",
        "auxiliary_forms": {
            "UA": "A^2-9T",
            "UB": "B^2-4T",
        },
        "identity_residual_zero": identity_residual == 0,
        "certificate_rhs_coeff_nonnegative": cert_nonneg,
        "certificate_rhs_negative_terms": cert_bad,
        "multiplier_UA_coeff_nonnegative": mult_A_nonneg,
        "multiplier_UA_negative_terms": mult_A_bad,
        "multiplier_UB_coeff_nonnegative": mult_B_nonneg,
        "multiplier_UB_negative_terms": mult_B_bad,
        "degrees": {
            "target": sp.Poly(target, A, B, T).total_degree(),
            "cert_rhs_in_aux_vars": sp.Poly(cert_rhs, A, B, T, UA, UB).total_degree(),
            "substituted_rhs": sp.Poly(substituted_rhs, A, B, T).total_degree(),
        },
        "verified": identity_residual == 0 and cert_nonneg and mult_A_nonneg and mult_B_nonneg,
    }
    out = Path("tmp/eq_bank_cert1_conic_core_v1_summary.json")
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS eq bank cert1 conic core "
        f"identity_zero={summary['identity_residual_zero']} coeff_nonneg={summary['certificate_rhs_coeff_nonnegative']}"
    )
    return 0 if summary["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
