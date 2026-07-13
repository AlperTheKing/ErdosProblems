"""Exact audit for P51's equal-three-sum partition constraint.

For a Sidon ruler Z and a fixed triple sum x, distinct unordered triple
representations have disjoint supports.  The audit separates representations
of type 111 or 3 (the balanced part) from type 21 (the double part), checks
the exact barycenter identity, and computes the resulting integer subset-sum
capacity.

All arithmetic and all searches are literal integer computations.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations, combinations_with_replacement
from pathlib import Path


HERE = Path(__file__).resolve().parent
P864 = HERE.parents[1]
P37_RESULTS = P864 / "compute" / "p37" / "audit_results.json"
BOSE_Q128 = P864 / "compute" / "p37" / "bose_q128_sample.jsonl"


def unordered_pair_sums(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def positive_differences(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )


def is_sidon(values: tuple[int, ...]) -> bool:
    sums = unordered_pair_sums(values)
    return len(sums) == len(set(sums))


def is_valid_pair(values: tuple[int, ...], gap: int) -> bool:
    sums = set(unordered_pair_sums(values))
    differences = set(positive_differences(values))
    return differences.isdisjoint(gap + value for value in sums)


def triple_classes(
    values: tuple[int, ...], cutoff: int
) -> dict[int, list[tuple[int, int, int]]]:
    low = tuple(value for value in values if value <= cutoff)
    classes: dict[int, list[tuple[int, int, int]]] = {}
    for triple in combinations_with_replacement(low, 3):
        total = sum(triple)
        if total <= cutoff:
            classes.setdefault(total, []).append(triple)
    return classes


def double_orientation(triple: tuple[int, int, int]) -> tuple[int, int]:
    a, b, c = triple
    if a == b < c:
        return a, c
    if a < b == c:
        return b, a
    raise AssertionError((triple, "not type 21"))


def class_profile(
    total: int, triples: list[tuple[int, int, int]]
) -> dict[str, object]:
    supports = [set(triple) for triple in triples]
    for i in range(len(supports)):
        for j in range(i):
            if not supports[i].isdisjoint(supports[j]):
                raise AssertionError((total, triples, "supports overlap"))

    balanced_support: set[int] = set()
    full_support: set[int] = set()
    correction = 0
    distinct = 0
    doubles = 0
    all_equal = 0
    for triple, support in zip(triples, supports, strict=True):
        full_support.update(support)
        support_size = len(support)
        if support_size == 3:
            distinct += 1
            balanced_support.update(support)
        elif support_size == 2:
            doubles += 1
            repeated, singleton = double_orientation(triple)
            correction += repeated - singleton
        elif support_size == 1:
            all_equal += 1
            balanced_support.update(support)
        else:
            raise AssertionError((total, triple, support_size))

    support_size = len(full_support)
    balanced_size = len(balanced_support)
    if support_size != balanced_size + 2 * doubles:
        raise AssertionError((total, triples, "support decomposition"))
    if total * support_size - 3 * sum(full_support) != correction:
        raise AssertionError((total, triples, "barycenter-defect identity"))
    if 3 * sum(balanced_support) != total * balanced_size:
        raise AssertionError((total, triples, "balanced barycenter"))
    if all_equal not in (0, 1):
        raise AssertionError((total, triples, "multiple all-equal triples"))
    if balanced_size % 3 != all_equal:
        raise AssertionError((total, triples, "balanced residue"))
    if all_equal:
        if total % 3 or total // 3 not in balanced_support:
            raise AssertionError((total, triples, "missing central singleton"))

    return {
        "sum": total,
        "representations": len(triples),
        "support_size": support_size,
        "balanced_support_size": balanced_size,
        "distinct": distinct,
        "doubles": doubles,
        "all_equal": all_equal,
        "correction": correction,
        "triples": [list(triple) for triple in triples],
    }


def barycentric_capacities(
    values: tuple[int, ...], cutoff: int, targets: set[int]
) -> tuple[dict[int, int], dict[int, tuple[int, ...]], int]:
    """Return the exact relaxed capacity beta_Z(x) on the requested targets.

    A candidate U must lie in Z intersect [0,x], have exact mean x/3, and
    have the size/central-singleton residue forced by unions of type 111 and
    type 3 representations.  It need not itself admit a triple partition, so
    this remains a relaxation and hence an upper capacity.
    """

    low = tuple(value for value in values if value <= cutoff)
    index = {value: i for i, value in enumerate(low)}
    capacities: dict[int, int] = {}
    witnesses: dict[int, tuple[int, ...]] = {}
    masks_checked = (1 << len(low)) - 1

    previous = 0
    subset_sum = 0
    subset_size = 0
    for step in range(1, 1 << len(low)):
        mask = step ^ (step >> 1)
        changed = mask ^ previous
        changed_index = (changed & -changed).bit_length() - 1
        if mask & changed:
            subset_sum += low[changed_index]
            subset_size += 1
        else:
            subset_sum -= low[changed_index]
            subset_size -= 1
        previous = mask

        numerator = 3 * subset_sum
        if numerator % subset_size:
            continue
        total = numerator // subset_size
        if total not in targets:
            continue
        if low[mask.bit_length() - 1] > total:
            continue

        center_index = index.get(total // 3) if total % 3 == 0 else None
        if center_index is None:
            residue_ok = subset_size % 3 == 0
        else:
            residue_ok = subset_size % 3 == 1 and bool(
                mask & (1 << center_index)
            )
        if not residue_ok:
            continue

        if subset_size > capacities.get(total, 0):
            capacities[total] = subset_size
            witnesses[total] = tuple(
                low[i] for i in range(len(low)) if mask & (1 << i)
            )

    return capacities, witnesses, masks_checked


def audit_case(
    name: str, values: tuple[int, ...], gap: int, include_examples: int = 5
) -> dict[str, object]:
    if not values or values[0] != 0 or tuple(sorted(values)) != values:
        raise AssertionError((name, values, "not endpoint normalized"))
    if gap < 1:
        raise AssertionError((name, gap, "gap must be positive"))
    if not is_sidon(values):
        raise AssertionError((name, values, "not Sidon"))
    if not is_valid_pair(values, gap):
        raise AssertionError((name, values, gap, "not valid"))

    width = values[-1]
    cutoff = width - gap
    classes = triple_classes(values, cutoff)
    profiles = {
        total: class_profile(total, triples)
        for total, triples in sorted(classes.items())
    }
    capacities, capacity_witnesses, masks_checked = barycentric_capacities(
        values, cutoff, set(classes)
    )

    pair_sums = unordered_pair_sums(values)
    incidence = sum(
        1 for value in values for pair_sum in pair_sums if value + pair_sum <= cutoff
    )
    profiled_incidence = sum(
        int(profile["support_size"]) for profile in profiles.values()
    )
    if incidence != profiled_incidence:
        raise AssertionError((name, incidence, profiled_incidence, "incidence"))

    double_count = sum(
        1
        for repeated in values
        for singleton in values
        if repeated != singleton and 2 * repeated + singleton <= cutoff
    )
    profiled_doubles = sum(int(profile["doubles"]) for profile in profiles.values())
    if double_count != profiled_doubles:
        raise AssertionError((name, double_count, profiled_doubles, "doubles"))

    for total, profile in profiles.items():
        balanced_size = int(profile["balanced_support_size"])
        if balanced_size > capacities.get(total, 0):
            raise AssertionError(
                (name, total, balanced_size, capacities.get(total, 0), "capacity")
            )

    balanced_capacity = sum(capacities.get(total, 0) for total in classes)
    integer_capacity = balanced_capacity + 2 * double_count
    if incidence > integer_capacity:
        raise AssertionError((name, incidence, integer_capacity, "global capacity"))

    old_capacity = max(0, len(values) - 1) * len(classes)
    collisions = sorted(
        (profile for profile in profiles.values() if int(profile["representations"]) > 1),
        key=lambda profile: (
            int(profile["representations"]),
            int(profile["support_size"]),
            -int(profile["sum"]),
        ),
        reverse=True,
    )
    beta_max = max(capacities.values(), default=0)
    beta_max_targets = sorted(
        total for total, capacity in capacities.items() if capacity == beta_max
    )
    beta_examples = [
        {"sum": total, "capacity": beta_max, "subset": capacity_witnesses[total]}
        for total in beta_max_targets[:include_examples]
    ]

    return {
        "name": name,
        "p": len(values),
        "W": width,
        "G": gap,
        "K": cutoff,
        "M": gap + 2 * width,
        "Z": values,
        "low_marks": sum(value <= cutoff for value in values),
        "represented_targets": len(classes),
        "triple_representations": sum(len(triples) for triples in classes.values()),
        "collision_targets": len(collisions),
        "all_distinct_collision_targets": sum(
            int(profile["distinct"]) >= 2 for profile in profiles.values()
        ),
        "maximum_representations": max(
            (int(profile["representations"]) for profile in profiles.values()), default=0
        ),
        "maximum_support_size": max(
            (int(profile["support_size"]) for profile in profiles.values()), default=0
        ),
        "actual_incidence": incidence,
        "balanced_actual_incidence": incidence - 2 * double_count,
        "double_representations": double_count,
        "double_incidence": 2 * double_count,
        "old_p_minus_1_capacity": old_capacity,
        "barycentric_balanced_capacity": balanced_capacity,
        "barycentric_integer_capacity": integer_capacity,
        "strict_capacity_reduction": old_capacity - integer_capacity,
        "beta_maximum": beta_max,
        "beta_maximum_examples": beta_examples,
        "subset_masks_checked": masks_checked,
        "collision_examples": collisions[:include_examples],
    }


def load_stored_witnesses() -> tuple[list[dict[str, object]], dict[str, object]]:
    report = json.loads(P37_RESULTS.read_text(encoding="ascii"))
    stored: list[dict[str, object]] = []
    for row in report["finite_witnesses"]:
        e = tuple(int(value) for value in row["E"])
        gap = e[0]
        values = tuple((value - gap) // 2 for value in e)
        stored.append(audit_case(f"stored_q{len(e)}", values, gap))

    sharp = report["degree_sharpness"]
    e = tuple(int(value) for value in sharp["E"])
    gap = e[0]
    values = tuple((value - gap) // 2 for value in e)
    degree_sharpness = audit_case("stored_degree_sharpness", values, gap)
    return stored, degree_sharpness


def load_bose_q128() -> dict[str, object]:
    record = json.loads(BOSE_Q128.read_text(encoding="ascii").splitlines()[0])
    candidate = record["best_candidate"]
    reflected = tuple(int(value) for value in candidate["points"])
    width = int(candidate["span"])
    center = int(candidate["candidate_center"])
    gap = center - 2 * width
    values = tuple(sorted(width - value for value in reflected))
    result = audit_case("stored_bose_q128", values, gap)
    if result["p"] != 128 or result["M"] != 42705:
        raise AssertionError((result["p"], result["M"], "q128 identity"))
    return result


def exhaustive_small(max_width: int) -> dict[str, object]:
    endpoint_sidon_rulers = 0
    valid_pairs = 0
    represented_targets = 0
    triple_representations = 0
    collision_targets = 0
    all_distinct_collision_targets = 0
    actual_incidence = 0
    old_capacity = 0
    integer_capacity = 0
    subset_masks_checked = 0
    strict_cases = 0
    maximum_representations = 0
    maximum_support_size = 0
    first_collision: dict[str, object] | None = None

    for width in range(1, max_width + 1):
        for count in range(width):
            for middle in combinations(range(1, width), count):
                values = (0, *middle, width)
                if not is_sidon(values):
                    continue
                endpoint_sidon_rulers += 1
                for gap in range(1, width):
                    if not is_valid_pair(values, gap):
                        continue
                    valid_pairs += 1
                    result = audit_case(f"W{width}_G{gap}", values, gap, 1)
                    represented_targets += int(result["represented_targets"])
                    triple_representations += int(result["triple_representations"])
                    collision_targets += int(result["collision_targets"])
                    all_distinct_collision_targets += int(
                        result["all_distinct_collision_targets"]
                    )
                    actual_incidence += int(result["actual_incidence"])
                    old_capacity += int(result["old_p_minus_1_capacity"])
                    integer_capacity += int(result["barycentric_integer_capacity"])
                    subset_masks_checked += int(result["subset_masks_checked"])
                    strict_cases += int(result["strict_capacity_reduction"] > 0)
                    maximum_representations = max(
                        maximum_representations,
                        int(result["maximum_representations"]),
                    )
                    maximum_support_size = max(
                        maximum_support_size, int(result["maximum_support_size"])
                    )
                    if first_collision is None and result["collision_examples"]:
                        first_collision = {
                            "Z": values,
                            "G": gap,
                            "profile": result["collision_examples"][0],
                        }

    if max_width == 18:
        expected = (1340, 6783, 13747, 89, 0, 2, 4)
        observed = (
            endpoint_sidon_rulers,
            valid_pairs,
            represented_targets,
            collision_targets,
            all_distinct_collision_targets,
            maximum_representations,
            maximum_support_size,
        )
        if observed != expected:
            raise AssertionError((observed, expected, "width-18 census"))

    return {
        "max_width": max_width,
        "endpoint_sidon_rulers": endpoint_sidon_rulers,
        "valid_overlap_pairs": valid_pairs,
        "represented_targets": represented_targets,
        "triple_representations": triple_representations,
        "collision_targets": collision_targets,
        "all_distinct_collision_targets": all_distinct_collision_targets,
        "maximum_representations": maximum_representations,
        "maximum_support_size": maximum_support_size,
        "actual_incidence": actual_incidence,
        "old_p_minus_1_capacity": old_capacity,
        "barycentric_integer_capacity": integer_capacity,
        "strict_capacity_reduction_cases": strict_cases,
        "subset_masks_checked": subset_masks_checked,
        "first_collision": first_collision,
    }


def equal_distinct_partition(
    six_values: tuple[int, ...]
) -> tuple[tuple[int, int, int], tuple[int, int, int], int] | None:
    total = sum(six_values)
    if total % 2:
        return None
    half = total // 2
    all_indices = set(range(6))
    for left_indices in combinations(range(6), 3):
        if 0 not in left_indices:
            continue
        if sum(six_values[i] for i in left_indices) != half:
            continue
        right_indices = tuple(sorted(all_indices.difference(left_indices)))
        left = tuple(six_values[i] for i in left_indices)
        right = tuple(six_values[i] for i in right_indices)
        return left, right, half
    return None


def smallest_all_distinct_falsifier(max_width: int) -> dict[str, object]:
    six_point_candidates = 0
    sidon_six_point_prefixes = 0
    balanced_sidon_prefixes = 0
    sidon_seven_point_rulers = 0

    for width in range(7, max_width + 1):
        for middle in combinations(range(1, width), 5):
            six = (0, *middle)
            six_point_candidates += 1
            if not is_sidon(six):
                continue
            sidon_six_point_prefixes += 1
            partition = equal_distinct_partition(six)
            if partition is None:
                continue
            balanced_sidon_prefixes += 1
            values = (*six, width)
            if not is_sidon(values):
                continue
            sidon_seven_point_rulers += 1
            left, right, total = partition
            if total >= width:
                continue
            for gap in range(1, width - total + 1):
                if not is_valid_pair(values, gap):
                    continue

                audited = audit_case("smallest_all_distinct_falsifier", values, gap)
                profile = next(
                    row
                    for row in audited["collision_examples"]
                    if int(row["sum"]) == total and int(row["distinct"]) >= 2
                )
                e = tuple(gap + 2 * value for value in values)
                e_triples = {
                    sum(triple) for triple in combinations_with_replacement(e, 3)
                }
                certificate = {
                    "claim_falsified": (
                        "every low equal-three-sum collision in a valid pair "
                        "contains a repeated summand"
                    ),
                    "minimality_order": ["p", "W", "Z lexicographic", "G"],
                    "minimality_reason_p": (
                        "two all-distinct representations use six disjoint marks, "
                        "and W cannot occur in a sum x<W, so p is at least 7"
                    ),
                    "exhaustive_search": {
                        "p": 7,
                        "max_width": width,
                        "six_point_candidates": six_point_candidates,
                        "sidon_six_point_prefixes": sidon_six_point_prefixes,
                        "balanced_sidon_prefixes": balanced_sidon_prefixes,
                        "sidon_seven_point_rulers": sidon_seven_point_rulers,
                    },
                    "p": 7,
                    "Z": values,
                    "W": width,
                    "G": gap,
                    "K": width - gap,
                    "M": gap + 2 * width,
                    "E": e,
                    "sum": total,
                    "partitions": [left, right],
                    "profile": profile,
                    "pair_sum_count": len(set(unordered_pair_sums(values))),
                    "positive_difference_count": len(set(positive_differences(values))),
                    "cross_intersection": sorted(
                        set(positive_differences(values)).intersection(
                            gap + value for value in unordered_pair_sums(values)
                        )
                    ),
                    "E_intersection_3E": sorted(set(e).intersection(e_triples)),
                }
                return certificate

    raise AssertionError((max_width, "no all-distinct falsifier found"))


def audit_all(max_width: int, falsifier_max_width: int) -> dict[str, object]:
    stored, degree_sharpness = load_stored_witnesses()
    bose = load_bose_q128()
    small = exhaustive_small(max_width)
    falsifier = smallest_all_distinct_falsifier(falsifier_max_width)

    if falsifier_max_width == 44:
        expected = ((0, 1, 5, 11, 13, 20, 44), 16, 25)
        observed = (tuple(falsifier["Z"]), falsifier["G"], falsifier["sum"])
        if observed != expected:
            raise AssertionError((observed, expected, "minimal falsifier"))

    return {
        "status": "PASS",
        "arithmetic": "integers only",
        "lemma": "P51.1 integer barycenter-defect and capacity lemma",
        "parameters": {
            "small_max_width": max_width,
            "falsifier_max_width": falsifier_max_width,
        },
        "stored_finite_witnesses": stored,
        "stored_degree_sharpness": degree_sharpness,
        "stored_bose_q128": bose,
        "exhaustive_small": small,
        "smallest_all_distinct_falsifier": falsifier,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    parser.add_argument("--falsifier-max-width", type=int, default=44)
    parser.add_argument("--output", type=Path, default=HERE / "audit_results.json")
    parser.add_argument(
        "--falsifier-output",
        type=Path,
        default=HERE / "smallest_all_distinct_falsifier.json",
    )
    args = parser.parse_args()
    if args.max_width < 1:
        parser.error("--max-width must be positive")
    if args.falsifier_max_width < 7:
        parser.error("--falsifier-max-width must be at least 7")

    report = audit_all(args.max_width, args.falsifier_max_width)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    args.output.write_text(encoded + "\n", encoding="ascii")
    falsifier_encoded = json.dumps(
        report["smallest_all_distinct_falsifier"], indent=2, sort_keys=True
    )
    args.falsifier_output.write_text(falsifier_encoded + "\n", encoding="ascii")
    print(encoded)


if __name__ == "__main__":
    main()
