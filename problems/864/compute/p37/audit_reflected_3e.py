"""Exact audits for P37's reflected same-parity three-free Sidon lane.

The finite portion verifies literal integer witnesses and P24's endpoint-
shadow injection.  The rational portion audits the continuum counterprofile
used to isolate what that injection still forgets.
"""

from __future__ import annotations

import argparse
import json
from bisect import bisect_right
from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement
from pathlib import Path


WITNESSES = (
    (2, (0, 1), 4, "optimal"),
    (3, (0, 1, 3), 10, "optimal"),
    (4, (0, 2, 5, 6), 19, "optimal"),
    (5, (0, 1, 3, 8, 12), 30, "optimal"),
    (6, (0, 1, 3, 8, 14, 18), 48, "optimal"),
    (7, (0, 5, 8, 9, 15, 26, 28), 68, "optimal"),
    (8, (0, 2, 3, 10, 16, 28, 33, 37), 85, "optimal"),
    (9, (0, 1, 3, 11, 15, 20, 36, 43, 49), 116, "optimal"),
    (10, (0, 1, 3, 8, 14, 26, 30, 47, 62, 71), 152, "feasible"),
    (11, (0, 1, 4, 6, 14, 30, 41, 50, 62, 69, 84), 191, "feasible"),
    (12, (0, 1, 4, 6, 14, 29, 36, 53, 69, 87, 96, 107), 240, "feasible"),
    (13, (0, 1, 4, 6, 13, 21, 35, 45, 71, 87, 98, 117, 135), 295, "feasible"),
    (14, (0, 1, 4, 9, 11, 23, 36, 51, 57, 75, 95, 124, 140, 157), 357, "feasible"),
)

DEGREE_SHARPNESS = (4, (0, 2, 8, 11), 23, "degree-sharp")


def unordered_pair_sums(values: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        values[i] + values[j]
        for i in range(len(values))
        for j in range(i, len(values))
    )


def triple_sums(values: tuple[int, ...], cutoff: int | None = None) -> set[int]:
    return {
        a + b + c
        for a, b, c in combinations_with_replacement(values, 3)
        if cutoff is None or a + b + c <= cutoff
    }


def reflected_e(lower: tuple[int, ...], center: int) -> tuple[int, ...]:
    width = lower[-1]
    gap = center - 2 * width
    assert gap > 0
    ruler = tuple(sorted(width - x for x in lower))
    return tuple(gap + 2 * z for z in ruler)


