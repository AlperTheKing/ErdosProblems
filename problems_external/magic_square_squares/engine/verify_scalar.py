#!/usr/bin/env python3
"""Exact scalar verifier for a 3 by 3 magic square of squares.

Accepted inputs
---------------

* ``--matrix '[[...], [...], [...]]'`` for the nine square *values*;
* ``--msq-d M B C`` for an MSQ-D certificate; or
* ``--input FILE`` (``-`` means stdin) containing JSON in one of these forms:

  - ``[[...], [...], [...]]``;
  - ``[M, B, C]``;
  - ``{"matrix": [[...], [...], [...]]}``;
  - ``{"msq_d": [M, B, C]}``; or
  - ``{"msq_d": {"m": M, "b": B, "c": C}}``.

The verifier uses only exact Python integers and ``math.isqrt``.  Exit status 0
means that every required check passed, 1 means a well-formed candidate failed
one or more mathematical checks, and 2 means that the input was malformed.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_INPUT_ERROR = 2


class InputError(ValueError):
    """Raised when input cannot be interpreted as a supported certificate."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Argument parser whose failures can be emitted as JSON."""

    def error(self, message: str) -> None:
        raise InputError(message)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _perfect_square_root(value: int) -> int | None:
    if value < 0:
        return None
    root = math.isqrt(value)
    return root if root * root == value else None


def _normalize_matrix(raw: Any) -> list[list[int]]:
    if not isinstance(raw, list) or len(raw) != 3:
        raise InputError("matrix must be a JSON array containing exactly three rows")

    matrix: list[list[int]] = []
    for row_index, row in enumerate(raw):
        if not isinstance(row, list) or len(row) != 3:
            raise InputError(
                f"matrix row {row_index + 1} must contain exactly three entries"
            )
        normalized_row: list[int] = []
        for column_index, value in enumerate(row):
            if not _is_integer(value):
                raise InputError(
                    "matrix entry "
                    f"({row_index + 1},{column_index + 1}) must be a JSON integer"
                )
            normalized_row.append(value)
        matrix.append(normalized_row)
    return matrix


def _normalize_msq_d(raw: Any) -> tuple[int, int, int]:
    if isinstance(raw, dict):
        if set(raw) != {"m", "b", "c"}:
            raise InputError("MSQ-D object must contain exactly the keys m, b, and c")
        values = (raw["m"], raw["b"], raw["c"])
    elif isinstance(raw, list) and len(raw) == 3:
        values = tuple(raw)
    elif isinstance(raw, tuple) and len(raw) == 3:
        values = raw
    else:
        raise InputError("MSQ-D certificate must contain exactly three integers: m, b, c")

    if not all(_is_integer(value) for value in values):
        raise InputError("MSQ-D entries m, b, and c must be JSON integers")
    return int(values[0]), int(values[1]), int(values[2])


def _decode_payload(raw: Any) -> tuple[str, Any]:
    if isinstance(raw, dict):
        recognized = [key for key in ("matrix", "msq_d") if key in raw]
        if len(recognized) != 1:
            raise InputError("JSON object must contain exactly one of matrix or msq_d")
        kind = recognized[0]
        return kind, raw[kind]

    if isinstance(raw, list):
        if len(raw) == 3 and all(isinstance(row, list) for row in raw):
            return "matrix", raw
        if len(raw) == 3 and all(_is_integer(value) for value in raw):
            return "msq_d", raw

    raise InputError(
        "JSON input must be a 3 by 3 matrix, an MSQ-D triple, or an object "
        "containing matrix or msq_d"
    )


