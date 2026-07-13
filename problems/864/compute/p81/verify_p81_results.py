#!/usr/bin/env python3
"""Independent exact audit of the P81 artifacts used in the write-up."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
P81 = ROOT / "problems/864/compute/p81"


def load(name: str) -> dict:
    return json.loads((P81 / name).read_text(encoding="utf-8"))


def verify_sparse() -> None:
    data = load("sparse_k66_witness.json")
    assert data["found"]
    row = data["witness"]
    values = row["B"]
    p, h, b = len(values), row["h"], row["b"]
    sums = Counter(
        values[i] + values[j]
        for i in range(p)
        for j in range(i, p)
    )
    differences = Counter(
        values[j] - values[i]
        for i in range(p)
        for j in range(i + 1, p)
    )
    assert p == 85 and values[-1] == h - 1
    assert len(sums) == p * (p + 1) // 2 and max(sums.values()) == 1
    assert len(differences) == p * (p - 1) // 2 and max(differences.values()) == 1
    assert set(differences).isdisjoint({total + b for total in sums})
    assert row["delta"] == (3 * p * p - p + 2) // 2 - h < 0
    edge_map = {tuple(edge["outer_edge"]): edge for edge in row["edges"]}
    assert set(edge_map) == {
        (left, right) for left in row["left"] for right in row["right"]
    }
    for edge in edge_map.values():
        assert edge["low_sum"] + h == edge["high_sum"]


def main() -> None:
    endpoint = load("p79_k55_endpoint_orders.json")
    assert endpoint["source_id"] == "singer-e82f2d6a63ca"
    low = endpoint["tests"]["inner_low"]
    high = endpoint["tests"]["inner_high"]
    assert [row["count"] for row in low["row_monotone_triples"]] == [3, 2, 2, 2, 3]
    assert [row["count"] for row in high["row_monotone_triples"]] == [3, 1, 2, 3, 3]
    assert low["aligned_3x3_count"] == high["aligned_3x3_count"] == 0
    assert len(low["shared_triples_on_at_least_three_rows"]) == 1
    assert len(high["shared_triples_on_at_least_three_rows"]) == 1

    first = load("singer_q151_cut_scan.json")
    assert (first["distinct_cuts_scanned"], first["K5_5_cuts"], first["K6_6_found"]) == (
        4712,
        12,
        False,
    )
    neighboring = [131, 137, 139, 149, 157, 163, 167]
    rows = [load(f"singer_q{q}_cut_scan.json") for q in neighboring]
    assert sum(row["distinct_cuts_scanned"] for row in rows) == 33600
    assert sum(row["K5_5_cuts"] for row in rows) == 54
    assert not any(row["K6_6_found"] for row in rows)

    shards = [load(f"singer_q167_u512_shard{index:02d}.json") for index in range(16)]
    assert sum(row["unit_classes_scanned"] for row in shards) == 512
    assert sum(row["distinct_cuts_scanned"] for row in shards) == 86016
    assert sum(row["K5_5_cuts"] for row in shards) == 320
    assert not any(row["K6_6_found"] for row in shards)

    centers = load("singer_q167_k55_all_centers.json")
    assert centers["retained_cuts"] == 16
    assert centers["hole_shifts_scanned"] == 27902
    assert centers["K5_5_shifts"] == 22
    assert not centers["K6_6_found"]

    range_rows = [load(f"singer_q{q}_range_u32.json") for q in (191, 193, 197, 199, 211)]
    assert sum(row["distinct_cuts_scanned"] for row in range_rows) == 31872
    assert sum(row["K5_5_cuts"] for row in range_rows) == 13
    assert not any(row["K6_6_found"] for row in range_rows)

    repair = load("p75_rectangle_repair.json")
    assert repair["initial_score"] == repair["final_score"] == 30
    assert repair["distinct_valid_neighbors_examined"] == 1
    assert not repair["K6_6_found"]
    optimization = load("cpsat_p75_rectangle_optimization.json")
    assert optimization["status"] == "FEASIBLE"
    assert optimization["objective_value"] == 30
    assert optimization["best_objective_bound"] == 36
    assert all(load(f"cpsat_k66_pairs_seed{seed}.json")["status"] == "UNKNOWN" for seed in range(1, 9))

    verify_sparse()
    print(
        json.dumps(
            {
                "status": "verified",
                "first_center_cuts": 4712 + 33600 + 86016 + 31872,
                "first_center_K5_5": 12 + 54 + 320 + 13,
                "all_center_hole_shifts": 27902,
                "K6_6": 0,
                "sparse_negative_defect_K6_6": 1,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
