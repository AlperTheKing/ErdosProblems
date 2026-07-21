#!/usr/bin/env python3
"""Exact audit of the omitted DKP regular extension.

This script independently reconstructs the two-parameter quintuple and the
published first regular extension from Dujella--Kazalicki--Petricevic (2019),
arXiv:1904.00348.  It performs symbolic identities only; it does not search
for parameter values.

The output is deterministic JSON.  Polynomial hashes use a canonical JSON
serialization of the primitive integer coefficients in generators ``u,t``.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import argparse
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import sympy as sp


u, t, x = sp.symbols("u t x")
GENS = (u, t)


def exact_zero(expr: sp.Expr) -> bool:
    """Return whether a rational-function expression is identically zero."""

    return sp.cancel(expr) == 0


def rational_square_root(value: sp.Rational) -> sp.Rational | None:
    """Return the nonnegative rational square root, or None."""

    value = sp.Rational(value)
    if value < 0:
        return None
    numerator = int(sp.numer(value))
    denominator = int(sp.denom(value))
    rn = math.isqrt(numerator)
    rd = math.isqrt(denominator)
    if rn * rn != numerator or rd * rd != denominator:
        return None
    return sp.Rational(rn, rd)


def polynomial_square_root(poly_expr: sp.Expr) -> sp.Expr | None:
    """Return a square root in Q[u,t], or None, using exact factorization."""

    coefficient, factors = sp.factor_list(poly_expr, *GENS)
    root_coefficient = rational_square_root(sp.Rational(coefficient))
    if root_coefficient is None or any(multiplicity % 2 for _, multiplicity in factors):
        return None
    root = root_coefficient
    for factor, multiplicity in factors:
        root *= factor ** (multiplicity // 2)
    return sp.expand(root)


def rational_function_square_root(expr: sp.Expr) -> sp.Expr | None:
    """Return a root in Q(u,t), or None, and verify the returned identity."""

    numerator, denominator = sp.fraction(sp.cancel(expr))
    numerator_root = polynomial_square_root(numerator)
    denominator_root = polynomial_square_root(denominator)
    if numerator_root is None or denominator_root is None:
        return None
    root = sp.cancel(numerator_root / denominator_root)
    if not exact_zero(root * root - expr):
        raise AssertionError("factor-derived square root failed exact replay")
    return root


def primitive_integer_poly(expr: sp.Expr) -> sp.Poly:
    """Canonical primitive integer polynomial with positive leading term."""

    poly_q = sp.Poly(sp.expand(expr), *GENS, domain=sp.QQ)
    _, poly_z = poly_q.clear_denoms(convert=True)
    _, primitive = poly_z.primitive()
    if primitive.LC() < 0:
        primitive = -primitive
    return primitive


def polynomial_record(
    expr: sp.Expr, multiplicity: int, *, irreducible_over_q: bool | None = None
) -> dict[str, object]:
    """Return exact expression, bidegree, and a coefficient-level hash."""

    poly = primitive_integer_poly(expr)
    terms = [[*monomial, str(coefficient)] for monomial, coefficient in poly.terms()]
    canonical = json.dumps(
        {"generators": ["u", "t"], "terms": terms},
        ensure_ascii=True,
        separators=(",", ":"),
    )
    record: dict[str, object] = {
        "degree_u": int(poly.degree(u)),
        "degree_t": int(poly.degree(t)),
        "multiplicity": int(multiplicity),
        "term_count": len(terms),
        "sha256": hashlib.sha256(canonical.encode("ascii")).hexdigest().upper(),
        "expanded": str(poly.as_expr()),
    }
    if irreducible_over_q is not None:
        record["irreducible_over_Q"] = irreducible_over_q
    return record


def reconstruct() -> tuple[list[sp.Expr], sp.Expr]:
    """Return [a1,...,a6] and the paper's special t(u)."""

    t3 = (16 - u**2) / (6 * u)
    t2 = (u**2 + 10 * u + 16) / ((u - 4) * (u + 4))
    common = (-1 + t * t2 * t3) * (1 + t * t2 * t3)

    a1 = 2 * t * (1 + t * t2 * (1 + t2 * t3)) / common
    a2 = 2 * t2 * (1 + t2 * t3 * (1 + t3 * t)) / common
    a3 = 2 * t3 * (1 + t3 * t * (1 + t * t2)) / common
    a4 = (
        -2
        * (1 - t3 + t2 * t3)
        * (t3 * t + 1 - t)
        * (-t2 + 1 + t * t2)
        * (-1 + t * t2 * t3)
        / (1 + t * t2 * t3) ** 3
    )
    a5 = (
        2
        * (t3 + t2 * t3 + 1)
        * (t3 * t + t + 1)
        * (1 + t2 + t * t2)
        * (1 + t * t2 * t3)
        / (-1 + t * t2 * t3) ** 3
    )

    a6_den_base = (
        4096 * t**2
        + 15360 * t**2 * u
        + 15168 * t**2 * u**2
        + 5920 * t**2 * u**3
        + 948 * t**2 * u**4
        + 60 * t**2 * u**5
        + t**2 * u**6
        - 12288 * t * u
        - 7680 * t * u**2
        + 480 * t * u**4
        + 48 * t * u**5
        - 5184 * u**2
        - 2592 * u**3
        - 324 * u**4
    )
    a6 = (
        6
        * (u + 4)
        * (u + 8)
        * (u + 2)
        * (u - 4)
        * (2 * t * u**2 + 3 * u**2 + 20 * t * u + 12 * u + 32 * t)
        * (t * u**2 + 10 * t * u + 16 * t - 6 * u)
        * (t * u**2 + 10 * t * u + 16 * t + 6 * u)
        * (t * u**2 + 10 * t * u + 16 * t - 24 - 6 * u)
        / a6_den_base**2
    )

    special_t = (
        3 * (3 * u**4 + 40 * u**3 + 368 * u**2 + 1280 * u + 1024)
        / (4 * (u**2 + 10 * u + 16) * (u + 20) * u)
    )
    return [sp.cancel(value) for value in (a1, a2, a3, a4, a5, a6)], sp.cancel(special_t)


