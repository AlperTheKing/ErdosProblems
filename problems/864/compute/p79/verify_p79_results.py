#!/usr/bin/env python3
"""Re-hash inputs and reconstruct every extremal witness in the P79 outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from audit_outer_codegrees import (
    ROOT,
    graph_statistics,
    literal_hole,
    outer_fold_graph,
    positive_defect_baseline,
    positive_differences,
    sum_pair_map,
)


HERE = Path(__file__).resolve().parent
OUTER = HERE / "outer_codegree_audit.json"
GLOBAL = HERE / "global_shift_bound_audit.json"
NAMED = HERE / "named_witness_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes(payload: dict[str, object]) -> None:
    for relative, expected in payload["input_sha256"].items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(("input hash mismatch", relative, expected, actual))


def verify_biclique(graph: dict[str, object], witness: dict[str, object] | None) -> None:
    if witness is None:
        return
    left = tuple(int(value) for value in witness["left"])
    right = tuple(int(value) for value in witness["right"])
    stored_edges = witness["edges"]
    if len(stored_edges) != len(left) * len(right):
        raise AssertionError(("biclique edge count", len(left), len(right), len(stored_edges)))
    folds = graph["folds"]
    for x in left:
        for y in right:
            if (x, y) not in folds:
                raise AssertionError(("missing biclique edge", x, y))


def verify_outer_record(record: dict[str, object] | None) -> None:
    if record is None:
        return
    values = tuple(int(value) for value in record["B"])
    h = int(record["h"])
    b = int(record["b"])
    translation = values[0]
    normalized = tuple(value - translation for value in values)
    sums = sum_pair_map(normalized)
    differences = positive_differences(normalized)
    if not literal_hole(sums, differences, translation, b):
        raise AssertionError(("reported row lacks literal hole", record["source_id"]))
    graph = outer_fold_graph(normalized, translation, h, sums)
    stats = graph_statistics(graph)
    p = len(values)
    expected = {
        "p": p,
        "delta": positive_defect_baseline(p) - h,
        "C_S": stats["C_S"],
        "left_max_codegree": stats["left_max_codegree"],
        "right_max_codegree": stats["right_max_codegree"],
        "two_sided_max_codegree": stats["two_sided_max_codegree"],
    }
    for key, value in expected.items():
        if int(record[key]) != int(value):
            raise AssertionError(("record mismatch", key, record[key], value))
    verify_biclique(graph, record.get("witness"))


def verify_outer() -> dict[str, object]:
    payload = json.loads(OUTER.read_text(encoding="ascii"))
    verify_hashes(payload)
    expected_counts = {
        "p20_all_translations": (165225, 92396),
        "p20_stored_positive_rows": (134, 134),
        "stored_large_rows": (37, 37),
    }
    for name, (rows, graphs) in expected_counts.items():
        domain = payload["domains"][name]
        if (int(domain["row_count"]), int(domain["distinct_graph_count"])) != (rows, graphs):
            raise AssertionError((name, domain["row_count"], domain["distinct_graph_count"]))
        if int(domain["K2_4_or_K4_2_failure_count"]) <= 0:
            raise AssertionError((name, "missing K2,4 failure"))
        if int(domain["K4_4_failure_count"]) <= 0:
            raise AssertionError((name, "missing K4,4 failure"))
        for key in (
            "maximum_codegree_witness",
            "smallest_codegree_four_witness",
            "smallest_K4_4_witness",
            "smallest_K3_3_witness",
            "maximum_balanced_biclique_witness",
        ):
            verify_outer_record(domain[key])
    return payload


def verify_global() -> dict[str, object]:
    payload = json.loads(GLOBAL.read_text(encoding="ascii"))
    verify_hashes(payload)
    scan = payload["all_shifts_exhaustive"]
    if (int(scan["normalized_rulers"]), int(scan["all_positive_relevant_shifts"])) != (
        2342, 80032
    ):
        raise AssertionError("all-shifts scan count changed")
    witness = scan["smallest_failure"]
    values = tuple(int(value) for value in witness["B"])
    sums = sum_pair_map(values)
    h = int(witness["h"])
    c_s = sum(low + h in sums for low in sums)
    if len(sums) != 15 or c_s != 10 or c_s <= 2 * len(values) - 1:
        raise AssertionError((values, h, len(sums), c_s))
    if int(scan["endpoint_regime"]["failure_count"]) != 0:
        raise AssertionError("endpoint-regime width-20 failure")
    endpoint = payload["p20_endpoint_shift_scan"]
    if (int(endpoint["tested_shifts"]), int(endpoint["failure_count"])) != (
        590650, 122240
    ):
        raise AssertionError("P20 endpoint scan count")
    endpoint_witness = endpoint["smallest_failure"]
    endpoint_values = tuple(int(value) for value in endpoint_witness["B"])
    endpoint_sums = sum_pair_map(endpoint_values)
    endpoint_h = int(endpoint_witness["h"])
    endpoint_c_s = sum(low + endpoint_h in endpoint_sums for low in endpoint_sums)
    if (
        len(endpoint_values) != 29
        or endpoint_values[-1] != endpoint_h - 1
        or len(endpoint_sums) != 435
        or endpoint_c_s != 58
        or endpoint_c_s <= 2 * len(endpoint_values) - 1
    ):
        raise AssertionError((endpoint_values, endpoint_h, len(endpoint_sums), endpoint_c_s))
    return payload


def verify_named() -> dict[str, object]:
    payload = json.loads(NAMED.read_text(encoding="ascii"))
    verify_hashes(payload)
    p53, p75, arbitrary = payload["records"]
    if (int(p53["C_S"]), int(p75["C_S"])) != (49, 51):
        raise AssertionError("named equality count")
    if not bool(p75["literal_hole"]):
        raise AssertionError("P75 literal hole")
    if int(p75["two_sided_max_codegree"]) != 7:
        raise AssertionError("P75 codegree")
    if not bool(p75["contains_K4_4"]):
        raise AssertionError("P75 K4,4")
    if int(arbitrary["C_S"]) != 10:
        raise AssertionError("arbitrary shift witness")
    return payload


def main() -> None:
    outer = verify_outer()
    global_result = verify_global()
    named = verify_named()
    print(json.dumps({
        "status": "verified",
        "outer_domains": {
            name: {
                "rows": domain["row_count"],
                "maximum_pairwise_codegree": domain["maximum_pairwise_codegree"],
                "K4_4_failures": domain["K4_4_failure_count"],
                "maximum_balanced_biclique_order": domain[
                    "maximum_balanced_biclique_order"
                ],
            }
            for name, domain in outer["domains"].items()
        },
        "all_shift_failures": global_result["all_shifts_exhaustive"]["failure_count"],
        "named_records": len(named["records"]),
    }, indent=2))


if __name__ == "__main__":
    main()
