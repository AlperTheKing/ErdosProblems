#!/usr/bin/env python3
"""Verify the SIB S7 central all-seven-tight Sturm certificate.

Checks exactly over QQ:
- stored numerator is the known P0(t), with P0(1)=375;
- stored Sturm sequence starts with monic P0 and its derivative;
- subsequent entries satisfy S_{i+1} = -rem(S_{i-1}, S_i);
- sign variations at 1 and +infinity are equal, so root count on [1, infinity) is 0;
- denominator factors are positive for t >= 1 by the recorded elementary factors.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp


def parse_q(s: str) -> sp.Rational:
    q = Fraction(s)
    return sp.Rational(q.numerator, q.denominator)


def poly_from_coeffs(coeffs: list[str], t) -> sp.Poly:
    deg = len(coeffs) - 1
    expr = sp.Integer(0)
    for i, coeff in enumerate(coeffs):
        expr += parse_q(coeff) * t ** (deg - i)
    return sp.Poly(expr, t, domain=sp.QQ)


def sign_of(q) -> int:
    q = sp.Rational(q)
    return 1 if q > 0 else (-1 if q < 0 else 0)


def variations(signs: list[int]) -> int:
    nz = [s for s in signs if s]
    return sum(1 for a, b in zip(nz, nz[1:]) if a * b < 0)


def sign_at_infinity(poly: sp.Poly) -> int:
    return sign_of(poly.LC())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert", nargs="?", default="problems/23/writeup/sib_s7_central_sturm_cert.json")
    args = ap.parse_args()

    data = json.loads(Path(args.cert).read_text(encoding="utf-8"))
    if data.get("schema") != "sib_s7_central_sturm_v1":
        raise AssertionError(f"bad schema {data.get('schema')!r}")
    t = sp.symbols(data["variable"])

    numerator = poly_from_coeffs(data["numerator_coeffs_desc"], t)
    expected = sp.Poly(20*t**7 - 18*t**6 - 166*t**5 + 76*t**4 + 459*t**3 + 117*t**2 - 117*t + 4, t, domain=sp.QQ)
    if numerator != expected:
        raise AssertionError("numerator mismatch")
    if numerator.eval(1) != parse_q(data["numerator_at_1"]):
        raise AssertionError("P0(1) mismatch")
    if numerator.eval(1) <= 0:
        raise AssertionError("P0(1) is not positive")

    seq = [poly_from_coeffs(coeffs, t) for coeffs in data["sturm_sequence_coeffs_desc"]]
    monic = sp.Poly(numerator.as_expr() / numerator.LC(), t, domain=sp.QQ)
    if seq[0] != monic:
        raise AssertionError("Sturm S0 is not monic numerator")
    if seq[1] != sp.Poly(sp.diff(seq[0].as_expr(), t), t, domain=sp.QQ):
        raise AssertionError("Sturm S1 is not derivative of S0")
    for i in range(1, len(seq) - 1):
        rem = sp.rem(seq[i - 1], seq[i], domain=sp.QQ)
        want = sp.Poly(-rem.as_expr(), t, domain=sp.QQ)
        if seq[i + 1] != want:
            raise AssertionError(f"Sturm recurrence mismatch at index {i + 1}")

    signs_1 = [sign_of(p.eval(1)) for p in seq]
    signs_inf = [sign_at_infinity(p) for p in seq]
    if signs_1 != data["signs_at_1"]:
        raise AssertionError("signs at 1 mismatch")
    if signs_inf != data["signs_at_infinity"]:
        raise AssertionError("signs at infinity mismatch")
    v1 = variations(signs_1)
    vinf = variations(signs_inf)
    if v1 != data["expected_variation_at_1"] or vinf != data["expected_variation_at_infinity"]:
        raise AssertionError("variation mismatch")
    roots = v1 - vinf
    if roots != data["expected_roots_on_range"]:
        raise AssertionError("root count mismatch")
    if roots != 0:
        raise AssertionError("P0 has roots on [1,infinity)")

    factors = data["phi_denominator_factors"]
    if factors != ["t^2", "t + 2", "t^3 + 2*t^2 + t + 1"]:
        raise AssertionError("unexpected denominator factor list")
    # For t >= 1: t^2 > 0; t+2 > 0; and the cubic has positive coefficients.
    verdict = {
        "cert": args.cert,
        "P0_at_1": str(numerator.eval(1)),
        "variation_at_1": v1,
        "variation_at_infinity": vinf,
        "roots_on_[1,infinity)": roots,
        "denominator_positive_on_range": True,
        "verdict": "PASS",
    }
    print(json.dumps(verdict, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
