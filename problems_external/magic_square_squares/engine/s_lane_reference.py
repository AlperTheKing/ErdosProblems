#!/usr/bin/env python3
"""Brute-force exact reference implementation for structural S lanes.

This program is intentionally simple.  It enumerates every canonical pair,
deduplicates exact ``fractions.Fraction`` values, and checks every ordered
choice ``f1 > f2``.  It is used to audit the optimized C++ hash join on small
P bands; it is not the eight-hour search engine.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable


@dataclass(frozen=True)
class PairData:
    p: int
    q: int
    h: int
    u: int
    v: int
    f: Fraction


@dataclass(frozen=True)
class Identity:
    f1: PairData
    f2: PairData
    f3: PairData
    f4: PairData

    @property
    def pairs(self) -> tuple[tuple[int, int], ...]:
        return tuple((item.p, item.q) for item in (self.f1, self.f2, self.f3, self.f4))

    @property
    def key(self) -> str:
        return ";".join(f"{p},{q}" for p, q in self.pairs)

    @property
    def max_p(self) -> int:
        return max(p for p, _ in self.pairs)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def canonical_values(p_max: int) -> tuple[list[PairData], int]:
    """Return values sorted by f and the pre-dedup canonical-pair count."""

    by_fraction: dict[Fraction, PairData] = {}
    generated = 0
    for p in range(2, p_max + 1):
        for q in range(1, p):
            if math.gcd(p, q) != 1 or (p - q) % 2 == 0:
                continue
            generated += 1
            p2 = p * p
            q2 = q * q
            h = p2 + q2
            u = p2 - 2 * p * q - q2
            v = p2 + 2 * p * q - q2
            numerator = 4 * p * q * (p2 - q2)
            denominator = h * h
            assert u * u == denominator - numerator
            assert v * v == denominator + numerator
            value = Fraction(numerator, denominator)
            assert 0 < value < 1
            pair = PairData(p=p, q=q, h=h, u=u, v=v, f=value)
            previous = by_fraction.get(value)
            if previous is None or (p, q) < (previous.p, previous.q):
                by_fraction[value] = pair

    values = sorted(by_fraction.values(), key=lambda item: item.f)
    return values, generated


def find_identities(
    values: list[PairData], p_min: int, p_max: int
) -> tuple[list[Identity], int]:
    """Check every exact f1>f2 pair and return the requested max-p band."""

    lookup = {item.f: item for item in values}
    identities: list[Identity] = []
    comparisons = 0
    for i in range(1, len(values)):
        first = values[i]
        for j in range(i):
            second = values[j]
            total = first.f + second.f
            if total >= 1:
                break
            comparisons += 1
            difference = first.f - second.f
            fourth = lookup.get(difference)
            if fourth is None:
                continue
            third = lookup.get(total)
            if third is None:
                continue
            identity = Identity(first, second, third, fourth)
            if p_min <= identity.max_p <= p_max:
                identities.append(identity)

    identities.sort(key=lambda item: item.pairs)
    return identities, comparisons


def lcm(left: int, right: int) -> int:
    return left // math.gcd(left, right) * right


def _root_denominators(pair: PairData) -> tuple[int, int]:
    return (
        pair.h // math.gcd(pair.h, abs(pair.u)),
        pair.h // math.gcd(pair.h, pair.v),
    )


def reconstruct(identity: Identity) -> dict[str, Any]:
    """Clear all rational-root denominators and construct primitive MSQ-D."""

    ordered = (identity.f1, identity.f2, identity.f3, identity.f4)
    m = 1
    for pair in ordered:
        for denominator in _root_denominators(pair):
            m = lcm(m, denominator)

    roots: list[int] = []
    for pair in ordered:
        assert (m * abs(pair.u)) % pair.h == 0
        assert (m * pair.v) % pair.h == 0
        roots.extend((m * abs(pair.u) // pair.h, m * pair.v // pair.h))

    b_fraction = m * m * identity.f1.f
    c_fraction = m * m * identity.f2.f
    assert b_fraction.denominator == 1
    assert c_fraction.denominator == 1
    b = b_fraction.numerator
    c = c_fraction.numerator

    primitive_gcd = m
    for root in roots:
        primitive_gcd = math.gcd(primitive_gcd, root)
    if primitive_gcd > 1:
        square_gcd = primitive_gcd * primitive_gcd
        assert b % square_gcd == 0 and c % square_gcd == 0
        m //= primitive_gcd
        b //= square_gcd
        c //= square_gcd
        roots = [root // primitive_gcd for root in roots]

    center = m * m
    matrix = [
        [center - b, center + b + c, center - c],
        [center + b - c, center, center - b + c],
        [center + c, center - b - c, center + b],
    ]
    flat = [value for row in matrix for value in row]
    square_roots = [math.isqrt(value) if value > 0 else -1 for value in flat]
    positive = all(value > 0 for value in flat)
    squares = positive and all(root * root == value for root, value in zip(square_roots, flat))
    distinct = len(set(flat)) == 9
    line_sums = [
        sum(matrix[0]),
        sum(matrix[1]),
        sum(matrix[2]),
        matrix[0][0] + matrix[1][0] + matrix[2][0],
        matrix[0][1] + matrix[1][1] + matrix[2][1],
        matrix[0][2] + matrix[1][2] + matrix[2][2],
        matrix[0][0] + matrix[1][1] + matrix[2][2],
        matrix[0][2] + matrix[1][1] + matrix[2][0],
    ]
    sums_equal = len(set(line_sums)) == 1

    return {
        "valid": positive and squares and distinct and sums_equal,
        "m": m,
        "b": b,
        "c": c,
        "roots": roots,
        "matrix": matrix,
        "checks": {
            "positive": positive,
            "perfect_squares": squares,
            "pairwise_distinct": distinct,
            "all_eight_sums_equal": sums_equal,
        },
    }


def identity_record(identity: Identity, candidate: dict[str, Any]) -> dict[str, Any]:
    ordered = (identity.f1, identity.f2, identity.f3, identity.f4)
    return {
        "type": "identity",
        "key": identity.key,
        "pairs": [[item.p, item.q] for item in ordered],
        "fractions": [fraction_text(item.f) for item in ordered],
        "max_p": identity.max_p,
        "candidate_valid": candidate["valid"],
    }


def emit_jsonl(records: Iterable[dict[str, Any]], output: Any) -> None:
    for record in records:
        output.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
        output.write("\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p-min", type=int, default=2)
    parser.add_argument("--p-max", type=int, required=True)
    parser.add_argument("--output", help="JSONL output path; default is stdout")
    parser.add_argument(
        "--emit-identities",
        action="store_true",
        help="emit every exact identity quartet before the summary",
    )
    parser.add_argument(
        "--emit-values",
        action="store_true",
        help="emit every deduplicated canonical f value before joins",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.p_min < 2 or args.p_max < args.p_min:
        print("invalid P band", file=sys.stderr)
        return 2

    values, generated = canonical_values(args.p_max)
    identities, comparisons = find_identities(values, args.p_min, args.p_max)
    candidates = [(identity, reconstruct(identity)) for identity in identities]
    valid_candidates = [(identity, item) for identity, item in candidates if item["valid"]]

    output = open(args.output, "w", encoding="utf-8", newline="\n") if args.output else sys.stdout
    try:
        if args.emit_values:
            emit_jsonl(
                (
                    {
                        "type": "value",
                        "fraction": fraction_text(item.f),
                        "pair": [item.p, item.q],
                        "h": item.h,
                        "u": item.u,
                        "v": item.v,
                    }
                    for item in values
                ),
                output,
            )
        if args.emit_identities:
            emit_jsonl(
                (identity_record(identity, candidate) for identity, candidate in candidates),
                output,
            )
        for identity, candidate in valid_candidates:
            emit_jsonl(
                [
                    {
                        "type": "candidate",
                        "key": identity.key,
                        "msq_d": {
                            "m": str(candidate["m"]),
                            "b": str(candidate["b"]),
                            "c": str(candidate["c"]),
                        },
                        "roots": [str(value) for value in candidate["roots"]],
                        "matrix": [
                            [str(value) for value in row] for row in candidate["matrix"]
                        ],
                    }
                ],
                output,
            )
        emit_jsonl(
            [
                {
                    "type": "summary",
                    "implementation": "python_bruteforce_reference",
                    "status": "EXHAUSTED",
                    "p_min": args.p_min,
                    "p_max": args.p_max,
                    "canonical_pair_count": generated,
                    "unique_f_count": len(values),
                    "pair_comparisons": comparisons,
                    "identity_count": len(identities),
                    "candidate_count": len(valid_candidates),
                }
            ],
            output,
        )
    finally:
        if args.output:
            output.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
