#!/usr/bin/env python3
"""Exact finite-field branch witnesses for the strong-pair Kummer cover.

This is a geometry calculation, not a rational-parameter search.  At a smooth
point of the base curve over F_p, a simple zero of one residual function while
the other two are units gives a transverse branch divisor in characteristic
zero by multivariate Hensel lifting.  Unit witnesses for f+ and f- certify
geometric square-class rank at least two.  Since the base has genus one,
Riemann--Hurwitz then proves that every geometric component has genus at least
three, irrespective of whether the unramified-looking f0 class raises the rank
from two to three.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class ZeroDenominator(Exception):
    pass


@dataclass(frozen=True)
class Dual:
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
        return self + (-self._coerce(other))

    def __rsub__(self, other: object) -> "Dual":
        return self._coerce(other) - self

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
        inv = pow(self.value, -1, self.prime)
        return Dual(inv, -self.derivative * inv * inv % self.prime, self.prime)

    def __truediv__(self, other: object) -> "Dual":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self * rhs.inverse()

    def __rtruediv__(self, other: object) -> "Dual":
        return self._coerce(other) / self

    def __pow__(self, exponent: int) -> "Dual":
        if exponent < 0:
            return (self.inverse()) ** (-exponent)
        result = Dual(1, 0, self.prime)
        base = self
        n = exponent
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result


Point = tuple[Dual, Dual] | None


def base_polynomial(u: Any, v: Any) -> Any:
    return (
        3 * u**4 * v**4
        - 8 * u**4 * v**3
        + 6 * u**4 * v**2
        - u**4
        - 8 * u**3 * v**4
        + 4 * u**3 * v**3
        - 8 * u**3 * v**2
        + 12 * u**3 * v
        + 6 * u**2 * v**4
        - 8 * u**2 * v**3
        + 4 * u**2 * v**2
        + 8 * u**2 * v
        + 6 * u**2
        + 12 * u * v**3
        + 8 * u * v**2
        + 4 * u * v
        + 8 * u
        - v**4
        + 6 * v**2
        + 8 * v
        + 3
    )


def add_points(left: Point, right: Point, a2: Dual) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        ysum = y1 + y2
        if ysum.value == 0 and ysum.derivative == 0:
            return None
        raise ZeroDenominator
    slope = (y2 - y1) / (x2 - x1)
    x3 = slope**2 - a2 - x1 - x2
    y3 = -y1 + slope * (x1 - x3)
    return x3, y3


def double_point(point: Point, a2: Dual, a4: Dual) -> Point:
    if point is None:
        return None
    x, y = point
    if y.value == 0:
        return None
    slope = (3 * x**2 + 2 * a2 * x + a4) / (2 * y)
    x2 = slope**2 - a2 - 2 * x
    y2 = -y + slope * (x - x2)
    return x2, y2


def negate(point: Point) -> Point:
    if point is None:
        return None
    return point[0], -point[1]


def curve_rhs(x: Dual, a2: Dual, a4: Dual, a6: Dual) -> Dual:
    return x**3 + a2 * x**2 + a4 * x + a6


def residual_data(u: Dual, v: Dual) -> dict[str, Any]:
    prime = u.prime
    one = Dual(1, 0, prime)
    zero = Dual(0, 0, prime)
    D = u * v - u - v - 1
    a = 2 * u / (u**2 - 1)
    b = 2 * v / (v**2 - 1)
    c = 2 * (u**2 - 1) * (v**2 - 1) / D**2

    root_ab = 2 * (u * v + 1) * D / ((u**2 - 1) * (v**2 - 1))
    root_ac = (u * v - u + v + 1) / D
    root_bc = (u * v + u - v + 1) / D
    y_s = root_ab * root_ac * root_bc

    ab = a * b
    ac = a * c
    bc = b * c
    abc = a * b * c
    a2 = ab + ac + bc
    a4 = ab * ac + ab * bc + ac * bc
    a6 = ab * ac * bc

    P: Point = (zero, abc)
    S: Point = (one, y_s)
    if P[1] ** 2 != curve_rhs(P[0], a2, a4, a6):
        raise AssertionError("P is off the induced curve")
    if S[1] ** 2 != curve_rhs(S[0], a2, a4, a6):
        raise AssertionError("S is off the induced curve")

    P2 = double_point(P, a2, a4)
    P3 = add_points(P2, P, a2)
    P4 = double_point(P2, a2, a4)
    P5 = add_points(P4, P, a2)
    S2 = double_point(S, a2, a4)
    S3 = add_points(S2, S, a2)
    if S3 is not None:
        raise AssertionError("3S is not the identity")
    if P3 is None or P5 is None:
        raise ZeroDenominator

    P3_plus = add_points(P3, S, a2)
    P3_minus = add_points(P3, negate(S), a2)
    if P3_plus is None or P3_minus is None:
        raise ZeroDenominator

    d0 = P3[0] / abc
    dplus = P3_plus[0] / abc
    dminus = P3_minus[0] / abc
    g = P5[0] / abc
    residuals = [one + g * d0, one + g * dplus, one + g * dminus]

    roots_ok = [
        root_ab**2 == one + ab,
        root_ac**2 == one + ac,
        root_bc**2 == one + bc,
    ]
    if not all(roots_ok):
        raise AssertionError("published pair root failed")

    values = [a, b, c, d0, dplus, dminus, g]
    return {
        "residuals": residuals,
        "values": values,
        "roots": [root_ab, root_ac, root_bc],
        "abc": abc,
    }


def value_only_p(prime: int, u: int, v: int) -> int:
    return int(base_polynomial(u, v)) % prime


def tangent_data(prime: int, u0: int, v0: int) -> tuple[int, int, dict[str, Any]]:
    du = base_polynomial(Dual(u0, 1, prime), Dual(v0, 0, prime)).derivative
    dv = base_polynomial(Dual(u0, 0, prime), Dual(v0, 1, prime)).derivative
    if du == 0 and dv == 0:
        raise ZeroDenominator
    # Tangent direction (du_coord,dv_coord)=(p_v,-p_u).
    u = Dual(u0, dv, prime)
    v = Dual(v0, -du % prime, prime)
    if base_polynomial(u, v) != Dual(0, 0, prime):
        raise AssertionError("tangent vector does not annihilate p")
    return du, dv, residual_data(u, v)


def all_distinct_nonzero(values: Iterable[Dual]) -> bool:
    raw = [x.value for x in values]
    return all(raw) and len(set(raw)) == len(raw)


def find_witnesses(primes: list[int]) -> dict[str, Any]:
    witnesses: dict[int, dict[str, Any]] = {}
    required = {1, 2}
    scanned: list[dict[str, int]] = []
    for prime in primes:
        base_points = 0
        admissible = 0
        for u0 in range(prime):
            for v0 in range(prime):
                if value_only_p(prime, u0, v0) != 0:
                    continue
                base_points += 1
                try:
                    pu, pv, data = tangent_data(prime, u0, v0)
                except (ZeroDenominator, AssertionError):
                    continue
                if not all_distinct_nonzero(data["values"]):
                    continue
                admissible += 1
                residuals: list[Dual] = data["residuals"]
                zeros = [i for i, f in enumerate(residuals) if f.value == 0]
                if len(zeros) != 1:
                    continue
                index = zeros[0]
                if residuals[index].derivative == 0 or index in witnesses:
                    continue
                witnesses[index] = {
                    "prime": prime,
                    "point_uv": [u0, v0],
                    "base_gradient": [pu, pv],
                    "tangent_vector": [pv, -pu % prime],
                    "residual_values": [f.value for f in residuals],
                    "tangent_derivatives": [f.derivative for f in residuals],
                    "parity_vector": [1 if i == index else 0 for i in range(3)],
                    "seven_values": [x.value for x in data["values"]],
                    "three_pair_roots": [x.value for x in data["roots"]],
                }
                if required.issubset(witnesses):
                    scanned.append(
                        {"prime": prime, "base_points": base_points, "admissible_points": admissible}
                    )
                    return make_result(witnesses, scanned)
        scanned.append({"prime": prime, "base_points": base_points, "admissible_points": admissible})
    raise RuntimeError(f"missing required witness classes: {sorted(required - set(witnesses))}")


def make_result(witnesses: dict[int, dict[str, Any]], scanned: list[dict[str, int]]) -> dict[str, Any]:
    ordered = [witnesses[i] for i in sorted(witnesses)]
    # The f+ and f- unit rows are independent over F_2.  The f0 class may or
    # may not add a third unramified square class; either outcome is decisive.
    branch_degree_lower_bound = 2
    square_class_rank_lower_bound = 2
    square_class_rank_upper_bound = 3
    component_count_upper_bound = 1 << (3 - square_class_rank_lower_bound)
    component_genus_lower_bound = 1 + branch_degree_lower_bound
    return {
        "status": "PASS",
        "method": "transverse finite-field branch witnesses plus multivariate Hensel lifting",
        "base_geometric_genus": 1,
        "square_class_parity_matrix": [w["parity_vector"] for w in ordered],
        "geometric_square_class_rank_lower_bound": square_class_rank_lower_bound,
        "geometric_square_class_rank_upper_bound": square_class_rank_upper_bound,
        "geometrically_connected_components_upper_bound": component_count_upper_bound,
        "connected_component_degree": "4 if rank=2; 8 if rank=3",
        "distinct_geometric_branch_points_lower_bound": branch_degree_lower_bound,
        "riemann_hurwitz": "2*gX-2 = 2^(r-1)*R for gC=1; hence gX=1+2^(r-2)*R",
        "geometric_component_genus_lower_bound": component_genus_lower_bound,
        "low_genus_gate": "CLOSED: every geometric horizontal component has genus >= 3 > 2",
        "witnesses": ordered,
        "scanned": scanned,
        "notes": [
            "Each witness is smooth on p=0, has all group-law denominators nonzero, and has seven distinct nonzero residue values.",
            "At each witness exactly one residual vanishes transversely and the other two are units.",
            "The f+ and f- unit parity rows prove rank at least two in algebraic-closure square classes, not only over Q.",
            "If rank=2 there are two degree-four components of genus at least 3; if rank=3 there is one degree-eight component of genus at least 5.",
            "The calculation certifies a decisive lower bound; it does not claim the complete branch divisor, f0 dependency, or exact genus.",
        ],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--primes",
        default="101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199",
    )
    args = parser.parse_args()
    primes = [int(item) for item in args.primes.split(",") if item]
    result = find_witnesses(primes)
    result["engine_file"] = str(Path(__file__).resolve())
    result["engine_sha256"] = sha256(Path(__file__).resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
