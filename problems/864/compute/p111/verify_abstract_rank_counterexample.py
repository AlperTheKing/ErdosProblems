#!/usr/bin/env python3
"""Exact abstract counterexample to the fold-only (S,E,dE) rank lemma."""

PRIME = 1_000_003
N = 20
EDGES = [
    (3, 7, 12), (0, 19, 12), (4, 6, 10), (13, 19, 15),
    (8, 12, 14), (3, 10, 5), (3, 6, 19), (2, 13, 12),
    (0, 8, 9), (13, 17, 16), (10, 19, 16), (5, 7, 14),
    (10, 17, 12), (2, 10, 11), (8, 17, 15), (9, 16, 15),
    (5, 17, 6), (3, 18, 8), (1, 14, 16), (0, 14, 4),
    (11, 18, 16), (3, 9, 14), (4, 8, 19), (1, 18, 6),
    (9, 13, 11), (4, 18, 15), (1, 4, 5), (11, 14, 19),
    (0, 7, 13), (4, 12, 11), (1, 17, 7), (10, 14, 18),
    (6, 8, 7), (5, 13, 8), (0, 18, 17), (2, 17, 14),
    (0, 11, 5), (3, 13, 4), (0, 6, 16), (5, 18, 19),
    (6, 14, 15), (2, 16, 4), (0, 15, 10), (9, 12, 18),
    (1, 19, 9), (4, 9, 7), (2, 6, 9), (2, 7, 18),
    (1, 15, 12), (1, 13, 10), (3, 15, 11),
]


def sparse_rank(rows):
    pivots = {}
    for source in rows:
        row = {column: value % PRIME for column, value in source.items() if value % PRIME}
        while row:
            pivot = max(row)
            value = row[pivot]
            if pivot not in pivots:
                inverse = pow(value, -1, PRIME)
                pivots[pivot] = {
                    column: coefficient * inverse % PRIME
                    for column, coefficient in row.items()
                }
                break
            for column, coefficient in pivots[pivot].items():
                row[column] = (row.get(column, 0) - value * coefficient) % PRIME
                if row[column] == 0:
                    del row[column]
    return len(pivots)


def main():
    used_pairs = set()
    rows = []
    for root, left, right in EDGES:
        assert root < left and root < right
        pairs = {tuple(sorted(pair)) for pair in ((root, left), (root, right), (left, right))}
        assert used_pairs.isdisjoint(pairs)
        used_pairs.update(pairs)
        phase = root + 1
        rows.append({
            root: 1, left: 1, right: 1,
            N + left: 1, N + right: -1,
            2 * N + left: phase, 2 * N + right: -phase,
        })
    rank = sparse_rank(rows)
    assert len(EDGES) == 51
    assert rank == 50
    print({"vertices": N, "edges": len(EDGES), "rank_mod_1000003": rank, "linear": True})


if __name__ == "__main__":
    main()