def audit_witness(
    q: int, lower: tuple[int, ...], center: int, solver_status: str
) -> dict[str, object]:
    assert len(lower) == q and lower[0] == 0
    values = reflected_e(lower, center)
    assert values[-1] == center
    assert len({value % 2 for value in values}) == 1

    pair_sums = tuple(sorted(unordered_pair_sums(values)))
    assert len(pair_sums) == q * (q + 1) // 2
    assert len(pair_sums) == len(set(pair_sums))
    all_triples = triple_sums(values)
    assert set(values).isdisjoint(all_triples)

    differences: dict[int, tuple[int, int]] = {}
    for i, x in enumerate(values):
        for j in range(i + 1, q):
            d = values[j] - x
            assert d not in differences
            differences[d] = (i, j)

    half_differences = {d // 2 for d in differences}
    half_sums = {s // 2 for s in pair_sums}
    assert all(d % 2 == 0 for d in differences)
    assert all(s % 2 == 0 for s in pair_sums)
    assert half_differences.isdisjoint(half_sums)
    assert len(half_differences | half_sums) == q * q

    parity = values[-1] % 2
    slots = set(range(1 if parity else 2, center + 1, 2))
    holes = slots.difference(values)
    shadow = triple_sums(values, center)
    assert shadow <= holes

    source_total = 0
    shadow_edge_total = 0
    hole_edge_total = 0
    minimum_source_slack: int | None = None
    target_edges: set[tuple[int, int]] = set()
    for d, (i, j) in differences.items():
        x, y = values[i], values[j]
        source = bisect_right(pair_sums, center - y)
        tau = sum(1 for u in shadow if u + d in shadow)
        hole_capacity = sum(1 for u in holes if u + d in holes)
        rank = lambda cutoff: bisect_right(values, cutoff)
        formula = (
            len(slots)
            - d // 2
            - rank(center - d)
            - q
            + rank(d)
            + 1
        )
        assert source <= tau <= hole_capacity == formula
        slack = tau - source
        minimum_source_slack = slack if minimum_source_slack is None else min(
            minimum_source_slack, slack
        )
        source_total += source
        shadow_edge_total += tau
        hole_edge_total += hole_capacity

        for pair_sum in pair_sums[:source]:
            edge = (x + pair_sum, y + pair_sum)
            assert edge[1] <= center
            assert edge[0] in shadow and edge[1] in shadow
            assert edge not in target_edges
            target_edges.add(edge)

    assert len(target_edges) == source_total
    assert source_total <= shadow_edge_total <= hole_edge_total
    assert source_total <= len(shadow) * (len(shadow) - 1) // 2

    blocks: dict[int, frozenset[int]] = {}
    for pair_sum in pair_sums:
        block = frozenset(value + pair_sum for value in values if value + pair_sum <= center)
        assert block <= shadow
        blocks[pair_sum] = block
    block_items = tuple(blocks.items())
    for a in range(len(block_items)):
        for b in range(a + 1, len(block_items)):
            assert len(block_items[a][1] & block_items[b][1]) <= 1
    assert sum(len(block) * (len(block) - 1) // 2 for block in blocks.values()) == source_total

    degrees: Counter[int] = Counter()
    for block in blocks.values():
        degrees.update(block)
    incidences = sum(map(len, blocks.values()))
    assert incidences == sum(degrees.values())
    assert incidences == sum(bisect_right(pair_sums, center - value) for value in values)

    triples_by_sum: dict[int, list[tuple[int, int, int]]] = {}
    for triple in combinations_with_replacement(values, 3):
        total = sum(triple)
        if total <= center:
            triples_by_sum.setdefault(total, []).append(triple)
    for total, triples in triples_by_sum.items():
        supports = [set(triple) for triple in triples]
        for i in range(len(supports)):
            for j in range(i + 1, len(supports)):
                assert supports[i].isdisjoint(supports[j])
        assert degrees[total] == sum(map(len, supports))
    # If a low triple sum covered every element, positivity would put the
    # maximum strictly below that sum, contradicting total <= center.
    assert all(degree <= q - 1 for degree in degrees.values())

    width = lower[-1]
    gap = center - 2 * width
    return {
        "q": q,
        "center": center,
        "center_over_q2": f"{center}/{q*q}",
        "gap": gap,
        "width": width,
        "solver_status": solver_status,
        "E": values,
        "shadow_size": len(shadow),
        "source_edges": source_total,
        "shadow_edges_at_represented_distances": shadow_edge_total,
        "hole_edges_at_represented_distances": hole_edge_total,
        "minimum_per_distance_slack": minimum_source_slack,
        "nonempty_translate_blocks": sum(bool(block) for block in blocks.values()),
        "translate_incidences": incidences,
        "maximum_shadow_degree": max(degrees.values(), default=0),
    }


def exhaustive_small_audit() -> dict[str, int]:
    valid_rulers = 0
    low_triple_targets = 0
    maximum_shadow_degree = 0

    for width in range(1, 15):
        for q in range(2, min(6, width + 1) + 1):
            for interior in combinations(range(1, width), q - 2):
                ruler = (0, *interior, width)
                sums = unordered_pair_sums(ruler)
                if len(sums) != len(set(sums)):
                    continue
                differences = {
                    ruler[j] - ruler[i]
                    for i in range(q)
                    for j in range(i + 1, q)
                }
                for gap in range(1, 16):
                    if differences.intersection(gap + total for total in sums):
                        continue
                    lower = tuple(sorted(width - value for value in ruler))
                    stats = audit_witness(q, lower, gap + 2 * width, "exhaustive")
                    valid_rulers += 1
                    low_triple_targets += int(stats["shadow_size"])
                    maximum_shadow_degree = max(
                        maximum_shadow_degree, int(stats["maximum_shadow_degree"])
                    )

    assert valid_rulers == 2861
    return {
        "valid_rulers": valid_rulers,
        "low_triple_targets": low_triple_targets,
        "maximum_shadow_degree": maximum_shadow_degree,
    }


def positive_part(value: Fraction) -> Fraction:
    return max(value, Fraction(0))


def difference_density(t: Fraction) -> Fraction:
    if 0 <= t <= 1:
        return 1 - t
    return Fraction(0)


def shifted_sum_density(t: Fraction, gap: Fraction) -> Fraction:
    if gap <= t <= gap + 1:
        return (t - gap) / 2
    if gap + 1 <= t <= gap + 2:
        return (gap + 2 - t) / 2
    return Fraction(0)


def audit_counterprofile(gap: Fraction, grid: int) -> dict[str, str | int]:
    assert 0 < gap < 1
    overlap = 1 - gap
    checked_endpoint_pairs = 0

    for i in range(grid + 1):
        x = Fraction(i, grid)
        for j in range(i + 1, grid + 1):
            y = Fraction(j, grid)
            delta = y - x
            source = positive_part(overlap - y) ** 2 / 4
            shadow_autocorrelation = positive_part(overlap - delta)
            hole_autocorrelation = 1 + gap / 2 - delta
            assert source <= shadow_autocorrelation <= hole_autocorrelation
            checked_endpoint_pairs += 1

    # The combined difference/shifted-sum occupation is P13's same-ruler law.
    for i in range((3 * grid) + 1):
        t = Fraction(i, grid)
        occupied = difference_density(t) + shifted_sum_density(t, gap)
        assert 0 <= occupied <= 1

    # Closed forms for all global P24 edge capacities in this profile.
    source_total = overlap**4 / 48
    incidences = overlap**3 / 12
    represented_shadow_edges = overlap**2 / 2 - overlap**3 / 6
    all_shadow_edges = overlap**2 / 2
    represented_hole_edges = Fraction(1, 3) + gap / 4
    assert source_total <= represented_shadow_edges <= all_shadow_edges
    assert represented_shadow_edges <= represented_hole_edges

    # Slot coordinates: A is uniform on [g/2, 1+g/2], while the low
    # threefold shadow is [3g/2, 1+g/2], of length 1-g.
    shadow_left = 3 * gap / 2
    shadow_right = 1 + gap / 2
    assert shadow_right - shadow_left == overlap

    return {
        "gap": str(gap),
        "span_coefficient": str(2 + gap),
        "grid": grid,
        "endpoint_pairs_checked": checked_endpoint_pairs,
        "shadow_interval_left": str(shadow_left),
        "shadow_interval_right": str(shadow_right),
        "normalized_source_edges": str(source_total),
        "normalized_translate_incidences": str(incidences),
        "normalized_shadow_size": str(overlap),
        "average_shadow_degree_over_q": str(overlap**2 / 12),
        "normalized_represented_shadow_edges": str(represented_shadow_edges),
        "normalized_all_shadow_edges": str(all_shadow_edges),
        "normalized_represented_hole_edges": str(represented_hole_edges),
    }


def audit_all(grid: int) -> dict[str, object]:
    witnesses = [audit_witness(*row) for row in WITNESSES]
    degree_sharpness = audit_witness(*DEGREE_SHARPNESS)
    assert degree_sharpness["E"] == (1, 7, 19, 23)
    assert degree_sharpness["maximum_shadow_degree"] == 3
    exhaustive_small = exhaustive_small_audit()
    profiles = [audit_counterprofile(Fraction(n, 16), grid) for n in range(1, 16)]
    return {
        "status": "PASS",
        "finite_witnesses": witnesses,
        "degree_sharpness": degree_sharpness,
        "exhaustive_small": exhaustive_small,
        "counterprofiles": profiles,
        "summary": {
            "finite_q_min": witnesses[0]["q"],
            "finite_q_max": witnesses[-1]["q"],
            "rational_gap_count": len(profiles),
            "grid": grid,
            "arithmetic": "integers and fractions only",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.grid < 1:
        parser.error("--grid must be positive")

    report = audit_all(args.grid)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="ascii")
    print(encoded)


if __name__ == "__main__":
    main()
