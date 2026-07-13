#!/usr/bin/env python3
"""Independent exact certificate for the positive-defect RM97 falsifier."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PRIMES = (1_000_003, 1_000_033)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p106a = load(
    "p106_positive_analyzer",
    ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py",
)
p106r = load(
    "p106_positive_rank",
    ROOT / "problems/864/compute/p106/verify_endpoint_transfer_and_rigidity.py",
)
p97 = load(
    "p106_positive_independent_matcher",
    ROOT / "problems/864/compute/p97/audit_residual_interval_matching.py",
)


def unique_pair_sums(values):
    seen = {}
    for i, left in enumerate(values):
        for right in values[i:]:
            total = left + right
            if total in seen:
                raise AssertionError((total, seen[total], (left, right)))
            seen[total] = (left, right)
    return seen


def collision_certificate(values, folds, b):
    representations = {}
    for i, left in enumerate(values):
        for right in values[i + 1 :]:
            representations.setdefault(right - left, (left, right))
    rows = []
    for fold_id, fold in enumerate(folds):
        a, c, _u, v = fold
        phase = a + c + b
        if phase not in representations:
            continue
        rows.append(
            {
                "fold_id": fold_id,
                "fold": list(fold),
                "phase_label": phase,
                "difference_pair": list(representations[phase]),
                "extra_slot_L": h_global - b - v,
            }
        )
    return rows


def system_row(values, h, b):
    folds, triangles, intervals, slots, _differences = p106a.residual_system(values, h, b)
    return {
        "p": len(values),
        "h": h,
        "b": b,
        "delta": (3 * len(values) * len(values) - len(values) + 2) // 2 - h,
        "C_S": len(folds),
        "T_F": len(triangles),
        "V_b": len(slots) - 2 * len(folds),
        "intervals": len(intervals),
        "slots": len(slots),
        "scalar_excess": len(intervals) - len(slots),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--hall", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.witness.read_text())
    witness = data["positive_defect_RM97_witness"]
    assert witness is not None
    values = tuple(witness["B"])
    h, b = int(witness["h"]), int(witness["b"])
    global h_global
    h_global = h

    sums = unique_pair_sums(values)
    digest = hashlib.sha256(
        ",".join(map(str, values)).encode("ascii")
    ).hexdigest()
    assert digest == witness["sha256"]
    assert values == tuple(sorted(values))
    assert values[-1] == h - 1
    differences = {
        right - left
        for i, left in enumerate(values)
        for right in values[i + 1 :]
    }
    hole_intersection = differences & {total + b for total in sums}
    assert len(hole_intersection) == 124
    row = system_row(values, h, b)
    assert row == {
        "p": 67,
        "h": 6572,
        "b": 1,
        "delta": 129,
        "C_S": 199,
        "T_F": 221,
        "V_b": 20,
        "intervals": 420,
        "slots": 418,
        "scalar_excess": 2,
    }

    folds, triangles, intervals, slots, _differences = p106a.residual_system(values, h, b)
    transfer_count = p106r.transfer_audit(values, h, b, folds, triangles)
    assert transfer_count == 221
    independent_ok, independent_c, independent_t, independent_v = p97.row_ok(values, h, b)
    assert not independent_ok
    assert (independent_c, independent_t, independent_v) == (199, 221, 20)

    hall = json.loads(args.hall.read_text())
    assert hall["deficient_windows"] == 15
    assert len(hall["minimal_deficient_windows"]) == 2
    window = hall["minimal_deficient_windows"][0]
    assert window["J"] == [-1444, 4730]
    assert window["contained_intervals"] == 411
    assert window["slots_in_J"] == 410
    assert window["deficit"] == 1
    left, right = window["J"]
    contained = [
        index
        for index, interval in enumerate(intervals)
        if left <= interval["left"] and interval["right"] <= right
    ]
    inside_slots = [slot for slot in slots if left <= slot["value"] <= right]
    assert len(contained) == 411 and len(inside_slots) == 410

    used = {
        fold
        for index in contained
        if intervals[index]["kind"] == "loose"
        for fold in intervals[index]["support"]
    }
    used.update(
        intervals[index]["id"]
        for index in contained
        if intervals[index]["kind"] == "canonical"
    )
    matrix = p106r.fold_matrix(values, h, folds)
    used_matrix = [matrix[index] for index in sorted(used)]
    full_ranks = [p106r.modular_rank(matrix, prime) for prime in PRIMES]
    closure_ranks = [p106r.modular_rank(used_matrix, prime) for prime in PRIMES]
    assert full_ranks == closure_ranks == [66, 66]
    assert len(values) + 1 == 68
    difference_gcd = math.gcd(*(mark - values[0] for mark in values[1:]))
    assert difference_gcd == 1

    collisions = collision_certificate(values, folds, b)
    assert len(collisions) == 20
    assert all(left <= collision["extra_slot_L"] <= right for collision in collisions)

    parent_data = json.loads(
        (ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text()
    )["full_P88_q2_lift"]
    parent_values = tuple(parent_data["B"])
    additions = tuple(mark for mark in values if mark not in set(parent_values))
    assert additions == (128, 958, 1916, 3272, 4778, 5924, 6510)
    parent_row = system_row(parent_values, h, b)
    assert parent_row["p"] == 60 and parent_row["delta"] == -1201
    assert parent_row["scalar_excess"] == 18

    baseline = (3 * len(values) * len(values) - len(values) + 2) // 2
    scale_rows = []
    for scale in (1, 2, 3):
        embedded = tuple(scale * mark + scale - 1 for mark in values)
        embedded_h = scale * h
        scaled = system_row(embedded, embedded_h, b)
        scale_rows.append(scaled)
    assert scale_rows[0] == row
    assert scale_rows[1]["V_b"] == scale_rows[2]["V_b"] == 0
    assert scale_rows[1]["delta"] == baseline - 2 * h == -6443

    result = {
        "schema_version": 1,
        "arithmetic": "integer enumeration; modular rank plus two explicit rational null vectors",
        "B": list(values),
        "additions_to_lifted_P88": list(additions),
        "sha256": digest,
        "unique_pair_sums": len(sums),
        "literal_hole": not hole_intersection,
        "literal_hole_intersection_size": len(hole_intersection),
        **row,
        "corrected_scalar_inequality": "T_F <= C_S + V_b",
        "corrected_scalar_left": row["T_F"],
        "corrected_scalar_right": row["C_S"] + row["V_b"],
        "independent_P97_matcher_rejects": not independent_ok,
        "minimal_Hall_windows": [
            candidate["J"] for candidate in hall["minimal_deficient_windows"]
        ],
        "minimal_Hall_window": window["J"],
        "minimal_Hall_window_intervals": window["contained_intervals"],
        "minimal_Hall_window_slots": window["slots_in_J"],
        "minimal_Hall_window_deficit": window["deficit"],
        "minimal_Hall_window_canonical": window["contained_canonical"],
        "minimal_Hall_window_loose": window["contained_loose"],
        "minimal_Hall_window_slot_kinds": window["slot_kind_counts"],
        "minimal_Hall_window_crossing_folds": window["crossing_fold_intervals"],
        "minimal_Hall_window_base_transfers": window["base_transfer_counts"],
        "P83_triangles_checked": transfer_count,
        "collision_certificates": collisions,
        "closure_fold_equations": len(used_matrix),
        "variables_marks_plus_h": len(values) + 1,
        "modular_primes": list(PRIMES),
        "full_ranks": full_ranks,
        "closure_ranks": closure_ranks,
        "exact_rational_rank": 66,
        "exact_rational_nullity": 2,
        "difference_gcd": difference_gcd,
        "parent_row": parent_row,
        "affine_scale_rows": scale_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    concise = {key: value for key, value in result.items() if key not in {"B", "collision_certificates"}}
    print(json.dumps(concise, indent=2))


if __name__ == "__main__":
    main()
