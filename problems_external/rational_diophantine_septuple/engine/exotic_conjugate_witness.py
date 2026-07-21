#!/usr/bin/env python3
"""Independent finite-field branch witnesses for the exotic conjugate cover.

The calculation evaluates the registered formulas directly over ``F_p``.  It
does not consume a symbolic numerator, factorization, or branch polynomial
from the primary geometry calculation.  At a smooth point of the base curve,
a nonzero tangent derivative of one vanishing residual, with the other two
residuals units, gives an odd valuation row for that residual square class.
Two independent rows certify geometric square-class rank at least two.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class ZeroDenominator(Exception):
    """A registered rational formula is undefined at the residue point."""


@dataclass(frozen=True)
class Dual:
    """A value and one directional derivative over a prime field."""

    value: int
    derivative: int
    prime: int

    def _coerce(self, other: object) -> "Dual":
        if isinstance(other, Dual):
            if other.prime != self.prime:
                raise ValueError("mixed characteristics")
            return other
        if isinstance(other, int):
            return Dual(other % self.prime, 0, self.prime)
        return NotImplemented

    def __add__(self, other: object) -> "Dual":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return Dual(
            (self.value + rhs.value) % self.prime,
            (self.derivative + rhs.derivative) % self.prime,
            self.prime,
        )

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.value % self.prime, -self.derivative % self.prime, self.prime)

    def __sub__(self, other: object) -> "Dual":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self + (-rhs)

    def __rsub__(self, other: object) -> "Dual":
        lhs = self._coerce(other)
        if lhs is NotImplemented:
            return NotImplemented
        return lhs - self

    def __mul__(self, other: object) -> "Dual":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return Dual(
            self.value * rhs.value % self.prime,
            (self.derivative * rhs.value + self.value * rhs.derivative) % self.prime,
            self.prime,
        )

    __rmul__ = __mul__

    def inverse(self) -> "Dual":
        if self.value == 0:
            raise ZeroDenominator
        inverse_value = pow(self.value, -1, self.prime)
        return Dual(
            inverse_value,
            -self.derivative * inverse_value * inverse_value % self.prime,
            self.prime,
        )

    def __truediv__(self, other: object) -> "Dual":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self * rhs.inverse()

    def __rtruediv__(self, other: object) -> "Dual":
        lhs = self._coerce(other)
        if lhs is NotImplemented:
            return NotImplemented
        return lhs / self

    def __pow__(self, exponent: int) -> "Dual":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        answer = Dual(1, 0, self.prime)
        base = self
        n = exponent
        while n:
            if n & 1:
                answer = answer * base
            base = base * base
            n >>= 1
        return answer


def base_curve(r: Any, s: Any) -> Any:
    return 3 * r**2 * s**2 - 4 * r**2 - 2 * r * s - 4 * s**2 + 7


def base_gradient(prime: int, r: int, s: int) -> tuple[int, int]:
    derivative_r = (6 * r * s * s - 8 * r - 2 * s) % prime
    derivative_s = (6 * r * r * s - 2 * r - 8 * s) % prime
    return derivative_r, derivative_s


def conjugate(p: Dual, q: Dual, u: Dual, v: Dual, x: Dual) -> tuple[Dual, dict[str, Dual]]:
    A = p * q * u * v - 1
    B = 2 * p * q * u + p + q + u - v
    N = (p * q + 1) * (p * u + 1) * (q * u + 1)
    denominator = A**2 * x
    result = (B**2 - 4 * N) / denominator
    return result, {"A": A, "x": x, "denominator": denominator}


def direct_family_data(r: Dual, s: Dual) -> dict[str, Any]:
    """Evaluate a,b,c,e,f,g and the three residuals directly."""

    one = Dual(1, 0, r.prime)
    two = Dual(2, 0, r.prime)
    a = r**2 - 1
    b = s**2 - 1
    c = (-r**2 * s**2 + 2 * s**2 + 2 * r**2 - 5) / two

    L = a * b * c - 1
    K = 2 * a * b + 1 + a + b - c
    M = (a + 1) * (b + 1) * (a * b + 1)
    e_denominator = L**2
    e = (4 * M * c - 2 * L * K) / e_denominator

    f, f_denominators = conjugate(a, b, c, e, one)
    g, g_denominators = conjugate(one, a, b, e, c)
    residuals = [f + 1, c * g + 1, f * g + 1]

    seven_values = [one, a, b, c, e, f, g]
    denominator_factors = [two, L, f_denominators["A"], g_denominators["A"], c]
    bad_locus_factors = list(denominator_factors)
    bad_locus_factors.extend(seven_values)
    for i, left in enumerate(seven_values):
        for right in seven_values[i + 1 :]:
            bad_locus_factors.append(left - right)
    bad_locus_product = one
    for factor in bad_locus_factors:
        bad_locus_product *= factor

    return {
        "named_values": {"a": a, "b": b, "c": c, "e": e, "f": f, "g": g},
        "seven_values": seven_values,
        "residuals": residuals,
        "denominator_values": {
            "2": two,
            "L": L,
            "A_f": f_denominators["A"],
            "A_g": g_denominators["A"],
            "c": c,
            "e_denominator": e_denominator,
            "f_denominator": f_denominators["denominator"],
            "g_denominator": g_denominators["denominator"],
        },
        "bad_locus_product": bad_locus_product,
    }


def rank_f2(rows: Iterable[list[int]]) -> int:
    packed = []
    for row in rows:
        value = 0
        for index, bit in enumerate(row):
            value |= (bit & 1) << index
        packed.append(value)
    rank = 0
    for column in range(3):
        pivot = next((i for i in range(rank, len(packed)) if (packed[i] >> column) & 1), None)
        if pivot is None:
            continue
        packed[rank], packed[pivot] = packed[pivot], packed[rank]
        for i in range(len(packed)):
            if i != rank and ((packed[i] >> column) & 1):
                packed[i] ^= packed[rank]
        rank += 1
    return rank


def is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def inspect_point(prime: int, r0: int, s0: int) -> dict[str, Any] | None:
    gradient_r, gradient_s = base_gradient(prime, r0, s0)
    if gradient_r == 0 and gradient_s == 0:
        return None

    # Tangent vector (dr,ds)=(C_s,-C_r).
    r = Dual(r0, gradient_s, prime)
    s = Dual(s0, -gradient_r % prime, prime)
    curve_value = base_curve(r, s)
    if curve_value.value != 0 or curve_value.derivative != 0:
        raise AssertionError("declared tangent direction does not annihilate C")
    try:
        data = direct_family_data(r, s)
    except ZeroDenominator:
        return None

    if data["bad_locus_product"].value == 0:
        return None
    residuals: list[Dual] = data["residuals"]
    zero_indices = [i for i, residual in enumerate(residuals) if residual.value == 0]
    if len(zero_indices) != 1:
        return None
    index = zero_indices[0]
    if residuals[index].derivative == 0:
        return None

    parity_row = [1 if i == index else 0 for i in range(3)]
    jacobian_determinant = (-residuals[index].derivative) % prime
    return {
        "prime": prime,
        "point_rs": [r0, s0],
        "base_gradient": [gradient_r, gradient_s],
        "tangent_vector": [gradient_s, -gradient_r % prime],
        "vanishing_residual_index": index,
        "vanishing_residual": ["f+1", "c*g+1", "f*g+1"][index],
        "residual_values": [residual.value for residual in residuals],
        "tangent_derivatives": [residual.derivative for residual in residuals],
        "intersection_jacobian_determinant": jacobian_determinant,
        "parity_row": parity_row,
        "named_values": {
            name: value.value for name, value in data["named_values"].items()
        },
        "seven_values_1_a_b_c_e_f_g": [value.value for value in data["seven_values"]],
        "denominator_values": {
            name: value.value for name, value in data["denominator_values"].items()
        },
        "bad_locus_product": data["bad_locus_product"].value,
    }


def find_witnesses(primes: list[int], target_rank: int) -> dict[str, Any]:
    if target_rank not in (2, 3):
        raise ValueError("target rank must be 2 or 3")
    witnesses_by_index: dict[int, dict[str, Any]] = {}
    scanned: list[dict[str, int]] = []

    for prime in primes:
        if prime == 2 or not is_prime(prime):
            raise ValueError(f"not an odd prime: {prime}")
        curve_points = 0
        smooth_points = 0
        admissible_points = 0
        transverse_points = 0
        for r0 in range(prime):
            for s0 in range(prime):
                if base_curve(r0, s0) % prime != 0:
                    continue
                curve_points += 1
                gradient = base_gradient(prime, r0, s0)
                if gradient == (0, 0):
                    continue
                smooth_points += 1
                try:
                    witness = inspect_point(prime, r0, s0)
                except AssertionError:
                    raise
                if witness is None:
                    # Count admissible points separately by reevaluating only when cheap.
                    continue
                admissible_points += 1
                transverse_points += 1
                index = witness["vanishing_residual_index"]
                witnesses_by_index.setdefault(index, witness)
        rows = [witness["parity_row"] for witness in witnesses_by_index.values()]
        scanned.append(
            {
                "prime": prime,
                "curve_points": curve_points,
                "smooth_curve_points": smooth_points,
                "transverse_single_residual_points": transverse_points,
                "new_square_class_rows_so_far": len(witnesses_by_index),
                "parity_rank_so_far": rank_f2(rows),
            }
        )
        if rank_f2(rows) >= target_rank:
            break

    ordered = [witnesses_by_index[index] for index in sorted(witnesses_by_index)]
    parity_matrix = [witness["parity_row"] for witness in ordered]
    parity_rank = rank_f2(parity_matrix)
    if parity_rank < target_rank:
        raise RuntimeError(
            f"only parity rank {parity_rank}; required {target_rank}; rows={parity_matrix}"
        )
    distinct_branch_labels = [
        f"p={witness['prime']},r={witness['point_rs'][0]},s={witness['point_rs'][1]},"
        f"R={witness['vanishing_residual_index'] + 1}"
        for witness in ordered
    ]
    return {
        "status": "PASS",
        "method": "direct dual-number evaluation of registered rational formulas over F_p",
        "independence_from_primary": (
            "No symbolic residual numerator, factorization, resultant, or branch polynomial is read."
        ),
        "base_curve": "3*r^2*s^2-4*r^2-2*r*s-4*s^2+7",
        "residual_order": ["f+1", "c*g+1", "f*g+1"],
        "parity_matrix": parity_matrix,
        "parity_rank_over_F2": parity_rank,
        "geometric_square_class_rank_lower_bound": parity_rank,
        "distinct_transverse_branch_witnesses": len(ordered),
        "branch_labels": distinct_branch_labels,
        "witnesses": ordered,
        "scanned": scanned,
        "interpretation": [
            "Each point is smooth on C and has nonzero registered denominators and bad-locus product.",
            "Exactly one residual vanishes and its derivative in the displayed tangent direction is nonzero.",
            "The nonzero 2 by 2 intersection determinant gives a simple local zero by Hensel lifting.",
            "The displayed odd-valuation rows are independent over F_2.",
        ],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--primes",
        default="5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251",
    )
    parser.add_argument("--target-rank", type=int, choices=(2, 3), default=3)
    args = parser.parse_args()
    primes = [int(token) for token in args.primes.split(",") if token]
    result = find_witnesses(primes, args.target_rank)
    engine_path = Path(__file__).resolve()
    result["engine_file"] = str(engine_path)
    result["engine_sha256"] = sha256(engine_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
