#!/usr/bin/env python3
"""Exact two-sided codegree audit for the P65 outer fold graph.

The script uses integer arithmetic only.  It regenerates the full P65 P20
translation domain, then separately audits the stored positive P46/P20 rows
and the 37-row P45 large-profile slice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Iterable, Iterator, Sequence


ROOT = Path(__file__).resolve().parents[4]
P20_SAMPLES = ROOT / "problems/864/compute/p20/results/samples.jsonl"
P45_RESULTS = ROOT / "problems/864/compute/p45/audit_signed_carry_identity.json"
P46_RESULTS = ROOT / "problems/864/compute/p46/carry_statistics.json"
P65_RESULTS = ROOT / "problems/864/compute/p65/p20_hole_fold_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def positive_defect_baseline(p: int) -> int:
    return (3 * p * p - p + 2) // 2


def sum_pair_map(values: Sequence[int]) -> dict[int, tuple[int, int]]:
    pairs: dict[int, tuple[int, int]] = {}
    for index, left in enumerate(values):
        for right in values[index:]:
            total = left + right
            if total in pairs:
                raise AssertionError(("not integer Sidon", total, pairs[total], (left, right)))
            pairs[total] = (left, right)
    expected = len(values) * (len(values) + 1) // 2
    if len(pairs) != expected:
        raise AssertionError(("wrong sum count", len(pairs), expected))
    return pairs


def positive_differences(values: Sequence[int]) -> set[int]:
    differences: set[int] = set()
    for index, upper in enumerate(values):
        for lower in values[:index]:
            difference = upper - lower
            if difference in differences:
                raise AssertionError(("not integer Sidon", difference, lower, upper))
            differences.add(difference)
    return differences


def literal_hole(
    sums: Iterable[int], differences: set[int], translation: int, b: int
) -> bool:
    """Test Delta+(Z) disjoint from 2*translation+b+(Z+Z)."""

    gap = 2 * translation + b
    return all(total + gap not in differences for total in sums)


def reflected_parameters(row: dict[str, object]) -> tuple[tuple[int, ...], int, int] | None:
    """Reconstruct the P45/P65 ruler from one P20 reflected sample."""

    reflected = tuple(sorted(int(value) for value in row["A"]))
    size = len(reflected)
    sigma = int(row.get("exceptional_sum") or 0)
    multiplicity = int(row.get("exceptional_multiplicity") or 0)
    if size % 2 or sigma <= 0 or multiplicity != size // 2:
        return None
    support = set(reflected)
    if any(sigma - value not in support for value in reflected):
        return None
    lower = [value for value in reflected if 2 * value < sigma]
    if len(lower) != size // 2:
        return None
    top = max(lower)
    ruler = tuple(sorted(top - value for value in lower))
    gap = sigma - 2 * top
    b = 1 if gap % 2 else 2
    translation = (gap - b) // 2
    h = translation + ruler[-1] + 1
    return tuple(translation + value for value in ruler), h, b


def outer_fold_graph(
    normalized: tuple[int, ...], translation: int, h: int,
    normalized_sums: dict[int, tuple[int, int]] | None = None,
) -> dict[str, object]:
    """Build P65's exact outer graph and retain every complementary label."""

    if normalized[0] != 0:
        raise AssertionError(("ruler is not normalized", normalized[0]))
    values = tuple(translation + value for value in normalized)
    if values[-1] != h - 1:
        raise AssertionError(("max(B) != h-1", values[-1], h))
    sums = normalized_sums if normalized_sums is not None else sum_pair_map(normalized)
    folds: dict[tuple[int, int], dict[str, object]] = {}
    for low_sum in sorted(sums):
        high_sum = low_sum + h
        if high_sum not in sums:
            continue
        a0, c0 = sums[low_sum]
        u0, v0 = sums[high_sum]
        a, c, u, v = (translation + x for x in (a0, c0, u0, v0))
        if not a <= c < u <= v:
            raise AssertionError(("fold order", a, c, u, v, h))
        if (v - a) + (u - c) != h:
            raise AssertionError(("complementary lengths", a, c, u, v, h))
        if 2 * (v - a) < h or not (2 * a < h <= 2 * v):
            raise AssertionError(("outer edge is not long/bipartite", a, v, h))
        edge = (a, v)
        if edge in folds:
            raise AssertionError(("outer edge repeated", edge))
        folds[edge] = {
            "edge": [a, v],
            "inner_edge": [c, u],
            "low_pair": [a, c],
            "high_pair": [u, v],
            "low_sum": a + c,
            "high_sum": u + v,
        }

    left = tuple(value for value in values if 2 * value < h)
    right = tuple(value for value in values if 2 * value >= h)
    adjacency_left = {value: set() for value in left}
    adjacency_right = {value: set() for value in right}
    for x, y in folds:
        adjacency_left[x].add(y)
        adjacency_right[y].add(x)
    return {
        "B": values,
        "h": h,
        "left": left,
        "right": right,
        "folds": folds,
        "adjacency_left": adjacency_left,
        "adjacency_right": adjacency_right,
    }


