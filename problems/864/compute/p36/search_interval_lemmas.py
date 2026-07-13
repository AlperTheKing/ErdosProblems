#!/usr/bin/env python3
"""Exact census for the centered C20 interval/gap frontier.

The script deliberately separates literal 864-admissibility from the weaker
condition nu_A(d) <= 2.  Every displayed inequality is evaluated after
clearing its positive denominator; no floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def ceil_cuberoot(value: int) -> int:
    lo, hi = 0, 1
    while hi**3 < value:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**3 >= value:
            hi = mid
        else:
            lo = mid
    return hi


def prescribed_h(n: int) -> int:
    return ceil_cuberoot(n * n)


def is_admissible(points: tuple[int, ...]) -> bool:
    sums: Counter[int] = Counter()
    for i, a in enumerate(points):
        for b in points[i:]:
            sums[a + b] += 1
    return sum(multiplicity >= 2 for multiplicity in sums.values()) <= 1


def difference_counts(points: tuple[int, ...]) -> Counter[int]:
    counts: Counter[int] = Counter()
    for j, right in enumerate(points):
        for left in points[:j]:
            counts[right - left] += 1
    return counts


@dataclass(frozen=True)
class Metrics:
    points: tuple[int, ...]
    n: int
    h: int
    k: int
    m_h: int
    w_h: int
    z_h: int
    d_h: int
    q_h: int
    gap_overlap: int
    ambient_holes: int
    max_degree: int
    degree_histogram: tuple[tuple[int, int], ...]
    c20_margin: int
    lg33_margin: int
    bare_gap_margin: int

    def record(self) -> dict[str, object]:
        return {
            "A": list(self.points),
            "N": self.n,
            "H": self.h,
            "k": self.k,
            "M_H": self.m_h,
            "W_H": self.w_h,
            "Z_H": self.z_h,
            "D_H": self.d_h,
            "Q_H": self.q_h,
            "gap_overlap": self.gap_overlap,
            "ambient_holes": self.ambient_holes,
            "max_degree": self.max_degree,
            "degree_histogram": [list(item) for item in self.degree_histogram],
            "c20_cleared_margin": self.c20_margin,
            "lg33_cleared_margin": self.lg33_margin,
            "bare_gap_cleared_margin": self.bare_gap_margin,
        }


def compute_metrics(points: tuple[int, ...], n: int) -> Metrics:
    assert points and 1 <= points[0] <= points[-1] <= n
    h = prescribed_h(n)
    k = len(points)
    differences = difference_counts(points)
    assert max(differences.values(), default=0) <= 2

    gaps = [right - left for left, right in zip(points, points[1:])]
    m_h_from_gaps = h + sum(min(h, gap) for gap in gaps)
    gap_overlap = sum(max(0, h - gap) for gap in gaps)
    assert m_h_from_gaps == k * h - gap_overlap

    lo = points[0] - h + 1
    hi = points[-1]
    degrees = [
        sum(a - h + 1 <= x <= a for a in points)
        for x in range(lo, hi + 1)
    ]
    positive_degrees = [degree for degree in degrees if degree]
    m_h = len(positive_degrees)
    assert m_h == m_h_from_gaps
    assert sum(positive_degrees) == k * h

    w_h = sum((h - d) * multiplicity for d, multiplicity in differences.items() if d < h)
    assert w_h == sum(degree * (degree - 1) // 2 for degree in positive_degrees)
    z_h = w_h - h * (h - 1) // 2
    d_h = sum(h - d for d, multiplicity in differences.items() if d < h and multiplicity == 2)
    q_h = sum(h - d for d in range(1, h) if differences[d] == 0)
    assert z_h == d_h - q_h

    ambient_holes = n + h - 1 - m_h
    assert ambient_holes >= 0

    # Six times C20 after multiplication by the positive integer N H^2.
    c20_margin = (
        6 * m_h * (h * h + 2 * z_h)
        - 8 * n * h * h
        - 9 * h**3
        - 9 * n * (k - 1) * h
    )

    # P33's sufficient linear gap lemma, written as left minus right.
    lg33_margin = (
        8 * n * z_h
        - 12 * h * h * ambient_holes
        + 3 * h**3
        - 12 * h * h
        - 9 * n * (k - 1) * h
    )

    # The sharp asymptotic core 2 N Z_H <= 3 H^2 G_H, with no corrections.
    bare_gap_margin = 2 * n * z_h - 3 * h * h * ambient_holes

    histogram = tuple(sorted(Counter(positive_degrees).items()))
    return Metrics(
        points=points,
        n=n,
        h=h,
        k=k,
        m_h=m_h,
        w_h=w_h,
        z_h=z_h,
        d_h=d_h,
        q_h=q_h,
        gap_overlap=gap_overlap,
        ambient_holes=ambient_holes,
        max_degree=max(positive_degrees),
        degree_histogram=histogram,
        c20_margin=c20_margin,
        lg33_margin=lg33_margin,
        bare_gap_margin=bare_gap_margin,
    )


def iter_subsets(n: int) -> Iterable[tuple[int, ...]]:
    for mask in range(1, 1 << n):
        yield tuple(index + 1 for index in range(n) if mask & (1 << index))


def update_maximum(
    maxima: dict[str, tuple[int, Metrics] | None],
    key: str,
    value: int,
    metrics: Metrics,
) -> None:
    previous = maxima[key]
    if previous is None or value > previous[0]:
        maxima[key] = (value, metrics)


def census(max_n: int) -> dict[str, object]:
    classes = ("nu2", "admissible")
    maxima: dict[str, dict[str, tuple[int, Metrics] | None]] = {
        name: {"c20": None, "lg33": None, "bare_gap": None}
        for name in classes
    }
    counts = {
        name: {"sets": 0, "c20_failures": 0, "lg33_failures": 0, "bare_gap_failures": 0}
        for name in classes
    }

    for n in range(1, max_n + 1):
        for points in iter_subsets(n):
            differences = difference_counts(points)
            if max(differences.values(), default=0) > 2:
                continue
            metrics = compute_metrics(points, n)
            memberships = ["nu2"]
            if is_admissible(points):
                memberships.append("admissible")

            for class_name in memberships:
                counts[class_name]["sets"] += 1
                if metrics.c20_margin > 0:
                    counts[class_name]["c20_failures"] += 1
                if metrics.lg33_margin > 0:
                    counts[class_name]["lg33_failures"] += 1
                if metrics.bare_gap_margin > 0:
                    counts[class_name]["bare_gap_failures"] += 1
                update_maximum(maxima[class_name], "c20", metrics.c20_margin, metrics)
                update_maximum(maxima[class_name], "lg33", metrics.lg33_margin, metrics)
                update_maximum(maxima[class_name], "bare_gap", metrics.bare_gap_margin, metrics)

    maximum_records: dict[str, dict[str, object]] = {}
    for class_name in classes:
        maximum_records[class_name] = {}
        for inequality, result in maxima[class_name].items():
            assert result is not None
            value, metrics = result
            maximum_records[class_name][inequality] = {
                "margin": value,
                "witness": metrics.record(),
            }

    return {
        "max_N": max_n,
        "integer_arithmetic_only": True,
        "counts": counts,
        "maxima": maximum_records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=18)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p36/interval_census.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = census(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
