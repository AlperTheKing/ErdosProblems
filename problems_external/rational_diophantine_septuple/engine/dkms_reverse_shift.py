#!/usr/bin/env python3
"""Exact reverse-shift reduction for the DKMS rational sextuple family."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import sympy as sp


t = sp.symbols("t")


def rat(expr: sp.Expr) -> sp.Expr:
    return sp.cancel(expr)


def dkms_family() -> dict[str, sp.Expr]:
    a = rat(18 * t * (t - 1) * (t + 1) / ((t**2 - 6*t + 1) * (t**2 + 6*t + 1)))
    b = rat((t - 1) * (t**2 + 6*t + 1)**2 /
            (6 * t * (t + 1) * (t**2 - 6*t + 1)))
    c = rat((t + 1) * (t**2 - 6*t + 1)**2 /
            (6 * t * (t - 1) * (t**2 + 6*t + 1)))

    d1 = (
        6 * (t + 1) * (t - 1) * (t**2 + 6*t + 1) * (t**2 - 6*t + 1)
        * (8*t**6 + 27*t**5 + 24*t**4 - 54*t**3 + 24*t**2 + 27*t + 8)
        * (8*t**6 - 27*t**5 + 24*t**4 + 54*t**3 + 24*t**2 - 27*t + 8)
        * (t**8 + 22*t**6 - 174*t**4 + 22*t**2 + 1)
    )
    d2 = t * (37*t**12 - 885*t**10 + 9735*t**8 - 13678*t**6
              + 9735*t**4 - 885*t**2 + 37)**2

    e1 = (
        -2 * t * (4*t**6 - 111*t**4 + 18*t**2 + 25)
        * (3*t**7 + 14*t**6 - 42*t**5 + 30*t**4 + 51*t**3 + 18*t**2 - 12*t + 2)
        * (3*t**7 - 14*t**6 - 42*t**5 - 30*t**4 + 51*t**3 - 18*t**2 - 12*t - 2)
        * (t**2 + 3*t - 2) * (t**2 - 3*t - 2)
        * (2*t**2 + 3*t - 1) * (2*t**2 - 3*t - 1)
        * (t**2 + 7) * (7*t**2 + 1)
    )
    e2 = (
        3 * (t + 1) * (t**2 - 6*t + 1) * (t - 1) * (t**2 + 6*t + 1)
        * (16*t**14 + 141*t**12 - 1500*t**10 + 7586*t**8
           - 2724*t**6 + 165*t**4 + 424*t**2 - 12)**2
    )

    f1 = (
        2 * t * (25*t**6 + 18*t**4 - 111*t**2 + 4)
        * (2*t**7 - 12*t**6 + 18*t**5 + 51*t**4 + 30*t**3 - 42*t**2 + 14*t + 3)
        * (2*t**7 + 12*t**6 + 18*t**5 - 51*t**4 + 30*t**3 + 42*t**2 + 14*t - 3)
        * (2*t**2 + 3*t - 1) * (2*t**2 - 3*t - 1)
        * (t**2 - 3*t - 2) * (t**2 + 3*t - 2)
        * (t**2 + 7) * (7*t**2 + 1)
    )
    f2 = (
        3 * (t + 1) * (t**2 - 6*t + 1) * (t - 1) * (t**2 + 6*t + 1)
        * (12*t**14 - 424*t**12 - 165*t**10 + 2724*t**8
           - 7586*t**6 + 1500*t**4 - 141*t**2 - 16)**2
    )
    return {"a": a, "b": b, "c": c, "d": rat(d1/d2),
            "e": rat(e1/e2), "f": rat(f1/f2)}


def rational_square_class(value: sp.Rational) -> tuple[sp.Integer, sp.Rational]:
    value = sp.Rational(value)
    sign = -1 if value < 0 else 1
    value = abs(value)
    num = int(value.p)
    den = int(value.q)
    sf_num = 1
    sf_den = 1
    for prime, exponent in sp.factorint(num).items():
        if exponent % 2:
            sf_num *= int(prime)
    for prime, exponent in sp.factorint(den).items():
        if exponent % 2:
            sf_den *= int(prime)
    representative = sp.Integer(sign * sf_num * sf_den)
    square = sp.Rational(value / abs(representative))
    root_num = math.isqrt(int(square.p))
    root_den = math.isqrt(int(square.q))
    if root_num * root_num != int(square.p) or root_den * root_den != int(square.q):
        raise ArithmeticError("constant square-class decomposition failed")
    return representative, sp.Rational(root_num, root_den)


def square_decomposition(expr: sp.Expr) -> tuple[sp.Expr, sp.Expr]:
    """Return q,h with expr=q*h^2 and q a square-class polynomial."""
    expr = rat(expr)
    numerator, denominator = sp.fraction(expr)
    coefficient_n, factors_n = sp.factor_list(numerator, t)
    coefficient_d, factors_d = sp.factor_list(denominator, t)
    constant_rep, constant_root = rational_square_class(
        sp.Rational(coefficient_n) / sp.Rational(coefficient_d)
    )
    q = sp.Integer(constant_rep)
    h_num = sp.sympify(constant_root)
    h_den = sp.Integer(1)
    for factor, exponent in factors_n:
        factor = sp.Poly(factor, t, domain=sp.QQ).as_expr()
        if exponent % 2:
            q *= factor
        h_num *= factor ** (exponent // 2)
    for factor, exponent in factors_d:
        factor = sp.Poly(factor, t, domain=sp.QQ).as_expr()
        if exponent % 2:
            q *= factor
        h_den *= factor ** ((exponent + 1) // 2 if exponent % 2 else exponent // 2)
    q = sp.Poly(sp.expand(q), t, domain=sp.QQ).as_expr()
    h = rat(h_num / h_den)
    if rat(expr - q*h*h) != 0:
        raise ArithmeticError("rational-function square decomposition failed")
    return q, h


def canonical(expr: sp.Expr) -> dict[str, object]:
    numerator, denominator = sp.fraction(rat(expr))
    numerator = sp.Poly(numerator, t, domain=sp.QQ)
    denominator = sp.Poly(denominator, t, domain=sp.QQ)
    payload = f"{numerator.as_expr()}/{denominator.as_expr()}"
    return {
        "numerator": str(numerator.as_expr()),
        "denominator": str(denominator.as_expr()),
        "numerator_degree": int(numerator.degree()),
        "denominator_degree": int(denominator.degree()),
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest().upper(),
    }


def branch_data(q1: sp.Expr, q2: sp.Expr) -> dict[str, object]:
    p1 = sp.Poly(q1, t, domain=sp.QQ).sqf_part().monic()
    p2 = sp.Poly(q2, t, domain=sp.QQ).sqf_part().monic()
    common = sp.gcd(p1, p2)
    union = sp.lcm(p1, p2).monic()
    infinity = bool((p1.degree() % 2) or (p2.degree() % 2))
    branch_count = int(union.degree()) + int(infinity)
    product_q, _ = square_decomposition(q1*q2)
    dependent = any(sp.Poly(q, t, domain=sp.QQ).degree() == 0
                    for q in (q1, q2, product_q))
    return {
        "q1_degree": int(p1.degree()),
        "q2_degree": int(p2.degree()),
        "common_degree": int(common.degree()),
        "union_degree": int(union.degree()),
        "infinity_branched": infinity,
        "branch_count": branch_count,
        "connected_v4": not dependent,
        "genus_if_connected": branch_count - 3 if not dependent else None,
        "q1_factorization": str(sp.factor(q1)),
        "q2_factorization": str(sp.factor(q2)),
        "q1q2_square_class": str(sp.factor(product_q)),
    }


def run() -> dict[str, object]:
    values = dkms_family()
    names = list(values)
    pair_checks: list[dict[str, object]] = []
    pair_roots: dict[tuple[str, str], sp.Expr] = {}
    for i, left in enumerate(names):
        for right in names[i+1:]:
            q, root = square_decomposition(1 + values[left]*values[right])
            if q != 1:
                raise ArithmeticError(f"published pair is not a square: {left},{right}; q={q}")
            pair_roots[(left, right)] = root
            pair_roots[(right, left)] = root
            pair_checks.append({"pair": [left, right], "root": canonical(root)})

    a, b, c, d, e, f = (values[name] for name in names)
    leading = rat(d*e*f)
    quadratic = rat(d*e + d*f + e*f)
    s = rat(1/leading)
    y_a = rat(pair_roots[("a", "d")] * pair_roots[("a", "e")] * pair_roots[("a", "f")])
    y_s = rat(pair_roots[("d", "e")] * pair_roots[("d", "f")] * pair_roots[("e", "f")] / leading)
    curve = lambda x: rat((d*x + 1)*(e*x + 1)*(f*x + 1))
    if rat(y_a*y_a - curve(a)) != 0 or rat(y_s*y_s - curve(s)) != 0:
        raise ArithmeticError("reverse-curve point reconstruction failed")

    slopes = {
        "plus": rat((y_a-y_s)/(a-s)),
        "minus": rat((y_a+y_s)/(a-s)),
    }
    results: dict[str, object] = {}
    residual_q: dict[str, tuple[sp.Expr, sp.Expr]] = {}
    for sign, slope in slopes.items():
        g = rat((slope*slope-quadratic)/leading-a-s)
        automatic: dict[str, object] = {}
        for name in ("a", "d", "e", "f"):
            q, root = square_decomposition(1 + values[name]*g)
            automatic[name] = {"square": q == 1, "q": str(sp.factor(q)),
                               "root": canonical(root) if q == 1 else None}
            if q != 1:
                raise ArithmeticError(f"automatic bridge failed for {sign},{name}")
        q_b, h_b = square_decomposition(1 + b*g)
        q_c, h_c = square_decomposition(1 + c*g)
        residual_q[sign] = (q_b, q_c)
        results[sign] = {
            "g": canonical(g),
            "automatic": automatic,
            "b_residual": {"q": canonical(q_b), "h": canonical(h_b), "is_square": q_b == 1},
            "c_residual": {"q": canonical(q_c), "h": canonical(h_c), "is_square": q_c == 1},
            "cover": branch_data(q_b, q_c),
        }

    return {
        "status": "EXACT_REDUCTION_COMPLETE",
        "parameter": "t",
        "family": {name: canonical(value) for name, value in values.items()},
        "published_pair_checks": pair_checks,
        "reverse_points": {"y_a": canonical(y_a), "y_s": canonical(y_s)},
        "signs": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    result = run()
    output = run_dir / "reduction.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    digest = hashlib.sha256(output.read_bytes()).hexdigest().upper()
    print(json.dumps({"status": result["status"], "output": str(output), "sha256": digest,
                      "plus_genus": result["signs"]["plus"]["cover"]["genus_if_connected"],
                      "minus_genus": result["signs"]["minus"]["cover"]["genus_if_connected"]}))


if __name__ == "__main__":
    main()
