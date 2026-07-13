"""Independent literal and carry audit for a stored Bose-Chowla sample."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path


def pair_sums(values: tuple[int, ...]) -> list[int]:
    return [a + b for a, b in combinations_with_replacement(values, 2)]


def positive_differences(values: tuple[int, ...]) -> list[int]:
    return [
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    ]


def triple_sums(values: tuple[int, ...]) -> set[int]:
    return {
        a + b + c
        for a, b, c in combinations_with_replacement(values, 3)
    }


def load_record(path: Path) -> dict[str, object]:
    lines = [line for line in path.read_text(encoding="ascii").splitlines() if line]
    if len(lines) != 1:
        raise AssertionError(f"expected one JSON record, found {len(lines)}")
    return json.loads(lines[0])


def verify(record: dict[str, object]) -> dict[str, object]:
    candidate = record["best_candidate"]
    modulus = int(record["modulus"])
    size = int(candidate["size"])
    center = int(candidate["candidate_center"])
    f = tuple(int(x) for x in candidate["points"])
    width = f[-1]

    if f[0] != 0 or len(f) != size or len(set(f)) != size:
        raise AssertionError("malformed reflected ruler")
    if not 2 * width < center < 3 * width:
        raise AssertionError("sample is outside the nontrivial reflected range")

    sums = pair_sums(f)
    diffs = positive_differences(f)
    if len(sums) != size * (size + 1) // 2 or len(sums) != len(set(sums)):
        raise AssertionError("literal diagonal-inclusive Sidon sum failure")
    if len(diffs) != size * (size - 1) // 2 or len(diffs) != len(set(diffs)):
        raise AssertionError("literal positive-difference failure")

    modular_sums = [s % modulus for s in sums]
    modular_diffs = [d % modulus for d in diffs]
    if len(modular_sums) != len(set(modular_sums)):
        raise AssertionError("modular diagonal-inclusive Sidon sum failure")
    if len(modular_diffs) != len(set(modular_diffs)):
        raise AssertionError("modular positive-difference failure")

    sum_set = set(sums)
    diff_set = set(diffs)
    literal_representations = sum(
        1 for d in diff_set if center - d in sum_set
    )
    if literal_representations:
        raise AssertionError("stored center is not a literal hole")

    layer_counts: Counter[int] = Counter()
    modular_representation_count = 0
    target_residue = center % modulus
    for s in sum_set:
        for d in diff_set:
            total = s + d
            if total % modulus == target_residue:
                modular_representation_count += 1
                layer_counts[(total - center) // modulus] += 1

    lower_bound = size * size - modulus
    if modular_representation_count < lower_bound:
        raise AssertionError("modular intersection bound failed")
    if layer_counts.get(0, 0):
        raise AssertionError("literal zero carry appeared")

    e = tuple(sorted(center - 2 * x for x in f))
    e_sums = pair_sums(e)
    e_triples = triple_sums(e)
    if e[0] <= 0 or len({x % 2 for x in e}) != 1:
        raise AssertionError("positivity or same-parity failure")
    if len(e_sums) != len(set(e_sums)):
        raise AssertionError("E is not Sidon with diagonals")
    if set(e) & e_triples:
        raise AssertionError("E meets 3E with repeated summands allowed")

    z = tuple(sorted(width - x for x in f))
    overlap = 3 * width - center
    low_three_z = {
        a + b + c
        for a, b, c in combinations_with_replacement(z, 3)
        if a + b + c <= overlap
    }
    low_reflected_hits = [x for x in f if overlap - x in low_three_z]
    if low_reflected_hits:
        raise AssertionError("reflected low-hole equivalence failed")

    reflected = tuple(sorted(set(f) | {center - x for x in f}))
    reflected_counts = Counter(pair_sums(reflected))
    repeated = sorted((s, count) for s, count in reflected_counts.items() if count > 1)
    if repeated != [(center, size)]:
        raise AssertionError("full reflected census failed")

    return {
        "parameter": int(record["parameter"]),
        "modulus": modulus,
        "size": size,
        "span": width,
        "center": center,
        "center_over_p2": f"{center}/{size * size}",
        "center_below_3p2_by": 3 * size * size - center,
        "E_min": e[0],
        "E_max": e[-1],
        "E_parity": e[0] % 2,
        "unordered_pair_sums_including_diagonals": len(e_sums),
        "repeated_sums_in_full_reflection": repeated,
        "reflected_overlap_K": overlap,
        "low_reflected_hits": low_reflected_hits,
        "modular_positive_representations": modular_representation_count,
        "modular_intersection_lower_bound": lower_bound,
        "carry_layers_relative_to_center": dict(sorted(layer_counts.items())),
        "literal_zero_carry_representations": layer_counts.get(0, 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("problems/864/compute/p37/bose_q128_sample.jsonl"),
    )
    args = parser.parse_args()
    print(json.dumps(verify(load_record(args.input)), sort_keys=True))


if __name__ == "__main__":
    main()