def verify_quintuple(values: list[sp.Expr]) -> dict[str, str]:
    """Verify all ten Q(u,t)-square identities for a1,...,a5."""

    t3 = (16 - u**2) / (6 * u)
    t2 = (u**2 + 10 * u + 16) / ((u - 4) * (u + 4))
    q = t * t2 * t3
    common_root_denominator = (q - 1) * (q + 1)

    roots_by_pair = {
        (0, 1): (q**2 + 2 * t * t2**2 * t3 + 2 * t * t2 + 1)
        / common_root_denominator,
        (0, 2): (q**2 + 2 * t**2 * t2 * t3 + 2 * t * t3 + 1)
        / common_root_denominator,
        (1, 2): (q**2 + 2 * t * t2 * t3**2 + 2 * t2 * t3 + 1)
        / common_root_denominator,
        (0, 3): (
            q**2
            - 2 * t**2 * t2**2 * t3
            + 2 * t**2 * t2 * t3
            - 2 * t**2 * t2
            + 2 * t * t2**2 * t3
            - 2 * q
            + 2 * t * t2
            + 2 * t * t3
            - 2 * t
            + 1
        )
        / (q + 1) ** 2,
        (0, 4): (
            q**2
            + 2 * t**2 * t2**2 * t3
            + 2 * t**2 * t2 * t3
            + 2 * t**2 * t2
            + 2 * t * t2**2 * t3
            + 2 * q
            + 2 * t * t2
            + 2 * t * t3
            + 2 * t
            + 1
        )
        / (q - 1) ** 2,
        (1, 3): (
            q**2
            - 2 * t * t2**2 * t3**2
            + 2 * t * t2**2 * t3
            + 2 * t * t2 * t3**2
            - 2 * q
            + 2 * t * t2
            - 2 * t2**2 * t3
            + 2 * t2 * t3
            - 2 * t2
            + 1
        )
        / (q + 1) ** 2,
        (1, 4): (
            q**2
            + 2 * t * t2**2 * t3**2
            + 2 * t * t2**2 * t3
            + 2 * t * t2 * t3**2
            + 2 * q
            + 2 * t * t2
            + 2 * t2**2 * t3
            + 2 * t2 * t3
            + 2 * t2
            + 1
        )
        / (q - 1) ** 2,
        (2, 3): (
            q**2
            - 2 * t**2 * t2 * t3**2
            + 2 * t**2 * t2 * t3
            + 2 * t * t2 * t3**2
            - 2 * q
            - 2 * t * t3**2
            + 2 * t * t3
            + 2 * t2 * t3
            - 2 * t3
            + 1
        )
        / (q + 1) ** 2,
        (2, 4): (
            q**2
            + 2 * t**2 * t2 * t3**2
            + 2 * t**2 * t2 * t3
            + 2 * t * t2 * t3**2
            + 2 * q
            + 2 * t * t3**2
            + 2 * t * t3
            + 2 * t2 * t3
            + 2 * t3
            + 1
        )
        / (q - 1) ** 2,
    }
    r45_numerator = (
        t**2 * u**6
        + 4 * t**2 * u**5
        - 172 * t**2 * u**4
        - 1472 * t**2 * u**3
        - 2752 * t**2 * u**2
        + 1024 * t**2 * u
        + 4096 * t**2
        - 32 * t * u**5
        - 320 * t * u**4
        + 5120 * t * u**2
        + 8192 * t * u
        + 156 * u**4
        + 1344 * u**3
        + 2496 * u**2
    )
    r45_denominator = (
        (u - 4)
        * (u + 4)
        * (t * u**2 + 10 * t * u + 16 * t - 6 * u)
        * (t * u**2 + 10 * t * u + 16 * t + 6 * u)
    )
    roots_by_pair[(3, 4)] = r45_numerator / r45_denominator

    roots: dict[str, str] = {}
    for i, j in combinations(range(5), 2):
        root = sp.cancel(roots_by_pair[(i, j)])
        if not exact_zero(root**2 - (values[i] * values[j] + 1)):
            raise AssertionError(f"square-root replay failed for a{i + 1}*a{j + 1}+1")
        roots[f"a{i + 1},a{j + 1}"] = str(root)
    return roots


