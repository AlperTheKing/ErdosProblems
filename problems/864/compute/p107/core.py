#!/usr/bin/env python3
"""Independent exact arithmetic for the P107 RM97/P101 search."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import heapq
from typing import Iterable, Sequence


def digest(values: Sequence[int]) -> str:
    return sha256(",".join(map(str, values)).encode("ascii")).hexdigest()


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in result:
                raise AssertionError(("repeated sum", total, result[total], (left, right)))
            result[total] = (left, right)
    return result


def positive_differences(values: Sequence[int]) -> set[int]:
    counts = Counter(
        values[j] - values[i]
        for j in range(len(values))
        for i in range(j)
    )
    if counts and max(counts.values()) != 1:
        raise AssertionError(("repeated difference", max(counts.values())))
    return set(counts)


def canonical_folds(
    values: Sequence[int], h: int
) -> list[tuple[int, int, int, int]]:
    sums = unordered_sum_map(values)
    folds: list[tuple[int, int, int, int]] = []
    for low in sorted(sums):
        high = low + h
        if high not in sums:
            continue
        a, c = sums[low]
        u, v = sums[high]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v))
        folds.append((a, c, u, v))
    return folds


def loose_triangles(
    folds: Sequence[tuple[int, int, int, int]],
) -> list[tuple[int, int, int]]:
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    triangles: list[tuple[int, int, int]] = []
    for a, c in ac:
        for aa, u in au:
            if aa != a:
                continue
            ids = (ac[a, c], au[a, u], cu.get((c, u)))
            if ids[2] is None or ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("nonlinear shadow", ids))
            triangles.append((ids[0], ids[1], int(ids[2])))
    return triangles


def greedy_interval_match(
    intervals: Iterable[tuple[int, int]], slots: Iterable[int]
) -> int:
    ordered_intervals = sorted(intervals)
    ordered_slots = sorted(slots)
    heap: list[int] = []
    index = matched = 0
    for point in ordered_slots:
        while index < len(ordered_intervals) and ordered_intervals[index][0] <= point:
            heapq.heappush(heap, ordered_intervals[index][1])
            index += 1
        if heap and heap[0] < point:
            return matched
        if heap:
            heapq.heappop(heap)
            matched += 1
    return matched


def audit(values_input: Iterable[int], h: int, b: int) -> dict[str, object]:
    values = tuple(sorted(values_input))
    if not values or len(values) != len(set(values)):
        raise AssertionError("marks must be nonempty and distinct")
    if values[-1] != h - 1 or b not in (1, 2):
        raise AssertionError(("endpoint", values[-1:], h, b))

    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    literal_hole = differences.isdisjoint(total + b for total in sums)
    folds = canonical_folds(values, h)
    triangles = loose_triangles(folds)
    collided = [fold for fold in folds if fold[0] + fold[1] + b in differences]
    delta = (3 * len(values) * len(values) - len(values) + 2) // 2 - h

    shared = [(a, c, u) for a, c, u, _v in folds]
    for base, au, cu in triangles:
        a, c, _r, _s = folds[base]
        u = folds[au][2]
        if folds[cu][2] != u:
            raise AssertionError(("triangle endpoint", base, au, cu))
        shared.append((a, c, u))
    intervals = [
        (
            min(u - a - c - b, h - b - u),
            max(u - a - c - b, h - b - u),
        )
        for a, c, u in shared
    ]
    slots: list[int] = []
    for a, c, u, v in folds:
        lower, upper = h - b - v, h - b - u
        slots.extend((lower, upper))
        if a + c + b in differences:
            slots.append(lower)
    matched = greedy_interval_match(intervals, slots)

    return {
        "B": list(values),
        "sha256": digest(values),
        "p": len(values),
        "h": h,
        "b": b,
        "delta": delta,
        "sum_count": len(sums),
        "difference_count": len(differences),
        "literal_hole": literal_hole,
        "C_S": len(folds),
        "T_F": len(triangles),
        "V_b": len(collided),
        "P101_excess": len(triangles) - len(folds) - len(collided),
        "RM97_demands": len(intervals),
        "RM97_slots": len(slots),
        "RM97_matched": matched,
        "RM97_unmatched": len(intervals) - matched,
        "folds": [list(fold) for fold in folds],
        "triangles": [list(triangle) for triangle in triangles],
    }

