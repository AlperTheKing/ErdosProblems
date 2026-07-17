#!/usr/bin/env python3
"""Exact exhaustive verifier for finite covering systems in Problem 273.

The implementation deliberately uses only Python integer arithmetic.  In
particular, primality is decided by exhaustive trial division through the
integer square root, and coverage is checked at every residue of the true LCM.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Any, Iterable


class VerificationError(ValueError):
    """Raised when a certificate is malformed."""


@dataclass(frozen=True)
class Congruence:
    residue: int
    modulus: int


def exact_int(value: Any, label: str) -> int:
    # bool is a subclass of int, so an exact type check is intentional.
    if type(value) is not int:
        raise VerificationError(f"{label} must be a JSON integer")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_certificate(path: Path) -> tuple[dict[str, Any], list[Congruence]]:
    try:
        document = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot parse {path}: {exc}") from exc

    if not isinstance(document, dict):
        raise VerificationError("certificate root must be a JSON object")
    rows = document.get("congruences")
    if not isinstance(rows, list) or not rows:
        raise VerificationError("congruences must be a nonempty JSON array")

    congruences: list[Congruence] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerificationError(f"congruences[{index}] must be an object")
        residue = exact_int(row.get("residue"), f"congruences[{index}].residue")
        modulus = exact_int(row.get("modulus"), f"congruences[{index}].modulus")
        if modulus <= 0:
            raise VerificationError(f"congruences[{index}].modulus must be positive")
        if not 0 <= residue < modulus:
            raise VerificationError(
                f"congruences[{index}].residue must be canonical: 0 <= residue < modulus"
            )
        congruences.append(Congruence(residue, modulus))
    return document, congruences


def lcm_pair(left: int, right: int) -> int:
    return left // math.gcd(left, right) * right


def true_lcm(congruences: Iterable[Congruence]) -> int:
    return reduce(lcm_pair, (row.modulus for row in congruences), 1)


def exact_primality_record(number: int) -> dict[str, Any]:
    """Decide primality by checking every integer divisor up to isqrt(number)."""
    limit = math.isqrt(number) if number >= 0 else 0
    checked: list[int] = []
    smallest_factor: int | None = None
    if number >= 2:
        for divisor in range(2, limit + 1):
            checked.append(divisor)
            if number % divisor == 0:
                smallest_factor = divisor
                break
    is_prime = number >= 2 and smallest_factor is None
    return {
        "number": number,
        "is_prime": is_prime,
        "integer_sqrt": limit,
        "checked_divisors": checked,
        "smallest_factor": smallest_factor,
        "method": "exhaustive integer trial division through floor(sqrt(number))",
    }


def coverage_report(
    congruences: list[Congruence], period: int
) -> dict[str, Any]:
    multiplicities = [
        sum(1 for row in congruences if (residue - row.residue) % row.modulus == 0)
        for residue in range(period)
    ]
    uncovered = [
        residue for residue, multiplicity in enumerate(multiplicities) if multiplicity == 0
    ]
    histogram = Counter(multiplicities)
    return {
        "period": period,
        "residues_checked": period,
        "covered_residue_count": period - len(uncovered),
        "uncovered_residue_count": len(uncovered),
        "uncovered_residues": uncovered,
        "minimum_multiplicity": min(multiplicities),
        "maximum_multiplicity": max(multiplicities),
        "multiplicity_histogram": {
            str(key): histogram[key] for key in sorted(histogram)
        },
        "multiplicity_vector_indexed_by_residue": multiplicities,
        "covers_every_integer": not uncovered,
    }


def canonical_json(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative_hash_name(target: Path, hash_file: Path) -> str:
    try:
        relative = target.resolve().relative_to(hash_file.parent.resolve())
        return relative.as_posix()
    except ValueError:
        return target.resolve().as_posix()


def run(certificate_path: Path, output_path: Path, hashes_path: Path) -> bool:
    document, congruences = parse_certificate(certificate_path)

    moduli = [row.modulus for row in congruences]
    modulus_counts = Counter(moduli)
    duplicate_moduli = sorted(
        modulus for modulus, count in modulus_counts.items() if count > 1
    )
    all_positive = all(modulus > 0 for modulus in moduli)
    pairwise_distinct = not duplicate_moduli

    primality_checks: list[dict[str, Any]] = []
    for row in congruences:
        record = exact_primality_record(row.modulus + 1)
        record["modulus"] = row.modulus
        primality_checks.append(record)
    all_successors_prime = all(record["is_prime"] for record in primality_checks)
    all_successors_at_least_3 = all(record["number"] >= 3 for record in primality_checks)
    all_successors_at_least_5 = all(record["number"] >= 5 for record in primality_checks)

    period = true_lcm(congruences)
    expected_lcm_value = document.get("expected_lcm")
    if expected_lcm_value is None:
        expected_lcm: int | None = None
        expected_lcm_matches = True
    else:
        expected_lcm = exact_int(expected_lcm_value, "expected_lcm")
        expected_lcm_matches = expected_lcm == period

    full = coverage_report(congruences, period)

    modulus_two_rows = [row for row in congruences if row.modulus == 2]
    without_modulus_two = [row for row in congruences if row.modulus != 2]
    reduced = coverage_report(without_modulus_two, period)
    expected_even_residues = list(range(0, period, 2))
    removed_zero_mod_two_once = modulus_two_rows == [Congruence(0, 2)]
    uncovered_equals_even_residues = (
        reduced["uncovered_residues"] == expected_even_residues
    )

    baseline_valid = all(
        [
            all_positive,
            pairwise_distinct,
            all_successors_prime,
            all_successors_at_least_3,
            expected_lcm_matches,
            full["covers_every_integer"],
            removed_zero_mod_two_once,
            uncovered_equals_even_residues,
        ]
    )

    report: dict[str, Any] = {
        "schema": "erdos-273-verifier-a-output-v1",
        "certificate_file": certificate_path.name,
        "certificate_sha256": sha256_file(certificate_path),
        "congruence_count": len(congruences),
        "structural_checks": {
            "all_moduli_positive": all_positive,
            "moduli_pairwise_distinct": pairwise_distinct,
            "duplicate_moduli": duplicate_moduli,
        },
        "primality_checks": primality_checks,
        "successor_prime_conditions": {
            "all_m_plus_1_prime": all_successors_prime,
            "all_m_plus_1_at_least_3": all_successors_at_least_3,
            "all_m_plus_1_at_least_5": all_successors_at_least_5,
            "successors_below_5": [
                {"modulus": row.modulus, "prime": row.modulus + 1}
                for row in congruences
                if row.modulus + 1 < 5
            ],
        },
        "period_check": {
            "true_lcm": period,
            "certificate_expected_lcm": expected_lcm,
            "expected_lcm_matches": expected_lcm_matches,
        },
        "full_system": full,
        "without_modulus_2": {
            "removed_congruences": [
                {"residue": row.residue, "modulus": row.modulus}
                for row in modulus_two_rows
            ],
            "remaining_true_lcm": true_lcm(without_modulus_two),
            "coverage_over_full_system_period": reduced,
            "expected_even_residues": expected_even_residues,
            "removed_exactly_zero_mod_2_once": removed_zero_mod_two_once,
            "uncovered_equals_even_residues": uncovered_equals_even_residues,
        },
        "conclusions": {
            "p_ge_3_baseline_is_valid": baseline_valid,
            "satisfies_problem_273_p_ge_5_requirement": (
                baseline_valid and all_successors_at_least_5
            ),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(canonical_json(report))
    output_hash = sha256_file(output_path)

    hashes_path.parent.mkdir(parents=True, exist_ok=True)
    hash_lines = [
        f"{report['certificate_sha256']}  {relative_hash_name(certificate_path, hashes_path)}",
        f"{output_hash}  {relative_hash_name(output_path, hashes_path)}",
    ]
    hashes_path.write_text("\n".join(hash_lines) + "\n", encoding="utf-8", newline="\n")

    print(f"certificate={certificate_path}")
    print(f"certificate_sha256={report['certificate_sha256']}")
    print(f"output={output_path}")
    print(f"output_sha256={output_hash}")
    print(f"congruence_count={len(congruences)}")
    print(f"true_lcm={period}")
    print(f"full_uncovered_count={full['uncovered_residue_count']}")
    print(f"full_multiplicity_histogram={full['multiplicity_histogram']}")
    print(
        "without_modulus_2_uncovered_count="
        f"{reduced['uncovered_residue_count']}"
    )
    print(
        "without_modulus_2_uncovered_equals_evens="
        f"{uncovered_equals_even_residues}"
    )
    print(f"p_ge_3_baseline_is_valid={baseline_valid}")
    print(
        "satisfies_problem_273_p_ge_5_requirement="
        f"{report['conclusions']['satisfies_problem_273_p_ge_5_requirement']}"
    )
    return baseline_valid


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--hashes", type=Path, required=True)
    args = parser.parse_args()
    try:
        valid = run(args.certificate, args.output, args.hashes)
    except VerificationError as exc:
        print(f"verification error: {exc}", file=sys.stderr)
        return 2
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