def maximum_codegree(
    pivot_adjacency: dict[int, set[int]],
) -> tuple[int, tuple[int, int] | None, tuple[int, ...]]:
    """Return max codegree among vertices opposite the pivot side.

    Every pivot contributes one to each pair of its neighbors.  Thus the
    Counter is exactly the common-neighbor count, with no graph relaxation.
    """

    counts: Counter[tuple[int, int]] = Counter()
    for pivot in sorted(pivot_adjacency):
        for pair in combinations(sorted(pivot_adjacency[pivot]), 2):
            counts[pair] += 1
    if not counts:
        return 0, None, ()
    best = max(counts.values())
    pair = min(pair for pair, count in counts.items() if count == best)
    common = tuple(
        pivot for pivot in sorted(pivot_adjacency)
        if pair[0] in pivot_adjacency[pivot] and pair[1] in pivot_adjacency[pivot]
    )
    if len(common) != best:
        raise AssertionError(("codegree reconstruction", pair, best, common))
    return best, pair, common


def find_k33(graph: dict[str, object]) -> dict[str, object] | None:
    """Find an exact K3,3, preferring three left vertices."""

    orientations = (
        ("three_left_three_right", graph["adjacency_right"], True),
        ("three_right_three_left", graph["adjacency_left"], False),
    )
    for orientation, pivot_adjacency, triple_is_left in orientations:
        counts: Counter[tuple[int, int, int]] = Counter()
        for pivot in sorted(pivot_adjacency):
            for triple in combinations(sorted(pivot_adjacency[pivot]), 3):
                counts[triple] += 1
        candidates = sorted(triple for triple, count in counts.items() if count >= 3)
        if not candidates:
            continue
        triple = candidates[0]
        common = tuple(
            pivot for pivot in sorted(pivot_adjacency)
            if all(value in pivot_adjacency[pivot] for value in triple)
        )[:3]
        left, right = (triple, common) if triple_is_left else (common, triple)
        return biclique_witness(graph, orientation, left, right)
    return None


