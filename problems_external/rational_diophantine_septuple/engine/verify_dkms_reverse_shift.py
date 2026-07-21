#!/usr/bin/env python3
"""Independent algebra and branch-count replay for the DKMS reverse-shift run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp


t = sp.symbols("t")


def value(record: dict[str, object]) -> sp.Expr:
    return sp.cancel(sp.sympify(record["numerator"]) / sp.sympify(record["denominator"]))


def assert_zero(expr: sp.Expr, label: str) -> None:
    if sp.cancel(expr) != 0:
        raise AssertionError(label)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--expect-sha256", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    result_path = run_dir / "reduction.json"
    actual_sha = hashlib.sha256(result_path.read_bytes()).hexdigest().upper()
    if actual_sha != args.expect_sha256.upper():
        raise AssertionError(f"output hash mismatch: {actual_sha}")
    data = json.loads(result_path.read_text(encoding="utf-8"))

    family = {name: value(record) for name, record in data["family"].items()}
    published_t6 = {
        "a": sp.Rational(3780, 73),
        "b": sp.Rational(26645, 252),
        "c": sp.Rational(7, 13140),
        "d": sp.Rational(791361752602550684660, 1827893092234556692801),
        "e": sp.Rational(95104852709815809228981184, 351041911654651335633266955),
        "f": sp.Rational(3210891270762333567521084544, 21712719223923581005355),
    }
    for name, expected in published_t6.items():
        if family[name].subs(t, 6) != expected:
            raise AssertionError(f"published t=6 mismatch: {name}")

    if len(data["published_pair_checks"]) != 15:
        raise AssertionError("pair-check count is not 15")
    for check in data["published_pair_checks"]:
        left, right = check["pair"]
        root = value(check["root"])
        assert_zero(root*root - (1 + family[left]*family[right]),
                    f"pair root mismatch: {left},{right}")

    a, d, e, f = (family[name] for name in ("a", "d", "e", "f"))
    leading = sp.cancel(d*e*f)
    quadratic = sp.cancel(d*e+d*f+e*f)
    s = sp.cancel(1/leading)
    y_a = value(data["reverse_points"]["y_a"])
    y_s = value(data["reverse_points"]["y_s"])
    curve = lambda x: sp.cancel((d*x+1)*(e*x+1)*(f*x+1))
    assert_zero(y_a*y_a-curve(a), "A point is off the reverse curve")
    assert_zero(y_s*y_s-curve(s), "S point is off the reverse curve")

    audit_signs: dict[str, object] = {}
    for sign in ("plus", "minus"):
        sign_data = data["signs"][sign]
        g = value(sign_data["g"])
        slope = sp.cancel((y_a-y_s)/(a-s) if sign == "plus" else (y_a+y_s)/(a-s))
        expected_g = sp.cancel((slope*slope-quadratic)/leading-a-s)
        assert_zero(g-expected_g, f"group-law x mismatch: {sign}")

        for name in ("a", "d", "e", "f"):
            automatic = sign_data["automatic"][name]
            if not automatic["square"] or automatic["q"] != "1":
                raise AssertionError(f"automatic flag mismatch: {sign},{name}")
            root = value(automatic["root"])
            assert_zero(root*root-(1+family[name]*g),
                        f"automatic root mismatch: {sign},{name}")

        residuals: list[sp.Expr] = []
        for name in ("b", "c"):
            residual = sign_data[f"{name}_residual"]
            q = value(residual["q"])
            h = value(residual["h"])
            assert_zero(q*h*h-(1+family[name]*g),
                        f"residual decomposition mismatch: {sign},{name}")
            if residual["is_square"]:
                raise AssertionError(f"unexpected identity square: {sign},{name}")
            q_poly = sp.Poly(q, t, domain=sp.QQ)
            if sp.gcd(q_poly, q_poly.diff()).degree() != 0:
                raise AssertionError(f"residual is not squarefree: {sign},{name}")
            residuals.append(q_poly.monic())

        q1, q2 = residuals
        common = sp.gcd(q1, q2)
        union = sp.lcm(q1, q2).monic()
        infinity = bool((q1.degree() % 2) or (q2.degree() % 2))
        branches = int(union.degree()) + int(infinity)
        connected = q1.degree() > 0 and q2.degree() > 0 and common.degree() == 0
        genus = branches-3 if connected else None
        cover = sign_data["cover"]
        expected = {
            "q1_degree": int(q1.degree()),
            "q2_degree": int(q2.degree()),
            "common_degree": int(common.degree()),
            "union_degree": int(union.degree()),
            "infinity_branched": infinity,
            "branch_count": branches,
            "connected_v4": connected,
            "genus_if_connected": genus,
        }
        for key, expected_value in expected.items():
            if cover[key] != expected_value:
                raise AssertionError(f"cover mismatch: {sign},{key}")
        audit_signs[sign] = expected

    audit = {
        "status": "PASS",
        "reduction_sha256": actual_sha,
        "published_specialization": "t=6 matched all six values",
        "pair_identities_checked": 15,
        "reverse_points_checked": 2,
        "group_law_candidates_checked": 2,
        "automatic_identities_checked": 8,
        "residual_decompositions_checked": 4,
        "signs": audit_signs,
    }
    audit_path = run_dir / "independent_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
    audit_sha = hashlib.sha256(audit_path.read_bytes()).hexdigest().upper()
    print(json.dumps({"status": "PASS", "audit": str(audit_path), "sha256": audit_sha,
                      "plus_genus": audit_signs["plus"]["genus_if_connected"],
                      "minus_genus": audit_signs["minus"]["genus_if_connected"]}))


if __name__ == "__main__":
    main()
