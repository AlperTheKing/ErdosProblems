"""Exhaustive exact check of the P21 signed-ruler/3-free-Sidon bijection."""

from __future__ import annotations

from itertools import combinations


def is_sidon(values: tuple[int, ...]) -> bool:
    sums = [values[i] + values[j] for i in range(len(values)) for j in range(i, len(values))]
    return len(sums) == len(set(sums))


def is_three_free(values: tuple[int, ...]) -> bool:
    value_set = set(values)
    three = {
        values[i] + values[j] + values[k]
        for i in range(len(values))
        for j in range(i, len(values))
        for k in range(j, len(values))
    }
    return value_set.isdisjoint(three)


def is_signed_ruler(values: tuple[int, ...]) -> bool:
    gap = values[0]
    points = [(x - gap) // 2 for x in values]
    labels = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            labels.append(points[j] - points[i])
        for j in range(i, len(points)):
            labels.append(gap + points[i] + points[j])
    return len(labels) == len(set(labels)) == len(points) ** 2


def main() -> None:
    checked = 0
    positive = 0
    for maximum in range(1, 21):
        universe = tuple(range(1, maximum + 1))
        for size in range(1, len(universe) + 1):
            for values in combinations(universe, size):
                if any((x - values[0]) % 2 for x in values):
                    continue
                checked += 1
                left = is_sidon(values) and is_three_free(values)
                right = is_signed_ruler(values)
                assert left == right, values
                positive += int(left)
    print({"maximum_checked": 20, "same_parity_sets": checked, "equivalent_positive_sets": positive})


if __name__ == "__main__":
    main()
