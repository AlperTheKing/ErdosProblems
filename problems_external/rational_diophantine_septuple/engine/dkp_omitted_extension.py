#!/usr/bin/env python3
"""Exact reconstruction of the omitted second regular extension in DKP 2019."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import sympy as sp


u, t, x = sp.symbols("u t x")


def rat(expr: sp.Expr) -> sp.Expr:
    return sp.cancel(expr)


def rational_square_class(value: sp.Rational) -> sp.Integer:
    value = sp.Rational(value)
    sign = -1 if value < 0 else 1
    value = abs(value)
    representative = sign
    for prime, exponent in sp.factorint(int(value.p)).items():
        if exponent % 2:
            representative *= int(prime)
    for prime, exponent in sp.factorint(int(value.q)).items():
        if exponent % 2:
            representative *= int(prime)
    return sp.Integer(representative)


def square_class(expr: sp.Expr) -> sp.Expr:
    numerator, denominator = sp.fraction(rat(expr))
    coefficient_n, factors_n = sp.factor_list(numerator, u, t)
    coefficient_d, factors_d = sp.factor_list(denominator, u, t)
    q = rational_square_class(sp.Rational(coefficient_n) / sp.Rational(coefficient_d))
    for factor, exponent in factors_n + factors_d:
        if exponent % 2:
            q *= factor
    return sp.factor(q)


def primitive_polynomial(expr: sp.Expr) -> sp.Poly:
    poly = sp.Poly(sp.expand(expr), u, t, domain=sp.QQ)
    _, primitive = poly.primitive()
    primitive = sp.Poly(primitive, u, t, domain=sp.ZZ)
    if primitive.LC() < 0:
        primitive = -primitive
    return primitive


def canonical(expr: sp.Expr) -> dict[str, object]:
    numerator, denominator = sp.fraction(rat(expr))
    numerator_poly = sp.Poly(sp.expand(numerator), u, t, domain=sp.QQ)
    denominator_poly = sp.Poly(sp.expand(denominator), u, t, domain=sp.QQ)
    payload = f"{numerator_poly.as_expr()}/{denominator_poly.as_expr()}"
    return {
        "numerator": str(numerator_poly.as_expr()),
        "denominator": str(denominator_poly.as_expr()),
        "numerator_degree_u": int(numerator_poly.degree(u)),
        "numerator_degree_t": int(numerator_poly.degree(t)),
        "denominator_degree_u": int(denominator_poly.degree(u)),
        "denominator_degree_t": int(denominator_poly.degree(t)),
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest().upper(),
    }


def family() -> dict[str, sp.Expr]:
    t3 = rat((16-u**2)/(6*u))
    t2 = rat((u**2+10*u+16)/((u-4)*(u+4)))
    common = (-1+t*t2*t3)*(1+t*t2*t3)
    a1 = rat(2*t*(1+t*t2*(1+t2*t3))/common)
    a2 = rat(2*t2*(1+t2*t3*(1+t3*t))/common)
    a3 = rat(2*t3*(1+t3*t*(1+t*t2))/common)
    a4 = rat(-2*(1-t3+t2*t3)*(t3*t+1-t)*(-t2+1+t*t2)*(-1+t*t2*t3)
             /(1+t*t2*t3)**3)
    a5 = rat(2*(t3+t2*t3+1)*(t3*t+t+1)*(1+t2+t*t2)*(1+t*t2*t3)
             /(-1+t*t2*t3)**3)
    d6 = (
        4096*t**2 + 15360*t**2*u + 15168*t**2*u**2 + 5920*t**2*u**3
        + 948*t**2*u**4 + 60*t**2*u**5 + t**2*u**6 - 12288*t*u
        - 7680*t*u**2 + 480*t*u**4 + 48*t*u**5 - 5184*u**2
        - 2592*u**3 - 324*u**4
    )
    a6 = rat(
        6*(u+4)*(u+8)*(u+2)*(u-4)
        *(2*t*u**2+3*u**2+20*t*u+12*u+32*t)
        *(t*u**2+10*t*u+16*t-6*u)
        *(t*u**2+10*t*u+16*t+6*u)
        *(t*u**2+10*t*u+16*t-24-6*u) / d6**2
    )
    return {"a1": a1, "a2": a2, "a3": a3, "a4": a4, "a5": a5, "a6": a6}


def h_quartic() -> sp.Expr:
    a4 = (u**12+120*u**11+5496*u**10+125600*u**9+1639440*u**8
          +13075200*u**7+65656320*u**6+209203200*u**5+419696640*u**4
          +514457600*u**3+360185856*u**2+125829120*u+16777216)
    a3 = (24*u**12+1296*u**11+32256*u**10+446208*u**9+3461760*u**8
          +13047552*u**7-208760832*u**5-886210560*u**4-1827667968*u**3
          -2113929216*u**2-1358954496*u-402653184)
    a2 = (36*u**12+1296*u**11+18072*u**10+48096*u**9-1681632*u**8
          -22516992*u**7-127051776*u**6-360271872*u**5-430497792*u**4
          +197001216*u**3+1184366592*u**2+1358954496*u+603979776)
    a1 = (-432*u**11-15552*u**10-259200*u**9-2267136*u**8-9116928*u**7
          +145870848*u**5+580386816*u**4+1061683200*u**3
          +1019215872*u**2+452984832*u)
    a0 = (1296*u**10+41472*u**9+670032*u**8+6054912*u**7+31643136*u**6
          +96878592*u**5+171528192*u**4+169869312*u**3+84934656*u**2)
    return sp.expand(a4*t**4+a3*t**3+a2*t**2+a1*t+a0)


def is_rational_square(value: sp.Rational) -> bool:
    value = sp.Rational(value)
    if value < 0:
        return False
    return (math.isqrt(int(value.p))**2 == int(value.p)
            and math.isqrt(int(value.q))**2 == int(value.q))


def run() -> dict[str, object]:
    values = family()
    a1, a2, a3, a4, a5, a6 = (values[f"a{i}"] for i in range(1, 7))
    pair_checks: list[dict[str, object]] = []
    first_five = [a1, a2, a3, a4, a5]
    for i in range(5):
        for j in range(i+1, 5):
            q = square_class(1+first_five[i]*first_five[j])
            if q != 1:
                raise ArithmeticError(f"quintuple identity failed: a{i+1},a{j+1}; q={q}")
            pair_checks.append({"pair": [f"a{i+1}", f"a{j+1}"], "square_class": "1"})

    A = rat(a1*a3*a4*a5)
    B = rat(2*a1*a3*a4+a1+a3+a4-a5)
    K = rat((a1*a3+1)*(a1*a4+1)*(a3*a4+1))
    c2 = (A-1)**2
    c1 = 2*(A-1)*B-4*K*a5
    c0 = B**2-4*K
    a7 = rat(c0/(c2*a6))
    values["a7"] = a7

    vieta_samples = []
    for u_value, t_value in ((1, 2), (2, 3), (3, 2), (5, 1)):
        substitutions = {u: sp.Rational(u_value), t: sp.Rational(t_value)}
        sample_c2 = rat(c2.subs(substitutions))
        sample_c1 = rat(c1.subs(substitutions))
        sample_c0 = rat(c0.subs(substitutions))
        sample_a6 = rat(a6.subs(substitutions))
        sample_a7 = rat(a7.subs(substitutions))
        if sample_c2 == 0 or sample_a6 == 0:
            raise ArithmeticError(f"degenerate Vieta calibration sample: {u_value},{t_value}")
        if rat(sample_c2*sample_a6**2+sample_c1*sample_a6+sample_c0) != 0:
            raise ArithmeticError(f"a6 Vieta calibration failed: {u_value},{t_value}")
        if rat(sample_c2*sample_a7**2+sample_c1*sample_a7+sample_c0) != 0:
            raise ArithmeticError(f"a7 Vieta calibration failed: {u_value},{t_value}")
        vieta_samples.append([u_value, t_value])

    for extension_name, extension in (("a6", a6), ("a7", a7)):
        for base_name, base in (("a1", a1), ("a3", a3), ("a4", a4), ("a5", a5)):
            q = square_class(1+extension*base)
            if q != 1:
                raise ArithmeticError(f"regular extension identity failed: {extension_name},{base_name}")

    H = h_quartic()
    if square_class((1+a2*a6)/H) != 1:
        raise ArithmeticError("published H square-class calibration failed")

    final_t = rat(3*(3*u**4+40*u**3+368*u**2+1280*u+1024)
                  /(4*(u**2+10*u+16)*(u+20)*u))
    published = [
        sp.Rational(27900,17479), sp.Rational(471352,112365),
        sp.Rational(261770,17479), sp.Rational(185535272,419265),
        sp.Rational(63737828,526368735), sp.Rational(79554420,408480247),
    ]
    specialized = [rat(rat(values[f"a{i}"].subs(t, final_t)).subs(u, -1))
                   for i in range(1, 7)]
    if specialized != published:
        raise ArithmeticError("published u=-1 sextuple mismatch")
    a7_special = rat(rat(a7.subs(t, final_t)).subs(u, -1))
    expected_a7 = sp.Rational(92944770896732495812600137840,
                              168403068682816328488636086769)
    if a7_special != expected_a7:
        raise ArithmeticError("omitted-root u=-1 calibration mismatch")
    missing_special = {
        "a2_a7": str(sp.factor(1+published[1]*a7_special)),
        "a6_a7": str(sp.factor(1+published[5]*a7_special)),
        "a2_a7_square": is_rational_square(1+published[1]*a7_special),
        "a6_a7_square": is_rational_square(1+published[5]*a7_special),
    }

    G = rat((A-3)**2-4*(a1*a3+a4*a5+3))
    g_numerator, g_denominator = sp.fraction(G)
    coefficient, raw_factors = sp.factor_list(g_numerator, u, t)
    factors: list[dict[str, object]] = []
    for factor, exponent in raw_factors:
        poly = primitive_polynomial(factor)
        text = str(poly.as_expr())
        factors.append({
            "polynomial": text,
            "exponent": int(exponent),
            "degree_u": int(poly.degree(u)),
            "degree_t": int(poly.degree(t)),
            "total_degree": int(poly.total_degree()),
            "terms": len(poly.terms()),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest().upper(),
        })
    if len(factors) != 4 or any(item["exponent"] != 1 for item in factors):
        raise ArithmeticError(f"unexpected G factorization: {len(factors)} factors")

    residual = rat(1+a2*a7)
    return {
        "status": "EXACT_RECONSTRUCTION_COMPLETE",
        "source_typo_normalization": "24*u^12++1296*u^11 interpreted as one plus",
        "quintuple_pair_checks": pair_checks,
        "regular_extension_checks": 8,
        "vieta_derivation": "a7=c0/(c2*a6) from the published quadratic",
        "vieta_exact_samples": vieta_samples,
        "published_u_minus_1": {
            "sextuple": [str(item) for item in specialized],
            "a7": str(a7_special),
            "missing_pairs": missing_special,
        },
        "functions": {name: canonical(value) for name, value in values.items()},
        "H": canonical(H),
        "G": {
            "denominator": canonical(g_denominator),
            "factor_coefficient": str(coefficient),
            "factors": factors,
        },
        "residual_a2_a7": canonical(residual),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    result = run()
    output = run_dir / "reconstruction.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    digest = hashlib.sha256(output.read_bytes()).hexdigest().upper()
    print(json.dumps({"status": result["status"], "output": str(output), "sha256": digest,
                      "g_factors": [(f["degree_u"], f["degree_t"], f["terms"])
                                    for f in result["G"]["factors"]]}))


if __name__ == "__main__":
    main()
