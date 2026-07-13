"""Independent literal verifier for the stored P48 JSON certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def pair_sums(values: tuple[int, ...]) -> list[int]:
    return [
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    ]


def triple_sums(values: tuple[int, ...]) -> set[int]:
    return {
        values[i] + values[j] + values[k]
        for i in range(len(values))
        for j in range(i, len(values))
        for k in range(j, len(values))
    }


def verify_lift(record: dict[str, object]) -> None:
    ruler = tuple(record["ruler"])
    gap = int(record["G"])
    values = tuple(gap + 2 * z for z in ruler)
    sums = pair_sums(values)
    assert len(sums) == len(set(sums)) == len(values) * (len(values) + 1) // 2
    assert set(values).isdisjoint(triple_sums(values))
    assert len({x % 2 for x in values}) == 1
    assert min(values) > 0 and max(values) == record["M"]


def verify_guarded(record: dict[str, object]) -> None:
    x_values = tuple(record["X"])
    y_values = tuple(record["Y"])
    gap = int(record["G"])
    shift = int(record["T"])
    assert gap > max(x_values[-1], y_values[-1])
    assert shift > gap + 3 * x_values[-1]
    ruler = x_values + tuple(shift + y for y in y_values)
    assert ruler == tuple(record["Z"])
    values = tuple(gap + 2 * z for z in ruler)
    assert values == tuple(record["E"])
    sums = pair_sums(values)
    assert len(sums) == len(set(sums))
    assert set(values).isdisjoint(triple_sums(values))


def verify_rectangle(sample: dict[str, object]) -> None:
    values = tuple(sample["product"])
    collision = sample["collision"]
    first = tuple(collision["first_pair"])
    second = tuple(collision["second_pair"])
    assert sum(first) == sum(second) == collision["sum"]
    assert first != second
    assert set(first + second).issubset(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("problems/864/compute/p48/audit_results.json"),
    )
    args = parser.parse_args()
    data = json.loads(args.path.read_text(encoding="ascii"))

    assert data["conventions"]["diagonal_pair_sums"]
    assert data["conventions"]["repeated_triple_summands"]
    verify_rectangle(data["tensor"]["sample"])
    verify_guarded(data["separated_unions"]["best_finite_guarded_union"])

    for falsifier in data["separated_unions"]["strict_guard_falsifiers"]:
        values = tuple(falsifier["E"])
        witness = falsifier["witness"]
        assert witness["target"] in values
        assert sum(witness["summands"]) == witness["target"]
        assert witness["repeated_summand"]

    lift_records = []
    lift_records.extend(row["best_affine_cut"] for row in data["bose"]["rows"])
    lift_records.extend(row["best_natural_cut"] for row in data["ruzsa"]["rows"])
    lift_records.extend(row["worst_natural_cut"] for row in data["ruzsa"]["rows"])
    lift_records.extend(
        row["best"] for row in data["welch"]["rows"] if row["best"] is not None
    )
    lift_records.extend(
        row["best_step_survivor"]
        for row in data["parabola_carries"]["rows"]
        if row["best_step_survivor"] is not None
    )

    # Parabola summaries omit their ruler, so verify all stored full records.
    full_records = [record for record in lift_records if "ruler" in record]
    for record in full_records:
        verify_lift(record)

    assert data["tensor"]["full_cartesian_products"] == 400
    assert data["costas_composition"]["compositions_checked"] == 324
    assert data["separated_unions"]["difference_disjoint_pairs"] > 0
    assert data["separated_unions"]["joint_lag_inequalities"] > 0

    print("PASS: independent P48 certificate verification")
    print("full algebraic records:", len(full_records))
    print("guard falsifiers:", len(data["separated_unions"]["strict_guard_falsifiers"]))


if __name__ == "__main__":
    main()
