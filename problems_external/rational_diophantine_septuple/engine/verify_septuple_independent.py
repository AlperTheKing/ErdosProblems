#!/usr/bin/env python3
"""Standalone exact verifier for rational Diophantine septuples.

This implementation intentionally imports neither ``fractions`` nor any
primary verifier or search module.  It uses a private normalized pair-of-
integers rational representation, Euclid's algorithm, and an independent
integer-square-root routine.  A certificate is valid only if it contains
seven distinct nonzero rationals and all 21 unordered products plus one are
rational squares.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


REQUIRED_SIZE = 7
EXPECTED_PAIR_COUNT = 21


def _gcd(left: int, right: int) -> int:
    """Compute the nonnegative greatest common divisor by Euclid's method."""

    left = abs(left)
    right = abs(right)
    while right:
        left, right = right, left % right
    return left


def _integer_square_root(value: int) -> int:
    """Return floor(sqrt(value)) using integer Newton iteration."""

    if value < 0:
        raise ValueError("integer square root is undefined for negative values")
    if value < 2:
        return value
    estimate = 1 << ((value.bit_length() + 1) // 2)
    while True:
        updated = (estimate + value // estimate) // 2
        if updated >= estimate:
            return estimate
        estimate = updated


class NormalizedRational:
    """Reduced rational number represented by a signed numerator and positive denominator."""

    __slots__ = ("numerator", "denominator")

    def __init__(self, numerator: int, denominator: int = 1) -> None:
        if denominator == 0:
            raise ValueError("rational denominator must be nonzero")
        if denominator < 0:
            numerator = -numerator
            denominator = -denominator
        divisor = _gcd(numerator, denominator)
        self.numerator = numerator // divisor
        self.denominator = denominator // divisor

    def __hash__(self) -> int:
        return hash((self.numerator, self.denominator))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NormalizedRational):
            return NotImplemented
        return (
            self.numerator == other.numerator
            and self.denominator == other.denominator
        )

    def __str__(self) -> str:
        if self.denominator == 1:
            return str(self.numerator)
        return f"{self.numerator}/{self.denominator}"


def _parse_integer(token: str) -> int:
    token = token.strip()
    if not token:
        raise ValueError("empty integer token")
    digits = token[1:] if token[0] in "+-" else token
    if not digits or not digits.isdecimal():
        raise ValueError(f"invalid integer token {token!r}")
    return int(token)


def _parse_decimal(token: str) -> NormalizedRational:
    """Parse a signed decimal/scientific token without floating-point arithmetic."""

    lowered = token.lower()
    if lowered.count("e") > 1:
        raise ValueError(f"invalid rational {token!r}")
    if "e" in lowered:
        mantissa, exponent_token = lowered.split("e")
        exponent = _parse_integer(exponent_token)
    else:
        mantissa = lowered
        exponent = 0

    sign = 1
    if mantissa.startswith(("+", "-")):
        if mantissa[0] == "-":
            sign = -1
        mantissa = mantissa[1:]
    if mantissa.count(".") > 1:
        raise ValueError(f"invalid rational {token!r}")
    if "." in mantissa:
        whole, fractional = mantissa.split(".")
    else:
        whole, fractional = mantissa, ""
    if not whole and not fractional:
        raise ValueError(f"invalid rational {token!r}")
    if (whole and not whole.isdecimal()) or (
        fractional and not fractional.isdecimal()
    ):
        raise ValueError(f"invalid rational {token!r}")

    digits = (whole or "0") + fractional
    numerator = sign * int(digits)
    denominator = 10 ** len(fractional)
    if exponent >= 0:
        numerator *= 10**exponent
    else:
        denominator *= 10 ** (-exponent)
    return NormalizedRational(numerator, denominator)


def parse_rational(value: Any) -> NormalizedRational:
    """Parse an integer or exact textual rational; reject binary floats."""

    if isinstance(value, bool):
        raise ValueError("booleans are not rational inputs")
    if isinstance(value, int):
        return NormalizedRational(value)
    if isinstance(value, float):
        raise ValueError(
            "binary floating-point inputs are forbidden; use an exact JSON token or string"
        )
    if not isinstance(value, str):
        raise ValueError(
            f"unsupported rational input type: {type(value).__name__}"
        )

    token = value.strip()
    if not token:
        raise ValueError("invalid empty rational")
    if "/" in token:
        if token.count("/") != 1:
            raise ValueError(f"invalid rational {value!r}")
        numerator_token, denominator_token = token.split("/")
        return NormalizedRational(
            _parse_integer(numerator_token),
            _parse_integer(denominator_token),
        )
    return _parse_decimal(token)


def _product_plus_one(
    left: NormalizedRational, right: NormalizedRational
) -> NormalizedRational:
    return NormalizedRational(
        left.numerator * right.numerator
        + left.denominator * right.denominator,
        left.denominator * right.denominator,
    )


def _rational_square_root(
    value: NormalizedRational,
) -> tuple[NormalizedRational | None, str | None]:
    if value.numerator < 0:
        return None, "negative"
    numerator_root = _integer_square_root(value.numerator)
    denominator_root = _integer_square_root(value.denominator)
    failures: list[str] = []
    if numerator_root * numerator_root != value.numerator:
        failures.append("numerator_not_square")
    if denominator_root * denominator_root != value.denominator:
        failures.append("denominator_not_square")
    if failures:
        return None, "+".join(failures)
    return NormalizedRational(numerator_root, denominator_root), None


def _duplicate_groups(
    values: Sequence[NormalizedRational],
) -> list[dict[str, Any]]:
    positions: dict[NormalizedRational, list[int]] = {}
    for index, value in enumerate(values, start=1):
        positions.setdefault(value, []).append(index)
    return [
        {"value": str(value), "indices": indices}
        for value, indices in positions.items()
        if len(indices) > 1
    ]


def verify_septuple(
    values: Iterable[Any], name: str = "candidate"
) -> dict[str, Any]:
    """Return a complete JSON-serializable septuple verification report."""

    parsed = tuple(parse_rational(value) for value in values)
    zero_entries = [
        index
        for index, value in enumerate(parsed, start=1)
        if value.numerator == 0
    ]
    duplicate_entries = _duplicate_groups(parsed)
    pair_reports: list[dict[str, Any]] = []

    for left_offset, left in enumerate(parsed):
        for right_offset in range(left_offset + 1, len(parsed)):
            right = parsed[right_offset]
            product_plus_one = _product_plus_one(left, right)
            root, failure = _rational_square_root(product_plus_one)
            pair_reports.append(
                {
                    "indices": [left_offset + 1, right_offset + 1],
                    "values": [str(left), str(right)],
                    "product_plus_one": str(product_plus_one),
                    "is_square": root is not None,
                    "root": str(root) if root is not None else None,
                    "failure": failure,
                }
            )

    pair_failures = [pair for pair in pair_reports if not pair["is_square"]]
    size_ok = len(parsed) == REQUIRED_SIZE
    pair_count_ok = len(pair_reports) == EXPECTED_PAIR_COUNT
    nonzero = not zero_entries
    distinct = not duplicate_entries
    return {
        "implementation": "standalone-normalized-integers",
        "name": name,
        "size": len(parsed),
        "required_size": REQUIRED_SIZE,
        "size_ok": size_ok,
        "values": [str(value) for value in parsed],
        "nonzero": nonzero,
        "zero_entries": zero_entries,
        "distinct": distinct,
        "duplicate_entries": duplicate_entries,
        "pair_count": len(pair_reports),
        "expected_pair_count": EXPECTED_PAIR_COUNT,
        "pair_count_ok": pair_count_ok,
        "square_pair_count": len(pair_reports) - len(pair_failures),
        "pair_failure_count": len(pair_failures),
        "pairs": pair_reports,
        "valid": (
            size_ok
            and pair_count_ok
            and nonzero
            and distinct
            and not pair_failures
        ),
    }


def _reject_nonfinite_json(token: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {token}")


def decode_json_document(text: str) -> tuple[str, list[Any]]:
    try:
        document = json.loads(
            text,
            parse_float=str,
            parse_int=int,
            parse_constant=_reject_nonfinite_json,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid JSON input: {exc}") from exc

    if isinstance(document, list):
        return "candidate", document
    if not isinstance(document, dict):
        raise ValueError("JSON input must be an array or an object")
    if "values" in document:
        values = document["values"]
    elif "tuple" in document:
        values = document["tuple"]
    else:
        raise ValueError("JSON object must contain a 'values' or 'tuple' array")
    if not isinstance(values, list):
        raise ValueError("the JSON tuple must be an array")
    name = document.get("name", "candidate")
    if not isinstance(name, str):
        raise ValueError("JSON field 'name' must be a string")
    return name, values


def load_json_source(source: str) -> tuple[str, list[Any]]:
    if source == "-":
        text = sys.stdin.read()
    elif source.lstrip().startswith(("[", "{")):
        text = source
    else:
        text = Path(source).read_text(encoding="utf-8")
    return decode_json_document(text)


def format_text(report: dict[str, Any]) -> str:
    lines = [
        f"CASE {report['name']}",
        (
            f"size={report['size']} required=7 size_ok={str(report['size_ok']).lower()} "
            f"nonzero={str(report['nonzero']).lower()} "
            f"distinct={str(report['distinct']).lower()} "
            f"pairs={report['pair_count']} expected_pairs=21 "
            f"pair_count_ok={str(report['pair_count_ok']).lower()} "
            f"squares={report['square_pair_count']} "
            f"failures={report['pair_failure_count']} "
            f"valid={str(report['valid']).lower()}"
        ),
    ]
    if report["zero_entries"]:
        lines.append(f"ZERO entries={report['zero_entries']}")
    for duplicate in report["duplicate_entries"]:
        lines.append(
            f"DUPLICATE value={duplicate['value']} indices={duplicate['indices']}"
        )
    for pair in report["pairs"]:
        left_index, right_index = pair["indices"]
        outcome = (
            f"root={pair['root']} OK"
            if pair["is_square"]
            else f"root=NONE FAIL:{pair['failure']}"
        )
        lines.append(
            f"PAIR {left_index},{right_index}: {pair['values'][0]} * "
            f"{pair['values'][1]} + 1 = {pair['product_plus_one']}; {outcome}"
        )
    return "\n".join(lines)


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        required=True,
        metavar="JSON_OR_PATH",
        help="JSON array/object, path to a JSON file, or '-' for stdin",
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="output format"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    try:
        name, values = load_json_source(args.json)
        report = verify_septuple(values, name)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_text(report))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