def bipartite_core(
    graph: dict[str, object], r: int,
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """Return the exact bipartite r-core; every Kr,r lies inside it."""

    adjacency_left = graph["adjacency_left"]
    adjacency_right = graph["adjacency_right"]
    active_left = set(adjacency_left)
    active_right = set(adjacency_right)
    while True:
        remove_left = {
            value for value in active_left
            if len(adjacency_left[value] & active_right) < r
        }
        active_left.difference_update(remove_left)
        remove_right = {
            value for value in active_right
            if len(adjacency_right[value] & active_left) < r
        }
        active_right.difference_update(remove_right)
        if not remove_left and not remove_right:
            break
    return (
        {value: adjacency_left[value] & active_right for value in active_left},
        {value: adjacency_right[value] & active_left for value in active_right},
    )


def find_krr(graph: dict[str, object], r: int) -> dict[str, object] | None:
    """Find Kr,r by exact r-neighbor subset multiplicities."""

    if r < 2:
        raise ValueError("r must be at least two")
    adjacency_left, adjacency_right = bipartite_core(graph, r)
    if len(adjacency_left) < r or len(adjacency_right) < r:
        return None
    orientations = [
        (
            sum(comb(len(neighbors), r) for neighbors in adjacency_right.values()),
            f"{r}_left_{r}_right", adjacency_right, True,
        ),
        (
            sum(comb(len(neighbors), r) for neighbors in adjacency_left.values()),
            f"{r}_right_{r}_left", adjacency_left, False,
        ),
    ]
    for _, orientation, pivot_adjacency, subset_is_left in sorted(
        orientations, key=lambda item: (item[0], item[1])
    ):
        counts: Counter[tuple[int, ...]] = Counter()
        for pivot in sorted(pivot_adjacency):
            for subset in combinations(sorted(pivot_adjacency[pivot]), r):
                counts[subset] += 1
                if counts[subset] < r:
                    continue
                common = tuple(
                    candidate for candidate in sorted(pivot_adjacency)
                    if all(value in pivot_adjacency[candidate] for value in subset)
                )[:r]
                left, right = (subset, common) if subset_is_left else (common, subset)
                return biclique_witness(graph, orientation, left, right)
        # Absence in either orientation is already conclusive.
        return None
    return None


def find_k44(graph: dict[str, object]) -> dict[str, object] | None:
    return find_krr(graph, 4)


def biclique_witness(
    graph: dict[str, object], orientation: str,
    left: Sequence[int], right: Sequence[int],
) -> dict[str, object]:
    folds = graph["folds"]
    edge_rows = []
    for x in left:
        for y in right:
            if (x, y) not in folds:
                raise AssertionError(("missing biclique edge", x, y))
            edge_rows.append(folds[(x, y)])
    return {
        "orientation": orientation,
        "left": list(left),
        "right": list(right),
        "edges": edge_rows,
    }


def graph_statistics(graph: dict[str, object]) -> dict[str, object]:
    left_codegree, left_pair, common_right = maximum_codegree(graph["adjacency_right"])
    right_codegree, right_pair, common_left = maximum_codegree(graph["adjacency_left"])
    result: dict[str, object] = {
        "C_S": len(graph["folds"]),
        "left_max_codegree": left_codegree,
        "right_max_codegree": right_codegree,
        "two_sided_max_codegree": max(left_codegree, right_codegree),
        "left_max_degree": max(map(len, graph["adjacency_left"].values()), default=0),
        "right_max_degree": max(map(len, graph["adjacency_right"].values()), default=0),
    }
    witnesses = []
    if left_pair is not None:
        witnesses.append({
            "orientation": "two_left_common_right",
            "pair": list(left_pair),
            "common_neighbors": list(common_right),
        })
    if right_pair is not None:
        witnesses.append({
            "orientation": "two_right_common_left",
            "pair": list(right_pair),
            "common_neighbors": list(common_left),
        })
    result["codegree_witnesses"] = witnesses
    k44 = find_k44(graph) if max(left_codegree, right_codegree) >= 4 else None
    result["contains_K4_4"] = k44 is not None
    result["K4_4_witness"] = k44
    balanced_order = 0
    balanced_witness = None
    if k44 is not None:
        balanced_order = 4
        balanced_witness = k44
        while True:
            candidate = find_krr(graph, balanced_order + 1)
            if candidate is None:
                break
            balanced_order += 1
            balanced_witness = candidate
    result["balanced_biclique_order_at_least_four"] = balanced_order
    result["maximum_balanced_biclique_witness_at_least_four"] = balanced_witness
    return result


def expand_codegree_witness(
    graph: dict[str, object], witness: dict[str, object], limit: int | None = None,
) -> dict[str, object]:
    pair = tuple(int(value) for value in witness["pair"])
    common = tuple(int(value) for value in witness["common_neighbors"])
    if limit is not None:
        common = common[:limit]
    if witness["orientation"] == "two_left_common_right":
        left, right = pair, common
    else:
        left, right = common, pair
    return biclique_witness(graph, str(witness["orientation"]), left, right)


def row_rank(row: dict[str, object]) -> tuple[object, ...]:
    return (
        int(row["p"]), int(row["h"]), int(row["b"]),
        tuple(int(value) for value in row["B"]), str(row["source_id"]),
    )


def row_record(
    source_id: str, b: int, graph: dict[str, object], stats: dict[str, object]
) -> dict[str, object]:
    values = tuple(int(value) for value in graph["B"])
    h = int(graph["h"])
    p = len(values)
    return {
        "source_id": source_id,
        "p": p,
        "h": h,
        "b": b,
        "delta": positive_defect_baseline(p) - h,
        "C_S": stats["C_S"],
        "left_max_codegree": stats["left_max_codegree"],
        "right_max_codegree": stats["right_max_codegree"],
        "two_sided_max_codegree": stats["two_sided_max_codegree"],
        "B": list(values),
    }


class DomainAudit:
    def __init__(self, name: str) -> None:
        self.name = name
        self.rows = 0
        self.graphs = 0
        self.codegree_histogram: Counter[int] = Counter()
        self.left_histogram: Counter[int] = Counter()
        self.right_histogram: Counter[int] = Counter()
        self.failure_count = 0
        self.k44_failure_count = 0
        self.balanced_order_histogram: Counter[int] = Counter()
        self.maximum_balanced_order = 0
        self.maximum_balanced_witness: dict[str, object] | None = None
        self.maximum_codegree = -1
        self.maximum_witness: dict[str, object] | None = None
        self.smallest_failure: dict[str, object] | None = None
        self.smallest_k44: dict[str, object] | None = None
        self.smallest_k33: dict[str, object] | None = None
        self.maximum_edges = -1
        self.maximum_edges_row: dict[str, object] | None = None

    def add(
        self, source_id: str, b: int, graph: dict[str, object],
        stats: dict[str, object], new_graph: bool,
    ) -> None:
        row = row_record(source_id, b, graph, stats)
        if int(row["delta"]) <= 0:
            raise AssertionError(("nonpositive defect entered domain", row))
        self.rows += 1
        self.graphs += int(new_graph)
        codegree = int(stats["two_sided_max_codegree"])
        self.codegree_histogram[codegree] += 1
        self.left_histogram[int(stats["left_max_codegree"])] += 1
        self.right_histogram[int(stats["right_max_codegree"])] += 1

        if codegree > self.maximum_codegree:
            self.maximum_codegree = codegree
            self.maximum_witness = self._attach_max_witness(row, graph, stats)
        elif codegree == self.maximum_codegree and self.maximum_witness is not None:
            candidate = self._attach_max_witness(row, graph, stats)
            if row_rank(candidate) < row_rank(self.maximum_witness):
                self.maximum_witness = candidate

        if int(row["C_S"]) > self.maximum_edges:
            self.maximum_edges = int(row["C_S"])
            self.maximum_edges_row = row
        elif int(row["C_S"]) == self.maximum_edges and self.maximum_edges_row is not None:
            if row_rank(row) < row_rank(self.maximum_edges_row):
                self.maximum_edges_row = row

        if codegree >= 4:
            self.failure_count += 1
            failure = self._attach_max_witness(row, graph, stats, limit=4)
            if self.smallest_failure is None or row_rank(failure) < row_rank(self.smallest_failure):
                self.smallest_failure = failure

        if bool(stats["contains_K4_4"]):
            self.k44_failure_count += 1
            k44 = {**row, "witness": stats["K4_4_witness"]}
            if self.smallest_k44 is None or row_rank(k44) < row_rank(self.smallest_k44):
                self.smallest_k44 = k44

        balanced_order = int(stats["balanced_biclique_order_at_least_four"])
        self.balanced_order_histogram[balanced_order] += 1
        if balanced_order > self.maximum_balanced_order:
            self.maximum_balanced_order = balanced_order
            self.maximum_balanced_witness = {
                **row,
                "witness": stats["maximum_balanced_biclique_witness_at_least_four"],
            }
        elif balanced_order == self.maximum_balanced_order and balanced_order >= 4:
            candidate = {
                **row,
                "witness": stats["maximum_balanced_biclique_witness_at_least_four"],
            }
            if self.maximum_balanced_witness is None or row_rank(candidate) < row_rank(
                self.maximum_balanced_witness
            ):
                self.maximum_balanced_witness = candidate

        if self.smallest_k33 is None:
            witness = find_k33(graph)
            if witness is not None:
                self.smallest_k33 = {**row, "witness": witness}

    @staticmethod
    def _attach_max_witness(
        row: dict[str, object], graph: dict[str, object], stats: dict[str, object],
        limit: int | None = None,
    ) -> dict[str, object]:
        target = int(stats["two_sided_max_codegree"])
        choices = [
            witness for witness in stats["codegree_witnesses"]
            if len(witness["common_neighbors"]) == target
        ]
        if not choices:
            if target != 0:
                raise AssertionError(("missing maximum codegree witness", target))
            return {**row, "witness": None}
        expanded = [expand_codegree_witness(graph, witness, limit) for witness in choices]
        return {**row, "witness": min(expanded, key=lambda item: json.dumps(item, sort_keys=True))}

    def finish(self) -> dict[str, object]:
        if self.rows == 0:
            raise AssertionError(("empty domain", self.name))
        return {
            "name": self.name,
            "row_count": self.rows,
            "distinct_graph_count": self.graphs,
            "maximum_pairwise_codegree": self.maximum_codegree,
            "K2_4_or_K4_2_failure_count": self.failure_count,
            "K4_4_failure_count": self.k44_failure_count,
            "two_sided_codegree_histogram": {
                str(key): value for key, value in sorted(self.codegree_histogram.items())
            },
            "left_codegree_histogram": {
                str(key): value for key, value in sorted(self.left_histogram.items())
            },
            "right_codegree_histogram": {
                str(key): value for key, value in sorted(self.right_histogram.items())
            },
            "maximum_codegree_witness": self.maximum_witness,
            "smallest_codegree_four_witness": self.smallest_failure,
            "smallest_K4_4_witness": self.smallest_k44,
            "maximum_balanced_biclique_order": max(
                self.maximum_balanced_order, 3 if self.smallest_k33 is not None else 0
            ),
            "maximum_balanced_biclique_witness": (
                self.maximum_balanced_witness
                if self.maximum_balanced_order >= 4 else self.smallest_k33
            ),
            "balanced_order_at_least_four_histogram": {
                str(key): value for key, value in sorted(self.balanced_order_histogram.items())
            },
            "contains_K3_3": self.smallest_k33 is not None,
            "smallest_K3_3_witness": self.smallest_k33,
            "maximum_C_S": self.maximum_edges,
            "maximum_C_S_row": self.maximum_edges_row,
        }


def load_p20_rulers() -> list[dict[str, object]]:
    rulers: dict[tuple[int, ...], dict[str, object]] = {}
    with P20_SAMPLES.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            parameters = reflected_parameters(row)
            if parameters is None:
                continue
            values, _, _ = parameters
            translation = values[0]
            normalized = tuple(value - translation for value in values)
            item = rulers.setdefault(normalized, {"Z": normalized, "source_ids": []})
            item["source_ids"].append(str(row["sample_id"]))
    return sorted(
        rulers.values(),
        key=lambda item: (len(item["Z"]), item["Z"][-1], item["Z"]),
    )


def audit_p20_translations() -> dict[str, object]:
    audit = DomainAudit("all positive-defect literal-hole translations of P20 rulers")
    rulers = load_p20_rulers()
    if len(rulers) != 133:
        raise AssertionError(("P20 ruler count", len(rulers)))
    for item in rulers:
        normalized = tuple(int(value) for value in item["Z"])
        p = len(normalized)
        width = normalized[-1]
        sums = sum_pair_map(normalized)
        differences = positive_differences(normalized)
        max_translation = positive_defect_baseline(p) - width - 2
        source_id = min(str(value) for value in item["source_ids"])
        for translation in range(max_translation + 1):
            admissible_b = [
                b for b in (1, 2)
                if literal_hole(sums, differences, translation, b)
            ]
            if not admissible_b:
                continue
            h = translation + width + 1
            graph = outer_fold_graph(normalized, translation, h, sums)
            stats = graph_statistics(graph)
            for index, b in enumerate(admissible_b):
                audit.add(source_id, b, graph, stats, new_graph=index == 0)
    result = audit.finish()
    if result["row_count"] != 165225:
        raise AssertionError(("P20 translation count", result["row_count"]))
    return result


def stored_positive_rows() -> list[dict[str, object]]:
    payload = json.loads(P46_RESULTS.read_text(encoding="ascii"))
    rows = [row for row in payload["p20"]["reports"] if int(row["delta"]) > 0]
    return sorted(rows, key=lambda row: (
        int(row["p"]), int(row["h"]), int(row["b"]),
        tuple(int(value) for value in row["B"]), str(row["source_id"]),
    ))


def audit_stored_rows(
    name: str, rows: Sequence[dict[str, object]], expected_count: int,
) -> dict[str, object]:
    audit = DomainAudit(name)
    for row in rows:
        values = tuple(int(value) for value in row["B"])
        h = int(row["h"])
        b = int(row["b"])
        if values[-1] != h - 1:
            raise AssertionError(("stored max(B)", row["source_id"]))
        translation = values[0]
        normalized = tuple(value - translation for value in values)
        sums = sum_pair_map(normalized)
        differences = positive_differences(normalized)
        if not literal_hole(sums, differences, translation, b):
            raise AssertionError(("stored row lacks literal hole", row["source_id"]))
        graph = outer_fold_graph(normalized, translation, h, sums)
        stats = graph_statistics(graph)
        if int(stats["C_S"]) != int(row["sum_collision_residues"]):
            raise AssertionError(("stored C_S mismatch", row["source_id"]))
        audit.add(str(row["source_id"]), b, graph, stats, new_graph=True)
    result = audit.finish()
    if result["row_count"] != expected_count:
        raise AssertionError((name, result["row_count"], expected_count))
    return result


def self_test() -> None:
    k33_left = {x: {10, 11, 12} for x in (0, 1, 2)}
    k33_right = {y: {0, 1, 2} for y in (10, 11, 12)}
    assert maximum_codegree(k33_right)[0] == 3
    assert maximum_codegree(k33_left)[0] == 3

    k24_left = {0: {10, 11, 12, 13}, 1: {10, 11, 12, 13}}
    k24_right = {y: {0, 1} for y in (10, 11, 12, 13)}
    assert maximum_codegree(k24_right)[0] == 4
    assert maximum_codegree(k24_left)[0] == 2

    k42_left = {x: {10, 11} for x in (0, 1, 2, 3)}
    k42_right = {10: {0, 1, 2, 3}, 11: {0, 1, 2, 3}}
    assert maximum_codegree(k42_right)[0] == 2
    assert maximum_codegree(k42_left)[0] == 4

    left = (0, 1, 2, 3)
    right = (10, 11, 12, 13)
    folds = {
        (x, y): {
            "edge": [x, y], "inner_edge": [x, y],
            "low_pair": [x, x], "high_pair": [y, y],
            "low_sum": 2 * x, "high_sum": 2 * y,
        }
        for x in left for y in right
    }
    k44_graph = {
        "adjacency_left": {x: set(right) for x in left},
        "adjacency_right": {y: set(left) for y in right},
        "folds": folds,
    }
    assert find_k44(k44_graph) is not None
    assert find_krr(k44_graph, 5) is None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).resolve().parent / "outer_codegree_audit.json",
    )
    args = parser.parse_args()
    self_test()

    p20_translations = audit_p20_translations()
    positive_rows = stored_positive_rows()
    p20_stored = audit_stored_rows(
        "stored positive-defect P46/P20 rows", positive_rows, 134,
    )

    p45 = json.loads(P45_RESULTS.read_text(encoding="ascii"))
    large_ids = {
        str(row["sample_id"]) for row in p45["large_profile_audit"]["profiles"]
    }
    if len(large_ids) != 37:
        raise AssertionError(("large profile id count", len(large_ids)))
    large_rows = [row for row in positive_rows if str(row["source_id"]) in large_ids]
    stored_large = audit_stored_rows(
        "stored P45 large rows (p>=72, positive defect)", large_rows, 37,
    )

    p65 = json.loads(P65_RESULTS.read_text(encoding="ascii"))
    if int(p65["source_rulers"]) != 133 or int(p65["admissible_translations"]) != 165225:
        raise AssertionError("P65 source-domain metadata changed")

    domains = {
        "p20_all_translations": p20_translations,
        "p20_stored_positive_rows": p20_stored,
        "stored_large_rows": stored_large,
    }
    payload = {
        "schema_version": 1,
        "arithmetic": "exact integers",
        "definitions": {
            "outer_edge": (
                "For a<=c<u<=v and a+c+h=u+v, the fold contributes edge (a,v); "
                "the complementary inner edge is (c,u)."
            ),
            "left_part": "{x in B: 2*x<h}",
            "right_part": "{x in B: 2*x>=h}",
            "left_pair_codegree": "|N(x) intersect N(y)| for distinct left vertices",
            "right_pair_codegree": "|N(x) intersect N(y)| for distinct right vertices",
            "forbidden_test": "both pair-codegrees <=3, equivalently no K2,4 and no K4,2",
        },
        "input_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in (P20_SAMPLES, P45_RESULTS, P46_RESULTS, P65_RESULTS)
        },
        "domains": domains,
        "all_rows_K2_4_and_K4_2_free": all(
            int(domain["K2_4_or_K4_2_failure_count"]) == 0
            for domain in domains.values()
        ),
        "all_rows_K4_4_free": all(
            int(domain["K4_4_failure_count"]) == 0
            for domain in domains.values()
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        name: {
            "rows": domain["row_count"],
            "max_pairwise_codegree": domain["maximum_pairwise_codegree"],
            "K2_4_or_K4_2_failures": domain["K2_4_or_K4_2_failure_count"],
            "K4_4_failures": domain["K4_4_failure_count"],
            "maximum_balanced_biclique_order": domain["maximum_balanced_biclique_order"],
            "contains_K3_3": domain["contains_K3_3"],
        }
        for name, domain in domains.items()
    }, indent=2))


if __name__ == "__main__":
    main()
