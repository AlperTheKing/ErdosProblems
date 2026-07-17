"""Exact audit of the neighbourhood-completion averaging lemma on C5[4]."""

from fractions import Fraction
from itertools import combinations


N = 20
PART_SIZE = 4
H = N // 2
VERTICES = tuple(range(N))


def part(v: int) -> int:
    return v // PART_SIZE


def adjacent(u: int, v: int) -> bool:
    if u == v:
        return False
    delta = (part(u) - part(v)) % 5
    return delta in (1, 4)


def edge_count(vertices) -> int:
    return sum(adjacent(u, v) for u, v in combinations(vertices, 2))


def main() -> None:
    # Structural audit of the labelled graph.
    triangles = [
        triple
        for triple in combinations(VERTICES, 3)
        if edge_count(triple) == 3
    ]
    assert not triangles

    rows = []
    for v in VERTICES:
        neighborhood = tuple(u for u in VERTICES if adjacent(u, v))
        outside = tuple(
            u for u in VERTICES if u != v and u not in neighborhood
        )
        d = len(neighborhood)
        b = len(outside)
        t = H - d
        q = sum(adjacent(u, w) for u in neighborhood for w in outside)
        r = edge_count(outside)
        expected = Fraction(q * t, b) + Fraction(r * t * (t - 1), b * (b - 1))

        completion_counts = [
            edge_count(neighborhood + completion)
            for completion in combinations(outside, t)
        ]
        enumerated_average = Fraction(sum(completion_counts), len(completion_counts))
        assert expected == enumerated_average
        rows.append((v, d, b, t, q, r, expected, min(completion_counts)))

    assert len(set(row[1:] for row in rows)) == 1
    _, d, b, t, q, r, expected, minimum = rows[0]
    threshold = Fraction(N * N, 50)
    assert (d, b, t, q, r) == (8, 11, 2, 56, 16)
    assert expected == Fraction(576, 55)
    assert expected > threshold
    assert minimum == threshold == 8

    all_half_counts = [edge_count(half) for half in combinations(VERTICES, H)]
    assert min(all_half_counts) == 8

    print("graph=C5[4]")
    print(f"n={N} h={H} triangles={len(triangles)}")
    print(f"all_vertices: d={d} b={b} t={t} q={q} r={r}")
    print(f"completion_expectation={expected} threshold={threshold}")
    print(f"minimum_neighborhood_completion={minimum}")
    print(f"minimum_over_all_half_sets={min(all_half_counts)}")
    print("verdict=COUNTEREXAMPLE_TO_AVERAGING_LEMMA")


if __name__ == "__main__":
    main()
