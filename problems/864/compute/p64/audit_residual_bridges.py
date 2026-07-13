#!/usr/bin/env python3
"""Exact audits for the prescribed-scale P50 residual.

All accepted comparisons use Python integers.  The endpoint census is
generated recursively, pruning as soon as two different unordered sums
have multiplicity at least two.
"""

from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PROFILES = ROOT / "problems/864/compute/p20/results/profiles.jsonl.gz"
DEFAULT_SAMPLES = ROOT / "problems/864/compute/p20/results/samples.jsonl"


def prescribed_h(n: int) -> int:
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid**3 >= n * n:
            hi = mid
        else:
            lo = mid + 1
    return lo


def is_prescribed(n: int, h: int) -> bool:
    return h**3 >= n * n and (h - 1) ** 3 < n * n


def sum_counts(points: tuple[int, ...]) -> Counter[int]:
    out: Counter[int] = Counter()
    for j, right in enumerate(points):
        for left in points[: j + 1]:
            out[left + right] += 1
    return out


def difference_edges(points: tuple[int, ...]) -> dict[int, list[tuple[int, int]]]:
    out: dict[int, list[tuple[int, int]]] = {}
    for j in range(1, len(points)):
        for i in range(j):
            out.setdefault(points[j] - points[i], []).append((i, j))
    return out


def metrics(points: tuple[int, ...], n: int, h: int | None = None) -> dict:
    if h is None:
        h = prescribed_h(n)
    k = len(points)
    sums = sum_counts(points)
    repeated = [value for value, count in sums.items() if count >= 2]
    if len(repeated) > 1:
        raise ValueError("nonadmissible input")
    sigma = repeated[0] if repeated else None

    edges = difference_edges(points)
    if max((len(value) for value in edges.values()), default=0) > 2:
        raise AssertionError("admissibility did not force nu(d) <= 2")
    duplicate_weight = sum(
        h - d for d, value in edges.items() if d < h and len(value) == 2
    )
    missing_weight = sum(h - d for d in range(1, h) if d not in edges)
    z = duplicate_weight - missing_weight

    gaps = tuple(points[i + 1] - points[i] for i in range(k - 1))
    support = h + sum(min(h, gap) for gap in gaps)
    ambient_holes = n + h - 1 - support
    short_gap_overlap = k * h - support
    if short_gap_overlap != sum(max(0, h - gap) for gap in gaps):
        raise AssertionError("short-gap identity failed")

    adjacent_duplicate_weight = 0
    adjacent_unique_weight = 0
    touched_duplicate_label_weight = 0
    double_adjacent_duplicate_weight = 0
    for d, value in edges.items():
        if d >= h:
            continue
        adjacent_count = sum(j == i + 1 for i, j in value)
        if len(value) == 2:
            adjacent_duplicate_weight += adjacent_count * (h - d)
            if adjacent_count:
                touched_duplicate_label_weight += h - d
            if adjacent_count == 2:
                double_adjacent_duplicate_weight += h - d
        elif adjacent_count:
            adjacent_unique_weight += h - d
    if adjacent_duplicate_weight + adjacent_unique_weight != short_gap_overlap:
        raise AssertionError("adjacent overlap classification failed")

    sharp_envelope = (
        9 * n * (n - 1)
        - 3 * h**3
        + 12 * h * h
        + (12 * h * h - 9 * n) * ambient_holes
    )
    rho = 8 * n * z - sharp_envelope
    rescue = 9 * n * short_gap_overlap
    return {
        "A": list(points),
        "N": n,
        "H": h,
        "k": k,
        "exceptional_sum": sigma,
        "M_H": support,
        "G_H": ambient_holes,
        "S_H": short_gap_overlap,
        "D_H": duplicate_weight,
        "Q_H": missing_weight,
        "Z_H": z,
        "adjacent_duplicate_weight": adjacent_duplicate_weight,
        "adjacent_unique_weight": adjacent_unique_weight,
        "touched_duplicate_label_weight": touched_duplicate_label_weight,
        "double_adjacent_duplicate_weight": double_adjacent_duplicate_weight,
        "rho": rho,
        "rescue": rescue,
        "lg33_margin": rho - rescue,
        "edge_bridge_margin": rho
        - n * (8 * short_gap_overlap + adjacent_duplicate_weight),
        "touch_bridge_margin": rho
        - n * (8 * short_gap_overlap + touched_duplicate_label_weight),
    }


