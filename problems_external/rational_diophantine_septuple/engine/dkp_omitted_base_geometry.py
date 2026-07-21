#!/usr/bin/env python3
"""Exact base-curve geometry audit for the DKP omitted-root route.

The four primitive Piezas factors are imported from the independent factor
audit transcript embedded in ``dkp_omitted_mod_geometry``.  This script works
over Q only.  It proves irreducibility, certifies a smooth rational point,
computes the complete singular support on P1 x P1 by Groebner elimination,
and resolves every singularity by exact blowups.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

from dkp_omitted_mod_geometry import FI_EXPRESSIONS


u, t = sp.symbols("u t")
X, Y, Z = sp.symbols("X Y Z")

EXPECTED_HASHES = [
    "BE54330E3F799B7E2134F9099145B2CE6559A7A0EC298A7C342CA2D40C39F5F8",
    "A095DC03815EAE091B3F77F83A097F4465CF95BEBF00BE75830503ED161EDF15",
    "A4970ED27A4BF0FD37D08894B9F3709A5DA5867D67FF4906595635EF1E7F3B2B",
    "09C8655ECD6B22DD9AE526DBA17C553903868689704D0BC993C5D383B4C060E5",
]

SMOOTH_RATIONAL_POINTS = [
    (sp.Rational(-8), sp.Rational(-1, 4)),
    (sp.Rational(-2), sp.Rational(3, 4)),
    (sp.Rational(-8), sp.Rational(-3, 4)),
    (sp.Rational(-2), sp.Rational(1, 4)),
]


def canonical_hash(poly: sp.Poly) -> str:
    terms = [[*monomial, str(coefficient)] for monomial, coefficient in poly.terms()]
    payload = json.dumps(
        {"generators": ["u", "t"], "terms": terms},
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("ascii")).hexdigest().upper()


def inverted_chart(poly: sp.Poly, invert_u: bool, invert_t: bool) -> sp.Poly:
    du = poly.degree(u)
    dt = poly.degree(t)
    expr = 0
    for (iu, it), coefficient in poly.terms():
        expr += coefficient * u ** (du - iu if invert_u else iu) * t ** (
            dt - it if invert_t else it
        )
    return sp.Poly(expr, u, t, domain=sp.QQ)


def jacobian_groebner(poly: sp.Poly) -> sp.GroebnerBasis:
    expr = poly.as_expr()
    return sp.groebner(
        [expr, sp.diff(expr, u), sp.diff(expr, t)],
        t,
        u,
        domain=sp.QQ,
        order="lex",
    )


def elimination_factorization(basis: sp.GroebnerBasis) -> str:
    eliminants = [item for item in basis.polys if item.degree(t) == 0]
    if len(eliminants) != 1:
        raise AssertionError(f"expected one u-eliminant, got {len(eliminants)}")
    return str(sp.factor(eliminants[0].as_expr()))


def singular_fiber_gcd(poly: sp.Poly, u0: sp.Rational) -> sp.Poly:
    expr = poly.as_expr()
    entries = [
        sp.Poly(item.subs(u, u0), t, domain=sp.QQ)
        for item in (expr, sp.diff(expr, u), sp.diff(expr, t))
    ]
    result = sp.gcd(entries[0], sp.gcd(entries[1], entries[2]))
    return sp.Poly(result.monic(), t, domain=sp.QQ)


def local_polynomial(poly: sp.Poly, u0: sp.Rational, t0: sp.Rational) -> sp.Poly:
    return sp.Poly(
        sp.expand(poly.as_expr().subs({u: X + u0, t: Y + t0})),
        X,
        Y,
        domain=sp.QQ,
    )


def tangent_cone(poly: sp.Poly) -> tuple[int, sp.Poly]:
    multiplicity = min(sum(monomial) for monomial, _ in poly.terms())
    cone = sp.Poly(
        sum(
            coefficient * X**monomial[0] * Y**monomial[1]
            for monomial, coefficient in poly.terms()
            if sum(monomial) == multiplicity
        ),
        X,
        Y,
        domain=sp.QQ,
    )
    return multiplicity, cone


def resolve_unique_repeated_tangent(poly: sp.Poly) -> dict[str, object]:
    multiplicities: list[int] = []
    tangent_factors: list[str] = []
    for _ in range(12):
        multiplicity, cone = tangent_cone(poly)
        multiplicities.append(multiplicity)
        tangent_factors.append(str(sp.factor(cone.as_expr())))
        _, factors = sp.factor_list(cone.as_expr(), X, Y)
        repeated = [
            (sp.Poly(factor, X, Y, domain=sp.QQ), exponent)
            for factor, exponent in factors
            if exponent > 1
        ]
        if not repeated:
            delta = sum(value * (value - 1) // 2 for value in multiplicities)
            return {
                "multiplicity_sequence": multiplicities,
                "tangent_cones": tangent_factors,
                "resolved": True,
                "delta": delta,
            }
        if len(repeated) != 1 or repeated[0][0].total_degree() != 1:
            raise AssertionError(f"unhandled repeated tangent: {repeated}")

        linear = repeated[0][0]
        a = linear.coeff_monomial(X)
        b = linear.coeff_monomial(Y)
        expr = poly.as_expr()
        if b != 0:
            slope = -a / b
            transformed = sp.cancel(expr.subs(Y, X * (slope + Y)) / X**multiplicity)
        else:
            temporary = sp.cancel(expr.subs(X, Y * Z) / Y**multiplicity)
            transformed = temporary.subs({Y: X, Z: Y}, simultaneous=True)
        poly = sp.Poly(sp.expand(transformed), X, Y, domain=sp.QQ)
    raise AssertionError("blowup depth exceeded")


def audit_factor(index: int, expression: str) -> dict[str, object]:
    poly = sp.Poly(sp.sympify(expression, locals={"u": u, "t": t}), u, t, domain=sp.QQ)
    if (poly.degree(u), poly.degree(t)) != (10, 4):
        raise AssertionError("unexpected bidegree")
    digest = canonical_hash(poly)
    if digest != EXPECTED_HASHES[index - 1]:
        raise AssertionError("factor hash mismatch")

    coefficient, factors = sp.factor_list(poly.as_expr(), u, t)
    irreducible_over_q = (
        coefficient == 1
        and len(factors) == 1
        and factors[0][1] == 1
        and sp.Poly(factors[0][0], u, t, domain=sp.QQ) == poly
    )
    if not irreducible_over_q:
        raise AssertionError("factor is reducible over Q")

    point = SMOOTH_RATIONAL_POINTS[index - 1]
    value = sp.cancel(poly.as_expr().subs({u: point[0], t: point[1]}))
    du_value = sp.cancel(sp.diff(poly.as_expr(), u).subs({u: point[0], t: point[1]}))
    dt_value = sp.cancel(sp.diff(poly.as_expr(), t).subs({u: point[0], t: point[1]}))
    smooth_point = value == 0 and (du_value != 0 or dt_value != 0)
    if not smooth_point:
        raise AssertionError("rational smooth-point certificate failed")

    affine = poly
    u_infinity = inverted_chart(poly, True, False)
    t_infinity = inverted_chart(poly, False, True)
    both_infinity = inverted_chart(poly, True, True)
    bases = {
        "finite": jacobian_groebner(affine),
        "u_infinity": jacobian_groebner(u_infinity),
        "t_infinity": jacobian_groebner(t_infinity),
    }
    elimination = {name: elimination_factorization(basis) for name, basis in bases.items()}

    if elimination["finite"] != "u**6" or elimination["u_infinity"] != "u**6":
        raise AssertionError(f"unexpected finite-boundary support: {elimination}")
    t_inf_poly = sp.Poly(
        [item for item in bases["t_infinity"].polys if item.degree(t) == 0][0],
        u,
        domain=sp.QQ,
    )
    _, t_inf_factors = sp.factor_list(t_inf_poly.as_expr(), u)
    t_inf_support = {str(sp.factor(factor)) for factor, _ in t_inf_factors}
    if t_inf_support != {"u + 2", "u + 8"}:
        raise AssertionError(f"unexpected t-infinity support: {t_inf_support}")
    if both_infinity.eval({u: 0, t: 0}) == 0:
        raise AssertionError("the (infinity,infinity) corner unexpectedly lies on the curve")

    fiber_gcds = {
        "finite_u=0": str(sp.factor(singular_fiber_gcd(affine, sp.Rational(0)).as_expr())),
        "u_infinity_v=0": str(
            sp.factor(singular_fiber_gcd(u_infinity, sp.Rational(0)).as_expr())
        ),
        "t_infinity_u=-8": str(
            sp.factor(singular_fiber_gcd(t_infinity, sp.Rational(-8)).as_expr())
        ),
        "t_infinity_u=-2": str(
            sp.factor(singular_fiber_gcd(t_infinity, sp.Rational(-2)).as_expr())
        ),
    }
    if any(sp.Poly(value, t, domain=sp.QQ).sqf_part().monic() != sp.Poly(t, t, domain=sp.QQ)
           for value in fiber_gcds.values()):
        raise AssertionError(f"a candidate singular fiber contains t != 0: {fiber_gcds}")

    singularities = [
        ("u=0,t=0", affine, sp.Rational(0), sp.Rational(0)),
        ("u=infinity,t=0", u_infinity, sp.Rational(0), sp.Rational(0)),
        ("u=-8,t=infinity", t_infinity, sp.Rational(-8), sp.Rational(0)),
        ("u=-2,t=infinity", t_infinity, sp.Rational(-2), sp.Rational(0)),
    ]
    resolutions: list[dict[str, object]] = []
    for name, chart_poly, u0, t0 in singularities:
        expr = chart_poly.as_expr()
        if any(
            sp.cancel(item.subs({u: u0, t: t0})) != 0
            for item in (expr, sp.diff(expr, u), sp.diff(expr, t))
        ):
            raise AssertionError(f"listed point is not singular: {name}")
        record = resolve_unique_repeated_tangent(local_polynomial(chart_poly, u0, t0))
        resolutions.append({"point": name, **record})

    total_delta = sum(int(item["delta"]) for item in resolutions)
    arithmetic_genus = (poly.degree(u) - 1) * (poly.degree(t) - 1)
    geometric_genus = arithmetic_genus - total_delta
    if total_delta != 22 or geometric_genus != 5:
        raise AssertionError(
            f"unexpected genus: pa={arithmetic_genus}, delta={total_delta}, g={geometric_genus}"
        )

    return {
        "factor": index,
        "sha256": digest,
        "bidegree": [10, 4],
        "term_count": len(poly.terms()),
        "irreducible_over_Q": irreducible_over_q,
        "smooth_rational_point": {
            "u": str(point[0]),
            "t": str(point[1]),
            "F": str(value),
            "dF_du": str(du_value),
            "dF_dt": str(dt_value),
        },
        "absolutely_irreducible_reason": (
            "A Q-irreducible reduced curve with a smooth Q-point cannot have multiple "
            "Galois-conjugate geometric components, since the fixed point would lie on all of them."
        ),
        "jacobian_eliminants": elimination,
        "singular_fiber_gcds": fiber_gcds,
        "projective_singular_support": [item[0] for item in singularities],
        "infinity_infinity_value": str(both_infinity.eval({u: 0, t: 0})),
        "resolutions": resolutions,
        "arithmetic_genus": arithmetic_genus,
        "total_delta": total_delta,
        "normalization_genus": geometric_genus,
    }


def run() -> dict[str, object]:
    factors = [audit_factor(index, expression) for index, expression in enumerate(FI_EXPRESSIONS, 1)]
    return {
        "status": "EXACT_BASE_GEOMETRY_COMPLETE",
        "field": "Q",
        "ambient": "P1_u x P1_t",
        "factors": factors,
        "square_cover_consequence": {
            "saturated_dimension": 1,
            "generic_algebra_rank_over_each_base": 4,
            "square_class_rank_cases": {
                "0": {"normalization_components": 4, "degree_each": 1, "genus_lower_bound": 5},
                "1": {"normalization_components": 2, "degree_each": 2, "genus_lower_bound": 9},
                "2": {"normalization_components": 1, "degree_each": 4, "genus_lower_bound": 17},
            },
            "reason": (
                "After denominator/bad-locus saturation the two monic square equations are integral "
                "over Q(C_i). Every normalized horizontal component is a finite surjective separable "
                "cover of C_i. Riemann-Hurwitz gives g(X)>=d*(5-1)+1."
            ),
            "low_genus_component_possible": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
