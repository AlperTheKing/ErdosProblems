"""Verify a scalar supermultiplicative countermodel to C102 Gate A."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


Q = 360
KNOWN_D = {
    1: 60,
    2: 13_068,
    3: 3_542_949,
    4: 1_054_111_467,
    5: 330_159_210_305,
}
KNOWN_S = {1: 36, 2: 7_779, 3: 2_111_340}
TAIL_NUMERATOR = 5
TAIL_SHIFT = 100
TAIL_START = 6


def target_density(k: int) -> Fraction:
    if k in KNOWN_D:
        return Fraction(KNOWN_D[k], Q**k)
    return Fraction(TAIL_NUMERATOR, k + TAIL_SHIFT)


def support_size(k: int) -> int:
    if k in KNOWN_D:
        return KNOWN_D[k]
    return TAIL_NUMERATOR * Q**k // (k + TAIL_SHIFT)


def selected_size(k: int) -> int:
    if k in KNOWN_S:
        return KNOWN_S[k]
    return support_size(k)


def ratio_payload(value: Fraction) -> dict[str, str | float]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": float(value),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--finite-check", type=int, default=200)
    args = parser.parse_args()
    if args.finite_check < 2 * TAIL_START:
        raise ValueError("--finite-check is too small")

    known_rows = []
    for k in sorted(KNOWN_D):
        d = support_size(k)
        s = selected_size(k)
        assert 2 * s >= d and s <= d
        known_rows.append(
            {
                "k": k,
                "D": d,
                "selected_size": s,
                "selected_size_is_measured": k in KNOWN_S,
                "D_over_Q_pow_k": ratio_payload(Fraction(d, Q**k)),
            }
        )

    for k in range(1, args.finite_check):
        assert Fraction(support_size(k), Q**k) >= Fraction(
            support_size(k + 1), Q ** (k + 1)
        )
    monotone_tail_base_margin = (
        TAIL_NUMERATOR * Q**TAIL_START
        - (TAIL_START + TAIL_SHIFT) * (TAIL_START + TAIL_SHIFT + 1)
    )
    assert monotone_tail_base_margin > 0

    pair_checks = []
    for m in range(1, args.finite_check + 1):
        for n in range(1, args.finite_check + 1 - m):
            lhs = support_size(m + n)
            rhs = support_size(m) * support_size(n)
            assert lhs >= rhs
            if m <= 6 and n <= 6:
                pair_checks.append(
                    {
                        "m": m,
                        "n": n,
                        "D_m_plus_n": str(lhs),
                        "D_m_times_D_n": str(rhs),
                        "margin": str(lhs - rhs),
                    }
                )

    # Infinite-tail certificate.  The cross inequality is weakest at n=6,
    # while the tail-tail polynomial is increasing in each variable on n>=6.
    cross_rows = []
    for m in sorted(KNOWN_D):
        left = target_density(m)
        right = Fraction(TAIL_START + TAIL_SHIFT, m + TAIL_START + TAIL_SHIFT)
        assert left <= right
        cross_rows.append(
            {
                "prefix_k": m,
                "prefix_density": ratio_payload(left),
                "minimum_cross_bound": ratio_payload(right),
            }
        )
    tail_tail_minimum_margin = (
        (TAIL_START + TAIL_SHIFT) ** 2
        - TAIL_NUMERATOR * (2 * TAIL_START + TAIL_SHIFT)
    )
    assert tail_tail_minimum_margin > 0

    central_rows = []
    for K in (18, 30, 100, 1_000, 10_000):
        first = (K + 2) // 3
        last = 2 * K // 3
        exact_upper = sum(
            Fraction(TAIL_NUMERATOR**2, (i + TAIL_SHIFT) * (K - i + TAIL_SHIFT))
            for i in range(first, last + 1)
        )
        simple_upper = Fraction(
            TAIL_NUMERATOR**2 * (K + 1) * 9,
            (K + 3 * TAIL_SHIFT) ** 2,
        )
        assert exact_upper <= simple_upper
        central_rows.append(
            {
                "K": K,
                "exact_density_upper": ratio_payload(exact_upper),
                "simple_density_upper": ratio_payload(simple_upper),
            }
        )

    result = {
        "purpose": "scalar countermodel; not a claim about the actual affine supports",
        "ray": [3, 2, 1],
        "Q": Q,
        "known_prefix": known_rows,
        "tail_definition": {
            "start_k": TAIL_START,
            "D_k": "floor(5*360^k/(k+100))",
            "s_k": "D_k",
        },
        "finite_supermultiplicativity_check": {
            "max_sum": args.finite_check,
            "sample_rows": pair_checks,
        },
        "infinite_certificate": {
            "prefix_tail_checks": cross_rows,
            "tail_tail_minimum_at": [TAIL_START, TAIL_START],
            "tail_tail_integer_margin": tail_tail_minimum_margin,
            "normalized_tail_monotonicity_base_margin": str(monotone_tail_base_margin),
            "normalized_tail_monotonicity_ratio": (
                "360*(k+100)/(k+102) > 1 for k>=6"
            ),
            "floor_argument": (
                "D_m*D_n is an integer bounded by the unfloored target for D_(m+n), "
                "hence it is at most its floor"
            ),
        },
        "gate_A_upper_bounds": central_rows,
        "limit": "N_K/360^K <= 225*(K+1)/(K+300)^2 -> 0",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