def verify_vieta(values: list[sp.Expr]) -> tuple[sp.Expr, dict[str, bool]]:
    """Recover a7 from Vieta and replay the regular-root quadratic."""

    a1, _, a3, a4, a5, a6 = values
    print("stage: Vieta coefficients", file=sys.stderr, flush=True)
    A = sp.cancel(a1 * a3 * a4 * a5)
    B = sp.cancel(2 * a1 * a3 * a4 + a1 + a3 + a4 - a5)
    K = sp.cancel((a1 * a3 + 1) * (a1 * a4 + 1) * (a3 * a4 + 1))
    print("stage: Vieta second root", file=sys.stderr, flush=True)
    constant = B**2 - 4 * K
    leading = sp.cancel((A - 1) ** 2)
    # Keep the published Vieta product form factored.  Expanding this quotient
    # is unnecessary for this audit and can obscure the source-level formula.
    a7 = constant / (leading * a6)

    print("stage: Vieta a6 root", file=sys.stderr, flush=True)
    # Replay the root equation with unreduced polynomial fractions.  This is
    # exact, and avoids an expensive multivariate gcd of a rational expression
    # that is identically zero.
    one_poly = sp.Poly(1, *GENS, domain=sp.QQ)

    def pf(value: sp.Expr) -> tuple[sp.Poly, sp.Poly]:
        numerator, denominator = sp.fraction(value)
        return (
            sp.Poly(numerator, *GENS, domain=sp.QQ),
            sp.Poly(denominator, *GENS, domain=sp.QQ),
        )

    def pf_add(
        left: tuple[sp.Poly, sp.Poly], right: tuple[sp.Poly, sp.Poly]
    ) -> tuple[sp.Poly, sp.Poly]:
        return left[0] * right[1] + right[0] * left[1], left[1] * right[1]

    def pf_neg(value: tuple[sp.Poly, sp.Poly]) -> tuple[sp.Poly, sp.Poly]:
        return -value[0], value[1]

    def pf_mul(
        left: tuple[sp.Poly, sp.Poly], right: tuple[sp.Poly, sp.Poly]
    ) -> tuple[sp.Poly, sp.Poly]:
        return left[0] * right[0], left[1] * right[1]

    def pf_scale(
        scalar: int, value: tuple[sp.Poly, sp.Poly]
    ) -> tuple[sp.Poly, sp.Poly]:
        return scalar * value[0], value[1]

    def pf_sum(*terms: tuple[sp.Poly, sp.Poly]) -> tuple[sp.Poly, sp.Poly]:
        total = (sp.Poly(0, *GENS, domain=sp.QQ), one_poly)
        for term in terms:
            total = pf_add(total, term)
        return total

    p1, p3, p4, p5, p6 = (pf(value) for value in (a1, a3, a4, a5, a6))
    pA = pf_mul(pf_mul(p1, p3), pf_mul(p4, p5))
    pA_minus_one = pf_add(pA, (-one_poly, one_poly))
    pB = pf_sum(
        pf_scale(2, pf_mul(pf_mul(p1, p3), p4)),
        p1,
        p3,
        p4,
        pf_neg(p5),
    )
    pK = pf_mul(
        pf_add(pf_mul(p1, p3), (one_poly, one_poly)),
        pf_mul(
            pf_add(pf_mul(p1, p4), (one_poly, one_poly)),
            pf_add(pf_mul(p3, p4), (one_poly, one_poly)),
        ),
    )
    left = pf_sum(pf_mul(pA_minus_one, p6), pB)
    left_squared = pf_mul(left, left)
    right = pf_scale(
        4,
        pf_mul(pK, pf_add(pf_mul(p5, p6), (one_poly, one_poly))),
    )
    quadratic_replay = pf_add(left_squared, pf_neg(right))
    a6_is_root = quadratic_replay[0].is_zero
    # Exact generic coefficient algebra: if q(r)=0 and s=-M/L-r, then
    # q(s)=0 and r*s=C/L.  This avoids a second expansion of the same very
    # large rational-function identity.
    L0, r0 = sp.symbols("L0 r0", nonzero=True)
    M0, C0 = sp.symbols("M0 C0")
    s0 = C0 / (L0 * r0)
    q0 = L0 * r0**2 + M0 * r0 + C0
    generic_product = exact_zero(r0 * s0 - C0 / L0)
    generic_second_root = exact_zero(
        L0 * s0**2 + M0 * s0 + C0 - C0 * q0 / (L0 * r0**2)
    )
    if not generic_product or not generic_second_root:
        raise AssertionError("generic Vieta coefficient identity failed")
    a7_is_root = a6_is_root and generic_second_root
    root_product = a6_is_root and generic_product
    checks = {
        "a6_is_root": a6_is_root,
        "a7_is_root": a7_is_root,
        "root_product": root_product,
    }
    if not all(checks.values()):
        raise AssertionError(f"Vieta replay failed: {checks}")
    return a7, checks


