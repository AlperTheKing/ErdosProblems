"""Probe exact couplings between P51 balanced-support columns.

The script exhausts every endpoint-normalized Sidon ruler and valid gap
through the requested width, then checks the stored Bose q=128 witness.
All candidate restrictions are tested with integer arithmetic.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations, combinations_with_replacement
from pathlib import Path


HERE = Path(__file__).resolve().parent
P864 = HERE.parents[1]
BOSE_Q128 = P864 / "compute" / "p37" / "bose_q128_sample.jsonl"


def pair_sums(values: tuple[int, ...]) -> set[int]:
    return {
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    }


def positive_differences(values: tuple[int, ...]) -> set[int]:
    return {
        values[j] - values[i]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    }


def is_sidon(values: tuple[int, ...]) -> bool:
    expected = len(values) * (len(values) + 1) // 2
    return len(pair_sums(values)) == expected


def is_valid_pair(values: tuple[int, ...], gap: int) -> bool:
    sums = pair_sums(values)
    return positive_differences(values).isdisjoint(gap + total for total in sums)


def balanced_columns(
    values: tuple[int, ...], cutoff: int
) -> dict[int, dict[str, object]]:
    """Return P51's actual B_x and its all-distinct/equal partition."""
    low = tuple(value for value in values if value <= cutoff)
    classes: dict[int, list[tuple[int, int, int]]] = {}
    for triple in combinations_with_replacement(low, 3):
        total = sum(triple)
        if total <= cutoff:
            classes.setdefault(total, []).append(triple)

    columns: dict[int, dict[str, object]] = {}
    for total, triples in sorted(classes.items()):
        balanced = [triple for triple in triples if len(set(triple)) in (1, 3)]
        support = frozenset(value for triple in balanced for value in triple)
        if 3 * sum(support) != total * len(support):
            raise AssertionError((values, cutoff, total, "barycenter"))
        if len(support) % 3 != int(total % 3 == 0 and total // 3 in values):
            raise AssertionError((values, cutoff, total, "residue"))
        columns[total] = {
            "B": support,
            "triples": tuple(balanced),
            "shifted": frozenset(total - value for value in support),
            "centered": frozenset(3 * value - total for value in support),
        }
    return columns


def capacity_columns(
    values: tuple[int, ...], cutoff: int, targets: set[int]
) -> dict[int, frozenset[int]]:
    """Choose the first maximum-cardinality P51 witness for every target."""
    low = tuple(value for value in values if value <= cutoff)
    index = {value: position for position, value in enumerate(low)}
    best_masks: dict[int, int] = {}
    best_sizes: dict[int, int] = {}
    previous = 0
    subset_sum = 0
    subset_size = 0
    for step in range(1, 1 << len(low)):
        mask = step ^ (step >> 1)
        changed = mask ^ previous
        position = (changed & -changed).bit_length() - 1
        if mask & changed:
            subset_sum += low[position]
            subset_size += 1
        else:
            subset_sum -= low[position]
            subset_size -= 1
        previous = mask

        numerator = 3 * subset_sum
        if numerator % subset_size:
            continue
        total = numerator // subset_size
        if total not in targets or low[mask.bit_length() - 1] > total:
            continue
        center = index.get(total // 3) if total % 3 == 0 else None
        if center is None:
            feasible = subset_size % 3 == 0
        else:
            feasible = subset_size % 3 == 1 and bool(mask & (1 << center))
        if feasible and subset_size > best_sizes.get(total, 0):
            best_sizes[total] = subset_size
            best_masks[total] = mask

    return {
        total: frozenset(
            low[position]
            for position in range(len(low))
            if mask & (1 << position)
        )
        for total, mask in best_masks.items()
    }


def epsilon(values: tuple[int, ...], total: int) -> int:
    return int(total % 3 == 0 and total // 3 in values)


def capacity_coupling_rows(
    values: tuple[int, ...], gap: int, source: str
) -> tuple[int, list[dict[str, object]]]:
    cutoff = values[-1] - gap
    targets = set(balanced_columns(values, cutoff))
    columns = capacity_columns(values, cutoff, targets)
    rows: list[dict[str, object]] = []
    for x, y in combinations(columns, 2):
        bx = columns[x]
        by = columns[y]
        h = len(bx & by)
        excess = 3 * h - len(bx) - len(by) - 2 * epsilon(values, x) - 2 * epsilon(values, y)
        rows.append(
            {
                "source": source,
                "Z": values,
                "W": values[-1],
                "G": gap,
                "K": cutoff,
                "x": x,
                "y": y,
                "B_x": tuple(sorted(bx)),
                "B_y": tuple(sorted(by)),
                "size_x": len(bx),
                "size_y": len(by),
                "intersection": tuple(sorted(bx & by)),
                "epsilon_x": epsilon(values, x),
                "epsilon_y": epsilon(values, y),
                "block_bound_excess": excess,
            }
        )
    return sum(map(len, columns.values())), rows


def case_record(
    values: tuple[int, ...], gap: int, source: str
) -> tuple[dict[str, object], list[dict[str, object]]]:
    cutoff = values[-1] - gap
    columns = balanced_columns(values, cutoff)
    pairs: list[dict[str, object]] = []
    for x, y in combinations(columns, 2):
        bx = columns[x]["B"]
        by = columns[y]["B"]
        shifted_x = columns[x]["shifted"]
        shifted_y = columns[y]["shifted"]
        centered_x = columns[x]["centered"]
        centered_y = columns[y]["centered"]
        assert isinstance(bx, frozenset) and isinstance(by, frozenset)
        assert isinstance(shifted_x, frozenset) and isinstance(shifted_y, frozenset)
        assert isinstance(centered_x, frozenset) and isinstance(centered_y, frozenset)
        pairs.append(
            {
                "source": source,
                "Z": values,
                "W": values[-1],
                "G": gap,
                "K": cutoff,
                "x": x,
                "y": y,
                "B_x": tuple(sorted(bx)),
                "B_y": tuple(sorted(by)),
                "size_x": len(bx),
                "size_y": len(by),
                "intersection": tuple(sorted(bx & by)),
                "shifted_intersection": tuple(sorted(shifted_x & shifted_y)),
                "centered_intersection": tuple(sorted(centered_x & centered_y)),
                "triples_x": columns[x]["triples"],
                "triples_y": columns[y]["triples"],
            }
        )

    nonempty = [column for column in columns.values() if column["B"]]
    total_balanced = sum(len(column["B"]) for column in nonempty)
    edge_degrees = Counter(
        edge for column in nonempty for edge in column["shifted"]
    )
    pair_intersections = sum(degree * (degree - 1) // 2 for degree in edge_degrees.values())
    record = {
        "source": source,
        "p": len(values),
        "W": values[-1],
        "G": gap,
        "K": cutoff,
        "Z": values,
        "columns": len(columns),
        "nonempty_balanced_columns": len(nonempty),
        "balanced_incidence": total_balanced,
        "shifted_union": len(edge_degrees),
        "shifted_pair_intersections": pair_intersections,
        "maximum_shifted_degree": max(edge_degrees.values(), default=0),
    }
    return record, pairs


def q128_case() -> tuple[tuple[int, ...], int]:
    record = json.loads(BOSE_Q128.read_text(encoding="ascii").splitlines()[0])
    candidate = record["best_candidate"]
    reflected = tuple(int(value) for value in candidate["points"])
    width = int(candidate["span"])
    center = int(candidate["candidate_center"])
    gap = center - 2 * width
    return tuple(sorted(width - value for value in reflected)), gap


def witness_key(row: dict[str, object]) -> tuple[object, ...]:
    return (
        len(row["Z"]),
        row["W"],
        row["Z"],
        row["G"],
        row["x"],
        row["y"],
    )


def intersection_excess(row: dict[str, object]) -> int:
    return (
        3 * len(row["intersection"])
        - int(row["size_x"])
        - int(row["size_y"])
    )


def summarize(max_width: int) -> dict[str, object]:
    endpoint_rulers = 0
    valid_pairs = 0
    column_pairs = 0
    records: list[dict[str, object]] = []
    pair_records: list[dict[str, object]] = []
    capacity_pairs: list[dict[str, object]] = []
    capacity_total = 0

    for width in range(1, max_width + 1):
        for count in range(width):
            for middle in combinations(range(1, width), count):
                values = (0, *middle, width)
                if not is_sidon(values):
                    continue
                endpoint_rulers += 1
                for gap in range(1, width):
                    if not is_valid_pair(values, gap):
                        continue
                    valid_pairs += 1
                    record, pairs = case_record(values, gap, "exhaustive")
                    case_capacity, case_capacity_pairs = capacity_coupling_rows(
                        values, gap, "exhaustive"
                    )
                    records.append(record)
                    pair_records.extend(pairs)
                    capacity_pairs.extend(case_capacity_pairs)
                    capacity_total += case_capacity
                    column_pairs += len(pairs)

    values, gap = q128_case()
    q128, q128_pairs = case_record(values, gap, "q128")
    q128_capacity, q128_capacity_pairs = capacity_coupling_rows(values, gap, "q128")

    all_pairs = pair_records + q128_pairs
    shifted_failures = [row for row in all_pairs if len(row["shifted_intersection"]) > 1]
    centered_failures = [row for row in all_pairs if len(row["centered_intersection"]) > 1]
    unshifted_gt_one = [row for row in all_pairs if len(row["intersection"]) > 1]
    one_third_failures = [row for row in all_pairs if intersection_excess(row) > 0]
    capacity_block_failures = [
        row
        for row in capacity_pairs + q128_capacity_pairs
        if int(row["block_bound_excess"]) > 0
    ]

    def smallest(rows: list[dict[str, object]]) -> dict[str, object] | None:
        return min(rows, key=witness_key) if rows else None

    def largest_intersection(
        rows: list[dict[str, object]],
    ) -> dict[str, object] | None:
        return max(
            rows,
            key=lambda row: (
                len(row["intersection"]),
                intersection_excess(row),
                tuple(-int(value) for value in witness_key(row)[:2]),
            ),
        ) if rows else None

    return {
        "parameters": {"max_width": max_width, "q128": True},
        "exhaustive": {
            "endpoint_sidon_rulers": endpoint_rulers,
            "valid_pairs": valid_pairs,
            "column_pairs": column_pairs,
            "maximum_unshifted_intersection": max(
                (len(row["intersection"]) for row in pair_records), default=0
            ),
            "maximum_shifted_intersection": max(
                (len(row["shifted_intersection"]) for row in pair_records), default=0
            ),
            "maximum_centered_intersection": max(
                (len(row["centered_intersection"]) for row in pair_records), default=0
            ),
            "aggregate_balanced_incidence": sum(
                int(record["balanced_incidence"]) for record in records
            ),
            "aggregate_shifted_union": sum(
                int(record["shifted_union"]) for record in records
            ),
            "aggregate_shifted_pair_intersections": sum(
                int(record["shifted_pair_intersections"]) for record in records
            ),
            "aggregate_barycentric_capacity": capacity_total,
            "capacity_column_pairs": len(capacity_pairs),
        },
        "q128": q128,
        "q128_column_pairs": len(q128_pairs),
        "q128_barycentric_capacity": q128_capacity,
        "q128_capacity_column_pairs": len(q128_capacity_pairs),
        "q128_maximum_unshifted_intersection": max(
            (len(row["intersection"]) for row in q128_pairs), default=0
        ),
        "q128_maximum_shifted_intersection": max(
            (len(row["shifted_intersection"]) for row in q128_pairs), default=0
        ),
        "q128_maximum_centered_intersection": max(
            (len(row["centered_intersection"]) for row in q128_pairs), default=0
        ),
        "shifted_codegree_failures": len(shifted_failures),
        "centered_codegree_failures": len(centered_failures),
        "one_third_intersection_failures": len(one_third_failures),
        "maximum_one_third_excess": max(
            (intersection_excess(row) for row in all_pairs), default=0
        ),
        "smallest_unshifted_intersection_gt_one": smallest(unshifted_gt_one),
        "smallest_one_third_intersection_failure": smallest(one_third_failures),
        "capacity_block_bound_failures": len(capacity_block_failures),
        "smallest_capacity_block_bound_failure": smallest(capacity_block_failures),
        "largest_exhaustive_intersection": largest_intersection(pair_records),
        "largest_q128_intersection": largest_intersection(q128_pairs),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=18)
    parser.add_argument("--output", type=Path, default=HERE / "probe_results.json")
    args = parser.parse_args()
    result = summarize(args.max_width)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
