#!/usr/bin/env python3
"""Independent exact verifier for an order-668 Goethals--Seidel certificate.

The production certificate is JSON of the form

    {
      "modulus": 167,
      "cardinalities": [k1, k2, k3, k4],
      "subsets": [[...], [...], [...], [...]]
    }

Normal verification requires modulus 167.  ``--self-test`` verifies a small
known SDS fixture and also checks that a one-entry corruption is rejected.
Only Python's standard library is used; all arithmetic is exact integer
arithmetic.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


TARGET_MODULUS = 167
BLOCK_COUNT = 4


class CertificateError(ValueError):
    """Raised when a purported certificate fails an exact check."""


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CertificateError(f"{label} must be a JSON integer")
    return value


def _aliased_field(data: dict[str, Any], names: Sequence[str], label: str) -> Any:
    present = [(name, data[name]) for name in names if name in data]
    if not present:
        raise CertificateError(f"missing {label} (expected key {names[0]!r})")
    first_name, first_value = present[0]
    for name, value in present[1:]:
        if value != first_value:
            raise CertificateError(
                f"conflicting aliases for {label}: {first_name!r} and {name!r}"
            )
    return first_value


def parse_certificate(
    raw: Any, expected_modulus: int | None
) -> tuple[int, list[int], list[list[int]]]:
    """Parse and strictly validate the structural part of a certificate."""

    if not isinstance(raw, dict):
        raise CertificateError("certificate root must be a JSON object")

    modulus = _integer(
        _aliased_field(raw, ("modulus", "n", "v"), "modulus"), "modulus"
    )
    if modulus <= 1 or modulus % 2 == 0:
        raise CertificateError("modulus must be an odd integer greater than 1")
    if expected_modulus is not None and modulus != expected_modulus:
        raise CertificateError(
            f"expected modulus {expected_modulus}, certificate has {modulus}"
        )

    cardinalities_raw = _aliased_field(
        raw, ("cardinalities", "sizes"), "cardinalities"
    )
    if not isinstance(cardinalities_raw, list) or len(cardinalities_raw) != BLOCK_COUNT:
        raise CertificateError("cardinalities must be a JSON list of length 4")
    cardinalities = [
        _integer(value, f"cardinalities[{index}]")
        for index, value in enumerate(cardinalities_raw)
    ]

    subsets_raw = _aliased_field(raw, ("subsets", "blocks"), "subsets")
    if not isinstance(subsets_raw, list) or len(subsets_raw) != BLOCK_COUNT:
        raise CertificateError("subsets must be a JSON list of four lists")

    subsets: list[list[int]] = []
    for block_index, block_raw in enumerate(subsets_raw):
        if not isinstance(block_raw, list):
            raise CertificateError(f"subsets[{block_index}] must be a JSON list")
        block = [
            _integer(value, f"subsets[{block_index}][{entry_index}]")
            for entry_index, value in enumerate(block_raw)
        ]
        if any(value < 0 or value >= modulus for value in block):
            raise CertificateError(
                f"subsets[{block_index}] contains an entry outside 0..{modulus - 1}"
            )
        if len(set(block)) != len(block):
            raise CertificateError(f"subsets[{block_index}] contains a duplicate")
        if cardinalities[block_index] != len(block):
            raise CertificateError(
                f"cardinalities[{block_index}]={cardinalities[block_index]} "
                f"but subsets[{block_index}] has {len(block)} entries"
            )
        if cardinalities[block_index] > modulus // 2:
            raise CertificateError(
                f"cardinalities[{block_index}] is not normalized: "
                f"{cardinalities[block_index]} > {modulus // 2}"
            )
        subsets.append(block)

    return modulus, cardinalities, subsets


def verify_ordered_differences(
    modulus: int, cardinalities: Sequence[int], subsets: Sequence[Sequence[int]]
) -> tuple[int, list[int]]:
    """Check every nonzero ordered difference and return lambda and totals."""

    lam = sum(cardinalities) - modulus
    if lam < 0:
        raise CertificateError(f"lambda is negative: {lam}")

    parameter_lhs = sum((modulus - 2 * size) ** 2 for size in cardinalities)
    parameter_rhs = 4 * modulus
    if parameter_lhs != parameter_rhs:
        raise CertificateError(
            "cardinality parameter equation fails: "
            f"sum((n-2k_i)^2)={parameter_lhs}, expected {parameter_rhs}"
        )

    totals = [0] * modulus
    for block in subsets:
        for left in block:
            for right in block:
                if left != right:
                    totals[(left - right) % modulus] += 1

    mismatches = [
        (difference, totals[difference])
        for difference in range(1, modulus)
        if totals[difference] != lam
    ]
    if mismatches:
        preview = ", ".join(
            f"d={difference}: got {actual}, expected {lam}"
            for difference, actual in mismatches[:12]
        )
        suffix = "" if len(mismatches) <= 12 else f"; ... {len(mismatches)} total"
        raise CertificateError(f"ordered-difference check fails: {preview}{suffix}")

    return lam, totals


def associated_sequence(modulus: int, block: Iterable[int]) -> list[int]:
    """Return the +/-1 sequence which is -1 exactly on ``block``."""

    block_set = set(block)
    return [-1 if index in block_set else 1 for index in range(modulus)]


def circulant(sequence: Sequence[int]) -> list[list[int]]:
    """Return C with C[i,j] = sequence[(j-i) mod n]."""

    modulus = len(sequence)
    return [
        [sequence[(column - row) % modulus] for column in range(modulus)]
        for row in range(modulus)
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def right_reverse(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return matrix * R, where R is the back-diagonal permutation matrix."""

    return [list(reversed(row)) for row in matrix]