def verify_u_minus_one(values: list[sp.Expr], special_t: sp.Expr) -> dict[str, object]:
    """Match the paper's u=-1 sextuple and verify all 15 pairs numerically."""

    published = [
        sp.Rational(27900, 17479),
        sp.Rational(471352, 112365),
        sp.Rational(261770, 17479),
        sp.Rational(185535272, 419265),
        sp.Rational(63737828, 526368735),
        sp.Rational(79554420, 408480247),
    ]
    t_at_minus_one = sp.cancel(special_t.subs(u, -1))
    reconstructed = [sp.cancel(value.subs(t, special_t).subs(u, -1)) for value in values]
    if reconstructed != published:
        raise AssertionError(
            "u=-1 calibration does not match the published ordered sextuple: "
            f"{reconstructed}"
        )

    pair_roots: dict[str, str] = {}
    for i, j in combinations(range(6), 2):
        root = rational_square_root(sp.Rational(reconstructed[i] * reconstructed[j] + 1))
        if root is None:
            raise AssertionError(f"published pair ({i + 1},{j + 1}) is not a rational square")
        pair_roots[f"a{i + 1},a{j + 1}"] = str(root)
    return {
        "t": str(t_at_minus_one),
        "ordered_values": [str(value) for value in reconstructed],
        "pair_count": len(pair_roots),
        "pair_roots": pair_roots,
    }


