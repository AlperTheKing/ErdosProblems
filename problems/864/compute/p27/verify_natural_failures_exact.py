"""Exact big-integer verification of every failure in the natural-cut census."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def cyclic_cuts(values: list[int], modulus: int):
    for base in values:
        yield base, sorted((value - base) % modulus for value in values)


def failure_bits(points: list[int], modulus: int) -> int:
    span = points[-1]
    reflected = [span - value for value in reversed(points)]
    differences = {
        points[j] - points[i]
        for i in range(len(points))
        for j in range(i + 1, len(points))
    }
    if len(differences) != (modulus - 1) // 2:
        raise AssertionError("Singer difference count failed")

    difference_bits = sum(1 << value for value in differences)
    nonzero_mask = (1 << modulus) - 2
    complement_bits = nonzero_mask & ~difference_bits
    sums = {
        reflected[i] + reflected[j]
        for i in range(len(reflected))
        for j in range(i, len(reflected))
        if reflected[i] + reflected[j] < modulus
    }
    covered = 0
    for total in sums:
        covered |= complement_bits << total
    return nonzero_mask & ~covered


def verify_record(record: dict[str, object], expected: dict[str, object]) -> dict[str, object]:
    q = int(record["parameter"])
    modulus = int(record["modulus"])
    residues = sorted(int(value) for value in record["residues"])
    rows = []
    for base, points in cyclic_cuts(residues, modulus):
        missing = failure_bits(points, modulus)
        if missing == 0:
            raise AssertionError("cut has no endpoint failure")
        maximum = missing.bit_length() - 1
        rows.append(
            {
                "base": base,
                "max_failure_d": maximum,
                "failure_count": missing.bit_count(),
            }
        )

    maximum = max(int(row["max_failure_d"]) for row in rows)
    thresholds = {
        name: sum(int(row["max_failure_d"]) * denominator >= numerator * modulus for row in rows)
        for name, numerator, denominator in (
            ("one_quarter", 1, 4),
            ("three_tenths", 3, 10),
            ("one_third", 1, 3),
            ("two_fifths", 2, 5),
        )
    }
    result = {
        "q": q,
        "v": modulus,
        "cuts": len(rows),
        "max_failure_d": maximum,
        "max_failure_d_over_v": str(Fraction(maximum, modulus)),
        "max_failure_cut_bases": [
            int(row["base"]) for row in rows if int(row["max_failure_d"]) == maximum
        ],
        "cuts_with_failure_at_or_above": thresholds,
        "min_cut_max_failure_d": min(int(row["max_failure_d"]) for row in rows),
    }
    for key in (
        "q",
        "v",
        "cuts",
        "max_failure_d",
        "max_failure_d_over_v",
        "max_failure_cut_bases",
        "cuts_with_failure_at_or_above",
        "min_cut_max_failure_d",
    ):
        if result[key] != expected[key]:
            raise AssertionError((q, key, result[key], expected[key]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    parser.add_argument("census", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = [json.loads(line) for line in args.records.read_text(encoding="ascii").splitlines()]
    expected_rows = json.loads(args.census.read_text(encoding="ascii"))["records"]
    expected = {int(row["q"]): row for row in expected_rows}
    results = [verify_record(record, expected[int(record["parameter"])]) for record in source]
    summary = {
        "records": len(results),
        "cuts": sum(int(row["cuts"]) for row in results),
        "all_fft_census_fields_match_exact_bitsets": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"records": results, "summary": summary}, indent=2, sort_keys=True)
        + "\n",
        encoding="ascii",
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
