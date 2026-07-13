#!/usr/bin/env python3
"""Cross-check all P53 certificates against their generating arithmetic."""

from __future__ import annotations

import json
from pathlib import Path

from incidence_kst_audit import audit as incidence_audit
from shifted_sum_overlap import audit as overlap_audit


HERE = Path(__file__).resolve().parent


def load(name: str) -> dict[str, object]:
    return json.loads((HERE / name).read_text(encoding="ascii"))


def main() -> None:
    counterexample = load("counterexample_p25_h494.json")
    reconstructed = overlap_audit(
        counterexample["hypotheses"]["B"], int(counterexample["hypotheses"]["h"])
    )
    assert reconstructed == counterexample
    assert counterexample["claim"] == {
        "C_S": 49,
        "C_S_minus_bound": 2,
        "holds": False,
        "two_p_minus_three": 47,
    }
    assert counterexample["checks"]["unordered_sum_support"] == 325
    assert counterexample["checks"]["positive_difference_support"] == 300
    assert len(counterexample["collisions"]) == 49
    assert counterexample["central_interval_graph"]["crossing_edge_pairs_in_mark_order"] == 304

    exhaustive = load("exhaustive_width45_all_translations.json")
    assert exhaustive["normalized_rulers"] == 745_733
    assert exhaustive["translations"] == 30_326_669
    assert exhaustive["smallest_failure"] is None
    assert exhaustive["ruler_sha256"] == (
        "772e239cc1a5d1a02f7f2d9a63f5e53fab579cb472834c14446d3bd97e2e9e53"
    )

    dense = load("dense_optimal_rulers_scan.json")
    assert dense["failure_count"] == 12
    dense_smallest = dense["smallest_failure"]
    assert dense_smallest["hypotheses"]["p"] == 26
    assert dense_smallest["hypotheses"]["h"] == 494
    assert dense_smallest["claim"]["C_S"] == 51

    minimization = load("counterexample_subset_minimization.json")
    assert all(row["status"] == "OPTIMAL" for row in minimization["per_size"])
    by_size = {row["subset_size"]: row for row in minimization["per_size"]}
    assert by_size[24]["maximum_C_S"] == 44
    assert by_size[25]["maximum_C_S"] == 49
    assert by_size[26]["maximum_C_S"] == 51
    assert minimization["smallest_proved_failure"]["hypotheses"]["p"] == 25

    incidence = incidence_audit()
    fold = incidence["fold_repair"]
    assert (fold["delta"], fold["C_S"], fold["C_D"], fold["residual"]) == (
        138, 0, 0, 138
    )
    assert (fold["ratio_numerator"], fold["ratio_denominator"]) == (19044, 4913)
    carry1 = incidence["carry_graphs"]["1"]["expanded_difference_edge_graph"]
    carry2 = incidence["carry_graphs"]["2"]["expanded_difference_edge_graph"]
    assert (carry1["edges"], carry1["maximum_left_codegree"]) == (94, 6)
    assert (carry2["edges"], carry2["maximum_left_codegree"]) == (67, 6)
    assert carry1["maximum_C4_free_subgraph"]["minimum_edge_deletions"] == 34
    assert carry2["maximum_C4_free_subgraph"]["minimum_edge_deletions"] == 17

    print(json.dumps({
        "counterexample": "p=25,h=494,C_S=49>47",
        "exhaustive": "745733 rulers; 30326669 translations; 0 failures",
        "subset_minimization": "all statuses OPTIMAL; first induced failure p=25",
        "incidence": "Bose p=17: direct carry graphs require 34 and 17 C4 deletions",
    }, indent=2))


if __name__ == "__main__":
    main()
