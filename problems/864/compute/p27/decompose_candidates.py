"""Exact uniform-profile decomposition for stored Singer carry failures."""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Iterable


def records(paths: list[Path]) -> Iterable[tuple[Path, dict[str, object]]]:
    for path in paths:
        for line in path.read_text(encoding="ascii").splitlines():
            record = json.loads(line)
            if record.get("family") == "singer":
                yield path, record


def candidate(record: dict[str, object]) -> dict[str, object] | None:
    for key in ("best_candidate", "best_below_3p2"):
        value = record.get(key)
        if isinstance(value, dict) and "points" in value:
            return value
    return None


def fraction_record(value: Fraction) -> dict[str, object]:
    return {"exact": str(value), "float": float(value)}


def decompose(path: Path, record: dict[str, object], item: dict[str, object]) -> dict[str, object]:
    q = int(record["parameter"])
    modulus = int(record["modulus"])
    points = sorted(int(value) for value in item["points"])
    span = points[-1]
    center = int(item.get("candidate_center", item.get("center")))
    d = modulus + 2 * span - center
    reflected = [span - value for value in reversed(points)]
    delta = {
        points[j] - points[i]
        for i in range(len(points))
        for j in range(i + 1, len(points))
    }

    ordered_sums = [0] * modulus
    for alpha in reflected:
        for beta in reflected:
            if alpha + beta < modulus:
                ordered_sums[alpha + beta] += 1
    complement = [0] * modulus
    for e in range(1, modulus):
        complement[e] = int(e not in delta)

    rho_squared = Fraction(len(points) ** 2, modulus**2)
    main = rho_squared**2 * math.comb(d + 2, 3)
    sum_main_difference = Fraction(0)
    difference_main_sum = Fraction(0)
    residual_correlation = Fraction(0)
    exact_count = 0
    for s in range(d):
        e = d - s
        sum_baseline = rho_squared * (s + 1)
        difference_baseline = rho_squared * e
        sum_residual = ordered_sums[s] - sum_baseline
        difference_residual = complement[e] - difference_baseline
        exact_count += ordered_sums[s] * complement[e]
        sum_main_difference += sum_baseline * difference_residual
        difference_main_sum += sum_residual * difference_baseline
        residual_correlation += sum_residual * difference_residual

    reconstructed = main + sum_main_difference + difference_main_sum + residual_correlation
    if reconstructed != exact_count:
        raise AssertionError("profile decomposition is not exact")
    if exact_count != 0:
        raise AssertionError("stored center is not a carry failure")
    return {
        "source": path.name,
        "q": q,
        "v": modulus,
        "d": d,
        "d_over_v": str(Fraction(d, modulus)),
        "ordered_count": exact_count,
        "uniform_main": fraction_record(main),
        "sum_main_times_difference_residual": fraction_record(sum_main_difference),
        "sum_residual_times_difference_main": fraction_record(difference_main_sum),
        "residual_correlation": fraction_record(residual_correlation),
        "reconstructed": fraction_record(reconstructed),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    output = []
    seen: set[tuple[int, int, tuple[int, ...]]] = set()
    for path, record in records(args.inputs):
        item = candidate(record)
        if item is None:
            continue
        key = (
            int(record["modulus"]),
            int(item.get("candidate_center", item.get("center"))),
            tuple(int(value) for value in item["points"]),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(decompose(path, record, item))
    if not output:
        raise AssertionError("no Singer candidates found")
    for row in output:
        print(json.dumps(row, sort_keys=True))
    summary = {
        "records": len(output),
        "all_reconstruct_exactly": all(row["ordered_count"] == 0 for row in output),
        "largest_uniform_main": max(row["uniform_main"]["float"] for row in output),
    }
    print(json.dumps({"summary": summary}, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({"records": output, "summary": summary}, indent=2, sort_keys=True)
            + "\n",
            encoding="ascii",
        )


if __name__ == "__main__":
    main()