def update_maximum(old: dict | None, row: dict, key: str) -> dict:
    if old is None or int(row[key]) > int(old[key]):
        return row
    return old


def summarize(rows) -> dict:
    total = residual = 0
    failures = Counter()
    maxima = {key: None for key in ("lg33_margin", "edge_bridge_margin", "touch_bridge_margin")}
    maximum_target_ratio = None
    maximum_edge_ratio = None
    for row in rows:
        total += 1
        if row["rho"] <= 0:
            continue
        residual += 1
        for key in maxima:
            maxima[key] = update_maximum(maxima[key], row, key)
            if row[key] > 0:
                failures[key] += 1
        s = row["S_H"]
        if s:
            ratio_record = {
                **row,
                "ratio_numerator": row["rho"],
                "target_ratio_denominator": 9 * row["N"] * s,
                "edge_ratio_denominator": row["N"]
                * (8 * s + row["adjacent_duplicate_weight"]),
            }
            if (
                maximum_target_ratio is None
                or ratio_record["ratio_numerator"]
                * maximum_target_ratio["target_ratio_denominator"]
                > maximum_target_ratio["ratio_numerator"]
                * ratio_record["target_ratio_denominator"]
            ):
                maximum_target_ratio = ratio_record
            if (
                maximum_edge_ratio is None
                or ratio_record["ratio_numerator"]
                * maximum_edge_ratio["edge_ratio_denominator"]
                > maximum_edge_ratio["ratio_numerator"]
                * ratio_record["edge_ratio_denominator"]
            ):
                maximum_edge_ratio = ratio_record
    return {
        "rows_checked": total,
        "positive_residual_rows": residual,
        "failure_counts": dict(failures),
        "maximum_margins": maxima,
        "maximum_target_ratio": maximum_target_ratio,
        "maximum_edge_ratio": maximum_edge_ratio,
    }


def admissible_endpoint_rows(max_n: int):
    yield metrics((0,), 1)

    def extend(points: tuple[int, ...], counts: Counter[int], repeated: frozenset[int]):
        last = points[-1]
        for value in range(last + 1, max_n):
            additions = [left + value for left in points] + [2 * value]
            new_repeated = set(repeated)
            valid = True
            for label in additions:
                if counts[label] == 1:
                    new_repeated.add(label)
                    if len(new_repeated) > 1:
                        valid = False
                        break
            if not valid:
                continue
            for label in additions:
                counts[label] += 1
            child = points + (value,)
            yield metrics(child, value + 1)
            yield from extend(child, counts, frozenset(new_repeated))
            for label in additions:
                counts[label] -= 1
                if not counts[label]:
                    del counts[label]

    initial = Counter({0: 1})
    yield from extend((0,), initial, frozenset())


def prescribed_profile_rows(profiles: Path, samples: Path):
    sample_map = {
        row["sample_id"]: row
        for row in (json.loads(line) for line in samples.read_text(encoding="utf-8").splitlines())
    }
    with gzip.open(profiles, "rt", encoding="utf-8") as source:
        for line in source:
            profile = json.loads(line)
            n = int(profile["N"])
            h = int(profile["H"])
            if not is_prescribed(n, h):
                continue
            sample = sample_map[profile["sample_id"]]
            row = metrics(tuple(int(x) for x in sample["A"]), n, h)
            for field, expected in {
                "k": profile["size"],
                "M_H": profile["M"],
                "D_H": profile["duplicate_weight"],
                "Q_H": profile["missing_weight"],
                "Z_H": profile["Z"],
            }.items():
                if row[field] != int(expected):
                    raise AssertionError(f"P20 mismatch for {field}")
            row["sample_id"] = profile["sample_id"]
            yield row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=24)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "problems/864/compute/p64/audit_results.json",
    )
    args = parser.parse_args()
    result = {
        "arithmetic": "integer",
        "edge_bridge": "rho <= N*(8*S_H + adjacent_duplicate_weight)",
        "endpoint_census": summarize(admissible_endpoint_rows(args.max_n)),
        "prescribed_P20": summarize(
            prescribed_profile_rows(args.profiles, args.samples)
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(
        json.dumps(
            {
                "endpoint": {
                    key: result["endpoint_census"][key]
                    for key in ("rows_checked", "positive_residual_rows", "failure_counts")
                },
                "P20": {
                    key: result["prescribed_P20"][key]
                    for key in ("rows_checked", "positive_residual_rows", "failure_counts")
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
