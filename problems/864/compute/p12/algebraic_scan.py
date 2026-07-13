"""Exact construction scan for the reflected lane of Erdos Problem 864.

For an integer Sidon set B with min(B)=0 and span L, the reflected set

    B union (M-B)

is admissible exactly when M > 2L and M is not in S(B)+Delta+(B).  This
script generates classical cyclic Sidon families, enumerates affine units and
cyclic cuts, and checks that literal integer criterion (diagonals included).

All arithmetic is integer or finite-field arithmetic over a prime field.
Floating-point numbers are emitted only as human-readable diagnostics.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from sympy import factorint
from sympy.polys.domains import ZZ
from sympy.polys.galoistools import gf_irreducible_p


Elt = tuple[int, ...]


def prime_power(q: int) -> tuple[int, int]:
    """Return q=p^r, rejecting non-prime-powers."""
    if q < 2:
        raise ValueError("q must be at least 2")
    fac = factorint(q)
    if len(fac) != 1:
        raise ValueError(f"{q} is not a prime power")
    p, r = next(iter(fac.items()))
    return int(p), int(r)


def first_irreducible(p: int, degree: int) -> tuple[int, ...]:
    """Lexicographically first monic irreducible polynomial, low first."""
    for low in itertools.product(range(p), repeat=degree):
        if low[0] == 0:
            continue
        high = [1, *reversed(low)]
        if gf_irreducible_p(high, p, ZZ):
            return (*low, 1)
    raise RuntimeError("irreducible polynomial search failed")


@dataclass(frozen=True)
class FiniteField:
    p: int
    modulus: tuple[int, ...]

    @property
    def degree(self) -> int:
        return len(self.modulus) - 1

    @property
    def size(self) -> int:
        return self.p**self.degree

    @property
    def zero(self) -> Elt:
        return (0,) * self.degree

    @property
    def one(self) -> Elt:
        return (1,) + (0,) * (self.degree - 1)

    def add(self, x: Elt, y: Elt) -> Elt:
        return tuple((a + b) % self.p for a, b in zip(x, y))

    def sub(self, x: Elt, y: Elt) -> Elt:
        return tuple((a - b) % self.p for a, b in zip(x, y))

    def mul(self, x: Elt, y: Elt) -> Elt:
        d = self.degree
        tmp = [0] * (2 * d - 1)
        for i, a in enumerate(x):
            for j, b in enumerate(y):
                tmp[i + j] = (tmp[i + j] + a * b) % self.p
        for k in range(2 * d - 2, d - 1, -1):
            c = tmp[k] % self.p
            if not c:
                continue
            for j in range(d):
                tmp[k - d + j] = (
                    tmp[k - d + j] - c * self.modulus[j]
                ) % self.p
        return tuple(tmp[:d])

    def pow(self, x: Elt, exponent: int) -> Elt:
        if exponent < 0:
            if x == self.zero:
                raise ZeroDivisionError
            x = self.pow(x, self.size - 2)
            exponent = -exponent
        out = self.one
        base = x
        while exponent:
            if exponent & 1:
                out = self.mul(out, base)
            base = self.mul(base, base)
            exponent >>= 1
        return out

    def decode(self, code: int) -> Elt:
        coeffs = []
        for _ in range(self.degree):
            coeffs.append(code % self.p)
            code //= self.p
        return tuple(coeffs)

    def primitive(self) -> Elt:
        order = self.size - 1
        prime_divisors = tuple(int(x) for x in factorint(order))
        for code in range(2, self.size):
            x = self.decode(code)
            if x == self.zero:
                continue
            if all(self.pow(x, order // r) != self.one for r in prime_divisors):
                return x
        raise RuntimeError("primitive element search failed")


def extension_field(p: int, degree: int) -> FiniteField:
    return FiniteField(p, first_irreducible(p, degree))


def bose_chowla(q: int) -> tuple[int, tuple[int, ...], dict[str, object]]:
    """Bose-Chowla Sidon set in Z/(q^2-1), for every prime power q."""
    p, r = prime_power(q)
    field = extension_field(p, 2 * r)
    theta = field.primitive()
    modulus = q * q - 1
    out = []
    power = field.one
    for exponent in range(modulus):
        delta = field.sub(power, theta)
        if field.pow(delta, q) == delta:
            out.append(exponent)
        power = field.mul(power, theta)
    if len(out) != q:
        raise AssertionError((q, len(out), out))
    return modulus, tuple(out), {
        "base_prime": p,
        "extension_degree": 2 * r,
        "irreducible_low_first": field.modulus,
        "primitive": theta,
    }


def singer(q: int) -> tuple[int, tuple[int, ...], dict[str, object]]:
    """Singer perfect difference set in Z/(q^2+q+1)."""
    p, r = prime_power(q)
    field = extension_field(p, 3 * r)
    alpha = field.primitive()
    modulus = q * q + q + 1
    out = []
    power = field.one
    for exponent in range(modulus):
        trace = field.add(power, field.pow(power, q))
        trace = field.add(trace, field.pow(power, q * q))
        if trace == field.zero:
            out.append(exponent)
        power = field.mul(power, alpha)
    if len(out) != q + 1:
        raise AssertionError((q, len(out), out))
    return modulus, tuple(out), {
        "base_prime": p,
        "extension_degree": 3 * r,
        "irreducible_low_first": field.modulus,
        "primitive": alpha,
    }


def primitive_root_prime(p: int) -> int:
    if len(factorint(p)) != 1 or next(iter(factorint(p).values())) != 1:
        raise ValueError("Ruzsa parameter must be prime")
    factors = tuple(int(x) for x in factorint(p - 1))
    for g in range(2, p):
        if all(pow(g, (p - 1) // r, p) != 1 for r in factors):
            return g
    raise RuntimeError("primitive root search failed")


def ruzsa(p: int) -> tuple[int, tuple[int, ...], dict[str, object]]:
    """Ruzsa graph Sidon set in Z/(p(p-1))."""
    g = primitive_root_prime(p)
    modulus = p * (p - 1)
    out = tuple(
        sorted((i * p - (p - 1) * pow(g, i, p)) % modulus for i in range(p - 1))
    )
    if len(set(out)) != p - 1:
        raise AssertionError("Ruzsa residues collided")
    return modulus, out, {"primitive_root": g}


def unordered_sums(values: Sequence[int]) -> set[int]:
    return {values[i] + values[j] for i in range(len(values)) for j in range(i, len(values))}


def positive_differences(values: Sequence[int]) -> set[int]:
    return {values[j] - values[i] for i in range(len(values)) for j in range(i + 1, len(values))}


def literal_sidon(values: Sequence[int]) -> bool:
    counts: Counter[int] = Counter()
    for i, a in enumerate(values):
        for b in values[i:]:
            counts[a + b] += 1
    return max(counts.values(), default=0) == 1


def modular_sum_profile(values: Sequence[int], modulus: int) -> tuple[int, int]:
    counts: Counter[int] = Counter()
    for i, a in enumerate(values):
        for b in values[i:]:
            counts[(a + b) % modulus] += 1
    return len(counts), max(counts.values(), default=0)


def modular_3b_minus_b(values: Sequence[int], modulus: int) -> set[int]:
    pair_sums = {(a + b) % modulus for a in values for b in values}
    differences = {(a - b) % modulus for a in values for b in values}
    return {(s + d) % modulus for s in pair_sums for d in differences}


def cyclic_lifts(
    values: Sequence[int], modulus: int
) -> Iterator[tuple[tuple[int, ...], int, int]]:
    vals = sorted(set(values))
    for index, base in enumerate(vals):
        previous = vals[index - 1]
        gap = (base - previous) % modulus
        yield tuple(sorted((x - base) % modulus for x in vals)), base, gap


def unit_multipliers(modulus: int, limit: int | None) -> list[int]:
    units = [u for u in range(1, modulus) if math.gcd(u, modulus) == 1]
    # Multipliers u and -u produce reflected lift collections.
    units = [u for u in units if u <= (-u) % modulus]
    if limit is None or limit >= len(units):
        return units
    if limit < 1:
        return []
    # Deterministic coverage of the whole ordered unit list.
    indices = sorted({round(i * (len(units) - 1) / (limit - 1)) for i in range(limit)}) if limit > 1 else [0]
    return [units[i] for i in indices]


def first_zero_bit(bits: int, lo: int, hi: int) -> int | None:
    for x in range(lo, hi + 1):
        if not ((bits >> x) & 1):
            return x
    return None


def analyze_lift(values: Sequence[int]) -> dict[str, object]:
    b = tuple(sorted(values))
    if not b or b[0] != 0:
        raise ValueError("lift must be normalized and nonempty")
    p = len(b)
    span = b[-1]
    sidon = literal_sidon(b)
    sums = unordered_sums(b)
    diffs = positive_differences(b)
    sum_bits = 0
    for s in sums:
        sum_bits |= 1 << s
    forbidden = 0
    for d in diffs:
        forbidden |= sum_bits << d
    lo = 2 * span + 1
    hi = 3 * p * p - 1
    hole = first_zero_bit(forbidden, lo, hi) if sidon and lo <= hi else None
    return {
        "points": b,
        "size": p,
        "span": span,
        "sidon": sidon,
        "candidate_center": hole,
        "center_over_p2": str(Fraction(hole, p * p)) if hole is not None else None,
        "window_nonempty": lo <= hi,
        "forbidden_count_in_window": (
            sum((forbidden >> x) & 1 for x in range(lo, hi + 1)) if lo <= hi else 0
        ),
        "window_size": max(0, hi - lo + 1),
    }


def scan_family(
    family: str,
    parameter: int,
    unit_limit: int | None,
) -> dict[str, object]:
    generators = {"bose": bose_chowla, "singer": singer, "ruzsa": ruzsa}
    modulus, residues, metadata = generators[family](parameter)
    sum_support, max_sum_mult = modular_sum_profile(residues, modulus)
    modular_cover = modular_3b_minus_b(residues, modulus)
    units = unit_multipliers(modulus, unit_limit)
    seen: set[tuple[int, ...]] = set()
    best: dict[str, object] | None = None
    candidate_count = 0
    sidon_lifts = 0
    for u in units:
        transformed = tuple((u * x) % modulus for x in residues)
        for lift, base, cut_gap in cyclic_lifts(transformed, modulus):
            if lift in seen:
                continue
            seen.add(lift)
            rec = analyze_lift(lift)
            if rec["sidon"]:
                sidon_lifts += 1
            if rec["candidate_center"] is not None:
                candidate_count += 1
                rec = {
                    **rec,
                    "affine_multiplier": u,
                    "cut_base": base,
                    "cut_gap": cut_gap,
                    "hole_offset_above_2span": int(rec["candidate_center"])
                    - 2 * int(rec["span"]),
                }
                key = (int(rec["candidate_center"]), int(rec["span"]), tuple(rec["points"]))
                if best is None or key < (
                    int(best["candidate_center"]), int(best["span"]), tuple(best["points"])
                ):
                    best = rec
    return {
        "family": family,
        "parameter": parameter,
        "modulus": modulus,
        "residue_size": len(residues),
        "residues": residues,
        "metadata": metadata,
        "modular_unordered_sum_support": sum_support,
        "modular_max_unordered_sum_multiplicity": max_sum_mult,
        "modular_3b_minus_b_coverage": len(modular_cover),
        "modular_3b_minus_b_holes": modulus - len(modular_cover),
        "unit_classes_total": len(unit_multipliers(modulus, None)),
        "unit_classes_scanned": len(units),
        "distinct_lifts_scanned": len(seen),
        "literal_sidon_lifts": sidon_lifts,
        "candidate_lifts": candidate_count,
        "best_candidate": best,
        "scan_exhaustive": unit_limit is None or len(units) == len(unit_multipliers(modulus, None)),
    }


def reflected_admissibility(points: Sequence[int], center: int) -> dict[str, object]:
    values = sorted(set(points) | {center - x for x in points})
    counts: Counter[int] = Counter()
    for i, a in enumerate(values):
        for b in values[i:]:
            counts[a + b] += 1
    repeats = sorted((s, m) for s, m in counts.items() if m >= 2)
    return {
        "reflected_set": values,
        "repeated_sums": repeats,
        "admissible": repeats == [(center, len(points))],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=("bose", "singer", "ruzsa"), required=True)
    parser.add_argument("--parameters", type=int, nargs="+", required=True)
    parser.add_argument(
        "--unit-limit",
        type=int,
        help="deterministic number of unit classes; omit for exhaustive affine scan",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = []
    for parameter in args.parameters:
        record = scan_family(args.family, parameter, args.unit_limit)
        best = record.get("best_candidate")
        if best is not None:
            check = reflected_admissibility(best["points"], int(best["candidate_center"]))
            if not check["admissible"]:
                raise AssertionError("literal reflected verification failed")
            record["best_candidate_check"] = check
        records.append(record)
        print(json.dumps(record, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "\n".join(json.dumps(x, sort_keys=True) for x in records) + "\n",
            encoding="ascii",
        )


if __name__ == "__main__":
    main()
