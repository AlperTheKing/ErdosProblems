#!/usr/bin/env python3
"""Exact small-template audit for the n=19 SSNC counting mechanism.

This is deliberately not a general graph search.  It enumerates the 2,304
translation-invariant orientations of Z/19Z having one missing inverse pair,
and checks the literal strict-second-neighbour predicate and the equality-case
incidence ledger.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product


N = 19


def new_second_neighbours(out: list[set[int]], v: int) -> set[int]:
    reached = {w for x in out[v] for w in out[x]}
    return reached - out[v] - {v}


def build_circulant(step_set: set[int]) -> list[set[int]]:
    return [{(v + step) % N for step in step_set} for v in range(N)]


def audit_template(step_set: set[int], missing_step: int) -> dict[str, object]:
    out = build_circulant(step_set)
    assert all(len(row) == 8 for row in out)
    assert all(v not in out[v] for v in range(N))
    assert all(not (w in out[v] and v in out[w]) for v in range(N) for w in range(N))

    missing = [
        {w for w in range(N) if w != v and w not in out[v] and v not in out[w]}
        for v in range(N)
    ]
    assert all(len(row) == 2 for row in missing)
    assert missing[0] == {missing_step, (-missing_step) % N}

    n2 = [new_second_neighbours(out, v) for v in range(N)]
    unreachable = [set(range(N)) - {v} - out[v] - n2[v] for v in range(N)]
    target_roots = [
        {v for v in range(N) if u in unreachable[v]} for u in range(N)
    ]

    # Equality-case ledger: e=0, mu=2, t=2, and a hypothetical hit must
    # have exactly three unreachable targets and three roots per target.
    assert sum(map(len, unreachable)) == sum(map(len, target_roots))
    strict_hit = all(len(row) < 8 for row in n2)

    return {
        "missing_step": missing_step,
        "steps": tuple(sorted(step_set)),
        "n2_size": len(n2[0]),
        "unreachable_size": len(unreachable[0]),
        "target_root_size": len(target_roots[0]),
        "strict_hit": strict_hit,
    }


def main() -> None:
    histogram: Counter[int] = Counter()
    records: list[dict[str, object]] = []

    # The nine inverse pairs are represented by 1,...,9.  Choose one pair to
    # omit, then one direction from each of the remaining eight pairs.
    for missing_step in range(1, 10):
        representatives = [d for d in range(1, 10) if d != missing_step]
        for choices in product((0, 1), repeat=len(representatives)):
            steps = {
                d if choice == 0 else (-d) % N
                for d, choice in zip(representatives, choices, strict=True)
            }
            record = audit_template(steps, missing_step)
            histogram[int(record["n2_size"])] += 1
            records.append(record)

    hits = [record for record in records if bool(record["strict_hit"])]
    minimum = min(int(record["n2_size"]) for record in records)
    minimizers = [record for record in records if int(record["n2_size"]) == minimum]

    print(
        {
            "status": "HIT" if hits else "NO_TEMPLATE_HIT",
            "templates": len(records),
            "minimum_n2_size": minimum,
            "strict_hits": len(hits),
            "n2_histogram": dict(sorted(histogram.items())),
        }
    )
    print({"first_minimizers": minimizers[:10]})
    if hits:
        print({"first_hits": hits[:10]})

    audit_q19_triangle_switches()


def literal_ledger(out: list[int]) -> tuple[bool, tuple[int, ...], tuple[int, ...]]:
    all_vertices = (1 << N) - 1
    degrees = tuple(mask.bit_count() for mask in out)
    second_sizes: list[int] = []
    for v, mask in enumerate(out):
        reached = 0
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            x = bit.bit_length() - 1
            reached |= out[x]
            remaining ^= bit
        new_second = reached & ~mask & ~(1 << v) & all_vertices
        second_sizes.append(new_second.bit_count())
    second = tuple(second_sizes)
    return all(s < d for s, d in zip(second, degrees, strict=True)), degrees, second


def set_rows_to_masks(out_sets: list[set[int]]) -> list[int]:
    return [sum(1 << w for w in row) for row in out_sets]


def audit_q19_triangle_switches() -> None:
    bases = [
        {2, 4, 6, 8, 10, 12, 14, 16},
        {3, 5, 7, 9, 11, 13, 15, 17},
    ]
    # These are exactly the two fixed-missing-step circulants with |N++|=8.
    tested = 0
    best_gap = N
    best_violators = N
    best: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []

    for steps in bases:
        base = set_rows_to_masks(build_circulant(steps))
        for triple in combinations(range(N), 3):
            a, b, c = triple
            vertices = set(triple)
            local_outdegrees = [
                sum((base[v] >> w) & 1 for w in vertices - {v}) for v in triple
            ]
            if local_outdegrees != [1, 1, 1]:
                continue

            out = base.copy()
            for v, w in combinations(triple, 2):
                if (out[v] >> w) & 1:
                    out[v] ^= 1 << w
                    out[w] |= 1 << v
                else:
                    assert (out[w] >> v) & 1
                    out[w] ^= 1 << v
                    out[v] |= 1 << w

            hit, degrees, second = literal_ledger(out)
            assert degrees == (8,) * N
            tested += 1
            gap = max(s - 8 for s in second)
            violators = sum(s >= 8 for s in second)
            record = {
                "base_steps": tuple(sorted(steps)),
                "reversed_triangle": triple,
                "second_sizes": second,
                "max_n2_minus_out": gap,
                "non_strict_vertices": violators,
            }
            key = (gap, violators)
            if key < (best_gap, best_violators):
                best_gap, best_violators = key
                best = [record]
            elif key == (best_gap, best_violators) and len(best) < 10:
                best.append(record)
            if hit:
                hits.append(record)

    print(
        {
            "status": "HIT" if hits else "NO_Q19_TRIANGLE_SWITCH_HIT",
            "templates": tested,
            "best_max_n2_minus_out": best_gap,
            "fewest_non_strict_vertices_at_best_gap": best_violators,
            "strict_hits": len(hits),
        }
    )
    print({"first_q19_triangle_best": best[:10]})
    if hits:
        print({"first_q19_triangle_hits": hits[:10]})


if __name__ == "__main__":
    main()
