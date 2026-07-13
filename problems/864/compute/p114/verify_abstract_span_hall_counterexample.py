#!/usr/bin/env python3
"""Exact abstract counterexample to endpoint-plus-span Hall matching."""

N = 13
TRIPLES = [
    (6, 10, 11), (4, 6, 7), (5, 8, 10), (9, 10, 12),
    (3, 5, 9), (2, 4, 12), (1, 8, 11), (2, 6, 9),
    (2, 7, 11), (0, 8, 9), (0, 1, 3), (0, 4, 5),
    (3, 7, 12), (5, 11, 12), (6, 8, 12), (1, 5, 7),
    (3, 4, 11), (1, 4, 10), (2, 3, 10), (0, 7, 10),
]


def maximum_matching(neighbors):
    owner = {}

    def augment(left, seen):
        for right in neighbors[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in owner or augment(owner[right], seen):
                owner[right] = left
                return True
        return False

    return sum(augment(left, set()) for left in range(len(neighbors)))


def main():
    used_pairs = set()
    lengths = sorted({right - left for left, _middle, right in TRIPLES})
    length_id = {length: index for index, length in enumerate(lengths)}
    neighbors = []
    for left, middle, right in TRIPLES:
        assert left < middle < right
        pairs = {(left, middle), (left, right), (middle, right)}
        assert used_pairs.isdisjoint(pairs)
        used_pairs.update(pairs)
        neighbors.append([left, right, N + length_id[right - left]])
    matched = maximum_matching(neighbors)
    assert matched == 19 < len(TRIPLES) == 20
    print({"vertices": N, "triples": len(TRIPLES), "span_lengths": len(lengths), "matching": matched, "linear": True})


if __name__ == "__main__":
    main()
