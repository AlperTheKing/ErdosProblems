#!/usr/bin/env python3
"""Strict scalar verifier for Seymour counterexample certificates.

Canonical input schema (and no other top-level keys)::

    {"n": N, "out_neighbors": [[...], ..., [...]]}

The outer-list index is the vertex.  There must be exactly ``N`` rows, and
each row must be a strictly increasing list of distinct JSON integers in
``0 .. N-1``.  Loops and digons are rejected.

Exit codes:

* 0: ``VERIFIED_COUNTEREXAMPLE``
* 1: ``VALID_GRAPH_NOT_COUNTEREXAMPLE``
* 2: ``INVALID_CERTIFICATE`` (including JSON and I/O failures)

Exactly one deterministic JSON ledger is written to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO


EXIT_VERIFIED_COUNTEREXAMPLE = 0
EXIT_VALID_GRAPH_NOT_COUNTEREXAMPLE = 1
EXIT_INVALID_CERTIFICATE = 2

STATUS_VERIFIED_COUNTEREXAMPLE = "VERIFIED_COUNTEREXAMPLE"
STATUS_VALID_GRAPH_NOT_COUNTEREXAMPLE = "VALID_GRAPH_NOT_COUNTEREXAMPLE"
STATUS_INVALID_CERTIFICATE = "INVALID_CERTIFICATE"

_TOP_LEVEL_KEYS = frozenset(("n", "out_neighbors"))


class DuplicateObjectKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""


def _reject_duplicate_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateObjectKeyError(f"duplicate object key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_number(token: str) -> None:
    raise ValueError(f"non-finite JSON number {token!r} is not permitted")


def parse_certificate_json(raw: str) -> Any:
    """Parse strict JSON, rejecting duplicate keys and non-finite numbers."""

    return json.loads(
        raw,
        object_pairs_hook=_reject_duplicate_object_keys,
        parse_constant=_reject_nonfinite_number,
    )


def _ledger(
    *,
    status: str,
    n: int | None,
    per_vertex: list[dict[str, Any]] | None = None,
    failing_vertices: list[int] | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "errors": [] if errors is None else errors,
        "failing_vertices": [] if failing_vertices is None else failing_vertices,
        "n": n,
        "per_vertex": [] if per_vertex is None else per_vertex,
        "status": status,
    }


def verify_certificate_data(data: Any) -> tuple[int, dict[str, Any]]:
    """Validate and exhaustively verify one decoded certificate.

    The implementation deliberately uses ordinary Python sets.  It shares no
    reachability machinery with the independent bitset verifier.
    """

    if type(data) is not dict:
        return (
            EXIT_INVALID_CERTIFICATE,
            _ledger(
                status=STATUS_INVALID_CERTIFICATE,
                n=None,
                errors=["top-level JSON value must be an object"],
            ),
        )

    errors: list[str] = []
    actual_keys = set(data)
    missing_keys = sorted(_TOP_LEVEL_KEYS - actual_keys)
    extra_keys = sorted(actual_keys - _TOP_LEVEL_KEYS)
    if missing_keys:
        errors.append(f"missing top-level keys: {missing_keys}")
    if extra_keys:
        errors.append(f"unexpected top-level keys: {extra_keys}")

    n_value = data.get("n")
    n: int | None
    if type(n_value) is not int:
        errors.append("n must be a JSON integer (booleans are not integers)")
        n = None
    elif n_value < 1:
        errors.append("n must be at least 1")
        n = n_value
    else:
        n = n_value

    rows_value = data.get("out_neighbors")
    if type(rows_value) is not list:
        errors.append("out_neighbors must be a JSON array")
        rows: list[Any] | None = None
    else:
        rows = rows_value

    if n is not None and n >= 1 and rows is not None and len(rows) != n:
        errors.append(f"out_neighbors must contain exactly n={n} rows; found {len(rows)}")

    if n is not None and n >= 1 and rows is not None:
        for vertex, row in enumerate(rows):
            if type(row) is not list:
                errors.append(f"out_neighbors[{vertex}] must be a JSON array")
                continue

            seen: set[int] = set()
            previous: int | None = None
            for index, neighbor in enumerate(row):
                if type(neighbor) is not int:
                    errors.append(
                        f"out_neighbors[{vertex}][{index}] must be a JSON integer "
                        "(booleans are not integers)"
                    )
                    continue

                if previous is not None and neighbor <= previous:
                    errors.append(
                        f"out_neighbors[{vertex}] must be strictly increasing; "
                        f"entry {index} is {neighbor} after {previous}"
                    )
                previous = neighbor

                if neighbor in seen:
                    errors.append(
                        f"out_neighbors[{vertex}] contains duplicate neighbor {neighbor}"
                    )
                seen.add(neighbor)

                if neighbor < 0 or neighbor >= n:
                    errors.append(
                        f"out_neighbors[{vertex}][{index}]={neighbor} is outside 0..{n - 1}"
                    )
                elif neighbor == vertex:
                    errors.append(f"loop at vertex {vertex}")

    if errors:
        return (
            EXIT_INVALID_CERTIFICATE,
            _ledger(status=STATUS_INVALID_CERTIFICATE, n=n, errors=errors),
        )

    # The preceding validation proves these types and dimensions.
    assert n is not None and n >= 1
    assert rows is not None and len(rows) == n
    typed_rows: list[list[int]] = rows
    out_sets = [set(row) for row in typed_rows]

    digon_errors: list[str] = []
    for source in range(n):
        for target in typed_rows[source]:
            if source < target and source in out_sets[target]:
                digon_errors.append(f"digon between vertices {source} and {target}")

    if digon_errors:
        return (
            EXIT_INVALID_CERTIFICATE,
            _ledger(status=STATUS_INVALID_CERTIFICATE, n=n, errors=digon_errors),
        )

    per_vertex: list[dict[str, Any]] = []
    failing_vertices: list[int] = []
    for vertex in range(n):
        n1 = out_sets[vertex]
        reachable_in_two: set[int] = set()
        for middle in n1:
            reachable_in_two.update(out_sets[middle])

        # "New" second out-neighbors exclude the source and all direct
        # out-neighbors, even if another two-step walk reaches them.
        n2_new = reachable_in_two - n1 - {vertex}
        d1 = len(n1)
        d2 = len(n2_new)
        strict = d2 < d1
        if not strict:
            failing_vertices.append(vertex)

        per_vertex.append(
            {
                "d1": d1,
                "d2": d2,
                "n1": sorted(n1),
                "n2_new": sorted(n2_new),
                "strict_d2_lt_d1": strict,
                "vertex": vertex,
            }
        )

    if failing_vertices:
        return (
            EXIT_VALID_GRAPH_NOT_COUNTEREXAMPLE,
            _ledger(
                status=STATUS_VALID_GRAPH_NOT_COUNTEREXAMPLE,
                n=n,
                per_vertex=per_vertex,
                failing_vertices=failing_vertices,
            ),
        )

    return (
        EXIT_VERIFIED_COUNTEREXAMPLE,
        _ledger(
            status=STATUS_VERIFIED_COUNTEREXAMPLE,
            n=n,
            per_vertex=per_vertex,
            failing_vertices=[],
        ),
    )


def verify_certificate_text(raw: str) -> tuple[int, dict[str, Any]]:
    try:
        data = parse_certificate_json(raw)
    except (json.JSONDecodeError, DuplicateObjectKeyError, ValueError) as exc:
        return (
            EXIT_INVALID_CERTIFICATE,
            _ledger(
                status=STATUS_INVALID_CERTIFICATE,
                n=None,
                errors=[f"invalid JSON: {exc}"],
            ),
        )
    return verify_certificate_data(data)


def _read_text(path: str, stdin: TextIO) -> str:
    if path == "-":
        return stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _emit_ledger(ledger: dict[str, Any], stdout: TextIO) -> None:
    stdout.write(json.dumps(ledger, sort_keys=True, separators=(",", ":")))
    stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Strict scalar verifier for an SSNC counterexample certificate."
    )
    parser.add_argument("certificate", help="certificate JSON path, or - for stdin")
    args = parser.parse_args(argv)

    try:
        raw = _read_text(args.certificate, sys.stdin)
    except (OSError, UnicodeError) as exc:
        code = EXIT_INVALID_CERTIFICATE
        ledger = _ledger(
            status=STATUS_INVALID_CERTIFICATE,
            n=None,
            errors=[f"unable to read certificate: {exc}"],
        )
    else:
        code, ledger = verify_certificate_text(raw)

    _emit_ledger(ledger, sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