def build_goethals_seidel(subsets: Sequence[Sequence[int]], modulus: int) -> list[list[int]]:
    """Build the standard Goethals--Seidel array from four circulants."""

    a, b, c, d = [
        circulant(associated_sequence(modulus, block)) for block in subsets
    ]
    br = right_reverse(b)
    cr = right_reverse(c)
    dr = right_reverse(d)
    btr = right_reverse(transpose(b))
    ctr = right_reverse(transpose(c))
    dtr = right_reverse(transpose(d))

    block_rows: list[list[tuple[Sequence[Sequence[int]], int]]] = [
        [(a, 1), (br, 1), (cr, 1), (dr, 1)],
        [(br, -1), (a, 1), (dtr, -1), (ctr, 1)],
        [(cr, -1), (dtr, 1), (a, 1), (btr, -1)],
        [(dr, -1), (ctr, -1), (btr, 1), (a, 1)],
    ]

    matrix: list[list[int]] = []
    for block_row in block_rows:
        for local_row in range(modulus):
            row: list[int] = []
            for block, sign in block_row:
                row.extend(sign * value for value in block[local_row])
            matrix.append(row)
    return matrix


def verify_exact_gram(matrix: Sequence[Sequence[int]]) -> int:
    """Check H H^T = order*I exactly, using integer Hamming distances."""

    order = len(matrix)
    if order == 0 or any(len(row) != order for row in matrix):
        raise CertificateError("Goethals--Seidel output is not a nonempty square matrix")

    row_bits: list[int] = []
    for row_index, row in enumerate(matrix):
        bits = 0
        for column_index, value in enumerate(row):
            if value not in (-1, 1):
                raise CertificateError(
                    f"matrix entry ({row_index},{column_index}) is {value}, not +/-1"
                )
            if value == 1:
                bits |= 1 << column_index
        row_bits.append(bits)

    pairs_checked = 0
    for left in range(order):
        for right in range(left, order):
            distance = (row_bits[left] ^ row_bits[right]).bit_count()
            dot_product = order - 2 * distance
            expected = order if left == right else 0
            pairs_checked += 1
            if dot_product != expected:
                raise CertificateError(
                    "exact Goethals--Seidel Gram check fails at "
                    f"({left},{right}): got {dot_product}, expected {expected}"
                )
    return pairs_checked


def _csv_lines(matrix: Sequence[Sequence[int]]) -> Iterable[bytes]:
    for row in matrix:
        yield (",".join(str(value) for value in row) + "\n").encode("ascii")


def csv_sha256(matrix: Sequence[Sequence[int]]) -> str:
    digest = hashlib.sha256()
    for line in _csv_lines(matrix):
        digest.update(line)
    return digest.hexdigest()


def write_csv(matrix: Sequence[Sequence[int]], output_path: Path) -> str:
    digest = hashlib.sha256()
    with output_path.open("wb") as output:
        for line in _csv_lines(matrix):
            output.write(line)
            digest.update(line)
    return digest.hexdigest()


def verify_certificate(
    raw: Any,
    *,
    expected_modulus: int | None = TARGET_MODULUS,
    csv_path: Path | None = None,
) -> dict[str, Any]:
    modulus, cardinalities, subsets = parse_certificate(raw, expected_modulus)
    lam, _totals = verify_ordered_differences(modulus, cardinalities, subsets)

    matrix = build_goethals_seidel(subsets, modulus)
    pairs_checked = verify_exact_gram(matrix)
    digest = write_csv(matrix, csv_path) if csv_path else csv_sha256(matrix)

    return {
        "status": "VALID",
        "modulus": modulus,
        "hadamard_order": 4 * modulus,
        "cardinalities": cardinalities,
        "lambda": lam,
        "ordered_nonzero_differences_checked": modulus - 1,
        "gram_row_pairs_checked": pairs_checked,
        "matrix_csv_sha256": digest,
        "csv_path": str(csv_path.resolve()) if csv_path else None,
    }


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as source:
            return json.load(source)
    except json.JSONDecodeError as error:
        raise CertificateError(
            f"invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error


def run_self_test(csv_path: Path | None) -> dict[str, Any]:
    fixture_path = Path(__file__).with_name("fixtures") / "sds_n7.json"
    raw = load_json(fixture_path)
    report = verify_certificate(raw, expected_modulus=None, csv_path=csv_path)

    corrupted = copy.deepcopy(raw)
    corrupted["subsets"][2] = [0, 1, 2]
    try:
        verify_certificate(corrupted, expected_modulus=None)
    except CertificateError:
        report["corruption_test"] = "REJECTED"
    else:
        raise RuntimeError("self-test corruption was incorrectly accepted")
    report["fixture"] = str(fixture_path.resolve())
    report["self_test"] = "PASS"
    return report


def argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a four-subset SDS certificate and independently check the "
            "resulting Goethals--Seidel Hadamard matrix."
        )
    )
    parser.add_argument("certificate", nargs="?", type=Path, help="certificate JSON")
    parser.add_argument("--csv", type=Path, help="write the verified +/-1 matrix as CSV")
    parser.add_argument(
        "--self-test", action="store_true", help="verify the bundled order-28 SDS fixture"
    )
    parser.add_argument(
        "--allow-any-modulus",
        action="store_true",
        help="do not require production modulus 167 (for independent small tests)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = argument_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        if args.certificate is not None or args.allow_any_modulus:
            parser.error("--self-test takes neither a certificate nor --allow-any-modulus")
        action = lambda: run_self_test(args.csv)
    else:
        if args.certificate is None:
            parser.error("certificate is required unless --self-test is used")
        expected_modulus = None if args.allow_any_modulus else TARGET_MODULUS
        action = lambda: verify_certificate(
            load_json(args.certificate),
            expected_modulus=expected_modulus,
            csv_path=args.csv,
        )

    try:
        report = action()
    except CertificateError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
