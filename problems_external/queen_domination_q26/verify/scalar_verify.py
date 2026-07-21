#!/usr/bin/env python3
"""Scalar, exhaustive checker for queen-domination certificates.

Certificate coordinates are zero-based ``[row, column]`` pairs.  JSON files
may provide ``n``, ``expected_count``, ``require_independent``, and
``coordinates``.  A plain-text certificate may use ``n = ...`` and one
``row column`` (or ``(row,column)``) pair per line.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _coordinates(values: Iterable[Any]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for index, pair in enumerate(values):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError(f"coordinate {index} is not a pair")
        result.append(
            (_integer(pair[0], f"coordinate {index} row"),
             _integer(pair[1], f"coordinate {index} column"))
        )
    return result


def load_certificate(path: Path) -> dict[str, Any]:
    """Load a JSON or simple text certificate without verifying it."""
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        n: int | None = None
        expected_count: int | None = None
        require_independent = False
        coordinates: list[tuple[int, int]] = []
        for line_number, raw_line in enumerate(text.splitlines(), 1):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue
            metadata = re.fullmatch(
                r"(?i)(n|expected_count|expect|require_independent)\s*[:=]\s*(\S+)",
                line,
            )
            if metadata:
                key, value = metadata.groups()
                key = key.lower()
                if key == "n":
                    n = int(value)
                elif key in {"expected_count", "expect"}:
                    expected_count = int(value)
                else:
                    require_independent = value.lower() in {"1", "true", "yes"}
                continue
            numbers = re.findall(r"[-+]?\d+", line)
            if len(numbers) != 2:
                raise ValueError(
                    f"line {line_number} must contain exactly one coordinate pair"
                )
            coordinates.append((int(numbers[0]), int(numbers[1])))
        if n is None:
            raise ValueError("plain-text certificate is missing n")
        return {
            "n": n,
            "expected_count": expected_count,
            "require_independent": require_independent,
            "coordinates": coordinates,
        }

    if not isinstance(payload, dict):
        raise ValueError("JSON certificate must be an object")
    if payload.get("coordinate_order", "row,column") not in {
        "row,column",
        "row_column",
    }:
        raise ValueError("coordinate_order must be row,column")
    if "n" not in payload or "coordinates" not in payload:
        raise ValueError("JSON certificate requires n and coordinates")
    expected = payload.get("expected_count")
    if expected is not None:
        expected = _integer(expected, "expected_count")
    require_independent = payload.get("require_independent", False)
    if not isinstance(require_independent, bool):
        raise ValueError("require_independent must be boolean")
    return {
        "n": _integer(payload["n"], "n"),
        "expected_count": expected,
        "require_independent": require_independent,
        "coordinates": _coordinates(payload["coordinates"]),
    }


def verify(
    n: int,
    coordinates: Iterable[tuple[int, int]],
    *,
    expected_count: int | None = None,
    require_independent: bool = False,
) -> dict[str, Any]:
    """Check every board square by direct coordinate comparisons."""
    queens = list(coordinates)
    errors: list[str] = []
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        errors.append("n must be a positive integer")
    if expected_count is not None and len(queens) != expected_count:
        errors.append(f"expected {expected_count} queens, found {len(queens)}")

    malformed = [q for q in queens if not isinstance(q, tuple) or len(q) != 2]
    if malformed:
        errors.append("all coordinates must be pairs")
    if not errors:
        out_of_range = [q for q in queens if not (0 <= q[0] < n and 0 <= q[1] < n)]
        if out_of_range:
            errors.append(f"out-of-range coordinates: {out_of_range}")
    if len(set(queens)) != len(queens):
        errors.append("coordinates are not distinct")

    undominated: list[tuple[int, int]] = []
    independent = False
    if not errors:
        for row in range(n):
            for column in range(n):
                if not any(
                    row == queen_row
                    or column == queen_column
                    or abs(row - queen_row) == abs(column - queen_column)
                    for queen_row, queen_column in queens
                ):
                    undominated.append((row, column))
        independent = all(
            row_a != row_b
            and column_a != column_b
            and abs(row_a - row_b) != abs(column_a - column_b)
            for index, (row_a, column_a) in enumerate(queens)
            for row_b, column_b in queens[index + 1 :]
        )
        if undominated:
            errors.append(f"{len(undominated)} board squares are undominated")
        if require_independent and not independent:
            errors.append("queen set is not independent")

    dominated_count = n * n - len(undominated) if n > 0 and not malformed else 0
    return {
        "valid": not errors,
        "n": n,
        "queen_count": len(queens),
        "dominated_count": dominated_count,
        "independent": independent,
        "undominated": [list(square) for square in undominated],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--n", type=int, help="override board size")
    parser.add_argument("--expect", type=int, help="override expected queen count")
    parser.add_argument("--require-independent", action="store_true")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args(argv)
    try:
        certificate = load_certificate(args.certificate)
        result = verify(
            args.n if args.n is not None else certificate["n"],
            certificate["coordinates"],
            expected_count=(
                args.expect if args.expect is not None else certificate["expected_count"]
            ),
            require_independent=(
                args.require_independent or certificate["require_independent"]
            ),
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json_output:
        print(json.dumps(result, sort_keys=True))
    elif result["valid"]:
        print(
            f"VALID n={result['n']} queens={result['queen_count']} "
            f"dominated={result['dominated_count']} independent={result['independent']}"
        )
    else:
        print("INVALID: " + "; ".join(result["errors"]))
        if result["undominated"]:
            print(f"first_undominated={result['undominated'][:20]}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