def factor_g(values: list[sp.Expr]) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Factor the numerator of the Piezas compatibility condition over Q."""

    a1, _, a3, a4, a5, _ = values
    A = sp.cancel(a1 * a3 * a4 * a5)
    G = sp.cancel((A - 3) ** 2 - 4 * (a1 * a3 + a4 * a5 + 3))
    numerator, denominator = sp.fraction(G)
    coefficient, factors = sp.factor_list(numerator, *GENS)
    factor_records = [
        polynomial_record(factor, multiplicity, irreducible_over_q=True)
        for factor, multiplicity in factors
    ]

    if len(factor_records) != 4:
        raise AssertionError(f"expected four nonconstant factors, got {len(factor_records)}")
    if any(
        record["degree_u"] != 10
        or record["degree_t"] != 4
        or record["multiplicity"] != 1
        for record in factor_records
    ):
        raise AssertionError(f"unexpected factor degree or multiplicity: {factor_records}")

    replay = sp.Integer(coefficient)
    for factor, multiplicity in factors:
        replay *= factor**multiplicity
    if sp.expand(replay - numerator) != 0:
        raise AssertionError("factorization does not multiply back to numerator(G)")

    numerator_record = polynomial_record(numerator, 1)
    numerator_record["factor_coefficient"] = str(coefficient)
    denominator_poly = primitive_integer_poly(denominator)
    denominator_record = polynomial_record(denominator_poly.as_expr(), 1)
    return {
        "numerator": numerator_record,
        "denominator": denominator_record,
        "factor_count": len(factor_records),
    }, factor_records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print("stage: reconstruct", file=sys.stderr, flush=True)
    values, special_t = reconstruct()
    print("stage: verify quintuple", file=sys.stderr, flush=True)
    quintuple_roots = verify_quintuple(values)
    print("stage: verify Vieta", file=sys.stderr, flush=True)
    a7, vieta_checks = verify_vieta(values)
    print("stage: verify u=-1", file=sys.stderr, flush=True)
    calibration = verify_u_minus_one(values, special_t)
    print("stage: factor G", file=sys.stderr, flush=True)
    g_summary, factor_records = factor_g(values)
    print("stage: emit", file=sys.stderr, flush=True)

    result = {
        "source": "Dujella--Kazalicki--Petricevic, arXiv:1904.00348",
        "method": "independent exact SymPy reconstruction over Q(u,t)",
        "quintuple": {
            "pair_count": len(quintuple_roots),
            "all_square": len(quintuple_roots) == 10,
            "roots": quintuple_roots,
        },
        "vieta": {
            **vieta_checks,
            "a7_formula": "(B^2-4*K)/((A-1)^2*a6)",
            "excluded_bad_locus": "(A-1)*a6 = 0",
        },
        "u_minus_one": calibration,
        "G": {**g_summary, "factors": factor_records},
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
