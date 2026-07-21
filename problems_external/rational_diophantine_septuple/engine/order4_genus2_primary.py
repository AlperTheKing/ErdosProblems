#!/usr/bin/env python3
"""Freeze and verify the canonical-order-four genus-two quotient.

This engine performs exact arithmetic only.  It does not run Magma and it
does not test a septuple candidate.  Its outputs are the frozen rational
data, symbolic quotient checks, an integral even sextic, its two elliptic
quotients, and three Magma V2.29-8 rank inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from functools import reduce
from math import gcd, isqrt, prod
from pathlib import Path
from typing import Any

import sympy as sp


Q = Fraction

A = Q(1884586446094351, 25415891646864180)
B = Q(14442883687791636, 7402559392524605)
C = Q(60340495895762708555, 14487505263205637124)

EXPECTED_DERIVATION_SHA256 = (
    "7909C6EB9741F7C6560243E3BDA343B5D738ABD1DE4F1DD401BE85F34A71625C"
)
EXPECTED_FIXED_CHECKER_SHA256 = (
    "F88A731BC57547D3E6D18D51B039953477E53C539E4E0216436EF37DFA36FC39"
)


def qtext(value: Q) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def symq(value: Q) -> sp.Rational:
    return sp.Rational(value.numerator, value.denominator)


def exact_sqrt(value: Q) -> Q:
    if value < 0:
        raise AssertionError("negative rational is not a rational square")
    numerator = isqrt(value.numerator)
    denominator = isqrt(value.denominator)
    if numerator * numerator != value.numerator:
        raise AssertionError("numerator is not a square")
    if denominator * denominator != value.denominator:
        raise AssertionError("denominator is not a square")
    return Q(numerator, denominator)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest().upper()


def write_ascii(path: Path, value: str) -> None:
    path.write_text(value, encoding="ascii", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_ascii(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def multiply_polynomials(left: list[int], right: list[int]) -> list[int]:
    output = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            output[left_index + right_index] += left_value * right_value
    return output


def polynomial_text(coefficients: list[int], variable: str) -> str:
    terms: list[str] = []
    for exponent, coefficient in enumerate(coefficients):
        if coefficient == 0:
            continue
        atom = str(coefficient) if coefficient >= 0 else f"({coefficient})"
        if exponent == 0:
            terms.append(atom)
        elif exponent == 1:
            terms.append(f"{atom}*{variable}")
        else:
            terms.append(f"{atom}*{variable}^{exponent}")
    return " + ".join(terms)


def add_points(
    left: tuple[Q, Q] | None,
    right: tuple[Q, Q] | None,
    a2: Q,
    a4: Q,
) -> tuple[Q, Q] | None:
    """Add points on y^2=x^3+a2*x^2+a4*x+a6."""

    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and y1 == -y2:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = (3 * x1 * x1 + 2 * a2 * x1 + a4) / (2 * y1)
    else:
        if x1 == x2:
            raise AssertionError("invalid vertical addition case")
        slope = (y2 - y1) / (x2 - x1)
    x3 = slope * slope - a2 - x1 - x2
    y3 = -(y1 + slope * (x3 - x1))
    return x3, y3


def discriminant_record(polynomial: sp.Expr, variable: sp.Symbol) -> dict[str, Any]:
    value = int(sp.discriminant(polynomial, variable))
    if value == 0:
        raise AssertionError("singular polynomial")
    decimal = str(value)
    return {
        "nonzero": True,
        "sign": 1 if value > 0 else -1,
        "decimal_digits": len(str(abs(value))),
        "decimal_sha256": sha256_text(decimal),
    }


def magma_rank_input(
    label: str,
    coefficients: list[int],
    expected_degree: int,
    expected_genus: int,
) -> str:
    polynomial = polynomial_text(coefficients, "x")
    return "\n".join(
        [
            "Q := Rationals();",
            "R<x> := PolynomialRing(Q);",
            f'label := "{label}";',
            f"f := {polynomial};",
            f"assert Degree(f) eq {expected_degree};",
            "assert Discriminant(f) ne 0;",
            "C := HyperellipticCurve(f);",
            f"assert Genus(C) eq {expected_genus};",
            "J := Jacobian(C);",
            'print "LABEL", label;',
            'print "DEGREE", Degree(f);',
            'print "GENUS", Genus(C);',
            'print "COEFFICIENTS", Coefficients(f);',
            'print "DISCRIMINANT_NONZERO", Discriminant(f) ne 0;',
            "lower, upper := RankBounds(J);",
            'print "RANK_BOUNDS", lower, upper;',
            'print "DONE";',
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    arguments = parser.parse_args()
    run_dir = arguments.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)

    engine_path = Path(__file__).resolve()
    problem_dir = engine_path.parent.parent
    derivation_path = (
        problem_dir
        / "runs"
        / "next_route_audit_20260720T171905"
        / "order4_genus2_quotient.md"
    )
    fixed_checker_path = engine_path.parent / "order4_fixed_triple_check.py"
    if sha256(derivation_path) != EXPECTED_DERIVATION_SHA256:
        raise AssertionError("quotient derivation hash mismatch")
    if sha256(fixed_checker_path) != EXPECTED_FIXED_CHECKER_SHA256:
        raise AssertionError("fixed-source checker hash mismatch")

    p = A * B
    q = A * C
    r = B * C
    alpha = A * B * C
    pair_roots = {
        "r_ab": exact_sqrt(p + 1),
        "r_ac": exact_sqrt(q + 1),
        "r_bc": exact_sqrt(r + 1),
    }
    sigma = prod(pair_roots.values(), start=Q(1))

    e_a2 = p + q + r
    e_a4 = p * q + p * r + q * r
    e_a6 = p * q * r
    if e_a6 != alpha * alpha:
        raise AssertionError("alpha^2 != p*q*r")
    S = (Q(1), sigma)
    if sigma * sigma != (1 + p) * (1 + q) * (1 + r):
        raise AssertionError("canonical point is not on E")
    two_s = add_points(S, S, e_a2, e_a4)
    four_s = add_points(two_s, two_s, e_a2, e_a4)
    H = (-p, Q(0))
    if two_s != H or four_s is not None:
        raise AssertionError("canonical point does not have exact order four")

    A0 = q + r - 2 * p
    K = (q - p) * (r - p)
    if K != (1 + p) ** 2:
        raise AssertionError("order-four K identity failed")
    U0 = (1 + p) * q * r / p
    if U0 != C * C * (1 + p):
        raise AssertionError("U0 simplification failed")
    j = q + r + 2
    k = q + r - 4 * p - 2
    if j != A0 + 2 * (1 + p) or k != A0 - 2 * (1 + p):
        raise AssertionError("quotient root labeling failed")
    if len({Q(0), j, k}) != 3:
        raise AssertionError("quotient cubic has repeated roots")

    # Fixed exact symbolic checks for the two-isogeny quotient and diagonals.
    u = sp.symbols("u")
    sp_A0 = symq(A0)
    sp_K = symq(K)
    sp_p = symq(p)
    sp_U0 = symq(U0)
    sp_j = symq(j)
    sp_k = symq(k)
    sp_alpha = symq(alpha)
    e_u = u * (u**2 + sp_A0 * u + sp_K)
    quotient_u = u + sp_A0 + sp_K / u
    quotient_cubic = quotient_u * (
        quotient_u**2
        - 2 * sp_A0 * quotient_u
        + sp_A0**2
        - 4 * sp_K
    )
    quotient_map_identity = sp.cancel(
        e_u * (sp_K - u**2) ** 2 / u**4 - quotient_cubic
    )
    if quotient_map_identity != 0:
        raise AssertionError("two-isogeny quotient identity failed")

    quotient_factor_identity = sp.expand(
        sp.Symbol("U")
        * (
            sp.Symbol("U") ** 2
            - 2 * sp_A0 * sp.Symbol("U")
            + sp_A0**2
            - 4 * sp_K
        )
        - sp.Symbol("U")
        * (sp.Symbol("U") - sp_j)
        * (sp.Symbol("U") - sp_k)
    )
    if quotient_factor_identity != 0:
        raise AssertionError("quotient cubic factorization failed")

    x_value = u - sp_p
    x_after_h = sp_K / u - sp_p
    first_diagonal_identity = sp.cancel(
        x_value * x_after_h
        + sp_alpha**2
        - sp_p * (sp_U0 - quotient_u)
    )
    if first_diagonal_identity != 0:
        raise AssertionError("first diagonal quotient identity failed")

    U = sp.symbols("U")
    quotient_polynomial = U * (U - sp_j) * (U - sp_k)
    group_translate_j = sp.cancel(
        quotient_polynomial / (U - sp_j) ** 2
        + 2 * sp_A0
        - U
        - sp_j
    )
    stated_translate_j = sp_j + 4 * sp_j * (1 + sp_p) / (U - sp_j)
    translation_identity = sp.cancel(group_translate_j - stated_translate_j)
    if translation_identity != 0:
        raise AssertionError("translation by J identity failed")

    W = sp.symbols("W")
    lifted_u = (U - sp_A0 - W) / 2
    lift_delta = (U - sp_A0) ** 2 - 4 * sp_K
    lift_identity = sp.expand(
        4 * (lifted_u**2 - (U - sp_A0) * lifted_u + sp_K)
        - (W**2 - lift_delta)
    )
    if lift_identity != 0:
        raise AssertionError("lift quadratic identity failed")

    # The adjacent compatibility identity is checked generically on E.
    x, y, s_var = sp.symbols("x y s")
    sp_a2 = symq(e_a2)
    sp_a4 = symq(e_a4)
    curve_x = x**3 + sp_a2 * x**2 + sp_a4 * x + sp_alpha**2
    curve_s = 1 + sp_a2 + sp_a4 + sp_alpha**2
    slope = (y - s_var) / (x - 1)
    x_after_s = slope**2 - sp_a2 - x - 1
    adjacent_numerator = sp.together(
        (x - 1) ** 2 * (x * x_after_s + sp_alpha**2)
        - (y - s_var * x) ** 2
    ).as_numer_denom()[0]
    adjacent_reduced = sp.expand(adjacent_numerator).subs(y**2, curve_x)
    adjacent_reduced = sp.expand(adjacent_reduced).subs(s_var**2, curve_s)
    if sp.expand(adjacent_reduced) != 0:
        raise AssertionError("automatic adjacent-edge identity failed")

    # Eliminate U from Z^2=p*(U0-U).  Since p=N/dp^2, the coordinate
    # X=dp*Z/N gives U=U0-N*X^2.
    p_squarefree_numerator = p.numerator
    p_square_denominator = isqrt(p.denominator)
    if p_square_denominator**2 != p.denominator:
        raise AssertionError("p denominator is not square")
    N = p_squarefree_numerator
    dp = p_square_denominator
    betas = [U0, U0 - j, U0 - k]
    if any(value == 0 for value in betas):
        raise AssertionError("genus-two branch degeneration")
    denominator_product = prod(value.denominator for value in betas)
    y_scale = isqrt(denominator_product)
    if y_scale * y_scale != denominator_product:
        raise AssertionError("integral-model denominator product is not square")

    integral_factors: list[list[int]] = []
    factor_records: list[dict[str, Any]] = []
    for label, beta in zip(("U0", "U0-j", "U0-k"), betas, strict=True):
        factor = [beta.numerator, -N * beta.denominator]
        integral_factors.append(factor)
        factor_records.append(
            {
                "label": label,
                "beta": qtext(beta),
                "factor_constant": factor[0],
                "factor_u_coefficient": factor[1],
            }
        )
    g_coefficients = reduce(multiply_polynomials, integral_factors, [1])
    if len(g_coefficients) != 4:
        raise AssertionError("elliptic quotient polynomial is not cubic")
    if reduce(gcd, (abs(value) for value in g_coefficients)) != 1:
        raise AssertionError("integral polynomial is not primitive")
    genus2_coefficients = [
        g_coefficients[0],
        0,
        g_coefficients[1],
        0,
        g_coefficients[2],
        0,
        g_coefficients[3],
    ]
    elliptic_minus_coefficients = [0] + g_coefficients

    z = sp.symbols("z")
    g_polynomial = sum(
        sp.Integer(coefficient) * U**exponent
        for exponent, coefficient in enumerate(g_coefficients)
    )
    genus2_polynomial = sum(
        sp.Integer(coefficient) * z**exponent
        for exponent, coefficient in enumerate(genus2_coefficients)
    )
    if sp.expand(g_polynomial.subs(U, z**2) - genus2_polynomial) != 0:
        raise AssertionError("even-sextic substitution failed")
    elliptic_minus_polynomial = sp.expand(U * g_polynomial)

    # Verify the coordinate conversion and both elliptic quotient maps.
    Z = sp.symbols("Z")
    X_substitution = sp.Rational(dp, N) * Z
    recovered_u = sp_U0 - sp.Integer(N) * X_substitution**2
    if sp.cancel(recovered_u - (sp_U0 - Z**2 / sp_p)) != 0:
        raise AssertionError("C2 coordinate conversion failed")
    V2_from_quotient = (
        recovered_u * (recovered_u - sp_j) * (recovered_u - sp_k)
    )
    integral_from_quotient = sp.cancel(
        sp.Integer(denominator_product) * V2_from_quotient
        - genus2_polynomial.subs(z, X_substitution)
    )
    if integral_from_quotient != 0:
        raise AssertionError("integral genus-two model identity failed")
    if sp.expand(genus2_polynomial - g_polynomial.subs(U, z**2)) != 0:
        raise AssertionError("E+ quotient map failed")
    if sp.expand(z**2 * genus2_polynomial - elliptic_minus_polynomial.subs(U, z**2)) != 0:
        raise AssertionError("E- quotient map failed")

    discriminants = {
        "elliptic_plus_g": discriminant_record(g_polynomial, U),
        "elliptic_minus_u_times_g": discriminant_record(
            elliptic_minus_polynomial, U
        ),
        "genus2_g_of_x_squared": discriminant_record(genus2_polynomial, z),
    }

    input_specs = {
        "input_genus2_rank.m": (
            "ORDER4_C2_GENUS2",
            genus2_coefficients,
            6,
            2,
        ),
        "input_elliptic_plus_rank.m": (
            "ORDER4_C2_ELLIPTIC_PLUS",
            g_coefficients,
            3,
            1,
        ),
        "input_elliptic_minus_rank.m": (
            "ORDER4_C2_ELLIPTIC_MINUS",
            elliptic_minus_coefficients,
            4,
            1,
        ),
    }
    input_hashes: dict[str, str] = {}
    for filename, (label, coefficients, degree, genus) in input_specs.items():
        path = run_dir / filename
        write_ascii(path, magma_rank_input(label, coefficients, degree, genus))
        input_hashes[filename] = sha256(path)

    fixed_data = {
        "triple": {"a": qtext(A), "b": qtext(B), "c": qtext(C)},
        "pair_products": {"p_ab": qtext(p), "q_ac": qtext(q), "r_bc": qtext(r)},
        "pair_roots": {label: qtext(value) for label, value in pair_roots.items()},
        "alpha_abc": qtext(alpha),
        "curve": {
            "equation": "y^2=(x+p)(x+q)(x+r)",
            "a2": qtext(e_a2),
            "a4": qtext(e_a4),
            "a6": qtext(e_a6),
        },
        "S": [qtext(S[0]), qtext(S[1])],
        "H_2S": [qtext(H[0]), qtext(H[1])],
        "A0": qtext(A0),
        "K": qtext(K),
        "U0": qtext(U0),
        "j": qtext(j),
        "k": qtext(k),
    }
    model = {
        "run_id": run_dir.name,
        "fixed_data": fixed_data,
        "original_C2": {
            "equations": [
                "V^2=U*(U-j)*(U-k)",
                "Z^2=p*(U0-U)",
            ],
            "coordinate_change_to_integral": {
                "N": N,
                "dp": dp,
                "X": "dp*Z/N",
                "Y": f"{y_scale}*V",
                "inverse_U": "U0-N*X^2",
                "inverse_Z": "N*X/dp",
                "inverse_V": f"Y/{y_scale}",
            },
        },
        "integral_even_sextic": {
            "equation": "Y^2=g(X^2)",
            "g_coefficients_low_to_high": g_coefficients,
            "sextic_coefficients_low_to_high": genus2_coefficients,
            "factor_records": factor_records,
            "factorization": "*".join(
                f"({factor[0]}+({factor[1]})*X^2)"
                for factor in integral_factors
            ),
            "content": 1,
            "genus": 2,
        },
        "elliptic_quotients": {
            "E_plus": {
                "equation": "y^2=g(u)",
                "coefficients_low_to_high": g_coefficients,
                "map_from_C2_integral": "u=X^2, y=Y",
                "rational_2_torsion_u": [
                    qtext(Q(beta.numerator, N * beta.denominator))
                    for beta in betas
                ],
            },
            "E_minus": {
                "equation": "v^2=u*g(u)",
                "coefficients_low_to_high": elliptic_minus_coefficients,
                "map_from_C2_integral": "u=X^2, v=X*Y",
                "rational_point": "(u,v)=(0,0)",
            },
        },
        "discriminants": discriminants,
    }
    model_path = run_dir / "model.json"
    write_json(model_path, model)

    checks = {
        "status": "PASS",
        "exact_arithmetic": "fractions plus symbolic polynomial identities over Q",
        "source_hashes_match": True,
        "base_pair_square_checks": 3,
        "alpha_squared_equals_pqr": True,
        "S_on_E": True,
        "two_S_equals_H": True,
        "four_S_equals_identity": True,
        "S_exact_order": 4,
        "K_identity": True,
        "quotient_map_identity": True,
        "quotient_cubic_factorization": True,
        "first_diagonal_identity": True,
        "lift_quadratic_identity": True,
        "translation_by_J_identity": True,
        "second_diagonal_test": "p*(U0-(j+4*j*(1+p)/(U-j))) is a rational square",
        "automatic_cycle_edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
        "automatic_edge_square_identity": (
            "x(T)*x(T+S)+alpha^2=((y(T)-sigma*x(T))/(x(T)-1))^2"
        ),
        "integral_model_identity": True,
        "elliptic_plus_map_identity": True,
        "elliptic_minus_map_identity": True,
        "smooth_models": True,
        "magma_executed": False,
        "candidate_tested": False,
    }
    checks_path = run_dir / "checks.json"
    write_json(checks_path, checks)

    manifest = {
        "run_id": run_dir.name,
        "status": "READY_UNSUBMITTED",
        "objective": (
            "Freeze the fixed canonical-order-four quotient and prepare exact "
            "Magma V2.29-8 rank gates"
        ),
        "scope": "one published triple and its single registered C2 quotient",
        "direct_bridge": (
            "Every full two-diagonal order-four orbit maps to the genus-two "
            "curve; it also maps to both elliptic quotients. A proven rank-zero "
            "elliptic quotient gives a finite rational u-list for exact lifting."
        ),
        "continuation_gate": (
            "Prefer a proven rank-zero elliptic quotient. Otherwise apply the "
            "registered genus-two gate only when its proven rank upper bound is at most one."
        ),
        "exit": (
            "Positive rank on both elliptic quotients and genus-two upper rank above one, "
            "unequal bounds, timeout, or incomplete point output is INCONCLUSIVE."
        ),
        "computer_algebra_system": "Magma V2.29-8",
        "calculator_url": "https://magma.maths.usyd.edu.au/calc/",
        "magma_submitted": False,
        "candidate_search_performed": False,
        "engine_sha256": sha256(engine_path),
        "fixed_checker_sha256": sha256(fixed_checker_path),
        "derivation_sha256": sha256(derivation_path),
        "model_sha256": sha256(model_path),
        "checks_sha256": sha256(checks_path),
        "input_sha256": input_hashes,
    }
    manifest_path = run_dir / "manifest.json"
    write_json(manifest_path, manifest)

    summary = {
        "status": "PASS_READY_UNSUBMITTED",
        "run_dir": str(run_dir),
        "engine_sha256": sha256(engine_path),
        "model_sha256": sha256(model_path),
        "checks_sha256": sha256(checks_path),
        "manifest_sha256": sha256(manifest_path),
        "input_sha256": input_hashes,
        "exact_integral_genus2_coefficients_low_to_high": genus2_coefficients,
        "exact_g_coefficients_low_to_high": g_coefficients,
        "magma_executed": False,
        "candidate_tested": False,
    }
    summary_path = run_dir / "summary.json"
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
