#!/usr/bin/env python3
"""Verify P83 residual transfers and affine rigidity of the P105 closure."""

from __future__ import annotations

import argparse
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


p106 = load("p106_transfer", ROOT / "problems/864/compute/p106/analyze_minimal_hall_interval.py")


def modular_rank(matrix, prime):
    rows = [[value % prime for value in row] for row in matrix]
    height = len(rows)
    width = len(rows[0]) if rows else 0
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, height) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [(value * inverse) % prime for value in rows[rank]]
        for i in range(height):
            if i == rank or rows[i][column] == 0:
                continue
            factor = rows[i][column]
            rows[i] = [
                (left - factor * right) % prime
                for left, right in zip(rows[i], rows[rank])
            ]
        rank += 1
    return rank


def fold_matrix(values, h, folds):
    index = {mark: i for i, mark in enumerate(values)}
    matrix = []
    for a, c, u, v in folds:
        row = [0] * (len(values) + 1)
        row[index[a]] += 1
        row[index[c]] += 1
        row[index[u]] -= 1
        row[index[v]] -= 1
        row[-1] += 1
        matrix.append(row)
        assert sum(row[i] * values[i] for i in range(len(values))) + row[-1] * h == 0
        assert sum(row[:-1]) == 0
    return matrix


def transfer_audit(values, h, b, folds, triangles):
    checked = 0
    for base, arm_au, arm_cu in triangles:
        a, c, r, s = folds[base]
        aa, z, u, w = folds[arm_au]
        x, cc, uu, y = folds[arm_cu]
        assert (aa, cc, uu) == (a, c, u)
        X, Z, R = x - a, z - c, r - u
        tau, lam = u - a - c - b, h - b - u
        residuals = [
            (h - b - s, h - b - r),
            (h - b - w, h - b - u),
            (h - b - y, h - b - u),
        ]
        assert residuals == [
            (tau + R, lam - R),
            (tau - Z, lam),
            (tau - X, lam),
        ]
        assert sum(residuals[0]) == tau + lam
        assert tau - residuals[1][0] == Z
        assert tau - residuals[2][0] == X
        # In the fixed-u arm graph, orient arm_au -> arm_cu.
        # These two identities telescope on every directed cycle.
        assert tau - residuals[1][0] == z - c
        assert tau - residuals[2][0] == x - a
        checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads((ROOT / "problems/864/compute/p105/corrected_c84_falsifier.json").read_text())
    source = data["subset_search"]["source_subset"]
    lifted = data["subset_search"]["q2_lifted_witness"]
    hall = json.loads((ROOT / "problems/864/compute/p106/p105_minimal_hall.json").read_text())
    window = hall["minimal_deficient_windows"][0]

    values = tuple(lifted["B"])
    h, b = int(lifted["h"]), int(lifted["b"])
    folds, triangles, intervals, _slots, _differences = p106.residual_system(values, h, b)
    assert folds == [tuple(row) for row in lifted["folds"]]
    assert set(triangles) == {tuple(row) for row in lifted["triangles"]}
    transfer_count = transfer_audit(values, h, b, folds, triangles)

    used = {fold for triangle in triangles for fold in triangle}
    left, right = window["J"]
    for fold_id, interval in enumerate(intervals[:len(folds)]):
        if left <= interval["left"] and interval["right"] <= right:
            used.add(fold_id)
    assert len(used) == 156

    matrix = fold_matrix(values, h, folds)
    used_matrix = [matrix[i] for i in sorted(used)]
    all_ranks = [modular_rank(matrix, prime) for prime in PRIMES]
    used_ranks = [modular_rank(used_matrix, prime) for prime in PRIMES]
    assert all_ranks == used_ranks == [56, 56]
    # Translation and the displayed coordinates are independent rational
    # null vectors, so rank <= 56.  Modular rank 56 gives rational rank >= 56.
    assert len(values) + 1 == 58

    source_values = tuple(source["B"])
    assert values == tuple(2 * mark + 1 for mark in source_values)
    assert h == 2 * int(source["h"])
    difference_gcd = math.gcd(*(mark - source_values[0] for mark in source_values[1:]))
    assert difference_gcd == 1

    p = len(source_values)
    baseline = (3 * p * p - p + 2) // 2
    rows = []
    for scale in range(1, 5):
        endpoint_translation = scale - 1
        embedded = tuple(scale * mark + endpoint_translation for mark in source_values)
        embedded_h = scale * int(source["h"])
        correction = p106.residual_system(embedded, embedded_h, 1)[3]
        V_b = len(correction) - 2 * len(folds)
        rows.append({
            "scale": scale, "h": embedded_h,
            "delta": baseline - embedded_h,
            "V_b": V_b,
        })
    assert rows[0]["delta"] == 1560 and rows[0]["V_b"] == 68
    assert rows[1]["delta"] == -1726 and rows[1]["V_b"] == 0
    assert all(row["V_b"] == 0 for row in rows[1:])

    result = {
        "P83_triangles_checked": transfer_count,
        "minimal_Hall_window": window["J"],
        "Hall_deficit": window["deficit"],
        "fold_equations_total": len(matrix),
        "fold_equations_used_by_closure": len(used_matrix),
        "variables_marks_plus_h": len(values) + 1,
        "modular_primes": list(PRIMES),
        "full_ranks": all_ranks,
        "closure_ranks": used_ranks,
        "exact_rational_rank": 56,
        "exact_rational_nullity": 2,
        "source_difference_gcd": difference_gcd,
        "source_h": source["h"],
        "source_p": p,
        "positive_defect_baseline": baseline,
        "affine_scale_rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
