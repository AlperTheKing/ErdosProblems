#!/usr/bin/env python3
"""Primary exact audit for the exotic regular-conjugate Kummer cover.

The symbolic calculation is performed in

    Q(s)[r] / ((3*s**2 - 4)*r**2 - 2*s*r + 7 - 4*s**2).

Every quotient-field element is reduced to degree at most one in ``r`` and
then normalized as a primitive integer numerator/denominator pair.  The
normal form, rather than SymPy's display text, is the hashed object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import sympy as sp
from sympy.polys.domains import QQ


r, s = sp.symbols("r s")
C = 3 * r**2 * s**2 - 4 * r**2 - 2 * r * s - 4 * s**2 + 7
K_S = QQ.frac_field(s)
C_POLY = sp.Poly(C, r, domain=K_S)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compact_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n",
        encoding="ascii",
        newline="\n",
    )


def quotient_reduce(expr: sp.Expr) -> sp.Expr:
    """Return the canonical degree-<2 representative in r modulo C."""

    expr = sp.cancel(expr)
    numerator, denominator = sp.fraction(expr)
    numerator_poly = sp.Poly(numerator, r, domain=K_S)
    denominator_poly = sp.Poly(denominator, r, domain=K_S)
    denominator_inverse = sp.invert(denominator_poly, C_POLY)
    remainder = (numerator_poly * denominator_inverse).rem(C_POLY)
    return sp.cancel(remainder.as_expr())


def _primitive_integer_pair(
    numerator: sp.Expr, denominator: sp.Expr
) -> tuple[sp.Poly, sp.Poly]:
    numerator_poly = sp.Poly(numerator, r, s, domain=QQ)
    denominator_poly = sp.Poly(denominator, r, s, domain=QQ)
    coefficient_denominators = [
        int(coefficient.q)
        for coefficient in numerator_poly.coeffs() + denominator_poly.coeffs()
    ]
    scale = 1
    for value in coefficient_denominators:
        scale = math.lcm(scale, value)
    numerator_integer = sp.Poly(
        sp.expand(numerator_poly.as_expr() * scale), r, s, domain=sp.ZZ
    )
    denominator_integer = sp.Poly(
        sp.expand(denominator_poly.as_expr() * scale), r, s, domain=sp.ZZ
    )
    all_coefficients = [
        abs(int(value))
        for value in numerator_integer.coeffs() + denominator_integer.coeffs()
        if value != 0
    ]
    content = 0
    for value in all_coefficients:
        content = math.gcd(content, value)
    if content > 1:
        numerator_integer = sp.Poly(
            numerator_integer.as_expr() / content, r, s, domain=sp.ZZ
        )
        denominator_integer = sp.Poly(
            denominator_integer.as_expr() / content, r, s, domain=sp.ZZ
        )
    if denominator_integer.LC() < 0:
        numerator_integer = -numerator_integer
        denominator_integer = -denominator_integer
    return numerator_integer, denominator_integer


def polynomial_object(poly: sp.Poly) -> dict[str, Any]:
    terms = []
    for exponents, coefficient in poly.terms():
        terms.append(
            {
                "exponents": [int(exponents[0]), int(exponents[1])],
                "coefficient": str(int(coefficient)),
            }
        )
    core = {"variables": ["r", "s"], "terms": terms}
    return {
        "canonical": core,
        "sha256": sha256_bytes(compact_json(core)),
        "text": sp.sstr(poly.as_expr(), order="lex"),
    }


def canonical_fraction(expr: sp.Expr) -> dict[str, Any]:
    reduced = quotient_reduce(expr)
    numerator, denominator = sp.fraction(sp.cancel(reduced))
    numerator_poly, denominator_poly = _primitive_integer_pair(
        numerator, denominator
    )
    numerator_object = polynomial_object(numerator_poly)
    denominator_object = polynomial_object(denominator_poly)
    core = {
        "numerator": numerator_object["canonical"],
        "denominator": denominator_object["canonical"],
    }
    return {
        "numerator": numerator_object,
        "denominator": denominator_object,
        "fraction_sha256": sha256_bytes(compact_json(core)),
        "text": (
            "(" + numerator_object["text"] + ")/("
            + denominator_object["text"] + ")"
        ),
    }


def is_zero_mod_curve(expr: sp.Expr) -> bool:
    return quotient_reduce(expr) == 0


def rational_function_square_root(expr: sp.Expr) -> sp.Expr | None:
    """Return a square root in Q(s), or None when no such root exists."""

    expr = sp.cancel(expr)
    numerator, denominator = sp.fraction(expr)

    def polynomial_square_root(poly_expr: sp.Expr) -> sp.Expr | None:
        poly = sp.Poly(poly_expr, s, domain=QQ)
        coefficient, factors = sp.factor_list(poly)
        coefficient_numerator = int(coefficient.p)
        coefficient_denominator = int(coefficient.q)
        if coefficient_numerator < 0:
            return None
        root_numerator = math.isqrt(coefficient_numerator)
        root_denominator = math.isqrt(coefficient_denominator)
        if (
            root_numerator * root_numerator != coefficient_numerator
            or root_denominator * root_denominator != coefficient_denominator
        ):
            return None
        result: sp.Expr = sp.Rational(root_numerator, root_denominator)
        for factor, exponent in factors:
            if exponent % 2:
                return None
            result *= factor.as_expr() ** (exponent // 2)
        return sp.cancel(result)

    numerator_root = polynomial_square_root(numerator)
    denominator_root = polynomial_square_root(denominator)
    if numerator_root is None or denominator_root is None:
        return None
    return sp.cancel(numerator_root / denominator_root)


def curve_square_root(expr: sp.Expr) -> sp.Expr | None:
    """Return a verified square root in Q(C), if one exists by exact algebra."""

    reduced = quotient_reduce(expr)
    if reduced == 0:
        return sp.Integer(0)
    reduced_poly = sp.Poly(reduced, r, domain=K_S)
    coefficient_r = reduced_poly.coeff_monomial(r)
    coefficient_one = reduced_poly.coeff_monomial(1)

    # From C, r^2 = alpha*r + beta.  Conjugation sends r to alpha-r.
    alpha = 2 * s / (3 * s**2 - 4)
    beta = (4 * s**2 - 7) / (3 * s**2 - 4)
    trace = sp.cancel(coefficient_r * alpha + 2 * coefficient_one)
    norm = sp.cancel(
        coefficient_one**2
        + coefficient_r * coefficient_one * alpha
        - coefficient_r**2 * beta
    )
    norm_root = rational_function_square_root(norm)
    if norm_root is None:
        return None
    for signed_norm_root in (norm_root, -norm_root):
        trace_root = rational_function_square_root(
            sp.cancel(trace + 2 * signed_norm_root)
        )
        if trace_root in (None, 0):
            continue
        candidate = quotient_reduce((reduced + signed_norm_root) / trace_root)
        if is_zero_mod_curve(candidate**2 - reduced):
            return candidate
    return None


def regular_triple(p: sp.Expr, q: sp.Expr, u: sp.Expr) -> sp.Expr:
    return (p + q - u) ** 2 - 4 * (p * q + 1)


def regular_quadruple(
    p: sp.Expr, q: sp.Expr, u: sp.Expr, v: sp.Expr
) -> sp.Expr:
    return (p + q - u - v) ** 2 - 4 * (p * q + 1) * (u * v + 1)


def regular_quintuple_equation(
    p: sp.Expr, q: sp.Expr, u: sp.Expr, v: sp.Expr, x: sp.Expr
) -> sp.Expr:
    aa = p * q * u * v - 1
    bb = 2 * p * q * u + p + q + u - v
    nn = (p * q + 1) * (p * u + 1) * (q * u + 1)
    return (aa * x + bb) ** 2 - 4 * nn * (v * x + 1)


def conjugate(
    p: sp.Expr, q: sp.Expr, u: sp.Expr, v: sp.Expr, x: sp.Expr
) -> sp.Expr:
    aa = p * q * u * v - 1
    bb = 2 * p * q * u + p + q + u - v
    nn = (p * q + 1) * (p * u + 1) * (q * u + 1)
    return sp.cancel((bb**2 - 4 * nn) / (aa**2 * x))


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def fraction_object(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "text": fraction_text(value),
    }


def exact_square_root(value: Fraction) -> Fraction | None:
    if value < 0:
        return None
    numerator_root = math.isqrt(value.numerator)
    denominator_root = math.isqrt(value.denominator)
    if (
        numerator_root * numerator_root != value.numerator
        or denominator_root * denominator_root != value.denominator
    ):
        return None
    return Fraction(numerator_root, denominator_root)


def regular_quintuple_equation_fraction(
    p: Fraction,
    q: Fraction,
    u: Fraction,
    v: Fraction,
    x: Fraction,
) -> Fraction:
    aa = p * q * u * v - 1
    bb = 2 * p * q * u + p + q + u - v
    nn = (p * q + 1) * (p * u + 1) * (q * u + 1)
    return (aa * x + bb) ** 2 - 4 * nn * (v * x + 1)


def conjugate_fraction(
    p: Fraction,
    q: Fraction,
    u: Fraction,
    v: Fraction,
    x: Fraction,
) -> Fraction:
    aa = p * q * u * v - 1
    bb = 2 * p * q * u + p + q + u - v
    nn = (p * q + 1) * (p * u + 1) * (q * u + 1)
    return (bb**2 - 4 * nn) / (aa**2 * x)


PRINTED_EXAMPLES: tuple[tuple[Fraction, Fraction, Fraction], ...] = (
    (Fraction(8), Fraction(312, 529), Fraction(495, 529)),
    (
        Fraction(312, 529),
        Fraction(-152880, 165649),
        Fraction(-78374557, 87628321),
    ),
    (
        Fraction(724255280, 736742449),
        Fraction(-152880, 165649),
        Fraction(-63009087694401, 122040649934401),
    ),
    (
        Fraction(24490915482072, 12448992625969),
        Fraction(724255280, 736742449),
        Fraction(-4510665894525110607837, 9171701314839342058081),
    ),
    (
        Fraction(-2539564321528123032, 5054545907282329441),
        Fraction(24490915482072, 12448992625969),
        Fraction(
            14261842404349331345950974819695,
            62924004727379507987985949853329,
        ),
    ),
)


def checked_roots(
    values: dict[str, Fraction], pairs: Iterable[tuple[str, str]]
) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for left, right in pairs:
        radicand = values[left] * values[right] + 1
        root = exact_square_root(radicand)
        output[f"{left}*{right}+1"] = {
            "radicand": fraction_object(radicand),
            "is_square": root is not None,
            "root": fraction_object(root) if root is not None else None,
        }
    return output


def audit_example(index: int, triple: tuple[Fraction, Fraction, Fraction]) -> dict[str, Any]:
    aa, bb, cc = triple
    abs_r = exact_square_root(aa + 1)
    abs_s = exact_square_root(bb + 1)
    if abs_r is None or abs_s is None:
        raise AssertionError(f"printed example {index}: a+1 or b+1 is nonsquare")
    rr = abs_r
    compatible_s = [
        signed_s
        for signed_s in (abs_s, -abs_s)
        if 3 * rr**2 * signed_s**2
        - 4 * rr**2
        - 2 * rr * signed_s
        - 4 * signed_s**2
        + 7
        == 0
    ]
    if len(compatible_s) != 1:
        raise AssertionError(
            f"printed example {index}: expected one s sign for canonical r>0"
        )
    ss = compatible_s[0]
    reconstructed_c = (-rr**2 * ss**2 + 2 * ss**2 + 2 * rr**2 - 5) / 2
    if reconstructed_c != cc:
        raise AssertionError(f"printed example {index}: c reconstruction failed")

    ll = aa * bb * cc - 1
    kk = 2 * aa * bb + 1 + aa + bb - cc
    mm = (aa + 1) * (bb + 1) * (aa * bb + 1)
    ee = (4 * mm * cc - 2 * ll * kk) / ll**2
    ff = conjugate_fraction(aa, bb, cc, ee, Fraction(1))
    gg = conjugate_fraction(Fraction(1), aa, bb, ee, cc)
    values = {
        "one": Fraction(1),
        "a": aa,
        "b": bb,
        "c": cc,
        "e": ee,
        "f": ff,
        "g": gg,
    }

    source_radicands = {
        "a+1": aa + 1,
        "b+1": bb + 1,
        "c+1": cc + 1,
        "a*b+1": aa * bb + 1,
        "a*c+1": aa * cc + 1,
        "b*c+1": bb * cc + 1,
        "a*b*c+1": aa * bb * cc + 1,
    }
    source_roots = {
        name: exact_square_root(value) for name, value in source_radicands.items()
    }
    quintuple_pairs = [
        (left, right)
        for position, left in enumerate(("one", "a", "b", "c", "e"))
        for right in ("one", "a", "b", "c", "e")[position + 1 :]
    ]
    f_pairs = [("f", name) for name in ("a", "b", "c", "e")]
    g_pairs = [("g", name) for name in ("one", "a", "b", "e")]
    residual_pairs = [("one", "f"), ("c", "g"), ("f", "g")]
    quintuple_checks = checked_roots(values, quintuple_pairs)
    f_checks = checked_roots(values, f_pairs)
    g_checks = checked_roots(values, g_pairs)
    residual_checks = checked_roots(values, residual_pairs)

    regular_values = {
        "H(1,a,b,c,e)": regular_quintuple_equation_fraction(
            Fraction(1), aa, bb, cc, ee
        ),
        "H(a,b,c,e,1)": regular_quintuple_equation_fraction(
            aa, bb, cc, ee, Fraction(1)
        ),
        "H(a,b,c,e,f)": regular_quintuple_equation_fraction(aa, bb, cc, ee, ff),
        "H(1,a,b,e,c)": regular_quintuple_equation_fraction(
            Fraction(1), aa, bb, ee, cc
        ),
        "H(1,a,b,e,g)": regular_quintuple_equation_fraction(
            Fraction(1), aa, bb, ee, gg
        ),
    }
    all_supplied_square_checks = (
        all(root is not None for root in source_roots.values())
        and all(item["is_square"] for item in quintuple_checks.values())
        and all(item["is_square"] for item in f_checks.values())
        and all(item["is_square"] for item in g_checks.values())
    )
    passed = (
        all_supplied_square_checks
        and all(value == 0 for value in regular_values.values())
        and reconstructed_c == cc
    )
    if not passed:
        raise AssertionError(f"printed example {index}: exact audit failed")

    return {
        "index": index,
        "r": fraction_object(rr),
        "s": fraction_object(ss),
        "values": {name: fraction_object(value) for name, value in values.items()},
        "source_seven_roots": {
            name: {
                "radicand": fraction_object(source_radicands[name]),
                "root": fraction_object(root) if root is not None else None,
            }
            for name, root in source_roots.items()
        },
        "quintuple_pair_checks": quintuple_checks,
        "f_automatic_pair_checks": f_checks,
        "g_automatic_pair_checks": g_checks,
        "residual_pair_checks": residual_checks,
        "regular_equations": {
            name: fraction_object(value) for name, value in regular_values.items()
        },
        "seven_values_distinct": len(set(values.values())) == 7,
        "seven_values_nonzero": all(value != 0 for value in values.values()),
        "all_supplied_square_checks": all_supplied_square_checks,
        "passed": passed,
    }


def build_symbolic_report() -> tuple[dict[str, Any], dict[str, Any]]:
    a = r**2 - 1
    b = s**2 - 1
    c = (-r**2 * s**2 + 2 * s**2 + 2 * r**2 - 5) / 2
    ll = a * b * c - 1
    kk = 2 * a * b + 1 + a + b - c
    mm = (a + 1) * (b + 1) * (a * b + 1)
    e = sp.cancel((4 * mm * c - 2 * ll * kk) / ll**2)
    f = conjugate(a, b, c, e, sp.Integer(1))
    g = conjugate(sp.Integer(1), a, b, e, c)

    source_square_candidates = {
        "a+1": (a + 1, r),
        "b+1": (b + 1, s),
        "c+1": (c + 1, (1 + c - a * b) / 2),
        "a*b+1": (a * b + 1, (1 + a * b - c) / 2),
        "a*c+1": (a * c + 1, (1 + b - a - c) / (2 * s)),
        "b*c+1": (b * c + 1, (1 + a - b - c) / (2 * r)),
        "a*b*c+1": (a * b * c + 1, (a * b + c - 1) / 2),
    }
    source_square_checks: dict[str, Any] = {}
    for name, (radicand, root_candidate) in source_square_candidates.items():
        verified = is_zero_mod_curve(root_candidate**2 - radicand)
        if not verified:
            raise AssertionError(f"symbolic source square identity failed: {name}")
        source_square_checks[name] = {
            "verified_mod_C": True,
            "root": canonical_fraction(root_candidate),
        }

    zero_identity_expressions = {
        "r3(1,a*b,c)": regular_triple(1, a * b, c),
        "r4(1,a,b,c)": regular_quadruple(1, a, b, c),
        "H(1,a,b,c,0)": regular_quintuple_equation(1, a, b, c, 0),
        "H(1,a,b,c,e)": regular_quintuple_equation(1, a, b, c, e),
        "H(a,b,c,e,1)": regular_quintuple_equation(a, b, c, e, 1),
        "H(1,a,b,e,c)": regular_quintuple_equation(1, a, b, e, c),
    }
    zero_identity_checks = {}
    for name, expression in zero_identity_expressions.items():
        verified = is_zero_mod_curve(expression)
        if not verified:
            raise AssertionError(f"symbolic zero identity failed: {name}")
        zero_identity_checks[name] = {"verified_mod_C": True}

    # The conjugate substitution is certified once, without expanding H at the
    # very large roots f and g.  If H(x)=A^2*x^2+E*x+D and
    # x'=D/(A^2*x), direct polynomial algebra gives
    # H(x')=D*H(x)/(A^2*x^2).  The known-root identities above are the only
    # family-specific hypotheses needed for this transfer.
    generic_aa, generic_ee, generic_dd, generic_x = sp.symbols("A E D x")
    generic_h = (
        generic_aa**2 * generic_x**2 + generic_ee * generic_x + generic_dd
    )
    generic_conjugate = generic_dd / (generic_aa**2 * generic_x)
    generic_transfer = sp.cancel(
        generic_aa**2 * generic_conjugate**2
        + generic_ee * generic_conjugate
        + generic_dd
        - generic_dd * generic_h / (generic_aa**2 * generic_x**2)
    )
    if generic_transfer != 0:
        raise AssertionError("generic conjugate-root transfer identity failed")
    conjugate_transfer = {
        "generic_identity_verified": True,
        "identity": "H(D/(A^2*x)) = D*H(x)/(A^2*x^2)",
        "f_transfer": "H(a,b,c,e,1)=0 implies H(a,b,c,e,f)=0",
        "g_transfer": "H(1,a,b,e,c)=0 implies H(1,a,b,e,g)=0",
    }

    definitions = {
        "C": polynomial_object(sp.Poly(C, r, s, domain=sp.ZZ)),
        "a": canonical_fraction(a),
        "b": canonical_fraction(b),
        "c": canonical_fraction(c),
        "e": canonical_fraction(e),
        "f": canonical_fraction(f),
        "g": canonical_fraction(g),
    }
    residual_expressions = {
        "R1=f+1": f + 1,
        "R2=c*g+1": c * g + 1,
        "R3=f*g+1": f * g + 1,
    }
    residuals = {
        name: canonical_fraction(expression)
        for name, expression in residual_expressions.items()
    }
    residual_core = {
        name: {
            "numerator": value["numerator"]["canonical"],
            "denominator": value["denominator"]["canonical"],
        }
        for name, value in residuals.items()
    }
    residual_report = {
        "normal_form": (
            "primitive integer numerator/denominator after reduction to "
            "degree < 2 in r over Q(s), positive denominator leading coefficient"
        ),
        "base_curve": sp.sstr(C, order="lex"),
        "residuals": residuals,
        "combined_sha256": sha256_bytes(compact_json(residual_core)),
    }

    symbolic_report = {
        "status": "PASS",
        "sympy_version": sp.__version__,
        "quotient_ring": "Q(s)[r]/((3*s^2-4)*r^2-2*s*r+7-4*s^2)",
        "definitions": definitions,
        "source_square_identities": source_square_checks,
        "regular_and_conjugate_zero_identities": zero_identity_checks,
        "conjugate_root_transfer": conjugate_transfer,
        "automatic_pair_verification_scope": (
            "all 12 automatically supplied pair squares are checked exactly "
            "for each of the five printed examples"
        ),
        "residual_combined_sha256": residual_report["combined_sha256"],
    }
    return symbolic_report, residual_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    symbolic_report, residual_report = build_symbolic_report()
    examples = [
        audit_example(index, triple)
        for index, triple in enumerate(PRINTED_EXAMPLES, start=1)
    ]
    examples_report = {
        "status": "PASS",
        "source": "Dujella-Kazalicki-Petricevic, arXiv:2604.08729v1",
        "example_count": len(examples),
        "all_passed": all(example["passed"] for example in examples),
        "examples": examples,
    }

    symbolic_path = output_dir / "symbolic_report.json"
    residual_path = output_dir / "residual_polynomials.json"
    examples_path = output_dir / "printed_examples.json"
    write_json(symbolic_path, symbolic_report)
    write_json(residual_path, residual_report)
    write_json(examples_path, examples_report)

    summary = {
        "status": "PASS",
        "engine": "exotic_conjugate_primary.py",
        "symbolic_zero_identity_count": len(
            symbolic_report["regular_and_conjugate_zero_identities"]
        ),
        "symbolic_source_square_identity_count": len(
            symbolic_report["source_square_identities"]
        ),
        "generic_conjugate_transfer_verified": symbolic_report[
            "conjugate_root_transfer"
        ]["generic_identity_verified"],
        "residual_count": len(residual_report["residuals"]),
        "residual_combined_sha256": residual_report["combined_sha256"],
        "printed_example_count": len(examples),
        "printed_examples_all_passed": examples_report["all_passed"],
        "printed_example_residual_square_vectors": [
            [
                item["is_square"]
                for item in example["residual_pair_checks"].values()
            ]
            for example in examples
        ],
        "artifacts": {
            symbolic_path.name: sha256_file(symbolic_path),
            residual_path.name: sha256_file(residual_path),
            examples_path.name: sha256_file(examples_path),
        },
    }
    summary_path = output_dir / "summary.json"
    write_json(summary_path, summary)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "FAILED",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        raise
