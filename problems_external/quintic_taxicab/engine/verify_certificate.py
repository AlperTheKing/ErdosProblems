#!/usr/bin/env python3
"""Standalone exact verifier for a positive fifth-power taxicab certificate.

The target is a quadruple of positive integers ``(a, b, c, d)`` satisfying

    a**5 + b**5 == c**5 + d**5

with no value occurring on both sides.  Repetition within one side is allowed.
Only Python integers are used.  Exit status 0 means valid, 1 means that a
well-formed candidate failed a mathematical check, and 2 means malformed
input.

Accepted inputs are ``--quadruple A B C D`` or JSON supplied with ``--json``
or ``--input``.  JSON may be an array of four integers, an object containing a
``quadruple`` or ``integer_quadruple`` array, or an object with exactly the
keys ``a``, ``b``, ``c``, and ``d``.  Prefix a ``--json`` value with ``@`` to
read it from a file; ``--input -`` reads standard input.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence


EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_INPUT_ERROR = 2


class InputError(ValueError):
    """Raised when an input is not a supported integer certificate."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Argument parser whose errors are returned in the JSON report."""

    def error(self, message: str) -> None:
        raise InputError(message)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def normalize_quadruple(raw: Any) -> tuple[int, int, int, int]:
    """Decode one strict four-integer certificate."""

    if isinstance(raw, dict):
        keys = set(raw)
        if keys == {"a", "b", "c", "d"}:
            values = [raw[name] for name in ("a", "b", "c", "d")]
        elif keys == {"quadruple"}:
            values = raw["quadruple"]
        elif keys == {"integer_quadruple"}:
            values = raw["integer_quadruple"]
        else:
            raise InputError(
                "JSON object must contain exactly a,b,c,d, quadruple, or "
                "integer_quadruple"
            )
    else:
        values = raw

    if not isinstance(values, (list, tuple)) or len(values) != 4:
        raise InputError("certificate must contain exactly four integers")
    if not all(_is_integer(value) for value in values):
        raise InputError("certificate entries must be JSON integers")
    return tuple(int(value) for value in values)  # type: ignore[return-value]


def verify_quadruple(a: int, b: int, c: int, d: int) -> dict[str, Any]:
    """Return a complete exact verification report for ``(a,b,c,d)``."""

    values = (a, b, c, d)
    if not all(_is_integer(value) for value in values):
        raise InputError("certificate entries must be integers")

    left_terms = [a**5, b**5]
    right_terms = [c**5, d**5]
    left_sum = sum(left_terms)
    right_sum = sum(right_terms)
    cross_collisions = sorted(set((a, b)).intersection((c, d)))
    checks = {
        "positive_integers": all(value > 0 for value in values),
        "fifth_power_equality": left_sum == right_sum,
        "cross_disjoint": not cross_collisions,
    }
    errors: list[str] = []
    if not checks["positive_integers"]:
        errors.append("a, b, c, and d must be positive integers")
    if not checks["fifth_power_equality"]:
        errors.append("a^5 + b^5 must equal c^5 + d^5")
    if not checks["cross_disjoint"]:
        errors.append("the two representations must be cross-disjoint")

    return {
        "schema_version": 1,
        "verifier": "quintic_taxicab_exact_python",
        "valid": all(checks.values()),
        "checks": checks,
        "errors": errors,
        "certificate": {"a": a, "b": b, "c": c, "d": d},
        "left_terms": left_terms,
        "right_terms": right_terms,
        "left_sum": left_sum,
        "right_sum": right_sum,
        "difference": left_sum - right_sum,
        "cross_collisions": cross_collisions,
        "primitive_gcd": math.gcd(math.gcd(abs(a), abs(b)), math.gcd(abs(c), abs(d))),
    }


def _load_json_text(text: str, source: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"invalid JSON in {source}: line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc


def _load_path(path: Path) -> Any:
    try:
        return _load_json_text(path.read_text(encoding="utf-8"), str(path))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def _build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--quadruple", nargs=4, metavar=("A", "B", "C", "D"))
    source.add_argument("--json", metavar="JSON")
    source.add_argument("--input", metavar="FILE")
    parser.add_argument("--pretty", action="store_true")
    return parser


def _emit(report: dict[str, Any], pretty: bool) -> None:
    json.dump(
        report,
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
        if args.quadruple is not None:
            try:
                raw: Any = [int(value, 10) for value in args.quadruple]
            except ValueError as exc:
                raise InputError("--quadruple entries must be base-10 integers") from exc
        elif args.json is not None:
            raw = (
                _load_path(Path(args.json[1:]))
                if args.json.startswith("@")
                else _load_json_text(args.json, "--json")
            )
        elif args.input == "-":
            raw = _load_json_text(sys.stdin.read(), "stdin")
        else:
            raw = _load_path(Path(args.input))

        report = verify_quadruple(*normalize_quadruple(raw))
        _emit(report, pretty)
        return EXIT_VALID if report["valid"] else EXIT_INVALID
    except InputError as exc:
        _emit(
            {
                "schema_version": 1,
                "verifier": "quintic_taxicab_exact_python",
                "valid": False,
                "input_error": str(exc),
                "errors": [str(exc)],
            },
            pretty,
        )
        return EXIT_INPUT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
