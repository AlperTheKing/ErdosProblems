#!/usr/bin/env python3
"""Exact verifier for rational Diophantine m-tuples.

For every unordered pair ``(a, b)`` this verifier checks, using only integer
arithmetic, whether ``a*b + 1`` is a square in Q.  It deliberately has no
dependency on the elliptic-curve search code that may have produced a
candidate.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Sequence


CALIBRATIONS: dict[str, dict[str, Any]] = {
    "gibbs-sextuple": {
        "values": (
            "11/192",
            "35/192",
            "155/27",
            "512/27",
            "1235/48",
            "180873/16",
        ),
        "expected_failures": 0,
        "description": "Gibbs's published rational Diophantine sextuple",
    },
    "dujella-almost-septuple": {
        "values": (
            "243/560",
            "1147/5040",
            "1100/63",
            "7820/567",
            "95/112",
            "38269/6480",
            "196/45",
        ),
        "expected_failures": 1,
        "description": "Dujella's 2026 published almost-septuple",
    },
}

CALIBRATION_ALIASES = {
    "gibbs": "gibbs-sextuple",
    "dujella": "dujella-almost-septuple",
}


def rational(value: Any) -> Fraction:
    """Parse a value as an exact rational, rejecting binary floats."""

    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise ValueError("booleans are not rational inputs")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        try:
            return Fraction(value.strip())
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"invalid rational {value!r}") from exc
    if isinstance(value, float):
        raise ValueError(
            "binary floating-point inputs are forbidden; use a JSON string "
            "such as \"11/192\" or an exact JSON decimal"
        )
    raise ValueError(f"unsupported rational input type: {type(value).__name__}")


def rational_square_root(value: Fraction) -> tuple[Fraction | None, str | None]:
    """Return the nonnegative rational square root, or an exact failure reason."""

    if value < 0:
        return None, "negative"

    numerator_root = isqrt(value.numerator)
    denominator_root = isqrt(value.denominator)
    failures: list[str] = []
    if numerator_root * numerator_root != value.numerator:
        failures.append("numerator_not_square")
    if denominator_root * denominator_root != value.denominator:
        failures.append("denominator_not_square")
    if failures:
        return None, "+".join(failures)
    return Fraction(numerator_root, denominator_root), None


def _duplicate_groups(values: Sequence[Fraction]) -> list[dict[str, Any]]:
    positions: dict[Fraction, list[int]] = {}
    for index, value in enumerate(values, start=1):
        positions.setdefault(value, []).append(index)
    return [
        {"value": str(value), "indices": indices}
        for value, indices in positions.items()
        if len(indices) > 1
    ]


def verify_tuple(
    values: Iterable[Any],
    name: str = "candidate",
    expect_size: int | None = None,
) -> dict[str, Any]:
    """Verify all defining conditions and return a JSON-serializable report.

    ``expect_size`` is an optional cardinality contract for proof-certificate
    verification.  Generic calibration calls leave it unset; a septuple
    certificate sets it to seven, which also requires all 21 unordered pairs
    to have been examined.
    """

    if expect_size is not None and expect_size < 1:
        raise ValueError("expected tuple size must be a positive integer")

    parsed = tuple(rational(value) for value in values)
    zero_entries = [index for index, value in enumerate(parsed, start=1) if value == 0]
    duplicate_entries = _duplicate_groups(parsed)
    pair_reports: list[dict[str, Any]] = []

    for left_index, left in enumerate(parsed, start=1):
        for right_index in range(left_index + 1, len(parsed) + 1):
            right = parsed[right_index - 1]
            product_plus_one = left * right + 1
            root, failure = rational_square_root(product_plus_one)
            pair_reports.append(
                {
                    "indices": [left_index, right_index],
                    "values": [str(left), str(right)],
                    "product_plus_one": str(product_plus_one),
                    "is_square": root is not None,
                    "root": str(root) if root is not None else None,
                    "failure": failure,
                }
            )

    pair_failures = [pair for pair in pair_reports if not pair["is_square"]]
    size = len(parsed)
    required_size = expect_size
    expected_pair_count = (
        size * (size - 1) // 2
        if required_size is None
        else required_size * (required_size - 1) // 2
    )
    size_ok = required_size is None or size == required_size
    pair_count_ok = len(pair_reports) == expected_pair_count
    nonzero = not zero_entries
    distinct = not duplicate_entries
    return {
        "name": name,
        "size": size,
        "required_size": required_size,
        "size_ok": size_ok,
        "values": [str(value) for value in parsed],
        "nonzero": nonzero,
        "zero_entries": zero_entries,
        "distinct": distinct,
        "duplicate_entries": duplicate_entries,
        "pair_count": len(pair_reports),
        "expected_pair_count": expected_pair_count,
        "pair_count_ok": pair_count_ok,
        "square_pair_count": len(pair_reports) - len(pair_failures),
        "pair_failure_count": len(pair_failures),
        "pairs": pair_reports,
        "valid": (
            nonzero
            and distinct
            and size_ok
            and pair_count_ok
            and not pair_failures
        ),
    }


def _reject_nonfinite_json(token: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {token}")


def decode_json_document(text: str) -> tuple[str, list[Any]]:
    """Decode a JSON array or an object containing ``values``/``tuple``.

    ``parse_float=str`` retains the decimal token exactly; for example, the
    JSON number 0.125 becomes the rational 1/8 rather than a binary float.
    """

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


def calibration_report(calibration_name: str) -> dict[str, Any]:
    canonical_name = CALIBRATION_ALIASES.get(calibration_name, calibration_name)
    calibration = CALIBRATIONS[canonical_name]
    report = verify_tuple(calibration["values"], canonical_name)
    expected = calibration["expected_failures"]
    report["description"] = calibration["description"]
    report["expected_pair_failure_count"] = expected
    report["calibration_ok"] = (
        report["nonzero"]
        and report["distinct"]
        and report["pair_failure_count"] == expected
    )
    return report


def format_text(report: dict[str, Any]) -> str:
    lines = [
        f"CASE {report['name']}",
        (
            f"size={report['size']} nonzero={str(report['nonzero']).lower()} "
            f"distinct={str(report['distinct']).lower()} "
            f"pairs={report['pair_count']} squares={report['square_pair_count']} "
            f"failures={report['pair_failure_count']} valid={str(report['valid']).lower()}"
        ),
    ]
    if report["required_size"] is not None:
        lines.append(
            f"CARDINALITY required={report['required_size']} "
            f"size_ok={str(report['size_ok']).lower()} "
            f"expected_pairs={report['expected_pair_count']} "
            f"pair_count_ok={str(report['pair_count_ok']).lower()}"
        )
    if report["zero_entries"]:
        lines.append(f"ZERO entries={report['zero_entries']}")
    for duplicate in report["duplicate_entries"]:
        lines.append(
            f"DUPLICATE value={duplicate['value']} indices={duplicate['indices']}"
        )
    for pair in report["pairs"]:
        left_index, right_index = pair["indices"]
        left, right = pair["values"]
        if pair["is_square"]:
            outcome = f"root={pair['root']} OK"
        else:
            outcome = f"root=NONE FAIL:{pair['failure']}"
        lines.append(
            f"PAIR {left_index},{right_index}: {left} * {right} + 1 "
            f"= {pair['product_plus_one']}; {outcome}"
        )
    if "expected_pair_failure_count" in report:
        lines.append(
            f"CALIBRATION expected_failures={report['expected_pair_failure_count']} "
            f"ok={str(report['calibration_ok']).lower()}"
        )
    return "\n".join(lines)


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--json",
        metavar="JSON_OR_PATH",
        help="JSON array/object, path to a JSON file, or '-' for stdin",
    )
    source_group.add_argument(
        "--calibration",
        choices=("all", *CALIBRATIONS, *CALIBRATION_ALIASES),
        help="run one built-in published calibration (default: all)",
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="output format"
    )
    parser.add_argument(
        "--expect-size",
        type=int,
        metavar="N",
        help=(
            "require exactly N entries and N*(N-1)/2 checked pairs for a JSON "
            "candidate (use 7 for a septuple certificate)"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _argument_parser().parse_args(argv)
    if args.json is not None:
        try:
            name, values = load_json_source(args.json)
            reports = [verify_tuple(values, name, expect_size=args.expect_size)]
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        exit_ok = reports[0]["valid"]
    else:
        selected = args.calibration or "all"
        names = list(CALIBRATIONS) if selected == "all" else [selected]
        reports = [calibration_report(name) for name in names]
        exit_ok = all(report["calibration_ok"] for report in reports)

    if args.format == "json":
        payload: Any = reports[0] if len(reports) == 1 else reports
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("\n\n".join(format_text(report) for report in reports))
    return 0 if exit_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
