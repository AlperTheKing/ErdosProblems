"""Exact gates and loose-triangle component data for P98."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Component:
    folds: int
    triangles: int
    fold_ids: tuple[int, ...]
    triangle_ids: tuple[int, ...]

    @property
    def excess(self) -> int:
        return self.triangles - self.folds


def unordered_sum_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    out: dict[int, tuple[int, int]] = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in out:
                raise ValueError(("repeated sum", total, out[total], (left, right)))
            out[total] = (left, right)
    return out


def positive_differences(values: Sequence[int]) -> set[int]:
    out: set[int] = set()
    for j, right in enumerate(values):
        for left in values[:j]:
            difference = right - left
            if difference in out:
                raise ValueError(("repeated difference", difference))
            out.add(difference)
    return out


def canonical_folds(values: Sequence[int], h: int) -> list[tuple[int, int, int, int]]:
    sums = unordered_sum_map(values)
    folds = []
    for low in sorted(sums):
        high = low + h
        if high not in sums:
            continue
        a, c = sums[low]
        u, v = sums[high]
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v, h))
        folds.append((a, c, u, v))
    return folds


def correction_V(values: Sequence[int], h: int, b: int) -> int:
    if b not in (1, 2):
        raise ValueError(b)
    differences = positive_differences(values)
    return sum(
        a + c + b in differences
        for a, c, _u, _v in canonical_folds(values, h)
    )


def component_data(
    folds: Sequence[tuple[int, int, int, int]], values: Sequence[int]
) -> tuple[list[tuple[int, int, int]], list[Component]]:
    ac = {(a, c): i for i, (a, c, _u, _v) in enumerate(folds)}
    au = {(a, u): i for i, (a, _c, u, _v) in enumerate(folds)}
    cu = {(c, u): i for i, (_a, c, u, _v) in enumerate(folds)}
    if len(ac) != len(folds) or len(au) != len(folds) or len(cu) != len(folds):
        raise AssertionError("fold shadows are not linear")

    triangles: list[tuple[int, int, int]] = []
    for a, c in ac:
        for u in values:
            ids = (ac.get((a, c)), au.get((a, u)), cu.get((c, u)))
            if None in ids or ids[0] == ids[1] == ids[2]:
                continue
            if len(set(ids)) != 3:
                raise AssertionError(("partial canonical triangle", ids))
            triangles.append((int(ids[0]), int(ids[1]), int(ids[2])))

    parent = list(range(len(folds)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for triangle in triangles:
        union(triangle[0], triangle[1])
        union(triangle[0], triangle[2])

    fold_groups: dict[int, list[int]] = {}
    triangle_groups: dict[int, list[int]] = {}
    for fold_id in range(len(folds)):
        fold_groups.setdefault(find(fold_id), []).append(fold_id)
    for triangle_id, triangle in enumerate(triangles):
        triangle_groups.setdefault(find(triangle[0]), []).append(triangle_id)
    components = [
        Component(
            folds=len(fold_ids),
            triangles=len(triangle_groups.get(root, ())),
            fold_ids=tuple(fold_ids),
            triangle_ids=tuple(triangle_groups.get(root, ())),
        )
        for root, fold_ids in fold_groups.items()
    ]
    components.sort(key=lambda row: (row.excess, row.triangles, row.folds), reverse=True)
    return triangles, components


def score(values_input: Iterable[int], h: int) -> dict[str, object]:
    values = tuple(sorted(int(value) for value in values_input))
    if len(values) != len(set(values)) or not values:
        raise AssertionError("marks must be distinct")
    if values[0] < 0 or values[-1] != h - 1:
        raise AssertionError(("endpoint", values, h))
    unordered_sum_map(values)
    positive_differences(values)
    p = len(values)
    folds = canonical_folds(values, h)
    triangles, components = component_data(folds, values)
    maximum = components[0] if components else Component(0, 0, (), ())
    return {
        "B": list(values),
        "p": p,
        "h": h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "maximum_component_excess": maximum.excess,
        "maximum_component_folds": maximum.folds,
        "maximum_component_triangles": maximum.triangles,
    }


def audit(values_input: Iterable[int], h: int, b: int) -> dict[str, object]:
    row = score(values_input, h)
    values = tuple(int(value) for value in row["B"])
    if b not in (1, 2):
        raise AssertionError(("phase", b))
    sums = unordered_sum_map(values)
    differences = positive_differences(values)
    if not differences.isdisjoint(total + b for total in sums):
        raise AssertionError("literal hole")
    p = len(values)
    defect_numerator = 3 * p * p - p + 2 - 2 * h
    if defect_numerator <= 0 or defect_numerator % 2:
        raise AssertionError(("positive defect", defect_numerator))
    row["b"] = b
    row["delta"] = defect_numerator // 2
    return row


def normalized(values: Iterable[int]) -> tuple[int, ...]:
    row = tuple(sorted(set(int(value) for value in values)))
    if not row:
        return ()
    return tuple(value - row[0] for value in row)
