"""Independent carry audit for the P26 algebraic reflected-set lane.

For a normalized lift B in [0,n), this script compares the literal set

    S(B) + Delta+(B)

against the two carry formulas for centers n+t and 2n+t.  It also rebuilds
every cyclic cut in the stored natural Singer scans.  Only Python's standard
library is used; no P12 checking code is imported.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


def unordered_sums(values: Sequence[int]) -> list[int]:
    return [
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    ]


def positive_differences(values: Sequence[int]) -> set[int]:
    return {
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    }


def bits(values: Iterable[int]) -> int:
    out = 0
    for value in values:
        out |= 1 << value
    return out


def first_zero(bitset: int, limit: int) -> int | None:
    mask = (1 << (limit + 1)) - 1
    missing = (~bitset) & mask
    if not missing:
        return None
    low = missing & -missing
    return low.bit_length() - 1


def literal_forbidden_bits(values: Sequence[int]) -> tuple[int, list[int], set[int]]:
    sums = unordered_sums(values)
    differences = positive_differences(values)
    sum_bits = bits(sums)
    forbidden = 0
    for difference in differences:
        forbidden |= sum_bits << difference
    return forbidden, sums, differences


def carry_layer_bits(
    values: Sequence[int], modulus: int, differences: set[int]
) -> tuple[int, int]:
    nonwrapping: set[int] = set()
    wrapping: set[int] = set()
    for total in unordered_sums(values):
        if total < modulus:
            nonwrapping.add(total)
        else:
            wrapping.add(total - modulus)

    difference_bits = bits(differences)
    mask = (1 << modulus) - 1

    layer_one = 0
    for residue in nonwrapping:
        layer_one |= difference_bits >> (modulus - residue)
    for residue in wrapping:
        layer_one |= (difference_bits << residue) & mask

    layer_two = 0
    for residue in wrapping:
        layer_two |= difference_bits >> (modulus - residue)
    return layer_one & mask, layer_two & mask


def verify_reflected(values: Sequence[int], center: int) -> None:
    reflected = sorted(set(values) | {center - value for value in values})
    if len(reflected) != 2 * len(values):
        raise AssertionError("reflected blocks overlap")
    counts = Counter(unordered_sums(reflected))
    repeated = sorted((total, count) for total, count in counts.items() if count > 1)
    if repeated != [(center, len(values))]:
        raise AssertionError(("bad reflected repeated sums", repeated))


def audit_candidate(record: dict[str, object]) -> dict[str, object]:
    best = record.get("best_candidate")
    if not isinstance(best, dict):
        raise AssertionError("candidate record has no best_candidate")
    values = [int(value) for value in best["points"]]
    modulus = int(record["modulus"])
    center = int(best["candidate_center"])
    p = len(values)
    if values != sorted(set(values)) or values[0] != 0 or values[-1] >= modulus:
        raise AssertionError("candidate is not a normalized cyclic lift")
    if center <= 2 * values[-1] or center >= 3 * p * p:
        raise AssertionError("candidate misses the reflected construction window")

    forbidden, sums, differences = literal_forbidden_bits(values)
    expected_pairs = p * (p + 1) // 2
    if len(set(sums)) != expected_pairs:
        raise AssertionError("candidate is not literal Sidon")
    if len({total % modulus for total in sums}) != expected_pairs:
        raise AssertionError("candidate is not strongly modular Sidon")
    if (forbidden >> center) & 1:
        raise AssertionError("stored center is literally forbidden")

    layer_one, layer_two = carry_layer_bits(values, modulus, differences)
    mask = (1 << modulus) - 1
    direct_one = (forbidden >> modulus) & mask
    direct_two = (forbidden >> (2 * modulus)) & mask
    if layer_one != direct_one or layer_two != direct_two:
        raise AssertionError("carry formula disagrees with literal convolution")

    verify_reflected(values, center)
    quotient, residue = divmod(center, modulus)
    first_two = first_zero(layer_two, modulus - 1)
    if quotient == 2 and first_two != residue:
        raise AssertionError(("stored center is not first layer-two hole", first_two, residue))

    return {
        "family": record["family"],
        "parameter": int(record["parameter"]),
        "p": p,
        "modulus": modulus,
        "span": values[-1],
        "center": center,
        "center_layer": quotient,
        "center_residue": residue,
        "first_layer_two_hole": first_two,
        "first_layer_two_hole_over_modulus": str(Fraction(first_two, modulus)),
        "has_layer_two_hole_through_one_half": first_zero(layer_two, modulus // 2)
        is not None,
        "has_layer_two_hole_through_two_thirds": first_zero(
            layer_two, 2 * modulus // 3
        )
        is not None,
        "carry_layers_match_literal_all_residues": True,
        "reflected_check": True,
    }


def cyclic_lifts(values: Sequence[int], modulus: int):
    for base in sorted(values):
        yield base, sorted((value - base) % modulus for value in values)


def singer_layer_two(values: Sequence[int], modulus: int) -> int:
    differences = positive_differences(values)
    if len(differences) != (modulus - 1) // 2:
        raise AssertionError("Singer lift does not have half of the nonzero residues")
    for difference in differences:
        if modulus - difference in differences:
            raise AssertionError("positive differences do not select one sign")
    return carry_layer_bits(values, modulus, differences)[1]


def audit_natural(record: dict[str, object]) -> dict[str, object]:
    best = record.get("best_below_3p2")
    if not isinstance(best, dict):
        raise AssertionError("natural record has no reconstruction witness")
    modulus = int(record["modulus"])
    points = [int(value) for value in best["points"]]
    witness_base = int(best["cut_base"])
    source = sorted((value + witness_base) % modulus for value in points)
    rebuilt = sorted((value - witness_base) % modulus for value in source)
    if rebuilt != points:
        raise AssertionError("failed to reconstruct natural Singer residues")

    half_successes = 0
    two_thirds_successes = 0
    best_hole: tuple[int, int] | None = None
    for base, lift in cyclic_lifts(source, modulus):
        layer_two = singer_layer_two(lift, modulus)
        first = first_zero(layer_two, modulus - 1)
        if first is None:
            raise AssertionError("top carry layer has no hole")
        item = (first, base)
        if best_hole is None or item < best_hole:
            best_hole = item
        if first_zero(layer_two, modulus // 2) is not None:
            half_successes += 1
        if first_zero(layer_two, 2 * modulus // 3) is not None:
            two_thirds_successes += 1

    if best_hole is None:
        raise AssertionError("no cyclic cuts were audited")
    stored_half = int(record["successful_cuts_in_2v_to_5v_over_2"])
    if half_successes != stored_half:
        raise AssertionError(("half-window count mismatch", half_successes, stored_half))

    first, base = best_hole
    return {
        "parameter": int(record["parameter"]),
        "p": len(source),
        "modulus": modulus,
        "cuts": len(source),
        "cuts_with_hole_through_one_half": half_successes,
        "cuts_with_hole_through_two_thirds": two_thirds_successes,
        "best_layer_two_hole": first,
        "best_layer_two_hole_over_modulus": str(Fraction(first, modulus)),
        "best_cut_base": base,
        "stored_half_window_count_matches": True,
    }


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="ascii").splitlines()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate-manifest",
        type=Path,
        default=Path("problems/864/compute/p12/verification_all_recheck.json"),
    )
    parser.add_argument(
        "--natural-jsonl",
        type=Path,
        nargs="+",
        default=[
            Path("problems/864/compute/p12/singer_natural_large.jsonl"),
            Path("problems/864/compute/p12/singer_natural_xlarge.jsonl"),
        ],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.candidate_manifest.read_text(encoding="ascii"))
    candidate_records: list[dict[str, object]] = []
    for item in manifest["inputs"]:
        candidate_records.extend(read_jsonl(Path(item["path"])))
    candidate_audits = [audit_candidate(record) for record in candidate_records]

    natural_records: list[dict[str, object]] = []
    for path in args.natural_jsonl:
        natural_records.extend(read_jsonl(path))
    natural_audits = [audit_natural(record) for record in natural_records]

    worst_natural = max(
        natural_audits,
        key=lambda row: Fraction(str(row["best_layer_two_hole_over_modulus"])),
    )
    q128 = next((row for row in natural_audits if row["parameter"] == 128), None)
    output = {
        "candidate_records_audited": len(candidate_audits),
        "candidate_all_carry_checks_passed": all(
            row["carry_layers_match_literal_all_residues"]
            and row["reflected_check"]
            for row in candidate_audits
        ),
        "candidate_all_have_hole_through_two_thirds": all(
            row["has_layer_two_hole_through_two_thirds"]
            for row in candidate_audits
        ),
        "natural_records_audited": len(natural_audits),
        "natural_all_have_some_cut_through_two_thirds": all(
            int(row["cuts_with_hole_through_two_thirds"]) > 0
            for row in natural_audits
        ),
        "worst_natural_best_hole": worst_natural,
        "q128_half_window_falsifier": q128,
        "candidate_audits": candidate_audits,
        "natural_audits": natural_audits,
    }
    rendered = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="ascii")
    print(rendered, end="")


if __name__ == "__main__":
    main()
