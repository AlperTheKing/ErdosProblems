#!/usr/bin/env python3
"""Exact census for the reflected-core/residual decomposition in Problem 864.

The search enumerates endpoint-normalized subsets A of [0, N-1].  For every
admissible set with a repeated sum and a nonempty residual, it verifies the
sum/difference label accounting, the virtual-completion criterion, and the
collision-repair construction.  All comparisons use integer arithmetic.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable


def pair_sums(values: Iterable[int]) -> Counter[int]:
    ordered = tuple(sorted(values))
    counts: Counter[int] = Counter()
    for right_index, right in enumerate(ordered):
        for left in ordered[: right_index + 1]:
            counts[left + right] += 1
    return counts


def positive_difference_counts(values: Iterable[int]) -> Counter[int]:
    ordered = tuple(sorted(values))
    counts: Counter[int] = Counter()
    for right_index, right in enumerate(ordered):
        for left in ordered[:right_index]:
            counts[right - left] += 1
    return counts


def is_admissible(values: Iterable[int]) -> bool:
    return sum(count >= 2 for count in pair_sums(values).values()) <= 1


def smaller_record(candidate: dict[str, Any], current: dict[str, Any] | None) -> bool:
    if current is None:
        return True
    candidate_key = (candidate["N"], candidate["k"], candidate["A"])
    current_key = (current["N"], current["k"], current["A"])
    return candidate_key < current_key


def build_record(a: tuple[int, ...], n: int) -> dict[str, Any] | None:
    sums = pair_sums(a)
    repeated = [label for label, count in sums.items() if count >= 2]
    if len(repeated) > 1:
        raise AssertionError("nonadmissible set reached record builder")
    if not repeated:
        return None

    sigma = repeated[0]
    a_set = set(a)
    core = tuple(x for x in a if sigma - x in a_set)
    residual = tuple(x for x in a if sigma - x not in a_set)
    if not residual:
        return None

    delta = int(sigma % 2 == 0 and sigma // 2 in a_set)
    if (len(core) - delta) % 2:
        raise AssertionError("core parity failed")
    p = (len(core) - delta) // 2
    c = len(core)
    u = len(residual)
    k = len(a)
    if sums[sigma] != p + delta or p + delta < 2:
        raise AssertionError("exceptional fibre/core identity failed")

    core_set = set(core)
    residual_set = set(residual)

    core_sum_pairs: list[tuple[int, tuple[int, int]]] = []
    residual_sum_pairs: list[tuple[int, tuple[int, int]]] = []
    for right_index, right in enumerate(a):
        for left in a[: right_index + 1]:
            item = (left + right, (left, right))
            if left in residual_set or right in residual_set:
                residual_sum_pairs.append(item)
            else:
                core_sum_pairs.append(item)

    residual_sum_labels = [label for label, _ in residual_sum_pairs]
    core_sum_labels = {label for label, _ in core_sum_pairs}
    expected_residual_sum_count = c * u + u * (u + 1) // 2
    if len(residual_sum_pairs) != expected_residual_sum_count:
        raise AssertionError("residual sum-pair count failed")
    if len(set(residual_sum_labels)) != expected_residual_sum_count:
        raise AssertionError("a residual sum label was not unique")
    if core_sum_labels.intersection(residual_sum_labels):
        raise AssertionError("core and residual sum labels intersect")
    if len(core_sum_labels) != 2 * p * (p + delta) + 1:
        raise AssertionError("core sum-support count failed")

    core_difference_pairs: list[tuple[int, tuple[int, int]]] = []
    residual_difference_pairs: list[tuple[int, tuple[int, int]]] = []
    for right_index, right in enumerate(a):
        for left in a[:right_index]:
            item = (right - left, (left, right))
            if left in residual_set or right in residual_set:
                residual_difference_pairs.append(item)
            else:
                core_difference_pairs.append(item)

    residual_difference_labels = [
        label for label, _ in residual_difference_pairs
    ]
    core_difference_labels = {label for label, _ in core_difference_pairs}
    expected_residual_difference_count = c * u + u * (u - 1) // 2
    if len(residual_difference_pairs) != expected_residual_difference_count:
        raise AssertionError("residual difference-pair count failed")
    if len(set(residual_difference_labels)) != expected_residual_difference_count:
        raise AssertionError("a residual difference label was not unique")
    if core_difference_labels.intersection(residual_difference_labels):
        raise AssertionError("core and residual difference labels intersect")
    if len(core_difference_labels) != p * (p + delta):
        raise AssertionError("core difference-support count failed")

    all_difference_labels = core_difference_labels | set(residual_difference_labels)
    if all_difference_labels != set(positive_difference_counts(a)):
        raise AssertionError("difference partition failed")
    a_difference_pairs: dict[int, list[tuple[int, int]]] = {}
    for right_index, right in enumerate(a):
        for left in a[:right_index]:
            a_difference_pairs.setdefault(right - left, []).append((left, right))

    # Cross sums fold exactly onto cross differences under reflection of the
    # core endpoint: r+x-sigma = r-(sigma-x).
    folded_cross_sums: list[int] = []
    cross_difference_labels: list[int] = []
    for r in residual:
        for x in core:
            folded_cross_sums.append(abs(r + x - sigma))
            cross_difference_labels.append(abs(r - x))
    if sorted(folded_cross_sums) != sorted(cross_difference_labels):
        raise AssertionError("cross-sum/cross-difference folding failed")
    if len(set(folded_cross_sums)) != c * u:
        raise AssertionError("folded cross sums were not injective")

    virtual_pairs: list[tuple[int, tuple[int, int]]] = []
    for right_index, right in enumerate(residual):
        for left_index, left in enumerate(residual[: right_index + 1]):
            label = abs(left + right - sigma)
            if label == 0:
                raise AssertionError("a residual pair summed to sigma")
            virtual_pairs.append((label, (left_index, right_index)))

    virtual_counts = Counter(label for label, _ in virtual_pairs)
    virtual_pair_count = u * (u + 1) // 2
    if len(virtual_pairs) != virtual_pair_count:
        raise AssertionError("virtual-pair count failed")

    reflected_residual = {sigma - r for r in residual}
    if reflected_residual.intersection(a_set):
        raise AssertionError("residual reflection met A")
    completion = tuple(sorted(a_set | reflected_residual))
    completion_differences = set(positive_difference_counts(completion))
    virtual_labels = set(virtual_counts)
    if completion_differences != all_difference_labels | virtual_labels:
        raise AssertionError("completion difference-orbit partition failed")

    collision_free = (
        len(virtual_labels) == virtual_pair_count
        and not virtual_labels.intersection(all_difference_labels)
    )
    completion_admissible = is_admissible(completion)
    if collision_free != completion_admissible:
        raise AssertionError("virtual-completion criterion failed")

    # The orbit excess beta is exactly the number of virtual pair instances
    # that must be discarded after retaining at most one new orbit per label.
    designated_pairs: list[tuple[int, int]] = []
    for label in sorted(virtual_counts):
        preimages = [pair for item_label, pair in virtual_pairs if item_label == label]
        if label in all_difference_labels:
            designated_pairs.extend(preimages)
        else:
            designated_pairs.extend(preimages[1:])
    beta = len(designated_pairs)
    orbit_total = (p + u) * (p + u + delta)
    orbit_deficit = orbit_total - len(completion_differences)
    if beta != orbit_deficit:
        raise AssertionError("completion orbit-deficit identity failed")
    if orbit_total != len(all_difference_labels) + virtual_pair_count:
        raise AssertionError("completion orbit count failed")

    deleted_indices = {pair[0] for pair in designated_pairs}
    if len(deleted_indices) > beta:
        raise AssertionError("repair hitting-set bound failed")
    kept_residual = tuple(
        value for index, value in enumerate(residual) if index not in deleted_indices
    )
    repaired = tuple(
        sorted(
            core_set
            | set(kept_residual)
            | {sigma - value for value in kept_residual}
        )
    )
    if not is_admissible(repaired):
        raise AssertionError("collision repair did not produce an admissible set")
    if any(sigma - x not in repaired for x in repaired):
        raise AssertionError("collision repair was not fully reflected")

    span = a[-1] - a[0]
    completion_span = completion[-1] - completion[0]
    reflection_shift = abs(sigma - a[0] - a[-1])
    if completion_span != span + reflection_shift:
        raise AssertionError("completion-span identity failed")

    new_virtual_labels = virtual_labels - all_difference_labels
    if len(completion_differences) != len(all_difference_labels) + len(
        new_virtual_labels
    ):
        raise AssertionError("new-label packing identity failed")

    virtual_collisions = []
    for label in sorted(virtual_counts):
        preimages = [pair for item_label, pair in virtual_pairs if item_label == label]
        if len(preimages) == 1 and label not in all_difference_labels:
            continue
        virtual_collisions.append(
            {
                "label": label,
                "virtual_residual_pairs": [
                    [residual[left_index], residual[right_index]]
                    for left_index, right_index in preimages
                ],
                "A_difference_pairs": [
                    list(pair) for pair in a_difference_pairs.get(label, [])
                ],
            }
        )
    completion_repeated_sums = [
        [label, count]
        for label, count in sorted(pair_sums(completion).items())
        if count >= 2
    ]

    return {
        "A": list(a),
        "N": n,
        "span": span,
        "k": k,
        "sigma": sigma,
        "exceptional_multiplicity": sums[sigma],
        "core": list(core),
        "residual": list(residual),
        "p": p,
        "delta": delta,
        "c": c,
        "u": u,
        "core_sum_support": len(core_sum_labels),
        "residual_sum_labels": expected_residual_sum_count,
        "core_difference_support": len(core_difference_labels),
        "residual_difference_labels": expected_residual_difference_count,
        "virtual_pair_count": virtual_pair_count,
        "virtual_distinct_labels": len(virtual_labels),
        "virtual_new_labels": len(new_virtual_labels),
        "virtual_collisions": virtual_collisions,
        "beta": beta,
        "collision_free_completion": collision_free,
        "completion": list(completion),
        "completion_repeated_sums": completion_repeated_sums,
        "completion_span": completion_span,
        "reflection_shift": reflection_shift,
        "same_span_completion": reflection_shift == 0,
        "repair_deleted_residual_count": len(deleted_indices),
        "repair_deleted_residual": [residual[index] for index in sorted(deleted_indices)],
        "repaired": list(repaired),
        "repaired_pair_count": p + len(kept_residual),
        "repaired_size": len(repaired),
        "orbit_total": orbit_total,
        "completion_difference_support": len(completion_differences),
    }


def search_n(n: int) -> dict[str, Any]:
    if n < 2:
        raise ValueError("N must be at least two")

    a = [0]
    sum_counts: dict[int, int] = {0: 1}
    admissible_count = 0
    repeated_residual_count = 0
    collision_free_count = 0
    same_span_count = 0
    same_span_blocked_count = 0
    first_blocked: dict[str, Any] | None = None
    first_same_span_blocked: dict[str, Any] | None = None
    largest_beta: dict[str, Any] | None = None

    def evaluate_leaf() -> None:
        nonlocal admissible_count, repeated_residual_count, collision_free_count
        nonlocal same_span_count, same_span_blocked_count, first_blocked
        nonlocal first_same_span_blocked, largest_beta

        admissible_count += 1
        record = build_record(tuple(a), n)
        if record is None:
            return
        repeated_residual_count += 1
        if record["collision_free_completion"]:
            collision_free_count += 1
        elif smaller_record(record, first_blocked):
            first_blocked = record
        if record["same_span_completion"]:
            same_span_count += 1
            if not record["collision_free_completion"]:
                same_span_blocked_count += 1
                if smaller_record(record, first_same_span_blocked):
                    first_same_span_blocked = record
        if largest_beta is None or record["beta"] > largest_beta["beta"]:
            largest_beta = record

    def try_add(x: int, repeated_labels: int, continuation: Callable[[int], None]) -> None:
        changed: list[tuple[int, int]] = []
        new_repeated = repeated_labels
        valid = True
        for old_point in (*a, x):
            label = x + old_point
            old_count = sum_counts.get(label, 0)
            sum_counts[label] = old_count + 1
            changed.append((label, old_count))
            if old_count == 1:
                new_repeated += 1
            if new_repeated > 1:
                valid = False
                break
        if valid:
            a.append(x)
            continuation(new_repeated)
            a.pop()
        for label, old_count in reversed(changed):
            if old_count:
                sum_counts[label] = old_count
            else:
                del sum_counts[label]

    def recurse(x: int, repeated_labels: int) -> None:
        if x == n - 1:
            try_add(x, repeated_labels, lambda _: evaluate_leaf())
            return
        recurse(x + 1, repeated_labels)
        try_add(x, repeated_labels, lambda value: recurse(x + 1, value))

    recurse(1, 0)
    return {
        "N": n,
        "total_endpoint_normalized_subsets": 1 << (n - 2),
        "admissible_count": admissible_count,
        "repeated_exception_with_residual_count": repeated_residual_count,
        "collision_free_completion_count": collision_free_count,
        "blocked_completion_count": repeated_residual_count - collision_free_count,
        "same_span_completion_count": same_span_count,
        "same_span_blocked_count": same_span_blocked_count,
        "first_blocked": first_blocked,
        "first_same_span_blocked": first_same_span_blocked,
        "largest_beta": largest_beta,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=2)
    parser.add_argument("--max-n", type=int, default=22)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p56/census_N22.json"),
    )
    args = parser.parse_args()

    by_n = [search_n(n) for n in range(args.min_n, args.max_n + 1)]
    first_blocked = None
    first_same_span_blocked = None
    largest_beta = None
    for row in by_n:
        candidate = row["first_blocked"]
        if candidate is not None and smaller_record(candidate, first_blocked):
            first_blocked = candidate
        candidate = row["first_same_span_blocked"]
        if candidate is not None and smaller_record(candidate, first_same_span_blocked):
            first_same_span_blocked = candidate
        candidate = row["largest_beta"]
        if candidate is not None and (
            largest_beta is None or candidate["beta"] > largest_beta["beta"]
        ):
            largest_beta = candidate

    summary = {
        "arithmetic": "integer only",
        "domain": (
            f"all A subset [0,N-1] with endpoints included, "
            f"{args.min_n} <= N <= {args.max_n}"
        ),
        "total_subset_count": sum(
            row["total_endpoint_normalized_subsets"] for row in by_n
        ),
        "admissible_count": sum(row["admissible_count"] for row in by_n),
        "repeated_exception_with_residual_count": sum(
            row["repeated_exception_with_residual_count"] for row in by_n
        ),
        "collision_free_completion_count": sum(
            row["collision_free_completion_count"] for row in by_n
        ),
        "blocked_completion_count": sum(
            row["blocked_completion_count"] for row in by_n
        ),
        "same_span_completion_count": sum(
            row["same_span_completion_count"] for row in by_n
        ),
        "same_span_blocked_count": sum(
            row["same_span_blocked_count"] for row in by_n
        ),
        "first_blocked": first_blocked,
        "first_same_span_blocked": first_same_span_blocked,
        "largest_beta": largest_beta,
        "verified_identities": [
            "all sums touching R are unique and avoid P+P",
            "all positive differences touching R are unique and avoid D+(P)",
            "folded P+R sums equal the P-R difference labels",
            "D+(A union (sigma-A)) = D+(A) union {|r_i+r_j-sigma|}",
            "completion is admissible iff the virtual labels are new and injective",
            "orbit deficit beta equals the designated-pair repair bound",
            "deleting at most beta residual reflection-pairs repairs completion",
            "completion span = span(A)+|sigma-min(A)-max(A)|",
        ],
        "by_N": by_n,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "by_N"},
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