def _load_json_text(text: str, source: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"invalid JSON in {source}: line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def _load_json_argument(text: str) -> Any:
    if text.startswith("@"):
        path = Path(text[1:])
        try:
            return _load_json_text(path.read_text(encoding="utf-8"), str(path))
        except OSError as exc:
            raise InputError(f"cannot read {path}: {exc}") from exc
    return _load_json_text(text, "command-line argument")


def _load_json_file(path_text: str) -> Any:
    if path_text == "-":
        return _load_json_text(sys.stdin.read(), "stdin")

    path = Path(path_text)
    try:
        return _load_json_text(path.read_text(encoding="utf-8"), str(path))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def _positions(values: Iterable[tuple[int, int, int]]) -> list[dict[str, int]]:
    return [
        {"row": row + 1, "column": column + 1, "value": value}
        for row, column, value in values
    ]


def verify_matrix(matrix: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Return a JSON-serializable exact verification report."""

    normalized = _normalize_matrix([list(row) for row in matrix])
    flat = [value for row in normalized for value in row]

    nonpositive = [
        (row, column, normalized[row][column])
        for row in range(3)
        for column in range(3)
        if normalized[row][column] <= 0
    ]

    roots: list[list[int | None]] = []
    nonsquares: list[tuple[int, int, int]] = []
    for row in range(3):
        root_row: list[int | None] = []
        for column in range(3):
            value = normalized[row][column]
            root = _perfect_square_root(value)
            root_row.append(root)
            if root is None:
                nonsquares.append((row, column, value))
        roots.append(root_row)

    duplicate_positions: dict[int, list[dict[str, int]]] = defaultdict(list)
    for row in range(3):
        for column in range(3):
            value = normalized[row][column]
            duplicate_positions[value].append({"row": row + 1, "column": column + 1})
    duplicates = [
        {"value": value, "positions": positions}
        for value, positions in sorted(duplicate_positions.items())
        if len(positions) > 1
    ]

    line_coordinates = {
        "row_1": ((0, 0), (0, 1), (0, 2)),
        "row_2": ((1, 0), (1, 1), (1, 2)),
        "row_3": ((2, 0), (2, 1), (2, 2)),
        "column_1": ((0, 0), (1, 0), (2, 0)),
        "column_2": ((0, 1), (1, 1), (2, 1)),
        "column_3": ((0, 2), (1, 2), (2, 2)),
        "diagonal_main": ((0, 0), (1, 1), (2, 2)),
        "diagonal_anti": ((0, 2), (1, 1), (2, 0)),
    }
    line_sums = {
        name: sum(normalized[row][column] for row, column in coordinates)
        for name, coordinates in line_coordinates.items()
    }

    grouped_lines: dict[int, list[str]] = defaultdict(list)
    for name, line_sum in line_sums.items():
        grouped_lines[line_sum].append(name)
    sum_groups = [
        {"sum": line_sum, "count": len(names), "lines": names}
        for line_sum, names in sorted(grouped_lines.items())
    ]
    dominant_count = max(len(names) for names in grouped_lines.values())
    dominant_sum = min(
        line_sum
        for line_sum, names in grouped_lines.items()
        if len(names) == dominant_count
    )

    checks = {
        "positive": not nonpositive,
        "perfect_squares": not nonsquares,
        "pairwise_distinct": len(set(flat)) == 9,
        "all_eight_sums_equal": len(grouped_lines) == 1,
    }
    errors: list[str] = []
    if not checks["positive"]:
        errors.append("matrix entries must be positive")
    if not checks["perfect_squares"]:
        errors.append("matrix entries must be perfect squares")
    if not checks["pairwise_distinct"]:
        errors.append("matrix entries must be pairwise distinct")
    if not checks["all_eight_sums_equal"]:
        errors.append("all eight line sums must be equal")

    return {
        "valid": all(checks.values()),
        "checks": checks,
        "errors": errors,
        "matrix": normalized,
        "roots": roots,
        "nonpositive_entries": _positions(nonpositive),
        "nonsquare_entries": _positions(nonsquares),
        "duplicate_entries": duplicates,
        "line_sums": line_sums,
        "sum_groups": sum_groups,
        "dominant_sum": dominant_sum,
        "dominant_line_count": dominant_count,
        "common_sum": dominant_sum if len(grouped_lines) == 1 else None,
    }


def _expand_msq_d(m: int, b: int, c: int) -> list[list[int]]:
    center = m * m
    return [
        [center - b, center + b + c, center - c],
        [center + b - c, center, center - b + c],
        [center + c, center - b - c, center + b],
    ]


def verify_msq_d(m: int, b: int, c: int) -> dict[str, Any]:
    """Expand and exactly verify an MSQ-D certificate."""

    if not all(_is_integer(value) for value in (m, b, c)):
        raise InputError("MSQ-D entries m, b, and c must be integers")

    center = m * m
    delta_values = (
        ("b", b),
        ("c", c),
        ("b_plus_c", b + c),
        ("abs_b_minus_c", abs(b - c)),
    )
    memberships: list[dict[str, Any]] = []
    for name, delta in delta_values:
        lower = center - delta
        upper = center + delta
        lower_root = _perfect_square_root(lower)
        upper_root = _perfect_square_root(upper)
        membership_valid = (
            delta > 0
            and lower > 0
            and lower_root is not None
            and upper_root is not None
        )
        memberships.append(
            {
                "name": name,
                "delta": delta,
                "lower": lower,
                "upper": upper,
                "lower_root": lower_root,
                "upper_root": upper_root,
                "valid": membership_valid,
            }
        )

    matrix_report = verify_matrix(_expand_msq_d(m, b, c))
    certificate_checks = {
        "m_b_c_positive": m > 0 and b > 0 and c > 0,
        "all_four_deltas_in_D": all(item["valid"] for item in memberships),
    }

    errors: list[str] = []
    if not certificate_checks["m_b_c_positive"]:
        errors.append("MSQ-D entries m, b, and c must be positive")
    if not certificate_checks["all_four_deltas_in_D"]:
        errors.append("b, c, b+c, and |b-c| must all belong to D_(m^2)")
    errors.extend(matrix_report["errors"])

    result = dict(matrix_report)
    result.update(
        {
            "valid": all(certificate_checks.values()) and matrix_report["valid"],
            "errors": errors,
            "certificate": {"m": m, "b": b, "c": c, "center": center},
            "msq_d_checks": certificate_checks,
            "d_memberships": memberships,
        }
    )
    return result


def _build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        description="Verify a 3 by 3 magic square of distinct positive squares."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--matrix",
        metavar="JSON",
        help="3 by 3 JSON matrix of square values; prefix with @ to read a file",
    )
    group.add_argument(
        "--msq-d",
        nargs=3,
        metavar=("M", "B", "C"),
        help="MSQ-D certificate triple",
    )
    group.add_argument(
        "--input",
        metavar="FILE",
        help="JSON input file; use - for stdin",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )
    return parser


def _emit(payload: dict[str, Any], pretty: bool = False) -> None:
    json.dump(
        payload,
        sys.stdout,
        indent=2 if pretty else None,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
    )
    sys.stdout.write("\n")


def main(argv: Sequence[str] | None = None) -> int:
    pretty = bool(argv and "--pretty" in argv)
    try:
        args = _build_parser().parse_args(argv)
        pretty = args.pretty

        if args.matrix is not None:
            kind, raw_value = "matrix", _load_json_argument(args.matrix)
        elif args.msq_d is not None:
            kind, raw_value = "msq_d", list(args.msq_d)
        else:
            kind, raw_value = _decode_payload(_load_json_file(args.input))

        if kind == "matrix":
            report = verify_matrix(_normalize_matrix(raw_value))
        else:
            if args.msq_d is not None:
                try:
                    raw_value = [int(value, 10) for value in raw_value]
                except ValueError as exc:
                    raise InputError("--msq-d values must be base-10 integers") from exc
            m, b, c = _normalize_msq_d(raw_value)
            report = verify_msq_d(m, b, c)

        report["input_kind"] = kind
        _emit(report, pretty=pretty)
        return EXIT_VALID if report["valid"] else EXIT_INVALID
    except InputError as exc:
        _emit(
            {
                "valid": False,
                "input_error": str(exc),
                "errors": [str(exc)],
            },
            pretty=pretty,
        )
        return EXIT_INPUT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
