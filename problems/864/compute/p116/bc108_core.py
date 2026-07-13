#!/usr/bin/env python3
"""Independent exact evaluator for the P108 budgeted color inequality."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable, Iterator, Sequence


def normalized(values: Iterable[int]) -> tuple[int, ...]:
    row = tuple(sorted(set(int(value) for value in values)))
    if not row:
        return ()
    return tuple(value - row[0] for value in row)


def reflected(values: Sequence[int]) -> tuple[int, ...]:
    width = values[-1]
    return tuple(width - value for value in reversed(values))


def unordered_sums(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    sums: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in sums:
                raise ValueError(("not Sidon", total, sums[total], (left, right)))
            sums[total] = (left, right)
    return sums


def positive_differences(values: Sequence[int]) -> set[int]:
    differences: set[int] = set()
    for j, right in enumerate(values):
        for left in values[:j]:
            difference = right - left
            if difference in differences:
                raise ValueError(("not Sidon", difference))
            differences.add(difference)
    return differences


def is_sidon(values: Sequence[int]) -> bool:
    try:
        positive_differences(values)
    except ValueError:
        return False
    return True


def literal_hole(values: Sequence[int], b: int) -> bool:
    sums = unordered_sums(values)
    differences = positive_differences(values)
    return all(total + b not in differences for total in sums)


def hole_conflicts(values: Sequence[int], b: int) -> list[dict[str, object]]:
    sums = unordered_sums(values)
    difference_pairs: dict[int, tuple[int, int]] = {}
    for j, right in enumerate(values):
        for left in values[:j]:
            difference_pairs[right - left] = (left, right)
    rows = []
    for total, sum_pair in sorted(sums.items()):
        difference_pair = difference_pairs.get(total + b)
        if difference_pair is not None:
            rows.append({
                "sum": total,
                "sum_pair": list(sum_pair),
                "difference": total + b,
                "difference_pair": list(difference_pair),
            })
    return rows


def fold_system(
    values: Sequence[int], h: int,
) -> tuple[list[tuple[int, int, int, int]], list[tuple[int, int, int]]]:
    sums = unordered_sums(values)
    folds: list[tuple[int, int, int, int]] = []
    for low in sorted(sums):
        high_pair = sums.get(low + h)
        if high_pair is None:
            continue
        a, c = sums[low]
        u, v = high_pair
        if not (a <= c < u <= v):
            raise AssertionError(("fold order", a, c, u, v, h))
        folds.append((a, c, u, v))

    ac: dict[tuple[int, int], int] = {}
    au: dict[tuple[int, int], int] = {}
    cu: dict[tuple[int, int], int] = {}
    by_a_u: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for fold_id, (a, c, u, _v) in enumerate(folds):
        if (a, c) in ac or (a, u) in au or (c, u) in cu:
            raise AssertionError("nonlinear fold projection")
        ac[a, c] = fold_id
        au[a, u] = fold_id
        cu[c, u] = fold_id
        by_a_u[a].append((u, fold_id))

    triangles: list[tuple[int, int, int]] = []
    for (a, c), base in ac.items():
        for u, arm_au in by_a_u.get(a, ()):
            arm_cu = cu.get((c, u))
            if arm_cu is None:
                continue
            ids = (base, arm_au, arm_cu)
            if ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("triangle linearity", ids))
            triangles.append(ids)
    return folds, triangles


def structure_score(values: Sequence[int], h: int) -> dict[str, object]:
    values = tuple(int(value) for value in values)
    if tuple(sorted(values)) != values or len(set(values)) != len(values):
        raise ValueError("values must be strictly increasing")
    if not values or values[-1] != h - 1 or values[0] < 0:
        raise ValueError(("endpoint normalization", values[:1], values[-1:], h))
    folds, triangles = fold_system(values, h)
    folds_by_color = Counter(fold[2] for fold in folds)
    triangles_by_color: Counter[int] = Counter()
    for _base, arm_au, arm_cu in triangles:
        color = folds[arm_au][2]
        if folds[arm_cu][2] != color:
            raise AssertionError("triangle colors disagree")
        triangles_by_color[color] += 1
    color_rows = []
    positive_excess = 0
    for color in sorted(folds_by_color.keys() | triangles_by_color.keys()):
        n_u = folds_by_color[color]
        t_u = triangles_by_color[color]
        excess = max(0, t_u - n_u)
        positive_excess += excess
        if n_u or t_u:
            color_rows.append({"u": color, "n_u": n_u, "t_u": t_u, "excess": excess})
    p = len(values)
    baseline = (3 * p * p - p + 2) // 2
    return {
        "B": list(values),
        "p": p,
        "h": h,
        "delta": baseline - h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "positive_color_excess": positive_excess,
        "bc108_residual": positive_excess - p,
        "colors": color_rows,
    }


def gated_score(values: Sequence[int], h: int, b: int) -> dict[str, object]:
    if b not in (1, 2):
        raise ValueError("b must be 1 or 2")
    row = structure_score(values, h)
    row["b"] = b
    row["literal_hole"] = literal_hole(values, b)
    row["positive_defect"] = int(row["delta"]) > 0
    row["bc108_failure"] = (
        bool(row["literal_hole"])
        and bool(row["positive_defect"])
        and int(row["bc108_residual"]) > 0
    )
    return row


def sidon_rulers_with_first(width: int, first: int) -> Iterator[tuple[int, ...]]:
    """All endpoint-normalized Sidon rulers with specified first internal mark."""
    if first == 0:
        yield (0, width)
        return
    if not (1 <= first < width):
        return
    chosen = [0, first]
    used = {first}

    def new_differences(value: int) -> tuple[int, ...] | None:
        differences = tuple(value - old for old in chosen)
        if len(set(differences)) != len(differences):
            return None
        if any(difference in used for difference in differences):
            return None
        return differences

    def recurse(next_value: int) -> Iterator[tuple[int, ...]]:
        endpoint = new_differences(width)
        if endpoint is not None:
            yield tuple(chosen + [width])
        for value in range(next_value, width):
            differences = new_differences(value)
            if differences is None:
                continue
            chosen.append(value)
            used.update(differences)
            yield from recurse(value + 1)
            used.difference_update(differences)
            chosen.pop()

    yield from recurse(first + 1)


def valid_insertions(values: Sequence[int], low: int, high: int) -> Iterator[int]:
    """All exact Sidon-preserving insertions in [low, high]."""
    occupied = set(values)
    old_differences = positive_differences(values)
    for candidate in range(low, high + 1):
        if candidate in occupied:
            continue
        new_differences = [abs(candidate - value) for value in values]
        if 0 in new_differences or len(set(new_differences)) != len(new_differences):
            continue
        if any(difference in old_differences for difference in new_differences):
            continue
        yield candidate
