#!/usr/bin/env python3
"""Independent bit-board checker for queen-domination certificates.

Unlike ``scalar_verify.py``, this checker builds each queen's closed attack
neighborhood by stepping in eight directions and unions Python-integer bitsets.
Coordinates are zero-based ``[row, column]`` pairs.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


def load_certificate(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    try:
        document = json.loads(raw)
    except json.JSONDecodeError:
        document = None
    if document is not None:
        if not isinstance(document, dict):
            raise ValueError("JSON certificate must be an object")
        if document.get("coordinate_order", "row,column") not in {
            "row,column",
            "row_column",
        }:
            raise ValueError("coordinate_order must be row,column")
        try:
            n = document["n"]
            source_coordinates = document["coordinates"]
        except KeyError as exc:
            raise ValueError(f"missing JSON field: {exc.args[0]}") from exc
        expected = document.get("expected_count")
        require_independent = document.get("require_independent", False)
    else:
        n = None
        expected = None
        require_independent = False
        source_coordinates = []
        for number, raw_line in enumerate(raw.splitlines(), 1):
            line = raw_line.partition("#")[0].strip()
            if not line:
                continue
            match = re.fullmatch(
                r"(?i)(n|expected_count|expect|require_independent)\s*[:=]\s*(\S+)",
                line,
            )
            if match:
                key, value = match.groups()
                key = key.lower()
                if key == "n":
                    n = int(value)
                elif key in {"expect", "expected_count"}:
                    expected = int(value)
                else:
                    require_independent = value.lower() in {"true", "yes", "1"}
                continue
            values = re.findall(r"[-+]?\d+", line)
            if len(values) != 2:
                raise ValueError(f"bad coordinate on line {number}")
            source_coordinates.append([int(values[0]), int(values[1])])
        if n is None:
            raise ValueError("plain-text certificate is missing n")

    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError("n must be an integer")
    if expected is not None and (isinstance(expected, bool) or not isinstance(expected, int)):
        raise ValueError("expected_count must be an integer")
    if not isinstance(require_independent, bool):
        raise ValueError("require_independent must be boolean")
    coordinates: list[tuple[int, int]] = []
    for index, value in enumerate(source_coordinates):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError(f"coordinate {index} is not a pair")
        row, column = value
        if any(isinstance(item, bool) or not isinstance(item, int) for item in value):
            raise ValueError(f"coordinate {index} is not an integer pair")
        coordinates.append((row, column))
    return {
        "n": n,
        "expected_count": expected,
        "require_independent": require_independent,
        "coordinates": coordinates,
    }


_DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),             (0, 1),
    (1, -1),  (1, 0),    (1, 1),
)


def _closed_neighborhood(n: int, row: int, column: int) -> int:
    mask = 1 << (row * n + column)
    for row_step, column_step in _DIRECTIONS:
        target_row = row + row_step
        target_column = column + column_step
        while 0 <= target_row < n and 0 <= target_column < n:
            mask |= 1 << (target_row * n + target_column)
            target_row += row_step
            target_column += column_step
    return mask


def verify(
    n: int,
    coordinates: Iterable[tuple[int, int]],
    *,
    expected_count: int | None = None,
    require_independent: bool = False,
) -> dict[str, Any]:
    queens = list(coordinates)
    errors: list[str] = []
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        errors.append("n must be a positive integer")
    if expected_count is not None and len(queens) != expected_count:
        errors.append(f"expected {expected_count} queens, found {len(queens)}")
    if len(set(queens)) != len(queens):
        errors.append("coordinates are not distinct")
    if not errors:
        bad = [square for square in queens if not (0 <= square[0] < n and 0 <= square[1] < n)]
        if bad:
            errors.append(f"out-of-range coordinates: {bad}")

    covered = 0
    neighborhoods: list[int] = []
    occupied = 0
    if not errors:
        for row, column in queens:
            square_bit = 1 << (row * n + column)
            occupied |= square_bit
            neighborhood = _closed_neighborhood(n, row, column)
            neighborhoods.append(neighborhood)
            covered |= neighborhood

    full_board = (1 << (n * n)) - 1 if n > 0 else 0
    missing_mask = full_board & ~covered
    undominated: list[list[int]] = []
    work = missing_mask
    while work:
        lowest = work & -work
        index = lowest.bit_length() - 1
        undominated.append([index // n, index % n])
        work ^= lowest

    independent = bool(not errors)
    if not errors:
        for row, column in queens:
            square = 1 << (row * n + column)
            if _closed_neighborhood(n, row, column) & (occupied ^ square):
                independent = False
                break
        if missing_mask:
            errors.append(f"{missing_mask.bit_count()} board squares are undominated")
        if require_independent and not independent:
            errors.append("queen set is not independent")

    return {
        "valid": not errors,
        "n": n,
        "queen_count": len(queens),
        "dominated_count": covered.bit_count(),
        "independent": independent,
        "undominated": undominated,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--n", type=int)
    parser.add_argument("--expect", type=int)
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
